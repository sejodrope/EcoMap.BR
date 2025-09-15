"""
Módulo de normalização temporal
Funções para padronização de datas e períodos temporais
"""

import pandas as pd
import numpy as np
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, List, Tuple

logger = logging.getLogger(__name__)

class TemporalNormalizer:
    """Classe para normalização de dados temporais"""
    
    def __init__(self):
        """Initialize the temporal normalizer"""
        self.common_date_formats = [
            '%Y-%m-%d',      # 2023-12-31
            '%Y/%m/%d',      # 2023/12/31  
            '%d-%m-%Y',      # 31-12-2023
            '%d/%m/%Y',      # 31/12/2023
            '%Y-%m',         # 2023-12
            '%Y/%m',         # 2023/12
            '%m-%Y',         # 12-2023
            '%m/%Y',         # 12/2023
            '%Y',            # 2023
        ]
        
        self.month_names_pt = {
            'janeiro': 1, 'jan': 1,
            'fevereiro': 2, 'fev': 2,
            'março': 3, 'mar': 3,
            'abril': 4, 'abr': 4,
            'maio': 5, 'mai': 5,
            'junho': 6, 'jun': 6,
            'julho': 7, 'jul': 7,
            'agosto': 8, 'ago': 8,
            'setembro': 9, 'set': 9,
            'outubro': 10, 'out': 10,
            'novembro': 11, 'nov': 11,
            'dezembro': 12, 'dez': 12,
        }
    
    def parse_date(self, date_str: Union[str, int, float]) -> Optional[datetime]:
        """
        Faz parsing de diferentes formatos de data
        
        Args:
            date_str: String, int ou float representando data
            
        Returns:
            Objeto datetime ou None se não conseguir fazer parse
        """
        if pd.isna(date_str) or date_str == '':
            return None
        
        # Se for número, tenta interpretar como ano
        if isinstance(date_str, (int, float)):
            year = int(date_str)
            if 1900 <= year <= 2100:
                return datetime(year, 1, 1)
            return None
        
        date_str = str(date_str).strip()
        
        # Tenta formatos padrão
        for fmt in self.common_date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Tenta parsing de nomes de meses em português
        return self._parse_portuguese_date(date_str)
    
    def _parse_portuguese_date(self, date_str: str) -> Optional[datetime]:
        """
        Faz parsing de datas com nomes de meses em português
        
        Args:
            date_str: String com data em português
            
        Returns:
            Objeto datetime ou None
        """
        date_str_lower = date_str.lower()
        
        # Pattern: "janeiro de 2023", "jan/2023", etc.
        for month_name, month_num in self.month_names_pt.items():
            if month_name in date_str_lower:
                # Extrai o ano
                year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
                if year_match:
                    year = int(year_match.group())
                    return datetime(year, month_num, 1)
        
        return None
    
    def standardize_period(self, period_str: Union[str, int, float]) -> Optional[str]:
        """
        Padroniza representação de períodos (anos, meses)
        
        Args:
            period_str: String ou número representando período
            
        Returns:
            Período padronizado no formato YYYY-MM ou YYYY
        """
        if pd.isna(period_str):
            return None
        
        date_obj = self.parse_date(period_str)
        if date_obj:
            if isinstance(period_str, str) and len(str(period_str).strip()) <= 4:
                # Apenas ano
                return date_obj.strftime('%Y')
            else:
                # Ano e mês
                return date_obj.strftime('%Y-%m')
        
        return None
    
    def extract_year(self, date_input: Union[str, int, float, datetime]) -> Optional[int]:
        """
        Extrai ano de diferentes formatos de entrada
        
        Args:
            date_input: Entrada de data em diversos formatos
            
        Returns:
            Ano como inteiro ou None
        """
        if isinstance(date_input, datetime):
            return date_input.year
        
        if isinstance(date_input, (int, float)) and 1900 <= date_input <= 2100:
            return int(date_input)
        
        date_obj = self.parse_date(date_input)
        if date_obj:
            return date_obj.year
        
        return None
    
    def extract_month(self, date_input: Union[str, int, float, datetime]) -> Optional[int]:
        """
        Extrai mês de diferentes formatos de entrada
        
        Args:
            date_input: Entrada de data em diversos formatos
            
        Returns:
            Mês como inteiro (1-12) ou None
        """
        if isinstance(date_input, datetime):
            return date_input.month
        
        date_obj = self.parse_date(date_input)
        if date_obj:
            return date_obj.month
        
        return None
    
    def create_date_range(self, start_year: int, end_year: int, 
                         frequency: str = 'yearly') -> List[datetime]:
        """
        Cria range de datas entre anos
        
        Args:
            start_year: Ano inicial
            end_year: Ano final
            frequency: 'yearly' ou 'monthly'
            
        Returns:
            Lista de objetos datetime
        """
        dates = []
        
        if frequency == 'yearly':
            for year in range(start_year, end_year + 1):
                dates.append(datetime(year, 1, 1))
        
        elif frequency == 'monthly':
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    dates.append(datetime(year, month, 1))
        
        return dates
    
    def validate_date_range(self, dates: List[Union[str, datetime]], 
                          min_year: int = 2000, max_year: int = 2030) -> Dict:
        """
        Valida range de datas
        
        Args:
            dates: Lista de datas para validar
            min_year: Ano mínimo válido
            max_year: Ano máximo válido
            
        Returns:
            Dicionário com resultados da validação
        """
        results = {
            'valid_dates': [],
            'invalid_dates': [],
            'parsed_dates': [],
            'date_range': None,
            'gaps': [],
        }
        
        for date_input in dates:
            if isinstance(date_input, datetime):
                date_obj = date_input
            else:
                date_obj = self.parse_date(date_input)
            
            if date_obj and min_year <= date_obj.year <= max_year:
                results['valid_dates'].append(date_input)
                results['parsed_dates'].append(date_obj)
            else:
                results['invalid_dates'].append(date_input)
        
        if results['parsed_dates']:
            results['date_range'] = {
                'start': min(results['parsed_dates']),
                'end': max(results['parsed_dates'])
            }
            
            # Detecta gaps se for sequencial
            if len(results['parsed_dates']) > 1:
                sorted_dates = sorted(results['parsed_dates'])
                results['gaps'] = self._detect_date_gaps(sorted_dates)
        
        return results
    
    def _detect_date_gaps(self, sorted_dates: List[datetime]) -> List[Tuple[datetime, datetime]]:
        """
        Detecta gaps em sequência de datas
        
        Args:
            sorted_dates: Lista ordenada de datas
            
        Returns:
            Lista de tuplas (start_gap, end_gap)
        """
        gaps = []
        
        for i in range(len(sorted_dates) - 1):
            current = sorted_dates[i]
            next_date = sorted_dates[i + 1]
            
            # Se for anual, verifica gap de anos
            if current.month == 1 and current.day == 1:
                expected_next = datetime(current.year + 1, 1, 1)
                if next_date > expected_next:
                    gaps.append((expected_next, next_date))
            
            # Se for mensal, verifica gap de meses  
            elif current.day == 1:
                if current.month == 12:
                    expected_next = datetime(current.year + 1, 1, 1)
                else:
                    expected_next = datetime(current.year, current.month + 1, 1)
                
                if next_date > expected_next:
                    gaps.append((expected_next, next_date))
        
        return gaps


def standardize_dates(data: pd.DataFrame, date_columns: List[str] = None) -> pd.DataFrame:
    """
    Padroniza colunas de data em DataFrame
    
    Args:
        data: DataFrame com dados
        date_columns: Lista de colunas de data para padronizar
        
    Returns:
        DataFrame com datas padronizadas
    """
    df = data.copy()
    normalizer = TemporalNormalizer()
    
    if date_columns is None:
        # Tenta detectar colunas de data automaticamente
        date_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(word in col_lower for word in ['data', 'date', 'ano', 'year', 'mes', 'month', 'periodo']):
                date_columns.append(col)
    
    for col in date_columns:
        if col in df.columns:
            logger.info(f"Padronizando coluna de data: {col}")
            
            # Aplica parsing de data
            df[f'{col}_parsed'] = df[col].apply(normalizer.parse_date)
            
            # Extrai ano se possível
            df[f'{col}_year'] = df[col].apply(normalizer.extract_year)
            
            # Extrai mês se possível
            df[f'{col}_month'] = df[col].apply(normalizer.extract_month)
    
    return df


def create_temporal_aggregations(data: pd.DataFrame, date_col: str, 
                               value_cols: List[str], 
                               aggregations: List[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Cria agregações temporais dos dados
    
    Args:
        data: DataFrame com dados
        date_col: Nome da coluna de data
        value_cols: Colunas de valores para agregar
        aggregations: Lista de agregações ('yearly', 'quarterly', 'monthly')
        
    Returns:
        Dicionário com DataFrames agregados por período
    """
    if aggregations is None:
        aggregations = ['yearly', 'monthly']
    
    results = {}
    normalizer = TemporalNormalizer()
    
    # Prepara coluna de data
    df = data.copy()
    df['date_parsed'] = df[date_col].apply(normalizer.parse_date)
    df = df.dropna(subset=['date_parsed'])
    
    # Agregações anuais
    if 'yearly' in aggregations:
        df['year'] = df['date_parsed'].dt.year
        yearly = df.groupby('year')[value_cols].sum().reset_index()
        results['yearly'] = yearly
    
    # Agregações mensais
    if 'monthly' in aggregations:
        df['year_month'] = df['date_parsed'].dt.to_period('M')
        monthly = df.groupby('year_month')[value_cols].sum().reset_index()
        results['monthly'] = monthly
    
    # Agregações trimestrais
    if 'quarterly' in aggregations:
        df['year_quarter'] = df['date_parsed'].dt.to_period('Q')
        quarterly = df.groupby('year_quarter')[value_cols].sum().reset_index()
        results['quarterly'] = quarterly
    
    return results


# Instância global para facilitar uso
temporal_normalizer = TemporalNormalizer()