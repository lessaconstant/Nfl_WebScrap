
# NFL Predict

  

NFL Predict é um projeto criado para prever dados e resultados de jogos da NFL com base em estatísticas históricas de jogadores, times e partidas anteriores (até o ano de 2020). Este projeto utiliza um pipeline de análise de dados que começa com a coleta de informações diretamente do site footballdb.com por meio de técnicas de web scraping.

  

## Objetivo

  

O principal objetivo do NFL Predict é fornecer insights e previsões sobre jogos da NFL, auxiliando analistas, fãs ou apostadores com informações detalhadas e estatísticas confiáveis.

  

## Funcionalidades

  

- Coleta de Dados: Utiliza web scraping para extrair informações detalhadas de jogadores e equipes, categorizando-as em estatísticas como passes, corridas, recepções, defesas e mais.

  

- Processamento de Dados: Limpeza e organização dos dados coletados para facilitar análises.

  

- Análise e Previsão: Aplicação de modelos estatísticos e de machine learning para prever resultados de jogos futuros.

  

## Tecnologias Utilizadas

  

- Linguagem de Programação: Python

  

- Framework de Web Scraping: Scrapy

  

- Bibliotecas de Análise de Dados: Pandas, NumPy

  

- Visualização de Dados: Matplotlib, Seaborn

  

- Modelos de Machine Learning: Scikit-learn, TensorFlow (em desenvolvimento)

  

- Gerenciamento de Versionamento: Git/GitHub

  

## Estrutura do Projeto

  

``spiders/``: Scripts de web scraping para coleta de dados do site footballdb.com.

  

``data/``: Diretório onde os dados extraídos e processados são armazenados.

  

``models/``: Scripts e modelos de machine learning para previsões (em desenvolvimento).

  

``notebooks/``: Notebooks Jupyter para análise exploratória de dados e desenvolvimento de modelos.

  

## Como Usar

  

Clone o Repositório:

  

``git clone https://github.com/lessaconstant/nfl_predict.git``

``cd nfl_predict``

  

## Instale as Dependências:

1. Certifique-se de ter o Python 3.8+ instalado e execute:

  

``pip install -r requirements.txt``

  

2. Execute o Web Scraping:

Inicie o processo de coleta de dados com:

  

``scrapy crawl nfl``

  

3. Analise os Dados:

Use os notebooks disponíveis na pasta notebooks/ para realizar análises exploratórias.

  

4. Execute Previsões:

(Em desenvolvimento) Scripts para realizar previsões estarão disponíveis na pasta ``models/``.

  

## Contribuições

  

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções de bugs ou novas funcionalidades.

  

## Licença

  

Este projeto está licenciado sob a Licença MIT.

  

## Contato

  

Para dúvidas ou sugestões, entre em contato pelo GitHub ou envie um e-mail para lessaconstant@gmail.com.