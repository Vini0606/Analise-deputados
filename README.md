# Análise de Deputados do Brasil

Sistema completo para extração, processamento e visualização de dados dos deputados federais brasileiros, com foco em análise de redes sociais e desempenho legislativo.

## 📋 Visão Geral do Projeto

Este projeto foi desenvolvido para coletar e analisar dados dos deputados federais da Câmara dos Deputados, integrando informações institucionais com dados de redes sociais (Instagram). O sistema permite:

- **Extração de dados legislativos**: Coleta de informações dos 513 deputados federais
- **Enriquecimento com redes sociais**: Identificação e extração de perfis do Instagram
- **Análise de engajamento**: Métricas detalhadas de performance nas redes sociais
- **Dashboard interativo**: Visualização em tempo real com simulador what-if

## 🏗️ Arquitetura do Sistema

```
analise-deputados-brasil/
├── main.py                      # Ponto de entrada da aplicação
├── pyproject.toml               # Configuração do projeto (Python 3.11+)
├── requirements.txt             # Dependências do projeto
├── config/
│   └── settings.py              # Configurações centralizadas
├── scripts/
│   ├── extract-deputados-link.py    # Extração de links do Instagram (Selenium)
│   ├── extract-deputados-data.py    # Extração de dados via API Apify
│   └── dashboard.py                 # Dashboard Streamlit interativo
├── data/
│   ├── raw/                     # Dados brutos (fontes originais)
│   │   ├── deputados.xls        # Dados originais dos deputados
│   │   └── Contato dos deputados federais.xlsx
│   ├── processed/               # Dados processados
│   │   ├── deputados.json      # Dados extraídos da API Instagram
│   │   ├── deputados.csv       # Versão CSV dos dados
│   │   └── deputados_com_instagram.xlsx  # Dados enriquecidos
│   └── Graphics/               # Visualizações geradas
│       ├── plot_1_desigualdade_real.png
│       ├── plot_2_dicotomia_real.png
│       ├── plot_3_quadrantes_real.png
│       └── plot_4_frequencia_real.png
└── notebooks/                  # Análise Exploratória de Dados (Jupyter)
    ├── AED.ipynb                # Análise exploratória principal
    ├── scrape-instagram.ipynb  # Notebook de scraping
    └── segmentacao.ipynb       # Análise de segmentação
```

## 🔄 Fluxo de Dados

### Pipeline Completo de Extração

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  dados/raw/    │────▶│ extract-deputados │────▶│ dados/processados/  │
│ deputados.xls  │     │    -link.py      │     │ deputados_com_     │
│                 │     │  (Selenium)      │     │ instagram.xlsx     │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                                         │
                                                         ▼
                        ┌──────────────────┐     ┌─────────────────────┐
                        │   Apify API      │◀────│ extract-deputados   │
                        │ (Instagram Data)│     │    -data.py         │
                        └──────────────────┘     └─────────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────────┐
                                                │  deputados.json    │
                                                │  deputados.csv     │
                                                └─────────────────────┘
```

## 📦 Dependências

O projeto utiliza as seguintes bibliotecas:

| Categoria | Biblioteca | Versão | Finalidade |
|-----------|------------|--------|------------|
| **Dados** | pandas | latest | Manipulação de DataFrames |
| | openpyxl | latest | Leitura/escrita Excel .xlsx |
| | xlrd | latest | Leitura Excel .xls |
| **Visualização** | seaborn | latest | Gráficos estatísticos |
| | matplotlib | latest | Biblioteca base de plots |
| | plotly | ≥6.7.0 | Gráficos interativos |
| **Web Scraping** | selenium | latest | Automação de navegador |
| | webdriver-manager | latest | Gerenciamento de drivers |
| **APIs** | apify-client | latest | Integração Apify (Instagram) |
| | python-dotenv | latest | Variáveis de ambiente |
| **Dashboard** | streamlit | ≥1.56.0 | Interface web interativa |
| | notebook | latest | Jupyter notebooks |

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
APIFY_API_TOKEN=sua_chave_aqui
```

> **Nota**: O token da API Apify é necessário para executar `extract-deputados-data.py`. Obtenha em [apify.com](https://apify.com).

## 🚀 Como Executar

### 1. Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 2. Pipeline de Extração

#### Passo 1: Extrair Links do Instagram

```bash
python scripts/extract-deputados-link.py
```

**O que faz**:
- Lê `data/raw/deputados.xls`
- Acessa o site da Câmara dos Deputados
- Busca cada deputade pelo nome
- Extrai o link do Instagram do perfil
- Salva em `data/processed/deputados_com_instagram.xlsx`

**Tecnologia**: Selenium + Chrome Driver

#### Passo 2: Extrair Dados do Instagram

```bash
python scripts/extract-deputados-data.py
```

**O que faz**:
- Lê `deputados_com_instagram.xlsx`
- Usa a API Apify para extrair métricas detalhadas
- Salva JSON e CSV em `data/processed/`

**Tecnologia**: Apify Client (Actor: `shu8hvrXbJbY3Eb9W`)

### 3. Executar Dashboard

```bash
streamlit run scripts/dashboard.py
```

**Acesso**: `http://localhost:8501`

O dashboard inclui:
- **Visão de Comando**: Métricas de influência e engajamento
- **Simulador What-if**: Projeção de impacto de posicionamentos
- **Biblioteca RAG**: Busca em histórico de discursos

## 📊 Dados Extraídos

### Dados da Câmara dos Deputado

| Campo | Descrição |
|------|-----------|
| Nome Parlamentar | Nome como o deputade é conhecido |
| Partido | Sigla do partido político |
| UF | Estado representado |
| Email | E-mail institucional |
| Telefone | Telefone do gabinete |

### Dados do Instagram (via Apify)

| Campo | Descrição |
|------|-----------|
| username | Nome de usuário |
| followers | Número de seguidores |
| following | Número de contas seguidas |
| posts | Número de publicações |
| avgLikes | Média de likes por post |
| avgComments | Média de comentários por post |
| engagementRate | Taxa de engajamento |

## 📈 Dashboard Streamlit

### Funcionalidades

1. **Métricas em Tempo Real**
   - Score de Influência (0-100)
   - Engajamento Médio
   - Sentimento da Base
   - Pautas Ativas

2. **Visualizações**
   - Tendência de Capital Político
   - Correlação Postagens vs. Impacto Digital
   - Aderência por Pauta

3. **Simulador What-if**
   - Seleção de pauta
   - Posicionamento (A Favor/Contra/Neutro)
   - Intensidade da comunicação
   - Projeção de risco

4. **Biblioteca RAG**
   - Busca vetorial em discursos
   - Transformação em legendas para redes

## 🔧 Configurações

As configurações centralizadas estão em `config/settings.py`:

```python
# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Arquivos de Entrada
DEPUTADOS_XLS_IN = RAW_DATA_DIR / "deputados.xls"
DEPUTADOS_CONTATOS_XLSX_IN = RAW_DATA_DIR / "Contato dos deputados federais.xlsx"

# Arquivos de Saída
DEPUTADOS_INSTA_XLSX_OUT = PROCESSED_DATA_DIR / "deputados_com_instagram.xlsx"
APIFY_JSON_OUT = PROCESSED_DATA_DIR / "deputados.json"
APIFY_CSV_OUT = PROCESSED_DATA_DIR / "deputados.csv"

# URLs e APIs
CAMARA_SEARCH_URL = "https://www.camara.leg.br/deputados/quem-sao"
APIFY_ACTOR_ID = "shu8hvrXbJbY3Eb9W"
```

## 📝 Notebooks

### AED.ipynb
Análise exploratória principal com:
- Limpeza de dados
- Tratamento de valores ausentes
- Visualizações estatísticas

### scrape-instagram.ipynb
Notebook de desenvolvimento do scraping:
- Testes de seletores
- Debug de erros
- Validação de dados

### segmentacao.ipynb
Análise de segmentação dos deputados:
- Agrupamento por partido/estado
- Análise de engajamento por segmento

## ⚠️ Considerações

- **Rate Limiting**: O scraping pode ser barrado pela Câmara. Ajuste os delays no código.
- **API Costs**: A API Apify tem custos por requisição. Monitore o uso.
- **LGPD**: Dados pessoais de deputados são públicos, mas use com responsabilidade.
- **Instagram Terms**: O uso da API deve seguir os Termos de Serviço do Instagram.

## 📚 Licença

MIT License - Veja arquivo LICENSE para detalhes.

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

---

**Autor**: Sistema de Análise de Deputados do Brasil  
**Versão**: 0.1.0  
**Python**: 3.11+