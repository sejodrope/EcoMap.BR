## Arquivo para anotar o que ainda precisa fazer!

### ✅ PROGRESSO ATUAL (29/08/2025)

**Status:** Item 1 concluído, iniciando Item 2

### 🎯 O que ainda precisa fazer URGENTE (até 02/09)?

- [x] ✅ **Item 1:** PIB e Crescimento Econômico (CONCLUÍDO)
- [ ] 🔄 **Item 2:** Empregos por Setor (EM ANDAMENTO - hoje)
- [ ] 📋 **Item 3:** Exportações (ComexStat) - amanhã 30/08
- [ ] 📋 **Item 4:** Vantagem Comparativa (RCA) - 31/08
- [ ] 📊 **Análise preliminar dos dados** - 01/09
- [ ] 📝 **Relatório base para orientador** - 02/09

### 🎓 SUCSTI 2025 (submissão 02-15/09)
- [ ] Definir foco do trabalho para o evento
- [ ] Preparar resumo executivo  
- [ ] Submeter inscrição

### 📅 Planejamento Completo (até 30/09)
- Finalizar coleta completa
- Analisar as informações e criar os indicadores 
- Fazer um relatório final completo
- Preparar apresentação para SUCSTI (21-23/10) 

### Guia base para coletar dados

Ótima observação, José! A matriz traz os indicadores com suas fontes e links genéricos, mas a **busca prática dos dados requer um passo a passo mais detalhado**, principalmente em sites como o **IBGE (SIDRA)** ou o **ComexStat** que têm estruturas técnicas.

Aqui está o **guia passo a passo completo**, com foco nos principais indicadores de prioridade **Alta**, conforme sua matriz.

---

## 🗺️ **Guia de Coleta de Dados para a Matriz de Classificação**

### 📂 Estrutura da Matriz:

Cada linha da matriz contém:

* Indicador
* O que mede
* Fonte sugerida
* Link de acesso genérico
* Periodicidade
* Prioridade
* Observações (que você vai preencher conforme coleta)

---

## ✅ **1. Coletando o PIB e Crescimento Econômico**

**🧭 Objetivo:** Obter o valor do PIB municipal de Joinville por ano.

### 🔗 Acesso:

* [Portal SIDRA – Tabela 5938: Produto Interno Bruto dos Municípios](https://sidra.ibge.gov.br/tabela/5938)

### 📌 Passo a passo:

1. Acesse o link da **Tabela 5938**.
2. Clique em **"Selecionar localidades"** → marque **Joinville (SC)**.
3. Clique em **"Selecionar períodos"** → marque os anos desejados (ex: 2010 a 2021).
4. Clique em **"Selecionar variáveis"**:

   * Produto Interno Bruto a preços correntes
   * Participação no PIB do estado
   * Crescimento do PIB
5. Clique em **"OK"** > depois clique em **"Tabela"**.
6. Clique em **"Baixar em Excel"** para salvar localmente ou copie/cole para o Google Sheets.

---

## ✅ **2. Coletando Empregos por Setor**

**🧭 Objetivo:** Ver quantos empregos formais existem por setor da economia.

### 🔗 Acesso:

* [Painel de Informações RAIS/CAGED – Novo CAGED](https://pdet.mte.gov.br/novo-caged)

### 📌 Passo a passo:

1. Acesse o site acima.
2. Clique em **"Novo CAGED" > "Consulta"**.
3. Escolha:

   * **Unidade da Federação**: Santa Catarina
   * **Município**: Joinville
4. Selecione:

   * Tipo: **Estoque**
   * Período: últimos anos
5. Escolha **Setor de Atividade Econômica (CNAE)** como classificação.
6. Exporte a tabela ou copie para o Google Sheets.

---

## ✅ **3. Coletando Exportações (o que Joinville vende ao mundo)**

**🧭 Objetivo:** Levantar os produtos exportados por Joinville.

### 🔗 Acesso:

* [ComexStat – Por Município](https://comexstat.mdic.gov.br/pt/município)

### 📌 Passo a passo:

1. Acesse o link acima.
2. Preencha:

   * Ano: 2022 ou mais recente
   * Unidade: **Município**
   * Município: Joinville (SC)
   * Tipo de produto: Selecione por SH2, SH4 ou SH6 (níveis de agregação)
3. Clique em **"Gerar Relatório"**.
4. Baixe o Excel ou clique em "Copiar Tabela".

---

## ✅ **4. Vantagem Comparativa (RCA - Revealed Comparative Advantage)**

**🧭 Objetivo:** Identificar produtos onde Joinville exporta mais que a média nacional.

### 📌 Cálculo do RCA:

Você precisará:

1. O valor exportado por Joinville por produto (ComexStat)
2. O total exportado pelo Brasil por produto (ComexStat)
3. Fórmula do RCA:

   $$
   RCA = \left( \frac{X_{Joinville,produto}}{X_{Joinville,total}} \right) \div \left( \frac{X_{Brasil,produto}}{X_{Brasil,total}} \right)
   $$

Se o valor for **> 1**, Joinville tem **vantagem comparativa revelada**.

---

## ✅ **5. Patentes e Propriedade Intelectual**

**🧭 Objetivo:** Quantidade de patentes registradas em Joinville.

### 🔗 Acesso:

* [INPI – Busca de Patentes](https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login)

### 📌 Passo a passo:

1. Vá até **“Busca Avançada”**.
2. Selecione “Município: Joinville”.
3. Se quiser, filtre por tipo: patentes, softwares, marcas etc.
4. Execute a busca e exporte os dados (uso mais visual/manual).

---

## ✅ **6. Startups Ativas**

**🧭 Objetivo:** Quantidade e perfil de startups em Joinville.

### 🔗 Acesso:

* [StartupBase - Joinville](https://startupbase.abstartups.com.br)

### 📌 Passo a passo:

1. Use a barra de pesquisa e digite **Joinville**.
2. Filtre por setor ou estágio (MVP, Tração, etc.).
3. Copie a lista manualmente ou use extensões para scraping (caso necessário).
4. Classifique por segmento, ano de fundação, etc.

---

## ✅ **7. Perfil da Força de Trabalho**

**🧭 Objetivo:** Características da população ocupada em Joinville.

### 🔗 Acesso:

* [IBGE – SIDRA Tabela 4099](https://sidra.ibge.gov.br/tabela/4099)

### 📌 Passo a passo:

1. Clique em **"Selecionar localidade"** > Joinville
2. Clique em **"Selecionar período"** > últimos anos
3. Clique em **"Selecionar características"**:

   * Sexo
   * Idade
   * Nível de escolaridade
4. Exiba a tabela e exporte para Excel ou Sheets.

---

## ✅ **8. Incentivos à Inovação**

**🧭 Objetivo:** Identificar políticas públicas, editais, incentivos.

### 🔗 Acesso:

* [FAPESC](https://www.fapesc.sc.gov.br/)
* [Prefeitura de Joinville](https://www.joinville.sc.gov.br/)

### 📌 Passo a passo:

1. Acesse os portais acima e vá em **Editais/Programas/Inovação**.
2. Levante quais iniciativas de fomento à inovação existem para empresas/startups.
3. Copie os nomes, links, valores e status para sua planilha.


---


## Bases de Dados Públicas para explorar e analisar 🔍

    1 – Base dos Dados 
    https://basedosdados.org/

    2 – Dados Abertos 
    https://dados.gov.br/home

    3 – Sistema Gerenciador de Séries (SGS) do Banco Central https://lnkd.in/eSNDxYx2

    4 - Estatísticas de emprego/desemprego do Ministério do Trabalho
    https://lnkd.in/ezW-yWzs

    5 - Estatísticas do Ministério da Saúde
    https://lnkd.in/eKD6sEEA

    6 - Indicadores Econômicos do IPEA
    https://lnkd.in/ebJvNTce

    7 - Estatísticas das Micro e Pequenas empresas DATASEBRAE
    https://lnkd.in/eh_Bh4iH

    8 – Estatísticas eleitorais
    https://lnkd.in/eusun2RW

    9 – Bases Socioeconômicas do IBGE
    https://lnkd.in/eZBPYtAD 

    10 – Estatísticas criminais do Ministério da Justiça
    https://lnkd.in/eTUQFzii 

    11 – Painéis Estatísticos do Supremo Tribunal Federal (STF)
    https://lnkd.in/eCT6bUC8 

    12 – Indice Firjan – Estatísticas municipais
    https://lnkd.in/ewdKt5hT 

    13 – Estatísticas do Comercio Exterior do Brasil 
    https://lnkd.in/eEz2UY-D 

    14 – Estatísticas Educacionais do Brasil 
    https://lnkd.in/eAw_pmMd 

    15 - Estatísticas Econômicas e Bancárias (FEBRABAN) 
    https://lnkd.in/eHhmfKVx

    16 - SINISA: Painel do Saneamento Básico (Ministério das Cidades).
    https://app.powerbi.com/view?r=eyJrIjoiNDU1ZmM4ZjYtNTU0YS00YjFkLWE5NzYtMjNkZThjYjg3YzVmIiwidCI6IjFmMWJlODA0LWViZGYtNDJmNC1iZGExLTdmMjlhYmU2ZDQ3YSJ9&pageName=344bbd2d217999c8e747

    17 - HidroWeb: Sistema Nacional de Informações sobre Recursos Hídricos (SNIRH) da ANA.

    18 - Painel de Geração de Resíduos Sólidos (IBAMA/MMA): 
    https://app.powerbi.com/view?r=eyJrIjoiNjQ0NWM2YjUtOWRmYS00M2ZjLWEzY2YtMjc0NTA3NDI3NGI5IiwidCI6IjZhZTNmNWU3LTU0MTktNDJhNy04MDc1LThjMTQ5MGM3MmIyNSJ9

    19 - Painel de Licenças Ambientais (IBAMA/MMA):
    https://app.powerbi.com/view?r=eyJrIjoiMjRhOWY4ZmMtNzk3ZS00ZjQzLWFmODctZmYwZWQ1NGM3YTNjIiwidCI6IjZhZTNmNWU3LTU0MTktNDJhNy04MDc1LThjMTQ5MGM3MmIyNSJ9

    20 - Painel das Unidades de Conservação (ICMBio/MMA):
    https://cnuc.mma.gov.br/powerbi

    21 - Painel do Orçamento Federal (SOF/Ministério do Planejamento):
    https://www1.siop.planejamento.gov.br/QvAJAXZfc/opendoc.htm?document=IAS%2FExecucao_Orcamentaria.qvw&host=QVS%40pqlk04&anonymous=true

    22 - PPA Participativo (SEPLAN) do MPO:
    https://app.powerbi.com/view?r=eyJrIjoiMWQ5ZTcyYmEtYmEwOC00OTVjLThkNGQtNGM5Y2ExMWE0ZTM5IiwidCI6IjNlYzkyOTY5LTVhNTEtNGYxOC04YWM5LWVmOThmYmFmYTk3OCJ9
