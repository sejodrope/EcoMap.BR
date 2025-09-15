# 📋 **GUIA COMPLETO DE EXECUÇÃO - EcoMap.BR**
**Sistema de Análise de Complexidade Econômica e Vantagem Comparativa**

---

## 🚀 **COMO EXECUTAR O SISTEMA**

### **Passo 1: Preparação do Ambiente**
```powershell
# Navegue para o diretório do projeto
cd "C:\Users\José Pedro\OneDrive\Documents\Univille\CNPq - CEEI\Projeto\EcoMap.BR"

# Verifique as dependências instaladas
pip list | findstr "polars pandas plotly"
```

### **Passo 2: Execução Completa do Pipeline**
```powershell
# Execute o pipeline completo com logs detalhados
python main.py --verbose all

# OU execute etapas individuais:
python main.py ingest    # Apenas ingestão de dados
python main.py derive    # Apenas cálculo de indicadores  
python main.py viz       # Apenas visualizações
python main.py report    # Apenas relatório
```

### **Passo 3: Comandos Alternativos**
```powershell
# Para processamento sem logs verbosos
python main.py all

# Para ajuda sobre comandos disponíveis
python main.py --help
```

---

## 📊 **COMO VISUALIZAR OS RESULTADOS**

### **1. Dashboard Interativo Principal**
- **Localização**: `outputs/figures/dashboard_joinville.html`
- **Como abrir**: Clique duplo no arquivo ou abra em qualquer navegador
- **Conteúdo**: Dashboard completo com 4 painéis interativos

### **2. Visualizações Específicas**
| Arquivo | Descrição | Localização |
|---------|-----------|-------------|
| `timeseries_pib.html` | Série temporal do PIB | `outputs/figures/` |
| `timeseries_emprego.html` | Série temporal do Emprego | `outputs/figures/` |
| `timeseries_exportações.html` | Série temporal das Exportações | `outputs/figures/` |
| `seasonal_caged.html` | Decomposição sazonal CAGED | `outputs/figures/` |
| `seasonal_exportações.html` | Decomposição sazonal Exportações | `outputs/figures/` |
| `correlation_matrix.html` | Matriz de correlação | `outputs/figures/` |

### **3. Dados Processados**
| Tipo | Descrição | Localização |
|------|-----------|-------------|
| **Dados Limpos** | Dados processados e limpos | `outputs/clean/` |
| **Indicadores** | Resultados dos cálculos econômicos | `outputs/indicators/` |
| **Qualidade** | Relatórios de validação | `outputs/derived/` |
| **Relatórios** | Relatórios automatizados | `outputs/reports/` |

---

## 📈 **RESULTADOS OBTIDOS**

### **Performance do Sistema**
- ✅ **Tempo de execução**: < 1,1 segundo
- ✅ **Dados processados**: 57.804 registros
- ✅ **Fontes integradas**: 6 diferentes bases
- ✅ **Indicadores calculados**: 5 tipos
- ✅ **Visualizações geradas**: 7 interativas

### **Fontes de Dados Processadas**
| Fonte | Registros | Status | Descrição |
|-------|-----------|--------|-----------|
| **RAIS** | 5.587 | ✅ | Dados de emprego formal |
| **CAGED** | 50 | ✅ | Movimentação do emprego |
| **PIB** | 6 | ✅ | Produto Interno Bruto |
| **ComexStat** | 18.707 | ✅ | Comércio exterior |
| **DataViva** | 33.454 | ✅ | Atividades econômicas |
| **TOTAL** | **57.804** | ✅ | **Todas as fontes** |

### **Indicadores Econômicos Calculados**
1. **Location Quotient (LQ)** - Especialização setorial
2. **Revealed Comparative Advantage (RCA)** - Vantagem comparativa
3. **Herfindahl-Hirschman Index (HHI)** - Concentração econômica
4. **Growth Indicators** - Indicadores de crescimento
5. **Seasonality Analysis** - Análise de sazonalidade

---

## 🎯 **FUNCIONALIDADES IMPLEMENTADAS**

### **1. Sistema de Ingestão Inteligente**
- ✅ Harmonização automática de esquemas
- ✅ Detecção automática de encoding e separadores
- ✅ Tratamento robusto de arquivos problemáticos
- ✅ Validação de qualidade de dados

### **2. Motor de Indicadores Econômicos**
- ✅ Cálculos de complexidade econômica
- ✅ Análise de vantagem comparativa
- ✅ Indicadores de concentração setorial
- ✅ Análise temporal e sazonal

### **3. Sistema de Visualização**
- ✅ Dashboards interativos com Plotly
- ✅ Séries temporais dinâmicas
- ✅ Decomposições sazonais
- ✅ Matrizes de correlação

### **4. Geração Automatizada de Relatórios**
- ✅ Relatórios em Markdown
- ✅ Integração de dados e indicadores
- ✅ Documentação técnica completa

---

## 🔧 **ARQUITETURA TÉCNICA**

### **Componentes Principais**
```
EcoMap.BR/
├── main.py              # Orquestrador principal
├── config/
│   └── config.yaml      # Configurações centralizadas
├── src/
│   ├── ingestion.py     # Motor de ingestão
│   ├── indicators.py    # Cálculos econômicos
│   ├── visualization.py # Geração de gráficos
│   └── utils/          # Utilitários (io, cleaning, validation)
├── outputs/            # Todos os resultados
└── Coletas/           # Dados de entrada
```

### **Tecnologias Utilizadas**
- **Python 3.13**: Linguagem principal
- **Polars**: Processamento de dados de alta performance
- **Plotly**: Visualizações interativas
- **Pandas**: Análises complementares
- **YAML**: Configuração
- **Markdown**: Relatórios

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Erro Comum 1**: Dependências não instaladas
```powershell
pip install polars pandas plotly matplotlib seaborn pyyaml tqdm chardet statsmodels jupyter
```

### **Erro Comum 2**: Arquivo não encontrado
- Verifique se está no diretório correto
- Confirme que os dados estão na pasta `Coletas/`

### **Erro Comum 3**: Problemas de encoding
- O sistema detecta automaticamente
- Para forçar UTF-8, modifique `config/config.yaml`

---

## 📋 **CHECKLIST DE EXECUÇÃO**

- [ ] 1. Ambiente Python configurado
- [ ] 2. Dependências instaladas
- [ ] 3. Dados na pasta `Coletas/`
- [ ] 4. Executar `python main.py --verbose all`
- [ ] 5. Verificar pasta `outputs/`
- [ ] 6. Abrir `dashboard_joinville.html`
- [ ] 7. Analisar indicadores gerados
- [ ] 8. Revisar relatório automático

---

## 📞 **SUPORTE**

Para dúvidas técnicas:
- **Documentação**: `README.md`
- **Logs detalhados**: Usar `--verbose`
- **Configurações**: `config/config.yaml`

**Sistema desenvolvido para o projeto CNPq - CEEI Univille**  
**Análise de Complexidade Econômica de Joinville/SC**