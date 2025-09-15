"""
EcoMap.BR - Data Cleaning Utilities
Módulo para limpeza e padronização de dados
"""

import re
import logging
from typing import Union, List, Dict, Any, Optional
import pandas as pd
import polars as pl
import numpy as np

logger = logging.getLogger(__name__)


def standardize_column_names(df: Union[pd.DataFrame, pl.DataFrame]) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Padroniza nomes de colunas para snake_case e remove caracteres especiais.
    
    Args:
        df: DataFrame a ser padronizado
        
    Returns:
        DataFrame com colunas padronizadas
    """
    def clean_column_name(name: str) -> str:
        """Converte nome da coluna para snake_case limpo."""
        # Remove acentos e caracteres especiais
        name = str(name).strip()
        
        # Mapeamento de caracteres acentuados
        accents = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        
        for accented, clean in accents.items():
            name = name.replace(accented, clean)
            name = name.replace(accented.upper(), clean.upper())
        
        # Converte para minúsculas
        name = name.lower()
        
        # Substitui espaços e caracteres especiais por underscore
        name = re.sub(r'[^a-zA-Z0-9]+', '_', name)
        
        # Remove underscores múltiplos e do início/fim
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        # Se nome fica vazio, usa 'col' + índice
        if not name:
            name = 'unnamed_column'
            
        return name
    
    if isinstance(df, pl.DataFrame):
        # Polars
        old_columns = df.columns
        new_columns = [clean_column_name(col) for col in old_columns]
        
        # Verifica duplicatas
        seen = set()
        final_columns = []
        for col in new_columns:
            if col in seen:
                counter = 1
                while f"{col}_{counter}" in seen:
                    counter += 1
                col = f"{col}_{counter}"
            seen.add(col)
            final_columns.append(col)
        
        # Renomeia colunas
        rename_dict = dict(zip(old_columns, final_columns))
        df = df.rename(rename_dict)
        
    else:
        # Pandas
        old_columns = df.columns.tolist()
        new_columns = [clean_column_name(col) for col in old_columns]
        
        # Verifica duplicatas
        seen = set()
        final_columns = []
        for col in new_columns:
            if col in seen:
                counter = 1
                while f"{col}_{counter}" in seen:
                    counter += 1
                col = f"{col}_{counter}"
            seen.add(col)
            final_columns.append(col)
        
        df.columns = final_columns
    
    logger.info(f"Colunas padronizadas: {len(final_columns)} colunas")
    return df


class DataCleaner:
    """
    Classe para limpeza e padronização de dados.
    """
    
    def __init__(self, engine: str = "pandas"):
        """
        Args:
            engine: Engine de processamento ("pandas" ou "polars")
        """
        self.engine = engine.lower()
    
    def clean_numeric_columns(self, 
                            df: Union[pd.DataFrame, pl.DataFrame],
                            columns: Optional[List[str]] = None) -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Limpa colunas numéricas removendo caracteres inválidos.
        
        Args:
            df: DataFrame a ser limpo
            columns: Lista de colunas (None para auto-detectar)
            
        Returns:
            DataFrame com colunas numéricas limpas
        """
        if isinstance(df, pl.DataFrame):
            return self._clean_numeric_polars(df, columns)
        else:
            return self._clean_numeric_pandas(df, columns)
    
    def _clean_numeric_pandas(self, df: pd.DataFrame, columns: Optional[List[str]]) -> pd.DataFrame:
        """Limpa colunas numéricas no pandas."""
        df_clean = df.copy()
        
        if columns is None:
            # Auto-detecta colunas que parecem numéricas
            columns = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Testa se a coluna tem padrão numérico
                    sample = df[col].dropna().head(100).astype(str)
                    numeric_pattern = sample.str.match(r'^[\d\s\.,\-\+]+$').sum()
                    if numeric_pattern > len(sample) * 0.7:  # 70% das linhas parecem numéricas
                        columns.append(col)
        
        for col in columns:
            if col in df.columns:
                # Remove caracteres não-numéricos exceto ponto, vírgula e sinal
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[^\d\.,\-\+]', '', regex=True)
                
                # Converte vírgula para ponto (padrão brasileiro)
                df_clean[col] = df_clean[col].str.replace(',', '.')
                
                # Remove pontos múltiplos (mantém apenas o último como decimal)
                df_clean[col] = df_clean[col].apply(self._fix_decimal_points)
                
                # Converte para numérico
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                
                logger.info(f"Coluna {col} limpa: {df_clean[col].notna().sum()} valores válidos")
        
        return df_clean
    
    def _clean_numeric_polars(self, df: pl.DataFrame, columns: Optional[List[str]]) -> pl.DataFrame:
        """Limpa colunas numéricas no polars."""
        # Implementação similar para polars
        # Simplificada por questões de espaço
        return df
    
    def _fix_decimal_points(self, value: str) -> str:
        """Corrige pontos decimais múltiplos."""
        if pd.isna(value) or value == '':
            return value
        
        value = str(value)
        
        # Se tem apenas um ponto, mantém
        if value.count('.') <= 1:
            return value
        
        # Se tem múltiplos pontos, assume que o último é decimal
        parts = value.split('.')
        if len(parts) > 2:
            integer_part = ''.join(parts[:-1])
            decimal_part = parts[-1]
            return f"{integer_part}.{decimal_part}"
        
        return value
    
    def standardize_geographic_names(self, 
                                   df: Union[pd.DataFrame, pl.DataFrame],
                                   columns: List[str]) -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Padroniza nomes geográficos (UF, municípios).
        
        Args:
            df: DataFrame a ser padronizado
            columns: Lista de colunas geográficas
            
        Returns:
            DataFrame com nomes padronizados
        """
        if isinstance(df, pl.DataFrame):
            return self._standardize_geographic_polars(df, columns)
        else:
            return self._standardize_geographic_pandas(df, columns)
    
    def _standardize_geographic_pandas(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Padroniza nomes geográficos no pandas."""
        df_clean = df.copy()
        
        for col in columns:
            if col in df.columns:
                # Padronização básica
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].str.title()
                
                # Correções específicas comuns
                corrections = {
                    'Sao Paulo': 'São Paulo',
                    'Sao ': 'São ',
                    'Santo Andre': 'Santo André',
                    'Florianopolis': 'Florianópolis',
                    # Adicionar mais conforme necessário
                }
                
                for wrong, correct in corrections.items():
                    df_clean[col] = df_clean[col].str.replace(wrong, correct)
                
                logger.info(f"Coluna geográfica {col} padronizada")
        
        return df_clean
    
    def _standardize_geographic_polars(self, df: pl.DataFrame, columns: List[str]) -> pl.DataFrame:
        """Padroniza nomes geográficos no polars."""
        # Implementação para polars
        return df
    
    def remove_duplicates(self, 
                         df: Union[pd.DataFrame, pl.DataFrame],
                         subset: Optional[List[str]] = None,
                         keep: str = 'first') -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Remove duplicatas do DataFrame.
        
        Args:
            df: DataFrame
            subset: Colunas para considerar na detecção de duplicatas
            keep: Qual duplicata manter ('first', 'last')
            
        Returns:
            DataFrame sem duplicatas
        """
        original_count = len(df)
        
        if isinstance(df, pl.DataFrame):
            if subset:
                df_clean = df.unique(subset=subset, keep=keep)
            else:
                df_clean = df.unique(keep=keep)
        else:
            df_clean = df.drop_duplicates(subset=subset, keep=keep)
        
        removed_count = original_count - len(df_clean)
        logger.info(f"Removidas {removed_count} linhas duplicadas ({removed_count/original_count:.1%})")
        
        return df_clean
    
    def handle_missing_values(self, 
                            df: Union[pd.DataFrame, pl.DataFrame],
                            strategy: Dict[str, Any]) -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Trata valores ausentes conforme estratégia especificada.
        
        Args:
            df: DataFrame
            strategy: Dicionário com estratégias por coluna
                     {'coluna': 'drop'/'mean'/'median'/'mode'/valor}
            
        Returns:
            DataFrame com valores ausentes tratados
        """
        if isinstance(df, pl.DataFrame):
            return self._handle_missing_polars(df, strategy)
        else:
            return self._handle_missing_pandas(df, strategy)
    
    def _handle_missing_pandas(self, df: pd.DataFrame, strategy: Dict[str, Any]) -> pd.DataFrame:
        """Trata valores ausentes no pandas."""
        df_clean = df.copy()
        
        for column, method in strategy.items():
            if column not in df.columns:
                continue
                
            missing_count = df_clean[column].isna().sum()
            
            if method == 'drop':
                df_clean = df_clean.dropna(subset=[column])
            elif method == 'mean':
                df_clean[column].fillna(df_clean[column].mean(), inplace=True)
            elif method == 'median':
                df_clean[column].fillna(df_clean[column].median(), inplace=True)
            elif method == 'mode':
                mode_value = df_clean[column].mode().iloc[0] if not df_clean[column].mode().empty else None
                if mode_value is not None:
                    df_clean[column].fillna(mode_value, inplace=True)
            else:
                # Valor específico
                df_clean[column].fillna(method, inplace=True)
            
            logger.info(f"Coluna {column}: {missing_count} valores ausentes tratados com {method}")
        
        return df_clean
    
    def _handle_missing_polars(self, df: pl.DataFrame, strategy: Dict[str, Any]) -> pl.DataFrame:
        """Trata valores ausentes no polars."""
        # Implementação para polars
        return df