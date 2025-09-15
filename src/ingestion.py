"""
EcoMap.BR - Data Ingestion Pipeline
Módulo principal para ingestão e padronização de dados de todas as fontes
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Union, Optional, Any
import pandas as pd
import polars as pl

from .utils.io_utils import DataLoader, safe_mkdir, save_dataframe
from .utils.data_cleaning import DataCleaner, standardize_column_names
from .utils.validation import DataValidator, QualityChecker

logger = logging.getLogger(__name__)


class EcoMapIngester:
    """
    Classe principal para ingestão de dados do projeto EcoMap.
    """
    
    def __init__(self, config_path: Union[str, Dict[str, Any]] = "config/config.yaml"):
        """
        Args:
            config_path: Caminho para arquivo de configuração ou dict com configurações
        """
        self.config = self._load_config(config_path)
        
        # Inicializa componentes
        engine = self.config['performance']['preferred_engine']
        chunk_size = self.config['performance'].get('chunk_size')
        
        self.engine = engine  # Armazena engine como atributo da instância
        self.loader = DataLoader(engine=engine, chunk_size=chunk_size)
        self.cleaner = DataCleaner(engine=engine)
        self.validator = DataValidator(engine=engine)
        self.quality_checker = QualityChecker(engine=engine)
        
        # Cria diretórios de saída
        self._setup_output_directories()
        
        logger.info(f"EcoMapIngester inicializado com engine: {engine}")
    
    def _load_config(self, config_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Carrega configurações do arquivo YAML ou dict."""
        if isinstance(config_input, dict):
            return config_input
        else:
            with open(config_input, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    
    def _setup_output_directories(self) -> None:
        """Cria estrutura de diretórios de saída."""
        directories = [
            self.config['paths']['clean_data'],
            self.config['paths']['derived_data'],
            self.config['paths']['figures'],
            self.config['paths']['reports'],
            self.config['paths'].get('logs', './logs')
        ]
        
        for directory in directories:
            safe_mkdir(directory)
    
    def ingest_all_sources(self) -> Dict[str, Union[pd.DataFrame, pl.DataFrame, None]]:
        """
        Executa ingestão de todas as fontes de dados configuradas.
        
        Returns:
            Dicionário com DataFrames carregados por fonte
        """
        logger.info("Iniciando ingestão de todas as fontes de dados...")
        
        ingested_data = {}
        
        # Carrega cada fonte configurada
        for source_name, source_config in self.config['data_sources'].items():
            if source_config.get('available', True):
                logger.info(f"Processando fonte: {source_name}")
                try:
                    df = self._ingest_source(source_name, source_config)
                    if df is not None and len(df) > 0:
                        ingested_data[source_name] = df
                        logger.info(f"Fonte {source_name} carregada com sucesso: {len(df)} linhas")
                    else:
                        logger.warning(f"Fonte {source_name} retornou dados vazios")
                        ingested_data[source_name] = None
                except Exception as e:
                    logger.error(f"Erro ao processar fonte {source_name}: {str(e)}")
                    ingested_data[source_name] = None
            else:
                logger.info(f"Fonte {source_name} marcada como indisponível - pulando")
                ingested_data[source_name] = None
        
        # Salva dados limpos
        self._save_clean_data(ingested_data)
        
        # Gera relatórios de qualidade
        self._generate_quality_reports(ingested_data)
        
        logger.info("Ingestão completa!")
        return ingested_data
    
    def _ingest_source(self, source_name: str, source_config: Dict[str, Any]) -> Union[pd.DataFrame, pl.DataFrame, None]:
        """
        Processa uma fonte específica de dados.
        
        Args:
            source_name: Nome da fonte
            source_config: Configuração da fonte
            
        Returns:
            DataFrame processado ou None
        """
        source_path = Path(source_config['path'])
        
        if not source_path.exists():
            logger.warning(f"Diretório da fonte {source_name} não encontrado: {source_path}")
            return None
        
        # Carrega arquivos da fonte com harmonização de esquemas
        pattern = source_config.get('pattern', '*.csv')
        dataframes = self.loader.load_directory(source_path, pattern=pattern, combine=False)  # Não combina imediatamente
        
        if isinstance(dataframes, dict) and not dataframes:
            logger.warning(f"Nenhum arquivo encontrado para fonte {source_name}")
            return None
        
        # Se retornou dicionário vazio ou DataFrame vazio
        if isinstance(dataframes, dict):
            # Harmonizar esquemas antes de combinar
            df = self._harmonize_schemas(dataframes, source_name)
            if df is None:
                logger.warning(f"Falha na harmonização de esquemas para fonte {source_name}")
                return None
        else:
            df = dataframes
        
        # Aplica padronização de colunas
        df = standardize_column_names(df)
        
        # Aplica limpeza específica da fonte
        df = self._apply_source_specific_cleaning(df, source_name)
        
        # Aplica filtros geográficos e temporais
        df = self._apply_filters(df, source_name)
        
        # Validação
        self._validate_source_data(df, source_name)
        
        return df
    
    def _harmonize_schemas(self, dataframes_dict: Dict[str, Union[pd.DataFrame, pl.DataFrame]], 
                          source_name: str) -> Union[pd.DataFrame, pl.DataFrame, None]:
        """
        Harmoniza esquemas de diferentes arquivos da mesma fonte.
        
        Args:
            dataframes_dict: Dicionário de DataFrames por arquivo
            source_name: Nome da fonte de dados
            
        Returns:
            DataFrame harmonizado ou None se falhar
        """
        try:
            if not dataframes_dict:
                return None
            
            logger.info(f"Harmonizando esquemas para fonte {source_name}: {len(dataframes_dict)} arquivos")
            
            # Filtrar DataFrames válidos (não vazios)
            valid_dfs = {name: df for name, df in dataframes_dict.items() 
                        if df is not None and len(df) > 0}
            
            if not valid_dfs:
                logger.warning(f"Nenhum DataFrame válido para fonte {source_name}")
                return None
            
            if len(valid_dfs) == 1:
                # Apenas um DataFrame válido
                return list(valid_dfs.values())[0]
            
            # Estratégias de harmonização por fonte
            if source_name == 'rais':
                return self._harmonize_rais_schemas(valid_dfs)
            elif source_name == 'comexstat':
                return self._harmonize_comexstat_schemas(valid_dfs)
            else:
                # Harmonização genérica
                return self._harmonize_generic_schemas(valid_dfs)
                
        except Exception as e:
            logger.error(f"Erro na harmonização de esquemas para {source_name}: {str(e)}")
            return None
    
    def _harmonize_rais_schemas(self, dataframes_dict: Dict[str, Union[pd.DataFrame, pl.DataFrame]]) -> Union[pd.DataFrame, pl.DataFrame, None]:
        """Harmonização específica para arquivos RAIS."""
        try:
            # Identifica o DataFrame com mais colunas (mais completo)
            df_sizes = {name: len(df.columns) for name, df in dataframes_dict.items()}
            main_df_name = max(df_sizes, key=df_sizes.get)
            main_df = dataframes_dict[main_df_name]
            
            logger.info(f"RAIS: Usando {main_df_name} como base ({df_sizes[main_df_name]} colunas)")
            
            # Concatena outros DataFrames compatíveis
            compatible_dfs = [main_df]
            
            for name, df in dataframes_dict.items():
                if name == main_df_name:
                    continue
                    
                # Verifica se tem colunas suficientemente semelhantes
                common_cols = set(df.columns) & set(main_df.columns)
                if len(common_cols) >= min(3, len(df.columns)):  # Pelo menos 3 colunas em comum ou todas
                    # Seleciona apenas colunas comuns
                    if self.engine == 'polars':
                        aligned_df = df.select([col for col in common_cols])
                    else:
                        aligned_df = df[list(common_cols)]
                    compatible_dfs.append(aligned_df)
                    logger.info(f"RAIS: Incluindo {name} com {len(common_cols)} colunas comuns")
                else:
                    logger.warning(f"RAIS: Pulando {name} - poucas colunas em comum ({len(common_cols)})")
            
            # Concatena DataFrames compatíveis
            if len(compatible_dfs) > 1:
                if self.engine == 'polars':
                    result = pl.concat(compatible_dfs, how='diagonal')
                else:
                    result = pd.concat(compatible_dfs, ignore_index=True, sort=False)
                logger.info(f"RAIS harmonizado: {len(compatible_dfs)} arquivos, {len(result)} linhas")
                return result
            else:
                return main_df
                
        except Exception as e:
            logger.error(f"Erro na harmonização RAIS: {str(e)}")
            return None
    
    def _harmonize_comexstat_schemas(self, dataframes_dict: Dict[str, Union[pd.DataFrame, pl.DataFrame]]) -> Union[pd.DataFrame, pl.DataFrame, None]:
        """Harmonização específica para arquivos ComexStat."""
        try:
            # Identifica colunas essenciais do comércio exterior
            essential_cols = ['municipio', 'produto', 'valor', 'ano', 'mes']
            
            harmonized_dfs = []
            
            for name, df in dataframes_dict.items():
                # Mapeia colunas essenciais
                column_mapping = {}
                df_cols_lower = {col.lower(): col for col in df.columns}
                
                for essential in essential_cols:
                    for col_lower, col_original in df_cols_lower.items():
                        if essential in col_lower or col_lower.startswith(essential):
                            column_mapping[col_original] = essential
                            break
                
                if column_mapping:
                    # Renomeia e seleciona colunas mapeadas
                    if self.engine == 'polars':
                        renamed_df = df.rename(column_mapping)
                        selected_cols = [col for col in essential_cols if col in renamed_df.columns]
                        if selected_cols:
                            aligned_df = renamed_df.select(selected_cols)
                            harmonized_dfs.append(aligned_df)
                    else:
                        aligned_df = df.rename(columns=column_mapping)
                        selected_cols = [col for col in essential_cols if col in aligned_df.columns]
                        if selected_cols:
                            aligned_df = aligned_df[selected_cols]
                            harmonized_dfs.append(aligned_df)
                    
                    logger.info(f"ComexStat: Harmonizado {name} com {len(selected_cols)} colunas")
            
            if harmonized_dfs:
                if self.engine == 'polars':
                    result = pl.concat(harmonized_dfs, how='diagonal')
                else:
                    result = pd.concat(harmonized_dfs, ignore_index=True, sort=False)
                logger.info(f"ComexStat harmonizado: {len(harmonized_dfs)} arquivos, {len(result)} linhas")
                return result
            else:
                # Se não conseguir harmonizar, retorna o maior DataFrame
                largest_df = max(dataframes_dict.values(), key=len)
                logger.warning("ComexStat: Usando maior DataFrame sem harmonização")
                return largest_df
                
        except Exception as e:
            logger.error(f"Erro na harmonização ComexStat: {str(e)}")
            return None
    
    def _harmonize_generic_schemas(self, dataframes_dict: Dict[str, Union[pd.DataFrame, pl.DataFrame]]) -> Union[pd.DataFrame, pl.DataFrame, None]:
        """Harmonização genérica para outras fontes."""
        try:
            # Encontra colunas comuns a todos os DataFrames
            all_columns = [set(df.columns) for df in dataframes_dict.values()]
            common_columns = set.intersection(*all_columns) if all_columns else set()
            
            if len(common_columns) >= 2:  # Pelo menos 2 colunas comuns
                compatible_dfs = []
                for name, df in dataframes_dict.items():
                    if self.engine == 'polars':
                        aligned_df = df.select(list(common_columns))
                    else:
                        aligned_df = df[list(common_columns)]
                    compatible_dfs.append(aligned_df)
                
                if self.engine == 'polars':
                    result = pl.concat(compatible_dfs, how='diagonal')
                else:
                    result = pd.concat(compatible_dfs, ignore_index=True)
                
                logger.info(f"Harmonização genérica: {len(common_columns)} colunas comuns, {len(result)} linhas")
                return result
            else:
                # Retorna o maior DataFrame
                largest_df = max(dataframes_dict.values(), key=len)
                logger.warning("Harmonização genérica: Usando maior DataFrame sem harmonização")
                return largest_df
                
        except Exception as e:
            logger.error(f"Erro na harmonização genérica: {str(e)}")
            return None

    def _apply_source_specific_cleaning(self, 
                                      df: Union[pd.DataFrame, pl.DataFrame], 
                                      source_name: str) -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Aplica limpeza específica para cada fonte de dados.
        
        Args:
            df: DataFrame a ser limpo
            source_name: Nome da fonte
            
        Returns:
            DataFrame limpo
        """
        if source_name == 'rais':
            return self._clean_rais_data(df)
        elif source_name == 'caged':
            return self._clean_caged_data(df)
        elif source_name == 'pib':
            return self._clean_pib_data(df)
        elif source_name == 'comexstat':
            return self._clean_comexstat_data(df)
        elif source_name == 'dataviva':
            return self._clean_dataviva_data(df)
        else:
            # Limpeza genérica
            return self._apply_generic_cleaning(df)
    
    def _clean_rais_data(self, df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
        """Limpeza específica para dados RAIS."""
        logger.info("Aplicando limpeza específica para dados RAIS...")
        
        # Padronização de nomes geográficos
        geographic_columns = [col for col in df.columns 
                            if any(geo in col.lower() for geo in ['municipio', 'uf', 'estado'])]
        if geographic_columns:
            df = self.cleaner.standardize_geographic_names(df, geographic_columns)
        
        # Limpeza de colunas numéricas (salários, vínculos)
        numeric_columns = [col for col in df.columns 
                          if any(num in col.lower() for num in ['remuneracao', 'salario', 'vinculo', 'valor'])]
        if numeric_columns:
            df = self.cleaner.clean_numeric_columns(df, numeric_columns)
        
        # Remove duplicatas
        subset_cols = [col for col in df.columns 
                      if any(key in col.lower() for key in ['ano', 'municipio', 'cnae'])]
        if len(subset_cols) >= 2:
            df = self.cleaner.remove_duplicates(df, subset=subset_cols)
        
        return df
    
    def _clean_caged_data(self, df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
        """Limpeza específica para dados CAGED."""
        logger.info("Aplicando limpeza específica para dados CAGED...")
        
        # Similar à RAIS, mas com foco em admissões/dispensas
        geographic_columns = [col for col in df.columns 
                            if any(geo in col.lower() for geo in ['municipio', 'uf', 'estado'])]
        if geographic_columns:
            df = self.cleaner.standardize_geographic_names(df, geographic_columns)
        
        numeric_columns = [col for col in df.columns 
                          if any(num in col.lower() for num in ['admiss', 'desligam', 'saldo', 'estoque'])]
        if numeric_columns:
            df = self.cleaner.clean_numeric_columns(df, numeric_columns)
        
        return df
    
    def _clean_pib_data(self, df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
        """Limpeza específica para dados PIB."""
        logger.info("Aplicando limpeza específica para dados PIB...")
        
        # Limpeza de valores monetários
        numeric_columns = [col for col in df.columns 
                          if any(num in col.lower() for num in ['pib', 'valor', 'produto', 'bruto'])]
        if numeric_columns:
            df = self.cleaner.clean_numeric_columns(df, numeric_columns)
        
        return df
    
    def _clean_comexstat_data(self, df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
        """Limpeza específica para dados ComexStat."""
        logger.info("Aplicando limpeza específica para dados ComexStat...")
        
        # Limpeza de valores de comércio exterior
        numeric_columns = [col for col in df.columns 
                          if any(num in col.lower() for num in ['valor', 'peso', 'quantidade', 'fob', 'usd'])]
        if numeric_columns:
            df = self.cleaner.clean_numeric_columns(df, numeric_columns)
        
        return df
    
    def _clean_dataviva_data(self, df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
        """Limpeza específica para dados DataViva."""
        logger.info("Aplicando limpeza específica para dados DataViva...")
        
        # Limpeza de múltiplos tipos de dados do DataViva
        numeric_columns = [col for col in df.columns 
                          if any(num in col.lower() for num in ['wage', 'num_jobs', 'growth', 'rca', 'eci'])]
        if numeric_columns:
            df = self.cleaner.clean_numeric_columns(df, numeric_columns)
        
        return df
    
    def _apply_generic_cleaning(self, df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
        """Aplica limpeza genérica."""
        logger.info("Aplicando limpeza genérica...")
        
        # Remove duplicatas completamente iguais
        df = self.cleaner.remove_duplicates(df)
        
        return df
    
    def _apply_filters(self, 
                      df: Union[pd.DataFrame, pl.DataFrame], 
                      source_name: str) -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Aplica filtros geográficos e temporais configurados.
        
        Args:
            df: DataFrame a ser filtrado
            source_name: Nome da fonte
            
        Returns:
            DataFrame filtrado
        """
        original_count = len(df)
        
        # Filtro geográfico - UF
        uf_columns = [col for col in df.columns if 'uf' in col.lower()]
        if uf_columns:
            uf_col = uf_columns[0]
            target_uf = self.config['geographic_filters']['uf_alvo']
            
            if isinstance(df, pd.DataFrame):
                df = df[df[uf_col].str.contains(target_uf, case=False, na=False)]
            else:  # polars
                df = df.filter(pl.col(uf_col).str.contains(f"(?i){target_uf}"))
        
        # Filtro geográfico - Município
        municipio_columns = [col for col in df.columns if 'municipio' in col.lower()]
        if municipio_columns:
            municipio_col = municipio_columns[0]
            target_municipio = self.config['geographic_filters']['municipio_principal']
            
            if isinstance(df, pd.DataFrame):
                df = df[df[municipio_col].str.contains(target_municipio, case=False, na=False)]
            else:  # polars
                df = df.filter(pl.col(municipio_col).str.contains(f"(?i){target_municipio}"))
        
        # Filtro temporal
        year_columns = [col for col in df.columns if 'ano' in col.lower() or 'year' in col.lower()]
        if year_columns:
            year_col = year_columns[0]
            min_year = self.config['temporal_filters']['periodo_inicial']
            max_year = self.config['temporal_filters']['periodo_final']
            
            if isinstance(df, pd.DataFrame):
                df = df[(df[year_col] >= min_year) & (df[year_col] <= max_year)]
            else:  # polars
                df = df.filter((pl.col(year_col) >= min_year) & (pl.col(year_col) <= max_year))
        
        filtered_count = len(df)
        logger.info(f"Fonte {source_name}: {original_count} -> {filtered_count} linhas após filtros "
                   f"({(filtered_count/original_count)*100:.1f}% mantidas)")
        
        return df
    
    def _validate_source_data(self, 
                             df: Union[pd.DataFrame, pl.DataFrame], 
                             source_name: str) -> None:
        """Executa validações específicas da fonte."""
        required_columns = self.config['data_quality']['required_columns'].get(source_name, [])
        
        if required_columns:
            self.validator.validate_required_columns(df, required_columns, source_name)
        
        # Verifica valores ausentes
        missing_threshold = self.config['data_quality']['thresholds']['missing_data_percent']
        self.validator.check_missing_values(df, missing_threshold, source_name)
        
        # Verifica tamanho mínimo
        min_rows = self.config['data_quality']['thresholds']['minimum_rows_per_source']
        if len(df) < min_rows:
            logger.warning(f"Fonte {source_name} tem apenas {len(df)} linhas (mínimo: {min_rows})")
    
    def _save_clean_data(self, ingested_data: Dict[str, Union[pd.DataFrame, pl.DataFrame, None]]) -> None:
        """Salva dados limpos no diretório de saída."""
        clean_dir = Path(self.config['paths']['clean_data'])
        
        for source_name, df in ingested_data.items():
            if df is not None:
                output_path = clean_dir / f"{source_name}_clean.csv"
                save_dataframe(df, output_path, format="csv")
                logger.info(f"Dados limpos salvos: {output_path}")
    
    def _generate_quality_reports(self, ingested_data: Dict[str, Union[pd.DataFrame, pl.DataFrame, None]]) -> None:
        """Gera relatórios de qualidade dos dados."""
        # Relatório de validação
        validation_report = self.validator.get_validation_report()
        validation_path = Path(self.config['paths']['derived_data']) / "quality_checks.csv"
        validation_report.to_csv(validation_path, index=False, encoding='utf-8')
        logger.info(f"Relatório de validação salvo: {validation_path}")
        
        # Relatórios de qualidade por fonte
        quality_reports = {}
        for source_name, df in ingested_data.items():
            if df is not None:
                quality_report = self.quality_checker.generate_quality_report(df, source_name)
                quality_reports[source_name] = quality_report
        
        # Salva relatórios de qualidade
        if quality_reports:
            import json
            quality_path = Path(self.config['paths']['derived_data']) / "data_quality_report.json"
            with open(quality_path, 'w', encoding='utf-8') as f:
                json.dump(quality_reports, f, indent=2, default=str)
            logger.info(f"Relatório de qualidade salvo: {quality_path}")


def main():
    """Função principal para execução standalone."""
    logging.basicConfig(level=logging.INFO)
    
    ingester = EcoMapIngester()
    data = ingester.ingest_all_sources()
    
    print("\n=== RESUMO DA INGESTÃO ===")
    for source, df in data.items():
        if df is not None:
            print(f"{source}: {len(df)} linhas, {len(df.columns)} colunas")
        else:
            print(f"{source}: FALHOU ou VAZIO")


if __name__ == "__main__":
    main()