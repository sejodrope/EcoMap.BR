"""
EcoMap.BR - Data Validation Utilities
Módulo para validação e controle de qualidade de dados
"""

import logging
from typing import Union, List, Dict, Any, Optional, Tuple
import pandas as pd
import polars as pl
from pathlib import Path

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Classe para validação de estrutura e qualidade de dados.
    """
    
    def __init__(self, engine: str = "pandas"):
        """
        Args:
            engine: Engine de processamento ("pandas" ou "polars")
        """
        self.engine = engine.lower()
        self.validation_results = []
    
    def validate_required_columns(self, 
                                 df: Union[pd.DataFrame, pl.DataFrame],
                                 required_columns: List[str],
                                 source_name: str = "") -> bool:
        """
        Valida se as colunas obrigatórias estão presentes.
        
        Args:
            df: DataFrame a ser validado
            required_columns: Lista de colunas obrigatórias
            source_name: Nome da fonte de dados para logging
            
        Returns:
            True se todas as colunas estão presentes
        """
        df_columns = set(df.columns)
        required_set = set(required_columns)
        missing_columns = required_set - df_columns
        
        if missing_columns:
            message = f"{source_name}: Colunas obrigatórias ausentes: {list(missing_columns)}"
            logger.warning(message)
            self.validation_results.append({
                'source': source_name,
                'validation': 'required_columns',
                'status': 'FAIL',
                'message': message,
                'details': {'missing': list(missing_columns)}
            })
            return False
        else:
            message = f"{source_name}: Todas as colunas obrigatórias presentes"
            logger.info(message)
            self.validation_results.append({
                'source': source_name,
                'validation': 'required_columns',
                'status': 'PASS',
                'message': message,
                'details': {}
            })
            return True
    
    def validate_data_types(self, 
                           df: Union[pd.DataFrame, pl.DataFrame],
                           expected_types: Dict[str, str],
                           source_name: str = "") -> bool:
        """
        Valida tipos de dados das colunas.
        
        Args:
            df: DataFrame a ser validado
            expected_types: Dicionário {coluna: tipo_esperado}
            source_name: Nome da fonte de dados
            
        Returns:
            True se todos os tipos estão corretos
        """
        type_issues = []
        
        for column, expected_type in expected_types.items():
            if column in df.columns:
                if isinstance(df, pl.DataFrame):
                    actual_type = str(df[column].dtype)
                else:
                    actual_type = str(df[column].dtype)
                
                # Simplificação da verificação de tipos
                if not self._is_compatible_type(actual_type, expected_type):
                    type_issues.append({
                        'column': column,
                        'expected': expected_type,
                        'actual': actual_type
                    })
        
        if type_issues:
            message = f"{source_name}: Tipos de dados incorretos: {type_issues}"
            logger.warning(message)
            self.validation_results.append({
                'source': source_name,
                'validation': 'data_types',
                'status': 'FAIL',
                'message': message,
                'details': {'type_issues': type_issues}
            })
            return False
        else:
            message = f"{source_name}: Tipos de dados corretos"
            logger.info(message)
            self.validation_results.append({
                'source': source_name,
                'validation': 'data_types',
                'status': 'PASS',
                'message': message,
                'details': {}
            })
            return True
    
    def _is_compatible_type(self, actual: str, expected: str) -> bool:
        """Verifica se os tipos são compatíveis."""
        # Mapeamento simplificado de tipos
        type_mapping = {
            'int': ['int64', 'int32', 'Int64', 'integer'],
            'float': ['float64', 'float32', 'Float64', 'double'],
            'string': ['object', 'string', 'str', 'Utf8'],
            'datetime': ['datetime64', 'datetime', 'Date', 'Datetime'],
            'bool': ['bool', 'boolean', 'Boolean']
        }
        
        expected_variants = type_mapping.get(expected.lower(), [expected])
        return any(variant.lower() in actual.lower() for variant in expected_variants)
    
    def check_missing_values(self, 
                           df: Union[pd.DataFrame, pl.DataFrame],
                           threshold: float = 0.1,
                           source_name: str = "") -> Dict[str, float]:
        """
        Verifica percentual de valores ausentes por coluna.
        
        Args:
            df: DataFrame a ser analisado
            threshold: Threshold para alertas (ex: 0.1 = 10%)
            source_name: Nome da fonte de dados
            
        Returns:
            Dicionário com percentual de valores ausentes por coluna
        """
        total_rows = len(df)
        missing_stats = {}
        problematic_columns = []
        
        for column in df.columns:
            if isinstance(df, pl.DataFrame):
                missing_count = df[column].null_count()
            else:
                missing_count = df[column].isna().sum()
            
            missing_percent = missing_count / total_rows if total_rows > 0 else 0
            missing_stats[column] = missing_percent
            
            if missing_percent > threshold:
                problematic_columns.append({
                    'column': column,
                    'missing_percent': missing_percent,
                    'missing_count': missing_count
                })
        
        if problematic_columns:
            message = f"{source_name}: Colunas com muitos valores ausentes (>{threshold:.1%})"
            logger.warning(message)
            for col_info in problematic_columns:
                logger.warning(f"  {col_info['column']}: {col_info['missing_percent']:.1%} ausentes")
        else:
            message = f"{source_name}: Percentual de valores ausentes dentro do aceitável"
            logger.info(message)
        
        self.validation_results.append({
            'source': source_name,
            'validation': 'missing_values',
            'status': 'FAIL' if problematic_columns else 'PASS',
            'message': message,
            'details': {'missing_stats': missing_stats, 'problematic': problematic_columns}
        })
        
        return missing_stats
    
    def check_temporal_consistency(self, 
                                 df: Union[pd.DataFrame, pl.DataFrame],
                                 date_columns: List[str],
                                 source_name: str = "") -> bool:
        """
        Verifica consistência temporal dos dados.
        
        Args:
            df: DataFrame a ser analisado
            date_columns: Lista de colunas de data
            source_name: Nome da fonte de dados
            
        Returns:
            True se as datas são consistentes
        """
        issues = []
        
        for date_col in date_columns:
            if date_col not in df.columns:
                continue
            
            # Verifica se é possível converter para datetime
            if isinstance(df, pd.DataFrame):
                try:
                    pd.to_datetime(df[date_col], errors='raise')
                except:
                    issues.append(f"Coluna {date_col} não pode ser convertida para datetime")
            
            # Outras validações temporais podem ser adicionadas aqui
        
        if issues:
            message = f"{source_name}: Problemas de consistência temporal: {issues}"
            logger.warning(message)
            self.validation_results.append({
                'source': source_name,
                'validation': 'temporal_consistency',
                'status': 'FAIL',
                'message': message,
                'details': {'issues': issues}
            })
            return False
        else:
            message = f"{source_name}: Consistência temporal OK"
            logger.info(message)
            self.validation_results.append({
                'source': source_name,
                'validation': 'temporal_consistency',
                'status': 'PASS',
                'message': message,
                'details': {}
            })
            return True
    
    def get_validation_report(self) -> pd.DataFrame:
        """
        Retorna relatório consolidado de validações.
        
        Returns:
            DataFrame com resultados das validações
        """
        if not self.validation_results:
            return pd.DataFrame(columns=['source', 'validation', 'status', 'message'])
        
        return pd.DataFrame(self.validation_results)
    
    def save_validation_report(self, file_path: Union[str, Path]) -> None:
        """
        Salva relatório de validações em arquivo.
        
        Args:
            file_path: Caminho para salvar o relatório
        """
        report_df = self.get_validation_report()
        report_df.to_csv(file_path, index=False, encoding='utf-8')
        logger.info(f"Relatório de validação salvo em: {file_path}")


class QualityChecker:
    """
    Classe para análise de qualidade de dados.
    """
    
    def __init__(self, engine: str = "pandas"):
        self.engine = engine.lower()
    
    def generate_quality_report(self, 
                              df: Union[pd.DataFrame, pl.DataFrame],
                              source_name: str = "") -> Dict[str, Any]:
        """
        Gera relatório completo de qualidade dos dados.
        
        Args:
            df: DataFrame a ser analisado
            source_name: Nome da fonte de dados
            
        Returns:
            Dicionário com métricas de qualidade
        """
        report = {
            'source': source_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': self._get_memory_usage(df),
            'column_info': {},
            'quality_score': 0.0
        }
        
        # Análise por coluna
        for column in df.columns:
            col_info = self._analyze_column(df, column)
            report['column_info'][column] = col_info
        
        # Calcula score geral de qualidade
        report['quality_score'] = self._calculate_quality_score(report)
        
        return report
    
    def _get_memory_usage(self, df: Union[pd.DataFrame, pl.DataFrame]) -> float:
        """Calcula uso de memória em MB."""
        if isinstance(df, pd.DataFrame):
            return df.memory_usage(deep=True).sum() / (1024 * 1024)
        else:
            # Estimativa para polars
            return len(df) * len(df.columns) * 8 / (1024 * 1024)  # Estimativa rough
    
    def _analyze_column(self, 
                       df: Union[pd.DataFrame, pl.DataFrame], 
                       column: str) -> Dict[str, Any]:
        """Análise detalhada de uma coluna."""
        if isinstance(df, pd.DataFrame):
            col_data = df[column]
            null_count = col_data.isna().sum()
            unique_count = col_data.nunique()
        else:
            col_data = df[column]
            null_count = col_data.null_count()
            unique_count = col_data.n_unique()
        
        total_count = len(df)
        
        analysis = {
            'dtype': str(col_data.dtype),
            'null_count': null_count,
            'null_percentage': (null_count / total_count) * 100 if total_count > 0 else 0,
            'unique_count': unique_count,
            'unique_percentage': (unique_count / total_count) * 100 if total_count > 0 else 0
        }
        
        # Análise específica por tipo
        if isinstance(df, pd.DataFrame):
            if pd.api.types.is_numeric_dtype(col_data):
                analysis.update({
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'mean': col_data.mean(),
                    'std': col_data.std(),
                    'median': col_data.median()
                })
            elif pd.api.types.is_string_dtype(col_data):
                analysis.update({
                    'avg_length': col_data.str.len().mean(),
                    'max_length': col_data.str.len().max(),
                    'min_length': col_data.str.len().min()
                })
        
        return analysis
    
    def _calculate_quality_score(self, report: Dict[str, Any]) -> float:
        """Calcula score de qualidade dos dados (0-100)."""
        scores = []
        
        for column, info in report['column_info'].items():
            # Penaliza valores ausentes
            null_penalty = max(0, 100 - info['null_percentage'])
            
            # Bonifica diversidade (mas não demais)
            diversity_bonus = min(info['unique_percentage'], 50)  # Max 50 pontos
            
            col_score = (null_penalty * 0.7 + diversity_bonus * 0.3)
            scores.append(col_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def detect_outliers(self, 
                       df: Union[pd.DataFrame, pl.DataFrame],
                       columns: List[str],
                       method: str = "iqr",
                       multiplier: float = 3.0) -> Dict[str, List]:
        """
        Detecta outliers nas colunas especificadas.
        
        Args:
            df: DataFrame
            columns: Lista de colunas numéricas
            method: Método de detecção ("iqr", "zscore")
            multiplier: Multiplicador para definir outliers
            
        Returns:
            Dicionário com índices de outliers por coluna
        """
        outliers = {}
        
        for column in columns:
            if column not in df.columns:
                continue
            
            if isinstance(df, pd.DataFrame):
                col_data = df[column]
                if pd.api.types.is_numeric_dtype(col_data):
                    if method == "iqr":
                        Q1 = col_data.quantile(0.25)
                        Q3 = col_data.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - multiplier * IQR
                        upper_bound = Q3 + multiplier * IQR
                        outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
                        outliers[column] = df.index[outlier_mask].tolist()
                    elif method == "zscore":
                        z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                        outlier_mask = z_scores > multiplier
                        outliers[column] = df.index[outlier_mask].tolist()
        
        return outliers