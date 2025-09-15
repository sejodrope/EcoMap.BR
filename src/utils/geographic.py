"""
Módulo de normalização geográfica
Funções para padronização de nomes de municípios e códigos geográficos
"""

import re
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class GeographicNormalizer:
    """Classe para normalização de dados geográficos"""
    
    def __init__(self):
        """Initialize the geographic normalizer"""
        self.municipality_mappings = {
            # Variações comuns de Joinville
            'joinville': 'Joinville',
            'joinvile': 'Joinville',
            'joinvilla': 'Joinville',
            
            # Variações de outras cidades SC comuns nos dados
            'florianopolis': 'Florianópolis',
            'florianópolis': 'Florianópolis',
            'blumenau': 'Blumenau',
            'itajai': 'Itajaí',
            'itajaí': 'Itajaí',
            'chapeco': 'Chapecó',
            'chapecó': 'Chapecó',
            'criciuma': 'Criciúma',
            'criciúma': 'Criciúma',
            'lages': 'Lages',
            'são josé': 'São José',
            'sao jose': 'São José',
        }
        
        self.state_mappings = {
            'sc': 'Santa Catarina',
            'santa catarina': 'Santa Catarina',
            'pr': 'Paraná',
            'parana': 'Paraná',
            'paraná': 'Paraná',
            'rs': 'Rio Grande do Sul',
            'rio grande do sul': 'Rio Grande do Sul',
            'sp': 'São Paulo',
            'sao paulo': 'São Paulo',
            'são paulo': 'São Paulo',
        }
    
    def normalize_municipality_name(self, name: str) -> str:
        """
        Normaliza nome do município
        
        Args:
            name: Nome do município para normalizar
            
        Returns:
            Nome normalizado do município
        """
        if not name or not isinstance(name, str):
            return ""
        
        # Remove espaços extras e converte para lowercase para matching
        clean_name = name.strip().lower()
        
        # Verifica se há mapeamento direto
        if clean_name in self.municipality_mappings:
            return self.municipality_mappings[clean_name]
        
        # Normalização genérica
        normalized = name.strip()
        
        # Capitaliza primeira letra de cada palavra
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        return normalized
    
    def normalize_state_name(self, name: str) -> str:
        """
        Normaliza nome do estado
        
        Args:
            name: Nome ou sigla do estado
            
        Returns:
            Nome completo normalizado do estado
        """
        if not name or not isinstance(name, str):
            return ""
        
        clean_name = name.strip().lower()
        
        if clean_name in self.state_mappings:
            return self.state_mappings[clean_name]
        
        # Se não encontrou mapeamento, retorna o nome capitalizado
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    def extract_municipality_from_text(self, text: str) -> Optional[str]:
        """
        Extrai nome de município de texto livre
        
        Args:
            text: Texto contendo nome do município
            
        Returns:
            Nome do município extraído ou None
        """
        if not text or not isinstance(text, str):
            return None
        
        # Patterns para extrair município
        patterns = [
            r'([A-ZÁÊÔÃÇ][a-záêôãç\s]+)',  # Palavras capitalizadas
            r'município\s+de\s+([^,\n]+)',   # "município de X"
            r'cidade\s+de\s+([^,\n]+)',     # "cidade de X"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                return self.normalize_municipality_name(candidate)
        
        return None


def get_municipality_code(municipality_name: str) -> Optional[str]:
    """
    Obtém código IBGE do município (implementação básica)
    
    Args:
        municipality_name: Nome do município
        
    Returns:
        Código IBGE do município ou None se não encontrado
    """
    # Códigos IBGE básicos para municípios principais de SC
    codes = {
        'Joinville': '4209102',
        'Florianópolis': '4205407',
        'Blumenau': '4202404', 
        'São José': '4216602',
        'Criciúma': '4204608',
        'Chapecó': '4204202',
        'Itajaí': '4208203',
        'Lages': '4209300',
        'Balneário Camboriú': '4201406',
        'Palhoça': '4211900',
    }
    
    return codes.get(municipality_name)


def validate_geographic_data(data_dict: Dict, required_fields: List[str] = None) -> Dict:
    """
    Valida dados geográficos básicos
    
    Args:
        data_dict: Dicionário com dados geográficos
        required_fields: Lista de campos obrigatórios
        
    Returns:
        Dicionário com resultados da validação
    """
    if required_fields is None:
        required_fields = ['municipio', 'uf']
    
    results = {
        'is_valid': True,
        'missing_fields': [],
        'normalized_data': {},
        'warnings': []
    }
    
    normalizer = GeographicNormalizer()
    
    # Verifica campos obrigatórios
    for field in required_fields:
        if field not in data_dict or not data_dict[field]:
            results['missing_fields'].append(field)
            results['is_valid'] = False
    
    # Normaliza dados disponíveis
    if 'municipio' in data_dict and data_dict['municipio']:
        results['normalized_data']['municipio'] = normalizer.normalize_municipality_name(
            str(data_dict['municipio'])
        )
    
    if 'uf' in data_dict and data_dict['uf']:
        results['normalized_data']['uf'] = normalizer.normalize_state_name(
            str(data_dict['uf'])
        )
    
    # Adiciona código IBGE se possível
    if 'municipio' in results['normalized_data']:
        code = get_municipality_code(results['normalized_data']['municipio'])
        if code:
            results['normalized_data']['codigo_ibge'] = code
        else:
            results['warnings'].append(f"Código IBGE não encontrado para {results['normalized_data']['municipio']}")
    
    return results


# Instância global para facilitar uso
geographic_normalizer = GeographicNormalizer()