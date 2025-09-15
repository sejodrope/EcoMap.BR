"""
Testes básicos para o pipeline EcoMap.BR
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path
import sys

# Adiciona src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.io_utils import DataLoader
from src.utils.data_cleaning import DataCleaner
from src.utils.validation import DataValidator, QualityChecker
from src.indicators import EconomicIndicators


class TestDataLoader(unittest.TestCase):
    """Testes para o módulo de carregamento de dados."""
    
    def setUp(self):
        self.loader = DataLoader()
        
        # Cria arquivo CSV temporário para teste
        self.test_data = pd.DataFrame({
            'municipio': ['Joinville', 'Florianópolis', 'Blumenau'],
            'ano': [2020, 2020, 2020],
            'emprego': [100000, 80000, 60000]
        })
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_load_csv_file(self):
        """Testa carregamento de arquivo CSV."""
        df = self.loader.load_file(self.temp_file.name)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)
        self.assertIn('municipio', df.columns)
    
    def test_detect_encoding_and_separator(self):
        """Testa detecção de encoding e separador."""
        encoding, separator = self.loader.detect_encoding_and_separator(self.temp_file.name)
        self.assertIsNotNone(encoding)
        self.assertIsNotNone(separator)


class TestDataCleaner(unittest.TestCase):
    """Testes para o módulo de limpeza de dados."""
    
    def setUp(self):
        self.cleaner = DataCleaner()
        self.test_df = pd.DataFrame({
            'Nome do Município': ['JOINVILLE', 'florianópolis', 'Blumenau'],
            'Ano de Referência': [2020, 2021, 2022],
            'Valor Emprego': ['1,000.50', '2.500,00', '3000'],
            'Observações': ['Teste 1', None, 'Teste 3']
        })
    
    def test_standardize_column_names(self):
        """Testa padronização de nomes de colunas."""
        df_clean = self.cleaner.standardize_column_names(self.test_df)
        expected_columns = ['nome_do_municipio', 'ano_de_referencia', 'valor_emprego', 'observacoes']
        self.assertEqual(list(df_clean.columns), expected_columns)
    
    def test_clean_numeric_columns(self):
        """Testa limpeza de colunas numéricas."""
        df_clean = self.cleaner.clean_numeric_columns(self.test_df, ['Valor Emprego'])
        # Verifica se valores foram convertidos para numérico
        self.assertTrue(pd.api.types.is_numeric_dtype(df_clean['Valor Emprego']))
    
    def test_standardize_geographic_names(self):
        """Testa padronização de nomes geográficos."""
        df_clean = self.cleaner.standardize_geographic_names(self.test_df, 'Nome do Município')
        # Verifica se nomes foram padronizados
        expected_names = ['Joinville', 'Florianópolis', 'Blumenau']
        self.assertEqual(list(df_clean['Nome do Município']), expected_names)


class TestDataValidator(unittest.TestCase):
    """Testes para validação de dados."""
    
    def setUp(self):
        self.validator = DataValidator()
        self.test_df = pd.DataFrame({
            'municipio': ['Joinville', 'Florianópolis', None],
            'ano': [2020, 2021, 2022],
            'valor': [100, None, 300]
        })
    
    def test_validate_required_columns(self):
        """Testa validação de colunas obrigatórias."""
        required_cols = ['municipio', 'ano']
        is_valid, missing = self.validator.validate_required_columns(self.test_df, required_cols)
        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
        
        # Testa com coluna faltante
        is_valid, missing = self.validator.validate_required_columns(self.test_df, ['municipio', 'estado'])
        self.assertFalse(is_valid)
        self.assertIn('estado', missing)
    
    def test_check_missing_values(self):
        """Testa verificação de valores faltantes."""
        missing_report = self.validator.check_missing_values(self.test_df)
        self.assertIn('municipio', missing_report)
        self.assertIn('valor', missing_report)
        self.assertEqual(missing_report['municipio']['count'], 1)
        self.assertEqual(missing_report['valor']['count'], 1)


class TestEconomicIndicators(unittest.TestCase):
    """Testes para indicadores econômicos."""
    
    def setUp(self):
        self.indicators = EconomicIndicators(engine="pandas")
        
        # Dados de teste para LQ
        self.employment_data = pd.DataFrame({
            'municipio': ['Joinville', 'Joinville', 'Florianópolis', 'Florianópolis'],
            'cnae': ['Indústria', 'Serviços', 'Indústria', 'Serviços'],
            'num_jobs': [1000, 500, 200, 800]
        })
        
        # Dados de teste para exportação (RCA)
        self.export_data = pd.DataFrame({
            'pais': ['Brasil', 'Brasil', 'Brasil', 'Brasil'],
            'produto': ['Automóveis', 'Soja', 'Automóveis', 'Soja'],
            'valor_exportacao': [100, 200, 50, 150]
        })
    
    def test_calculate_location_quotient(self):
        """Testa cálculo do Location Quotient."""
        lq_result = self.indicators.calculate_location_quotient(
            self.employment_data,
            region_col='municipio',
            sector_col='cnae',
            employment_col='num_jobs'
        )
        
        self.assertIsNotNone(lq_result)
        self.assertIn('location_quotient', lq_result.columns)
        self.assertIn('specialization', lq_result.columns)
        self.assertEqual(len(lq_result), 4)  # 2 cidades x 2 setores
    
    def test_calculate_hhi(self):
        """Testa cálculo do Índice HHI."""
        hhi_result = self.indicators.calculate_herfindahl_hirschman_index(
            self.employment_data,
            region_col='municipio',
            sector_col='cnae',
            value_col='num_jobs'
        )
        
        self.assertIsNotNone(hhi_result)
        self.assertIn('hhi', hhi_result.columns)
        self.assertIn('concentration_level', hhi_result.columns)
        self.assertEqual(len(hhi_result), 2)  # 2 cidades
        
        # Verifica se valores HHI estão no intervalo correto (0-1)
        self.assertTrue(all(0 <= x <= 1 for x in hhi_result['hhi']))
    
    def test_calculate_growth_rates(self):
        """Testa cálculo de taxas de crescimento."""
        # Cria dados temporais
        temporal_data = pd.DataFrame({
            'municipio': ['Joinville'] * 5,
            'ano': [2018, 2019, 2020, 2021, 2022],
            'emprego': [1000, 1100, 1000, 1150, 1200]
        })
        
        growth_result = self.indicators.calculate_growth_rates(
            temporal_data,
            value_col='emprego',
            time_col='ano',
            group_cols=['municipio'],
            periods=[1, 3]
        )
        
        self.assertIsNotNone(growth_result)
        self.assertIn('emprego_growth_1y', growth_result.columns)
        self.assertIn('emprego_growth_3y', growth_result.columns)


class TestQualityChecker(unittest.TestCase):
    """Testes para verificação de qualidade."""
    
    def setUp(self):
        self.checker = QualityChecker()
        self.test_df = pd.DataFrame({
            'municipio': ['Joinville', 'Florianópolis', 'Joinville'],
            'ano': [2020, 2020, 2020],
            'valor': [100, 200, 100]
        })
    
    def test_generate_quality_report(self):
        """Testa geração de relatório de qualidade."""
        report = self.checker.generate_quality_report(self.test_df)
        
        self.assertIn('shape', report)
        self.assertIn('completeness', report)
        self.assertIn('duplicates', report)
        self.assertIn('data_types', report)
        
        # Verifica estrutura do relatório
        self.assertEqual(report['shape']['rows'], 3)
        self.assertEqual(report['shape']['columns'], 3)


class TestIntegration(unittest.TestCase):
    """Testes de integração entre módulos."""
    
    def test_full_pipeline_mock(self):
        """Testa pipeline completo com dados mock."""
        # Cria dados mock
        mock_data = pd.DataFrame({
            'municipio': ['Joinville'] * 10 + ['Florianópolis'] * 10,
            'cnae': ['Indústria', 'Serviços'] * 10,
            'ano': [2020, 2021] * 10,
            'num_jobs': np.random.randint(100, 1000, 20)
        })
        
        # 1. Limpeza
        cleaner = DataCleaner()
        clean_data = cleaner.standardize_column_names(mock_data)
        
        # 2. Validação
        validator = DataValidator()
        is_valid, missing = validator.validate_required_columns(clean_data, ['municipio', 'cnae'])
        self.assertTrue(is_valid)
        
        # 3. Cálculo de indicadores
        indicators = EconomicIndicators()
        lq_result = indicators.calculate_location_quotient(clean_data)
        
        self.assertIsNotNone(lq_result)
        self.assertGreater(len(lq_result), 0)


def run_tests():
    """Executa todos os testes."""
    # Descobre e executa testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retorna resultado
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)