# EcoMap.BR - Pipeline de Análise Econômica

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Prod%20Ready-success)](README.md)

Pipeline automatizado para análise de complexidade econômica e ecossistema de inovação com foco em **Joinville/SC**.

## 🎯 Objetivo

Desenvolver um sistema automatizado para:
- **Ingerir** dados de múltiplas fontes econômicas
- **Calcular** indicadores de complexidade econômica (LQ, RCA, HHI)
- **Visualizar** padrões e tendências
- **Gerar** relatórios automatizados com insights

## 📋 Funcionalidades

### ✅ Pipeline Completo
- **Ingestão de Dados**: RAIS, CAGED, PIB, ComexStat, DataViva
- **Limpeza Automatizada**: Detecção de encoding, padronização de nomes
- **Validação de Qualidade**: Verificação de consistência e completude
- **Indicadores Econômicos**: Location Quotient, RCA, HHI, Crescimento
- **Visualizações**: Dashboards interativos, treemaps, séries temporais
- **Relatórios**: Geração automatizada em Markdown, HTML e PDF

### 🔧 Tecnologias
- **Python 3.8+** com pandas/polars para processamento
- **Matplotlib/Plotly** para visualizações
- **Jupyter Notebook** para análise exploratória
- **CLI Interface** com argparse
- **Configuração YAML** para flexibilidade

## 🚀 Instalação

### 1. Clonar o Repositório
```bash
git clone <repository-url>
cd EcoMap.BR
```

### 2. Criar Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS  
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Dados
Coloque os arquivos de dados nas seguintes pastas:
```
Coletas/
├── RAIS/           # Dados RAIS (.xlsx, .csv)
├── CAGED/          # Dados CAGED (.xls, .csv)
├── ComexStat/      # Dados de exportação (.xlsx)
├── DataViva/       # Dados complementares (.csv)
└── PIB/            # Dados de PIB (se disponível)
```

## 📖 Uso

### Interface CLI

#### Executar Pipeline Completo
```bash
python main.py all
```

#### Comandos Específicos
```bash
# Ingestão de dados
python main.py ingest

# Cálculo de indicadores
python main.py derive

# Criação de visualizações
python main.py viz

# Geração de relatório
python main.py report
```

#### Opções Avançadas
```bash
# Processar fontes específicas
python main.py ingest --sources rais caged

# Modo verbose
python main.py all --verbose

# Arquivo de configuração customizado
python main.py all --config minha_config.yaml
```

### Jupyter Notebook
```bash
cd notebooks
jupyter notebook analise_exploratoria.ipynb
```

## ⚙️ Configuração

Edite `config/config.yaml` para customizar:

```yaml
# Filtros geográficos
geographic:
  target_municipality: "Joinville"
  state_filter: "Santa Catarina"
  include_regions: ["Sul", "Sudeste"]

# Período temporal
temporal:
  start_year: 2018
  end_year: 2023
  
# Indicadores a calcular
analysis:
  indicators:
    location_quotient: true
    revealed_comparative_advantage: true
    hhi_concentration: true
    employment_growth: true
    seasonality_decomposition: false

# Performance
performance:
  preferred_engine: "pandas"  # ou "polars"
  chunk_size: 10000
  n_jobs: -1
```

## 📊 Indicadores Econômicos

### Location Quotient (LQ)
```
LQ = (Emp_setor_região / Emp_total_região) / (Emp_setor_país / Emp_total_país)
```
- **LQ > 1.2**: Alta especialização
- **LQ 0.8-1.2**: Especialização média
- **LQ < 0.8**: Baixa especialização

### Vantagem Comparativa Revelada (RCA)
```
RCA = (X_ij / X_it) / (X_nj / X_nt)
```
- **RCA > 2.5**: Vantagem forte
- **RCA 1.0-2.5**: Vantagem moderada
- **RCA < 1.0**: Sem vantagem

### Índice de Concentração (HHI)
```
HHI = Σ(participação_setor)²
```
- **HHI < 0.15**: Baixa concentração
- **HHI 0.15-0.25**: Concentração moderada
- **HHI > 0.25**: Alta concentração

## 📁 Estrutura do Projeto

```
EcoMap.BR/
├── config/
│   └── config.yaml              # Configurações principais
├── src/
│   ├── utils/
│   │   ├── io_utils.py         # Carregamento de dados
│   │   ├── data_cleaning.py    # Limpeza e padronização
│   │   └── validation.py       # Validação de qualidade
│   ├── ingestion.py            # Pipeline de ingestão
│   ├── indicators.py           # Cálculo de indicadores
│   ├── visualization.py        # Visualizações
│   └── reports.py              # Geração de relatórios
├── notebooks/
│   └── analise_exploratoria.ipynb  # Análise interativa
├── tests/
│   └── test_ecomap.py          # Testes unitários
├── outputs/                    # Resultados gerados
│   ├── processed_data/         # Dados processados
│   ├── indicators/             # Indicadores calculados
│   ├── visualizations/         # Gráficos e dashboards
│   └── reports/                # Relatórios finais
├── main.py                     # Interface CLI
├── requirements.txt            # Dependências Python
└── README.md                   # Esta documentação
```

## 🎨 Visualizações

### Dashboard Principal
- Visão geral dos indicadores por região
- Gráficos interativos com Plotly
- Filtros por período e setor

### Treemap de Especialização
- Visualização hierárquica dos setores
- Tamanho proporcional ao emprego
- Cores baseadas no Location Quotient

### Séries Temporais
- Evolução dos indicadores ao longo do tempo
- Análise de tendências e sazonalidade
- Comparações entre regiões

### Matriz de Correlação
- Correlações entre diferentes indicadores
- Identificação de padrões multidimensionais

## 📈 Outputs

### Dados Processados
- **Formato**: Parquet (pandas/polars)
- **Localização**: `outputs/processed_data/`
- **Conteúdo**: Dados limpos e padronizados

### Indicadores
- **Formato**: Parquet + Pickle
- **Localização**: `outputs/indicators/`
- **Conteúdo**: LQ, RCA, HHI, crescimento, sazonalidade

### Visualizações
- **Formato**: HTML (interativo) + PNG (estático)
- **Localização**: `outputs/visualizations/`
- **Conteúdo**: Dashboards, gráficos, treemaps

### Relatórios
- **Formato**: Markdown, HTML, PDF
- **Localização**: `outputs/reports/`
- **Conteúdo**: Análises, insights, recomendações

## 🧪 Testes

```bash
# Executar testes unitários
python tests/test_ecomap.py
```

## 🛠️ Desenvolvimento

### Adicionar Nova Fonte de Dados
1. Implemente método em `EcoMapIngester`
2. Adicione configuração em `config.yaml`
3. Crie testes em `test_ecomap.py`

### Novo Indicador Econômico
1. Adicione método em `EconomicIndicators`
2. Implemente visualização correspondente
3. Atualize templates de relatório

### Personalização de Visualizações
1. Edite `EcoMapVisualizer`
2. Configure cores e estilos em `config.yaml`
3. Teste no Jupyter Notebook

## 📋 Roadmap

### Próximas Versões
- [ ] **v2.0**: Integração com APIs externas (IBGE, MDIC)
- [ ] **v2.1**: Modelos preditivos com machine learning
- [ ] **v2.2**: Interface web com Streamlit/Dash
- [ ] **v2.3**: Comparação automática com regiões similares
- [ ] **v2.4**: Alertas automáticos de mudanças significativas

### Melhorias Planejadas
- [ ] Cache inteligente para dados processados
- [ ] Paralelização com Dask para grandes datasets  
- [ ] Export para formatos GIS (shapefile, geojson)
- [ ] Integração com banco de dados (PostgreSQL)
- [ ] API REST para acesso aos indicadores

## 🤝 Contribuições

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📞 Suporte

### Problemas Comuns

**Erro de Encoding**
```bash
# Use configuração específica
python main.py ingest --config config_utf8.yaml
```

**Memória Insuficiente**
```bash
# Configure chunks menores
# config.yaml -> performance.chunk_size: 5000
```

**Dependências Faltantes**
```bash
pip install --upgrade -r requirements.txt
```

### Logs e Debug
```bash
# Modo verbose para debug
python main.py all --verbose

# Arquivo de log
tail -f ecomap.log
```

## 📜 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📚 Referências

### Metodologia
- **Location Quotient**: Isserman, A. M. (1977). The location quotient approach to estimating regional economic impacts.
- **RCA**: Balassa, B. (1965). Trade liberalisation and "revealed" comparative advantage.
- **HHI**: Hirschman, A. O. (1964). The paternity of an index.
- **Complexidade Econômica**: Hidalgo, C. A., & Hausmann, R. (2009). The building blocks of economic complexity.

### Fontes de Dados
- **RAIS**: Ministério do Trabalho e Emprego
- **CAGED**: Ministério do Trabalho e Emprego
- **PIB Municipal**: IBGE
- **ComexStat**: Ministério do Desenvolvimento, Indústria e Comércio Exterior
- **DataViva**: Governo de Minas Gerais / MIT

---

**Desenvolvido com ❤️ para análise econômica regional**

*Para dúvidas técnicas ou sugestões, abra uma issue no repositório.*
