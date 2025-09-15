"""
EcoMap.BR - I/O Utilities
Módulo para carregamento e detecção automática de encoding/separadores
"""

import os
import logging
from pathlib import Path
from typing import Union, Tuple, Optional, Dict, List
import pandas as pd
import polars as pl
import chardet
from tqdm import tqdm

logger = logging.getLogger(__name__)


def detect_encoding_and_separator(file_path: Union[str, Path]) -> Tuple[str, str]:
    """
    Detecta automaticamente o encoding e separador de um arquivo CSV.
    
    Args:
        file_path: Caminho para o arquivo CSV
        
    Returns:
        Tuple com (encoding, separator)
    """
    file_path = Path(file_path)
    
    # Detecta encoding
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Lê primeiros 10KB
        encoding_result = chardet.detect(raw_data)
        encoding = encoding_result['encoding'] or 'utf-8'
    
    # Detecta separador
    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        first_line = f.readline()
        
    # Conta frequência de possíveis separadores
    separators = [',', ';', '\t', '|']
    separator_counts = {sep: first_line.count(sep) for sep in separators}
    separator = max(separator_counts, key=separator_counts.get)
    
    # Se nenhum separador foi detectado, usa vírgula como padrão
    if separator_counts[separator] == 0:
        separator = ','
    
    logger.info(f"Arquivo {file_path.name}: encoding={encoding}, separator='{separator}'")
    return encoding, separator


class DataLoader:
    """
    Classe para carregamento robusto de dados com diferentes engines.
    """
    
    def __init__(self, engine: str = "pandas", chunk_size: Optional[int] = None):
        """
        Args:
            engine: Engine para carregamento ("pandas" ou "polars")
            chunk_size: Tamanho do chunk para arquivos grandes
        """
        self.engine = engine.lower()
        self.chunk_size = chunk_size
        
        if self.engine not in ["pandas", "polars"]:
            raise ValueError("Engine deve ser 'pandas' ou 'polars'")
    
    def load_csv(self, 
                 file_path: Union[str, Path],
                 encoding: Optional[str] = None,
                 separator: Optional[str] = None,
                 **kwargs) -> Union[pd.DataFrame, pl.DataFrame]:
        """
        Carrega arquivo CSV com detecção automática de parâmetros.
        
        Args:
            file_path: Caminho para o arquivo
            encoding: Encoding (detectado automaticamente se None)
            separator: Separador (detectado automaticamente se None)
            **kwargs: Argumentos adicionais para pd.read_csv ou pl.read_csv
            
        Returns:
            DataFrame carregado
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Auto-detecção se não especificado
        if encoding is None or separator is None:
            detected_encoding, detected_separator = detect_encoding_and_separator(file_path)
            encoding = encoding or detected_encoding
            separator = separator or detected_separator
        
        try:
            if self.engine == "polars":
                return self._load_with_polars(file_path, encoding, separator, **kwargs)
            else:
                return self._load_with_pandas(file_path, encoding, separator, **kwargs)
                
        except Exception as e:
            logger.error(f"Erro ao carregar {file_path}: {str(e)}")
            # Tenta fallback com parâmetros padrão
            logger.info("Tentando carregamento com parâmetros padrão...")
            return self._load_fallback(file_path)
    
    def _load_with_pandas(self, file_path: Path, encoding: str, separator: str, **kwargs) -> pd.DataFrame:
        """Carrega arquivo usando pandas."""
        default_params = {
            'encoding': encoding,
            'sep': separator,
            'low_memory': False,
            'parse_dates': True,
            'infer_datetime_format': True
        }
        default_params.update(kwargs)
        
        if self.chunk_size:
            # Carregamento em chunks
            chunks = []
            for chunk in tqdm(pd.read_csv(file_path, chunksize=self.chunk_size, **default_params),
                             desc=f"Carregando {file_path.name}"):
                chunks.append(chunk)
            return pd.concat(chunks, ignore_index=True)
        else:
            return pd.read_csv(file_path, **default_params)
    
    def _load_with_polars(self, file_path: Path, encoding: str, separator: str, **kwargs) -> pl.DataFrame:
        """Carrega arquivo usando polars."""
        default_params = {
            'encoding': encoding,
            'separator': separator,
            'try_parse_dates': True,
            'ignore_errors': True,
            'truncate_ragged_lines': True  # Corrige problema de colunas extras
        }
        default_params.update(kwargs)
        
        return pl.read_csv(file_path, **default_params)
    
    def _load_fallback(self, file_path: Path) -> Union[pd.DataFrame, pl.DataFrame]:
        """Carregamento de fallback com parâmetros conservadores."""
        try:
            if self.engine == "polars":
                return pl.read_csv(file_path, encoding='utf-8', separator=',', ignore_errors=True, truncate_ragged_lines=True)
            else:
                return pd.read_csv(file_path, encoding='utf-8', sep=',', low_memory=False, 
                                 on_bad_lines='skip')
        except Exception as e:
            logger.error(f"Fallback também falhou para {file_path}: {str(e)}")
            raise
    
    def load_directory(self, 
                       directory_path: Union[str, Path],
                       pattern: str = "*.csv",
                       combine: bool = False) -> Union[Dict[str, pd.DataFrame], pd.DataFrame, 
                                                      Dict[str, pl.DataFrame], pl.DataFrame]:
        """
        Carrega todos os arquivos de um diretório.
        
        Args:
            directory_path: Caminho para o diretório
            pattern: Padrão de arquivos (ex: "*.csv")
            combine: Se deve combinar todos os DataFrames
            
        Returns:
            Dicionário com DataFrames ou DataFrame combinado
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            logger.warning(f"Diretório não encontrado: {directory_path}")
            return {} if not combine else (pl.DataFrame() if self.engine == "polars" else pd.DataFrame())
        
        files = list(directory_path.glob(pattern))
        
        if not files:
            logger.warning(f"Nenhum arquivo encontrado em {directory_path} com padrão {pattern}")
            return {} if not combine else (pl.DataFrame() if self.engine == "polars" else pd.DataFrame())
        
        dataframes = {}
        
        for file_path in tqdm(files, desc=f"Carregando arquivos de {directory_path.name}"):
            try:
                df = self.load_csv(file_path)
                dataframes[file_path.stem] = df
                logger.info(f"Carregado: {file_path.name} ({len(df)} linhas)")
            except Exception as e:
                logger.error(f"Erro ao carregar {file_path.name}: {str(e)}")
        
        if combine and dataframes:
            if self.engine == "polars":
                return pl.concat(list(dataframes.values()))
            else:
                return pd.concat(list(dataframes.values()), ignore_index=True)
        
        return dataframes


def safe_mkdir(directory_path: Union[str, Path]) -> Path:
    """
    Cria diretório de forma segura.
    
    Args:
        directory_path: Caminho do diretório
        
    Returns:
        Path do diretório criado
    """
    directory_path = Path(directory_path)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def save_dataframe(df: Union[pd.DataFrame, pl.DataFrame], 
                   file_path: Union[str, Path],
                   format: str = "csv",
                   **kwargs) -> None:
    """
    Salva DataFrame em diferentes formatos.
    
    Args:
        df: DataFrame a ser salvo
        file_path: Caminho de destino
        format: Formato de saída ("csv", "parquet", "json")
        **kwargs: Argumentos adicionais
    """
    file_path = Path(file_path)
    safe_mkdir(file_path.parent)
    
    if isinstance(df, pl.DataFrame):
        if format == "csv":
            df.write_csv(file_path, **kwargs)
        elif format == "parquet":
            df.write_parquet(file_path, **kwargs)
        elif format == "json":
            df.write_json(file_path, **kwargs)
    else:  # pandas
        if format == "csv":
            df.to_csv(file_path, index=False, encoding='utf-8', **kwargs)
        elif format == "parquet":
            df.to_parquet(file_path, index=False, **kwargs)
        elif format == "json":
            df.to_json(file_path, orient='records', **kwargs)
    
    logger.info(f"DataFrame salvo: {file_path} ({len(df)} linhas, formato: {format})")