"""
EcoMap.BR - Automated Report Generation Module
Módulo para geração automatizada de relatórios em múltiplos formatos
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import pandas as pd
import polars as pl

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Gerador automatizado de relatórios para o EcoMap.BR.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Configurações do projeto
        """
        self.config = config
        self.output_path = Path(config['paths']['outputs']) / "reports"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Templates de seções
        self.templates = {
            'header': self._get_header_template(),
            'executive_summary': self._get_executive_summary_template(),
            'data_overview': self._get_data_overview_template(),
            'indicators_analysis': self._get_indicators_template(),
            'visualizations': self._get_visualizations_template(),
            'recommendations': self._get_recommendations_template(),
            'footer': self._get_footer_template()
        }
        
        logger.info(f"Gerador de relatórios inicializado. Output: {self.output_path}")
    
    def generate_full_report(self,
                           data_dict: Dict[str, Any],
                           indicators_dict: Dict[str, Any],
                           figures_dict: Optional[Dict[str, Any]] = None,
                           format_type: str = "markdown") -> str:
        """
        Gera relatório completo com todas as seções.
        
        Args:
            data_dict: Dados ingeridos e processados
            indicators_dict: Indicadores econômicos calculados
            figures_dict: Figuras e visualizações criadas
            format_type: Formato do relatório ("markdown", "html", "pdf")
            
        Returns:
            Caminho do arquivo de relatório gerado
        """
        logger.info(f"Gerando relatório completo em formato {format_type}")
        
        # Coleta informações para o relatório
        report_data = self._collect_report_data(data_dict, indicators_dict, figures_dict)
        
        # Gera conteúdo do relatório
        report_content = self._build_report_content(report_data)
        
        # Salva relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_ecomap_{timestamp}"
        
        if format_type.lower() == "markdown":
            report_file = self.output_path / f"{filename}.md"
            self._save_markdown_report(report_content, report_file)
        elif format_type.lower() == "html":
            report_file = self.output_path / f"{filename}.html"
            self._save_html_report(report_content, report_file)
        elif format_type.lower() == "pdf":
            report_file = self.output_path / f"{filename}.pdf"
            self._save_pdf_report(report_content, report_file)
        else:
            raise ValueError(f"Formato não suportado: {format_type}")
        
        logger.info(f"Relatório gerado: {report_file}")
        return str(report_file)
    
    def _collect_report_data(self,
                           data_dict: Dict[str, Any],
                           indicators_dict: Dict[str, Any],
                           figures_dict: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Coleta e organiza dados para o relatório."""
        report_data = {
            'metadata': self._extract_metadata(),
            'data_sources': self._analyze_data_sources(data_dict),
            'indicators': self._analyze_indicators(indicators_dict),
            'key_insights': self._extract_key_insights(data_dict, indicators_dict),
            'recommendations': self._generate_recommendations(indicators_dict),
            'visualizations': self._list_visualizations(figures_dict)
        }
        return report_data
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extrai metadados do projeto."""
        return {
            'title': 'Relatório EcoMap.BR - Análise Econômica',
            'subtitle': f'Região de Foco: {self.config["geographic"]["target_municipality"]}',
            'period': f'{self.config["temporal"]["start_year"]} - {self.config["temporal"]["end_year"]}',
            'generated_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'target_region': self.config["geographic"]["target_municipality"],
            'author': 'Sistema EcoMap.BR'
        }
    
    def _analyze_data_sources(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa fontes de dados disponíveis."""
        sources_info = {}
        
        for source_name, df in data_dict.items():
            if df is not None:
                # Converte para pandas se necessário
                if hasattr(df, 'to_pandas'):
                    df_pd = df.to_pandas()
                else:
                    df_pd = df
                
                sources_info[source_name] = {
                    'records': len(df_pd),
                    'columns': len(df_pd.columns),
                    'period_coverage': self._get_temporal_coverage(df_pd),
                    'data_quality': self._assess_data_quality(df_pd)
                }
        
        return sources_info
    
    def _get_temporal_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa cobertura temporal dos dados."""
        time_cols = [col for col in df.columns if any(keyword in col.lower() 
                                                     for keyword in ['ano', 'year', 'data', 'date'])]
        
        if not time_cols:
            return {'available': False}
        
        time_col = time_cols[0]
        return {
            'available': True,
            'column': time_col,
            'min_value': str(df[time_col].min()),
            'max_value': str(df[time_col].max()),
            'unique_periods': int(df[time_col].nunique())
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Avalia qualidade dos dados."""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        
        return {
            'completeness': round((total_cells - missing_cells) / total_cells * 100, 2),
            'missing_values': int(missing_cells),
            'duplicate_rows': int(df.duplicated().sum()),
            'quality_score': self._calculate_quality_score(df)
        }
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> str:
        """Calcula score qualitativo de qualidade."""
        completeness = (df.shape[0] * df.shape[1] - df.isnull().sum().sum()) / (df.shape[0] * df.shape[1])
        duplicates_ratio = df.duplicated().sum() / len(df)
        
        if completeness > 0.95 and duplicates_ratio < 0.01:
            return "Excelente"
        elif completeness > 0.85 and duplicates_ratio < 0.05:
            return "Boa"
        elif completeness > 0.70:
            return "Regular"
        else:
            return "Baixa"
    
    def _analyze_indicators(self, indicators_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa indicadores calculados."""
        indicators_info = {}
        
        for indicator_name, result in indicators_dict.items():
            if result is not None:
                indicators_info[indicator_name] = self._analyze_single_indicator(indicator_name, result)
        
        return indicators_info
    
    def _analyze_single_indicator(self, name: str, result: Any) -> Dict[str, Any]:
        """Analisa um indicador específico."""
        info = {
            'calculated': True,
            'type': type(result).__name__
        }
        
        try:
            if hasattr(result, 'shape'):
                # DataFrame
                if hasattr(result, 'to_pandas'):
                    df = result.to_pandas()
                else:
                    df = result
                
                info.update({
                    'records': len(df),
                    'columns': len(df.columns),
                    'summary': self._get_indicator_summary(name, df)
                })
            elif isinstance(result, dict):
                # Dicionário (ex: sazonalidade)
                info.update({
                    'keys': list(result.keys())[:5],  # Primeiras 5 chaves
                    'total_series': len(result)
                })
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _get_indicator_summary(self, name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera resumo específico por tipo de indicador."""
        summary = {}
        
        if 'location_quotient' in name.lower():
            if 'location_quotient' in df.columns:
                lq_col = 'location_quotient'
                summary = {
                    'avg_lq': round(df[lq_col].mean(), 3),
                    'max_lq': round(df[lq_col].max(), 3),
                    'specialized_sectors': int((df[lq_col] > 1.2).sum()),
                    'total_sectors': len(df)
                }
        
        elif 'hhi' in name.lower():
            if 'hhi' in df.columns:
                summary = {
                    'avg_concentration': round(df['hhi'].mean(), 3),
                    'max_concentration': round(df['hhi'].max(), 3),
                    'regions_analyzed': int(df['municipio'].nunique()) if 'municipio' in df.columns else len(df)
                }
        
        elif 'growth' in name.lower():
            growth_cols = [col for col in df.columns if 'growth' in col]
            if growth_cols:
                growth_col = growth_cols[0]
                summary = {
                    'avg_growth': round(df[growth_col].mean() * 100, 2),
                    'positive_growth_periods': int((df[growth_col] > 0).sum()),
                    'total_periods': len(df)
                }
        
        return summary
    
    def _extract_key_insights(self, data_dict: Dict[str, Any], indicators_dict: Dict[str, Any]) -> List[str]:
        """Extrai principais insights dos dados."""
        insights = []
        target_region = self.config['geographic']['target_municipality']
        
        # Insights de Location Quotient
        if 'location_quotient' in indicators_dict:
            lq_data = indicators_dict['location_quotient']
            if lq_data is not None:
                try:
                    if hasattr(lq_data, 'to_pandas'):
                        lq_df = lq_data.to_pandas()
                    else:
                        lq_df = lq_data
                    
                    region_data = lq_df[lq_df['municipio'].str.contains(target_region, case=False, na=False)]
                    if len(region_data) > 0:
                        specialized = len(region_data[region_data['location_quotient'] > 1.2])
                        total_sectors = len(region_data)
                        
                        insights.append(f"{target_region} possui {specialized} setores especializados de um total de {total_sectors} analisados")
                        
                        if specialized > 0:
                            top_sector = region_data.nlargest(1, 'location_quotient').iloc[0]
                            insights.append(f"Setor com maior especialização: {top_sector['cnae']} (LQ: {top_sector['location_quotient']:.2f})")
                except Exception:
                    pass
        
        # Insights de Concentração
        if 'hhi_concentration' in indicators_dict:
            hhi_data = indicators_dict['hhi_concentration']
            if hhi_data is not None:
                try:
                    if hasattr(hhi_data, 'to_pandas'):
                        hhi_df = hhi_data.to_pandas()
                    else:
                        hhi_df = hhi_data
                    
                    region_data = hhi_df[hhi_df['municipio'].str.contains(target_region, case=False, na=False)]
                    if len(region_data) > 0:
                        hhi_value = region_data['hhi'].iloc[0]
                        concentration_level = region_data['concentration_level'].iloc[0]
                        insights.append(f"Concentração setorial: {concentration_level} (HHI: {hhi_value:.3f})")
                except Exception:
                    pass
        
        # Insights de Crescimento
        growth_keys = [k for k in indicators_dict.keys() if 'growth' in k]
        for growth_key in growth_keys[:2]:  # Limita a 2
            try:
                growth_data = indicators_dict[growth_key]
                if growth_data is not None and hasattr(growth_data, 'columns'):
                    if hasattr(growth_data, 'to_pandas'):
                        growth_df = growth_data.to_pandas()
                    else:
                        growth_df = growth_data
                    
                    region_data = growth_df[growth_df['municipio'].str.contains(target_region, case=False, na=False)]
                    if len(region_data) > 0:
                        growth_cols = [col for col in growth_df.columns if 'growth' in col]
                        if growth_cols:
                            avg_growth = region_data[growth_cols[0]].mean()
                            insights.append(f"Taxa média de crescimento em {growth_key.replace('_', ' ')}: {avg_growth:.1%}")
            except Exception:
                pass
        
        # Insights de dados
        total_sources = len([k for k, v in data_dict.items() if v is not None])
        total_indicators = len([k for k, v in indicators_dict.items() if v is not None])
        insights.append(f"Análise baseada em {total_sources} fontes de dados com {total_indicators} indicadores calculados")
        
        return insights if insights else ["Análise exploratória concluída com sucesso"]
    
    def _generate_recommendations(self, indicators_dict: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos indicadores."""
        recommendations = []
        
        # Recomendações baseadas em LQ
        if 'location_quotient' in indicators_dict:
            recommendations.append("**Especialização Setorial**: Focar no desenvolvimento dos setores com LQ > 1.5 para maximizar vantagens competitivas")
            recommendations.append("**Diversificação**: Considerar o desenvolvimento de setores complementares aos já especializados")
        
        # Recomendações baseadas em HHI
        if 'hhi_concentration' in indicators_dict:
            recommendations.append("**Gestão de Risco**: Monitorar a concentração setorial para evitar dependência excessiva")
            recommendations.append("**Política Industrial**: Desenvolver políticas que promovam tanto eficiência quanto diversificação")
        
        # Recomendações baseadas em crescimento
        growth_keys = [k for k in indicators_dict.keys() if 'growth' in k]
        if growth_keys:
            recommendations.append("**Sustentabilidade**: Acompanhar tendências de crescimento para identificar setores em declínio")
            recommendations.append("**Investimento**: Priorizar investimentos em setores com crescimento consistente")
        
        # Recomendações baseadas em sazonalidade
        if 'seasonality_analysis' in indicators_dict:
            recommendations.append("**Planejamento**: Considerar padrões sazonais para políticas de emprego e capacitação")
        
        # Recomendações gerais
        recommendations.extend([
            "**Monitoramento Contínuo**: Estabelecer rotina de atualização dos indicadores",
            "**Benchmarking**: Comparar desempenho com regiões similares",
            "**Integração de Dados**: Expandir fontes de dados para análises mais robustas"
        ])
        
        return recommendations
    
    def _list_visualizations(self, figures_dict: Optional[Dict[str, Any]]) -> List[str]:
        """Lista visualizações disponíveis."""
        if not figures_dict:
            return ["Visualizações serão geradas separadamente via comando 'python main.py viz'"]
        
        viz_list = []
        for fig_name in figures_dict.keys():
            viz_list.append(f"- {fig_name.replace('_', ' ').title()}")
        
        return viz_list
    
    def _build_report_content(self, report_data: Dict[str, Any]) -> str:
        """Constrói o conteúdo completo do relatório."""
        sections = []
        
        # Header
        sections.append(self.templates['header'].format(**report_data['metadata']))
        
        # Executive Summary
        sections.append(self.templates['executive_summary'].format(
            key_insights='\n'.join([f"- {insight}" for insight in report_data['key_insights']]),
            total_sources=len(report_data['data_sources']),
            total_indicators=len(report_data['indicators'])
        ))
        
        # Data Overview
        data_overview = self._build_data_overview_section(report_data['data_sources'])
        sections.append(data_overview)
        
        # Indicators Analysis
        indicators_section = self._build_indicators_section(report_data['indicators'])
        sections.append(indicators_section)
        
        # Visualizations
        viz_section = self.templates['visualizations'].format(
            visualizations='\n'.join(report_data['visualizations'])
        )
        sections.append(viz_section)
        
        # Recommendations
        recommendations_section = self.templates['recommendations'].format(
            recommendations='\n'.join([f"- {rec}" for rec in report_data['recommendations']])
        )
        sections.append(recommendations_section)
        
        # Footer
        sections.append(self.templates['footer'])
        
        return '\n\n'.join(sections)
    
    def _build_data_overview_section(self, sources_info: Dict[str, Any]) -> str:
        """Constrói seção de overview dos dados."""
        content = ["## 📊 Visão Geral dos Dados", ""]
        
        for source_name, info in sources_info.items():
            content.append(f"### {source_name.upper()}")
            content.append(f"- **Registros**: {info['records']:,}")
            content.append(f"- **Colunas**: {info['columns']}")
            content.append(f"- **Qualidade**: {info['data_quality']['quality_score']} ({info['data_quality']['completeness']}% completo)")
            
            if info['period_coverage']['available']:
                content.append(f"- **Período**: {info['period_coverage']['min_value']} até {info['period_coverage']['max_value']}")
            
            content.append("")
        
        return '\n'.join(content)
    
    def _build_indicators_section(self, indicators_info: Dict[str, Any]) -> str:
        """Constrói seção de análise de indicadores."""
        content = ["## 🎯 Análise de Indicadores Econômicos", ""]
        
        for indicator_name, info in indicators_info.items():
            display_name = indicator_name.replace('_', ' ').title()
            content.append(f"### {display_name}")
            
            if 'summary' in info and info['summary']:
                summary = info['summary']
                
                if 'location_quotient' in indicator_name:
                    content.extend([
                        f"- **LQ Médio**: {summary.get('avg_lq', 'N/A')}",
                        f"- **Setores Especializados**: {summary.get('specialized_sectors', 0)}/{summary.get('total_sectors', 0)}",
                        f"- **Maior Especialização**: LQ = {summary.get('max_lq', 'N/A')}"
                    ])
                
                elif 'hhi' in indicator_name:
                    content.extend([
                        f"- **Concentração Média**: {summary.get('avg_concentration', 'N/A')}",
                        f"- **Concentração Máxima**: {summary.get('max_concentration', 'N/A')}",
                        f"- **Regiões Analisadas**: {summary.get('regions_analyzed', 'N/A')}"
                    ])
                
                elif 'growth' in indicator_name:
                    content.extend([
                        f"- **Crescimento Médio**: {summary.get('avg_growth', 'N/A')}%",
                        f"- **Períodos de Crescimento**: {summary.get('positive_growth_periods', 0)}/{summary.get('total_periods', 0)}"
                    ])
            
            else:
                content.append(f"- **Registros**: {info.get('records', 'N/A')}")
                content.append(f"- **Tipo**: {info.get('type', 'N/A')}")
            
            content.append("")
        
        return '\n'.join(content)
    
    def _save_markdown_report(self, content: str, filepath: Path) -> None:
        """Salva relatório em formato Markdown."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _save_html_report(self, content: str, filepath: Path) -> None:
        """Salva relatório em formato HTML."""
        try:
            import markdown
            
            # Converte Markdown para HTML
            html_content = markdown.markdown(content, extensions=['tables', 'toc'])
            
            # Template HTML básico
            html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório EcoMap.BR</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #2E86AB; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metadata {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_template)
                
        except ImportError:
            logger.warning("markdown não instalado, salvando como HTML básico")
            html_content = f"<html><body><pre>{content}</pre></body></html>"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
    
    def _save_pdf_report(self, content: str, filepath: Path) -> None:
        """Salva relatório em formato PDF."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
            
            # Cria documento PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Processa conteúdo Markdown para PDF
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    story.append(Paragraph(line[2:], styles['Title']))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], styles['Heading2']))
                elif line.startswith('### '):
                    story.append(Paragraph(line[4:], styles['Heading3']))
                elif line.strip():
                    story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
            
            doc.build(story)
            
        except ImportError:
            logger.warning("reportlab não instalado, convertendo para HTML ao invés de PDF")
            html_path = filepath.with_suffix('.html')
            self._save_html_report(content, html_path)
            logger.info(f"Relatório salvo como HTML: {html_path}")
    
    # Templates de seções
    
    def _get_header_template(self) -> str:
        return """# {title}

## {subtitle}

**Período de Análise**: {period}  
**Data de Geração**: {generated_at}  
**Sistema**: {author}

---"""
    
    def _get_executive_summary_template(self) -> str:
        return """## 📋 Resumo Executivo

Este relatório apresenta uma análise abrangente da economia regional com base em **{total_sources} fontes de dados** e **{total_indicators} indicadores econômicos** calculados.

### Principais Insights:
{key_insights}

### Metodologia:
- **Location Quotient (LQ)**: Mede especialização setorial comparada ao país
- **Vantagem Comparativa Revelada (RCA)**: Identifica produtos competitivos nas exportações  
- **Índice Herfindahl-Hirschman (HHI)**: Avalia concentração setorial da economia
- **Análise de Crescimento**: Taxa de crescimento em diferentes períodos
- **Decomposição Sazonal**: Padrões sazonais nos dados mensais"""
    
    def _get_data_overview_template(self) -> str:
        return "{data_overview}"  # Será preenchido dinamicamente
    
    def _get_indicators_template(self) -> str:
        return "{indicators_analysis}"  # Será preenchido dinamicamente
    
    def _get_visualizations_template(self) -> str:
        return """## 📈 Visualizações Disponíveis

As seguintes visualizações foram geradas para facilitar a interpretação dos dados:

{visualizations}

### Acesso às Visualizações:
- **Arquivos estáticos**: `outputs/visualizations/`
- **Dashboard interativo**: `dashboard_*.html`
- **Comando CLI**: `python main.py viz`"""
    
    def _get_recommendations_template(self) -> str:
        return """## 🎯 Recomendações Estratégicas

Com base na análise dos indicadores econômicos, as seguintes recomendações são propostas:

{recommendations}

### Próximos Passos:
1. Implementar monitoramento contínuo dos indicadores
2. Desenvolver políticas setoriais baseadas nos achados
3. Estabelecer benchmarks com regiões similares
4. Expandir análise para incluir novos indicadores"""
    
    def _get_footer_template(self) -> str:
        return """---

## 📚 Referências e Metodologia

### Fontes de Dados:
- **RAIS**: Relação Anual de Informações Sociais (Ministério do Trabalho)
- **CAGED**: Cadastro Geral de Empregados e Desempregados (Ministério do Trabalho)  
- **PIB Municipal**: Instituto Brasileiro de Geografia e Estatística (IBGE)
- **ComexStat**: Sistema de Análise das Informações de Comércio Exterior (MDIC)
- **DataViva**: Plataforma de dados de comércio internacional e mercado de trabalho

### Metodologia dos Indicadores:
- **Location Quotient**: (Emp_setor_região/Emp_total_região) / (Emp_setor_país/Emp_total_país)
- **RCA**: (Export_produto_país/Export_total_país) / (Export_produto_mundo/Export_total_mundo)  
- **HHI**: Σ(participação_setor)² para todos os setores

### Contato e Suporte:
Para dúvidas sobre este relatório ou o sistema EcoMap.BR, consulte a documentação técnica.

*Relatório gerado automaticamente pelo sistema EcoMap.BR*"""


def generate_automated_report(data_dict: Dict[str, Any],
                            indicators_dict: Dict[str, Any],
                            config: Dict[str, Any],
                            figures_dict: Optional[Dict[str, Any]] = None,
                            format_type: str = "markdown") -> str:
    """
    Função principal para gerar relatório automatizado.
    
    Args:
        data_dict: Dados processados
        indicators_dict: Indicadores calculados
        config: Configurações do projeto
        figures_dict: Figuras geradas (opcional)
        format_type: Formato do relatório
        
    Returns:
        Caminho do arquivo de relatório
    """
    logger.info("Gerando relatório automatizado...")
    
    generator = ReportGenerator(config)
    report_path = generator.generate_full_report(
        data_dict=data_dict,
        indicators_dict=indicators_dict,
        figures_dict=figures_dict,
        format_type=format_type
    )
    
    logger.info(f"Relatório automatizado gerado: {report_path}")
    return report_path