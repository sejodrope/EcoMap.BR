"""
EcoMap.BR - Command Line Interface
Interface principal do pipeline de análise econômica
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Imports dos módulos locais
from src.utils.io_utils import DataLoader
from src.utils.data_cleaning import DataCleaner
from src.utils.validation import DataValidator, QualityChecker
from src.ingestion import EcoMapIngester
from src.indicators import calculate_all_indicators
from src.visualization import create_all_visualizations

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecomap.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Carrega configurações do arquivo YAML."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configurações carregadas de {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Arquivo de configuração não encontrado: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}")
        sys.exit(1)


def setup_directories(config: Dict[str, Any]) -> None:
    """Cria diretórios necessários para o pipeline."""
    paths = config['paths']
    
    for path_key, path_value in paths.items():
        path_obj = Path(path_value)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório criado: {path_value}")


def cmd_ingest(args, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comando para ingestão de dados de todas as fontes.
    
    Args:
        args: Argumentos da linha de comando
        config: Configurações do projeto
        
    Returns:
        Dicionário com dados ingeridos
    """
    logger.info("=== INICIANDO INGESTÃO DE DADOS ===")
    
    ingester = EcoMapIngester(config)
    
    # Lista de fontes a processar
    sources = args.sources if args.sources else ["all"]
    
    if "all" in sources:
        logger.info("Processando todas as fontes de dados...")
        data_dict = ingester.ingest_all_sources()
    else:
        logger.info(f"Processando fontes específicas: {sources}")
        data_dict = {}
        
        for source in sources:
            try:
                if source.lower() == "rais":
                    data_dict[source] = ingester.ingest_rais_data()
                elif source.lower() == "caged":
                    data_dict[source] = ingester.ingest_caged_data()
                elif source.lower() == "pib":
                    data_dict[source] = ingester.ingest_pib_data()
                elif source.lower() == "comexstat":
                    data_dict[source] = ingester.ingest_comexstat_data()
                elif source.lower() == "dataviva":
                    data_dict[source] = ingester.ingest_dataviva_data()
                else:
                    logger.warning(f"Fonte desconhecida: {source}")
            except Exception as e:
                logger.error(f"Erro ao processar fonte {source}: {str(e)}")
    
    # Salva dados processados
    output_path = Path(config['paths']['outputs']) / "processed_data"
    output_path.mkdir(parents=True, exist_ok=True)
    
    for source_name, df in data_dict.items():
        if df is not None and len(df) > 0:
            logger.info(f"Tipo de DataFrame para {source_name}: {type(df)}")
            if hasattr(df, 'write_parquet'):  # polars
                df.write_parquet(output_path / f"{source_name}.parquet")
                logger.info(f"[OK] {source_name}: {len(df)} registros salvos (Polars)")
            elif hasattr(df, 'to_parquet'):  # pandas
                df.to_parquet(output_path / f"{source_name}.parquet", index=False)
                logger.info(f"[OK] {source_name}: {len(df)} registros salvos (Pandas)")
            else:
                logger.error(f"DataFrame de {source_name} não tem método parquet: {type(df)}")
    
    logger.info("=== INGESTÃO CONCLUÍDA ===")
    return data_dict


def cmd_derive(args, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comando para calcular indicadores econômicos derivados.
    
    Args:
        args: Argumentos da linha de comando
        config: Configurações do projeto
        
    Returns:
        Dicionário com indicadores calculados
    """
    logger.info("=== CALCULANDO INDICADORES DERIVADOS ===")
    
    # Carrega dados processados
    data_dict = {}
    processed_path = Path(config['paths']['outputs']) / "processed_data"
    
    if not processed_path.exists():
        logger.error("Dados processados não encontrados. Execute 'ingest' primeiro.")
        sys.exit(1)
    
    for parquet_file in processed_path.glob("*.parquet"):
        source_name = parquet_file.stem
        try:
            # Decide se usa pandas ou polars baseado na config
            if config['performance']['preferred_engine'] == 'polars':
                import polars as pl
                df = pl.read_parquet(parquet_file)
            else:
                import pandas as pd
                df = pd.read_parquet(parquet_file)
            
            data_dict[source_name] = df
            logger.info(f"[OK] {source_name}: {len(df)} registros carregados")
        except Exception as e:
            logger.error(f"Erro ao carregar {source_name}: {str(e)}")
    
    # Calcula indicadores
    indicators_dict = calculate_all_indicators(data_dict)
    
    # Salva indicadores
    indicators_path = Path(config['paths']['outputs']) / "indicators"
    indicators_path.mkdir(parents=True, exist_ok=True)
    
    for indicator_name, result in indicators_dict.items():
        try:
            if result is not None:
                if hasattr(result, 'to_parquet'):  # polars DataFrame
                    result.write_parquet(indicators_path / f"{indicator_name}.parquet")
                elif hasattr(result, 'to_json'):  # pandas DataFrame
                    result.to_parquet(indicators_path / f"{indicator_name}.parquet", index=False)
                else:  # Dict ou outro formato
                    import pickle
                    with open(indicators_path / f"{indicator_name}.pkl", 'wb') as f:
                        pickle.dump(result, f)
                logger.info(f"[OK] {indicator_name} salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar {indicator_name}: {str(e)}")
    
    logger.info("=== CÁLCULO DE INDICADORES CONCLUÍDO ===")
    return indicators_dict


def cmd_visualize(args, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comando para criar visualizações dos dados e indicadores.
    
    Args:
        args: Argumentos da linha de comando
        config: Configurações do projeto
        
    Returns:
        Dicionário com figuras criadas
    """
    logger.info("=== CRIANDO VISUALIZAÇÕES ===")
    
    # Carrega indicadores
    indicators_dict = {}
    indicators_path = Path(config['paths']['outputs']) / "indicators"
    
    if not indicators_path.exists():
        logger.error("Indicadores não encontrados. Execute 'derive' primeiro.")
        sys.exit(1)
    
    for indicator_file in indicators_path.glob("*"):
        indicator_name = indicator_file.stem
        try:
            if indicator_file.suffix == '.parquet':
                # Decide engine baseado na config
                if config['performance']['preferred_engine'] == 'polars':
                    import polars as pl
                    result = pl.read_parquet(indicator_file)
                else:
                    import pandas as pd
                    result = pd.read_parquet(indicator_file)
            elif indicator_file.suffix == '.pkl':
                import pickle
                with open(indicator_file, 'rb') as f:
                    result = pickle.load(f)
            else:
                continue
            
            indicators_dict[indicator_name] = result
            logger.info(f"[OK] {indicator_name} carregado")
        except Exception as e:
            logger.error(f"Erro ao carregar {indicator_name}: {str(e)}")
    
    # Cria visualizações
    figures_dict = create_all_visualizations(indicators_dict, config)
    
    logger.info(f"[OK] {len(figures_dict)} visualizações criadas")
    logger.info("=== VISUALIZAÇÕES CONCLUÍDAS ===")
    return figures_dict


def cmd_report(args, config: Dict[str, Any]) -> str:
    """
    Comando para gerar relatório automatizado.
    
    Args:
        args: Argumentos da linha de comando
        config: Configurações do projeto
        
    Returns:
        Caminho do relatório gerado
    """
    logger.info("=== GERANDO RELATÓRIO AUTOMATIZADO ===")
    
    # Implementação simplificada do relatório
    report_path = Path(config['paths']['outputs']) / "reports"
    report_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = report_path / f"relatorio_ecomap_{timestamp}.md"
    
    # Template básico de relatório
    report_content = f"""# Relatório EcoMap.BR - Análise Econômica

**Data:** {time.strftime("%d/%m/%Y %H:%M:%S")}
**Região de Foco:** {config['geographic']['target_municipality']}
**Período:** {config['temporal']['start_year']} - {config['temporal']['end_year']}

## Resumo Executivo

Este relatório apresenta a análise econômica da região de {config['geographic']['target_municipality']} 
com base nos dados das seguintes fontes:

- RAIS (Relação Anual de Informações Sociais)
- CAGED (Cadastro Geral de Empregados e Desempregados)
- PIB Municipal (IBGE)
- ComexStat (Dados de Exportação/Importação)
- DataViva (Indicadores Complementares)

## Indicadores Calculados

### Location Quotient (LQ)
Mede a especialização setorial da região comparada ao país.

### Vantagem Comparativa Revelada (RCA)
Identifica produtos com vantagem competitiva nas exportações.

### Índice de Concentração Herfindahl-Hirschman (HHI)
Avalia o grau de concentração setorial da economia local.

### Análise de Crescimento
Taxa de crescimento do emprego e PIB em diferentes períodos.

### Decomposição Sazonal
Análise da sazonalidade nos dados de emprego mensal.

## Visualizações

As seguintes visualizações foram geradas:

1. Dashboard Interativo de Indicadores
2. Treemap do Location Quotient
3. Séries Temporais de Crescimento
4. Decomposição Sazonal
5. Matriz de Correlação

## Recomendações

### Setores Estratégicos
Com base no Location Quotient, os setores com maior especialização são...

### Oportunidades de Exportação
A análise RCA indica potencial de crescimento em...

### Diversificação Econômica
O HHI sugere nível de concentração...

---

*Relatório gerado automaticamente pelo sistema EcoMap.BR*
*Para mais detalhes, consulte as visualizações interativas*
"""
    
    # Salva relatório
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"[OK] Relatório gerado: {report_file}")
    logger.info("=== RELATÓRIO CONCLUÍDO ===")
    return str(report_file)


def cmd_all(args, config: Dict[str, Any]) -> None:
    """
    Comando para executar todo o pipeline completo.
    
    Args:
        args: Argumentos da linha de comando
        config: Configurações do projeto
    """
    logger.info("=== EXECUTANDO PIPELINE COMPLETO ===")
    
    # Cronometra execução
    start_time = time.time()
    
    try:
        # Cria um objeto args simulado para cada comando
        from argparse import Namespace
        
        # 1. Ingestão
        logger.info("Etapa 1/4: Ingestão de dados")
        ingest_args = Namespace(sources=None)  # None significa todas as fontes
        data_dict = cmd_ingest(ingest_args, config)
        
        # 2. Cálculo de indicadores
        logger.info("Etapa 2/4: Cálculo de indicadores")
        derive_args = Namespace(indicators=None)  # None significa todos os indicadores
        indicators_dict = cmd_derive(derive_args, config)
        
        # 3. Visualizações
        logger.info("Etapa 3/4: Criação de visualizações")
        viz_args = Namespace(type='all')
        figures_dict = cmd_visualize(viz_args, config)
        
        # 4. Relatório
        logger.info("Etapa 4/4: Geração de relatório")
        report_args = Namespace(format='markdown')
        report_path = cmd_report(report_args, config)
        
        # Resumo final
        elapsed_time = time.time() - start_time
        logger.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")
        logger.info(f"Tempo total: {elapsed_time:.2f} segundos")
        logger.info(f"Dados processados: {len(data_dict)} fontes")
        logger.info(f"Indicadores calculados: {len(indicators_dict)}")
        logger.info(f"Visualizações criadas: {len(figures_dict)}")
        logger.info(f"Relatório: {report_path}")
        
    except Exception as e:
        logger.error(f"Erro na execução do pipeline: {str(e)}")
        sys.exit(1)


def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description="EcoMap.BR - Pipeline de Análise Econômica",
        epilog="Exemplo: python main.py all --config config/config.yaml"
    )
    
    # Argumentos globais
    parser.add_argument(
        "--config", "-c",
        default="config/config.yaml",
        help="Caminho para arquivo de configuração (padrão: config/config.yaml)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Saída detalhada (modo DEBUG)"
    )
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando ingest
    ingest_parser = subparsers.add_parser('ingest', help='Ingerir e limpar dados das fontes')
    ingest_parser.add_argument(
        '--sources', '-s',
        nargs='+',
        choices=['rais', 'caged', 'pib', 'comexstat', 'dataviva', 'all'],
        help='Fontes específicas para processar (padrão: all)'
    )
    
    # Comando derive
    derive_parser = subparsers.add_parser('derive', help='Calcular indicadores econômicos')
    derive_parser.add_argument(
        '--indicators', '-i',
        nargs='+',
        help='Indicadores específicos para calcular'
    )
    
    # Comando visualize  
    viz_parser = subparsers.add_parser('viz', help='Criar visualizações')
    viz_parser.add_argument(
        '--type', '-t',
        choices=['dashboard', 'timeseries', 'treemap', 'heatmap', 'all'],
        default='all',
        help='Tipo de visualização (padrão: all)'
    )
    
    # Comando report
    report_parser = subparsers.add_parser('report', help='Gerar relatório automatizado')
    report_parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'pdf'],
        default='markdown',
        help='Formato do relatório (padrão: markdown)'
    )
    
    # Comando all
    all_parser = subparsers.add_parser('all', help='Executar pipeline completo')
    
    # Parse argumentos
    args = parser.parse_args()
    
    # Configura logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Carrega configurações
    config = load_config(args.config)
    
    # Cria diretórios necessários
    setup_directories(config)
    
    # Executa comando
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'ingest':
            cmd_ingest(args, config)
        elif args.command == 'derive':
            cmd_derive(args, config)
        elif args.command == 'viz':
            cmd_visualize(args, config)
        elif args.command == 'report':
            cmd_report(args, config)
        elif args.command == 'all':
            cmd_all(args, config)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()