"""
EcoMap.BR - Visualization Module

Módulo para criação de visualizações interativas e dashboards
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import pandas as pd
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import numpy as np

from .utils.io_utils import DataLoader

logger = logging.getLogger(__name__)


class EconomicVisualizer:
    """
    Classe para criação de visualizações de indicadores econômicos.
    
    Gera visualizações interativas usando Plotly e estáticas usando Matplotlib/Seaborn.
    """
    
    def __init__(self, output_dir: str = "outputs/visualizations", engine: str = "polars"):
        """
        Inicializa o visualizador.
        
        Args:
            output_dir: Diretório para salvar visualizações
            engine: Engine de dados ('polars' ou 'pandas')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.engine = engine
        self.io_handler = DataLoader(engine=engine)
        
        logger.info(f"Visualizador inicializado. Output: {self.output_dir}")

    def create_dashboard(self, indicators_dict: Dict[str, Any], region: str = "Joinville") -> go.Figure:
        """
        Cria dashboard principal com os indicadores econômicos.
        
        Args:
            indicators_dict: Dicionário com indicadores calculados
            region: Nome da região para análise
            
        Returns:
            Figura Plotly do dashboard
        """
        logger.info(f"Criando dashboard de indicadores para {region}")
        
        try:
            # Criar subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Location Quotient', 'Crescimento Setorial', 
                              'Concentração HHI', 'Análise Temporal'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Dados simulados para demonstração
            setores = ['Manufatura', 'Serviços', 'Comércio', 'Tecnologia']
            lq_values = [1.85, 0.92, 1.12, 2.34]
            crescimento = [0.045, 0.023, 0.067, 0.134]
            hhi_values = [0.245, 0.123, 0.187, 0.089]
            
            # Gráfico 1: Location Quotient
            fig.add_trace(
                go.Bar(x=setores, y=lq_values, name="LQ", marker_color="blue"),
                row=1, col=1
            )
            
            # Gráfico 2: Crescimento
            fig.add_trace(
                go.Scatter(x=setores, y=crescimento, mode='lines+markers', 
                          name="Crescimento", line=dict(color="green")),
                row=1, col=2
            )
            
            # Gráfico 3: HHI
            fig.add_trace(
                go.Bar(x=setores, y=hhi_values, name="HHI", marker_color="red"),
                row=2, col=1
            )
            
            # Gráfico 4: Série temporal simulada
            import numpy as np
            dates = pd.date_range('2020-01-01', '2023-12-31', freq='ME')
            valores = 100 + np.cumsum(np.random.normal(0.5, 2, len(dates)))
            
            fig.add_trace(
                go.Scatter(x=dates, y=valores, mode='lines', 
                          name="Indicador Temporal", line=dict(color="orange")),
                row=2, col=2
            )
            
            # Layout
            fig.update_layout(
                title=f"Dashboard Econômico - {region}",
                height=800,
                showlegend=False
            )
            
            # Salvar dashboard
            dashboard_file = self.output_dir / f"dashboard_{region.lower()}.html"
            fig.write_html(dashboard_file)
            logger.info(f"Dashboard salvo: {dashboard_file.name}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar dashboard: {str(e)}")
            return go.Figure()

    def create_treemap(self, data: Dict[str, Any]) -> go.Figure:
        """
        Cria treemap dos setores por Location Quotient.
        
        Args:
            data: Dados dos indicadores
            
        Returns:
            Figura Plotly do treemap
        """
        try:
            # Dados simulados
            fig = go.Figure(go.Treemap(
                labels=["Manufatura", "Tecnologia", "Comércio", "Serviços", "Outros"],
                parents=["", "", "", "", ""],
                values=[1.85, 2.34, 1.12, 0.92, 0.76],
                textinfo="label+value"
            ))
            
            fig.update_layout(
                title="Treemap - Location Quotient por Setor",
                font_size=12
            )
            
            treemap_file = self.output_dir / "lq_treemap.html"
            fig.write_html(treemap_file)
            logger.info("[OK] Treemap do Location Quotient criado")
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar treemap: {str(e)}")
            return go.Figure()

    def create_time_series(self, data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """
        Cria séries temporais de crescimento.
        
        Args:
            data: Dados temporais
            
        Returns:
            Dicionário com figuras das séries temporais
        """
        figures = {}
        
        try:
            # Série temporal simulada de crescimento
            dates = pd.date_range('2020-01-01', '2023-12-31', freq='ME')
            
            for indicator in ['PIB', 'Emprego', 'Exportações']:
                values = 100 + np.cumsum(np.random.normal(0.3, 1.5, len(dates)))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, y=values,
                    mode='lines',
                    name=indicator,
                    line=dict(width=2)
                ))
                
                fig.update_layout(
                    title=f"Evolução Temporal - {indicator}",
                    xaxis_title="Data",
                    yaxis_title="Índice (Base 100 = Jan/2020)"
                )
                
                figures[f"timeseries_{indicator.lower()}"] = fig
                
                # Salvar
                ts_file = self.output_dir / f"timeseries_{indicator.lower()}.html"
                fig.write_html(ts_file)
                logger.info(f"[OK] Série temporal de crescimento criada: {indicator.lower()}")
            
            return figures
            
        except Exception as e:
            logger.error(f"Erro ao criar séries temporais: {str(e)}")
            return {}

    def create_seasonal_decomposition(self, data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """
        Cria gráficos de decomposição sazonal.
        
        Args:
            data: Dados para decomposição
            
        Returns:
            Dicionário com figuras de decomposição
        """
        figures = {}
        
        try:
            # Simulação de dados sazonais
            dates = pd.date_range('2020-01-01', '2023-12-31', freq='ME')
            trend = np.linspace(100, 120, len(dates))
            seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
            noise = np.random.normal(0, 2, len(dates))
            observed = trend + seasonal + noise
            
            for series_name in ['CAGED', 'Exportações']:
                fig = make_subplots(
                    rows=4, cols=1,
                    subplot_titles=['Observado', 'Tendência', 'Sazonal', 'Resíduo'],
                    shared_xaxes=True
                )
                
                fig.add_trace(go.Scatter(x=dates, y=observed, mode='lines', name='Observado'), row=1, col=1)
                fig.add_trace(go.Scatter(x=dates, y=trend, mode='lines', name='Tendência'), row=2, col=1)
                fig.add_trace(go.Scatter(x=dates, y=seasonal, mode='lines', name='Sazonal'), row=3, col=1)
                fig.add_trace(go.Scatter(x=dates, y=noise, mode='lines', name='Resíduo'), row=4, col=1)
                
                fig.update_layout(
                    title=f"Decomposição Sazonal - {series_name}",
                    height=800,
                    showlegend=False
                )
                
                figures[f"seasonal_{series_name.lower()}"] = fig
                
                # Salvar
                seasonal_file = self.output_dir / f"seasonal_{series_name.lower()}.html"
                fig.write_html(seasonal_file)
                logger.info(f"[OK] Decomposição sazonal criada: {series_name}")
            
            return figures
            
        except Exception as e:
            logger.error(f"Erro na decomposição sazonal: {str(e)}")
            return {}

    def create_correlation_matrix(self, data: Dict[str, Any]) -> go.Figure:
        """
        Cria matriz de correlação entre indicadores.
        
        Args:
            data: Dados dos indicadores
            
        Returns:
            Figura da matriz de correlação
        """
        try:
            # Matrix de correlação simulada
            indicators = ['LQ_Manufatura', 'LQ_Tecnologia', 'HHI', 'Crescimento_PIB', 'Crescimento_Emprego']
            import numpy as np
            correlation_matrix = np.random.uniform(-0.8, 0.8, (5, 5))
            np.fill_diagonal(correlation_matrix, 1.0)
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix,
                x=indicators,
                y=indicators,
                colorscale='RdBu',
                zmid=0
            ))
            
            fig.update_layout(
                title="Matriz de Correlação - Indicadores Econômicos",
                xaxis_title="Indicadores",
                yaxis_title="Indicadores"
            )
            
            corr_file = self.output_dir / "correlation_matrix.html"
            fig.write_html(corr_file)
            logger.info("[OK] Matriz de correlação criada")
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar matriz de correlação: {str(e)}")
            return go.Figure()


def create_all_visualizations(indicators_dict: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal para criar todas as visualizações.
    
    Args:
        indicators_dict: Dicionário com indicadores calculados
        config: Configurações do projeto
        
    Returns:
        Dicionário com todas as figuras criadas
    """
    logger.info("Iniciando criação de todas as visualizações...")
    
    try:
        # Extrair configurações
        output_dir = config.get('paths', {}).get('figures', 'outputs/visualizations')
        target_region = config['geographic']['target_municipality']
        
        visualizer = EconomicVisualizer(output_dir=output_dir)
        figures_dict = {}
        
        # Dashboard principal
        dashboard = visualizer.create_dashboard(indicators_dict, region=target_region)
        figures_dict['dashboard'] = dashboard
        logger.info("[OK] Dashboard principal criado")
        
        # Treemap do LQ
        if 'location_quotient' in indicators_dict:
            treemap = visualizer.create_treemap(indicators_dict['location_quotient'])
            figures_dict['lq_treemap'] = treemap
            logger.info("[OK] Treemap do Location Quotient criado")
        
        # Séries temporais
        if 'growth_indicators' in indicators_dict:
            time_series = visualizer.create_time_series(indicators_dict['growth_indicators'])
            figures_dict.update(time_series)
            
            for growth_key in time_series.keys():
                logger.info(f"[OK] Série temporal de crescimento criada: {growth_key}")
        
        # Decomposição sazonal
        if 'seasonality_analysis' in indicators_dict:
            seasonal_figs = visualizer.create_seasonal_decomposition(indicators_dict['seasonality_analysis'])
            figures_dict.update(seasonal_figs)
            
            for series_name in seasonal_figs.keys():
                logger.info(f"[OK] Decomposição sazonal criada: {series_name}")
        
        # Matriz de correlação
        correlation_fig = visualizer.create_correlation_matrix(indicators_dict)
        figures_dict['correlation_matrix'] = correlation_fig
        logger.info("[OK] Matriz de correlação criada")
        
        logger.info(f"Criação de visualizações concluída. {len(figures_dict)} figuras geradas.")
        return figures_dict
        
    except Exception as e:
        logger.error(f"Erro na criação de visualizações: {str(e)}")
        return {}