
# NFL Scraping

  

NFL Scraping é um projeto criado para coletar dados do site footballdb.com usando técnicas de web scraping com o framework Scrapy.

  

## Objetivo

  

O principal objetivo do NFL Scraping é extrair informações detalhadas de jogos, jogadores e estatísticas da NFL diretamente do footballdb.com para posterior análise e processamento.

  

## Funcionalidades

  

-  **Coleta de Dados:** Utiliza o Scrapy para extrair informações de jogos, estatísticas de jogadores (por exemplo, passing, rushing, fumbles) e dados de times.

-  **Processamento de Dados:** Organiza e salva os dados extraídos em arquivos JSON para uso em análises futuras e desenvolvimento de algoritmos de ML.

  

## Tecnologias Utilizadas

  

-  **Linguagem de Programação:** Python

-  **Framework de Web Scraping:** Scrapy

-  **Gerenciamento de Versionamento:** Git/GitHub

  

## Estrutura do Projeto

  

``ScrapingNfl/ScrapingNfl/spiders/``: Scripts de web scraping para coleta de dados do site footballdb.com.

  

``data/``: Diretório onde os dados extraídos são armazenados.

  

## Como Usar

  

### Clone o Repositório

```git clone [https://github.com/lessaconstant/Nfl_WebScrap.git](https://github.com/lessaconstant/ScrapingNfl.git)```

``cd Nfl_WebScrap``


### Crie um Ambiente Virtual (recomendado)

#### Pelo bash:
1. Crie o ambiente virtual:
``python3 -m venv venv``
2. Ative o ambiente:
- **Linux:**
``source venv/bin/activate``
- **Windows:**
``venv\Scripts\activate``

#### Pelo pyenv:
1. Instale a versão do Python:
``pyenv install 3.10.0``
2. Crie o ambiente virtual:
``pyenv virtualenv 3.10.0 env``
3. Ative o ambiente:
``pyenv activate env``

### Instale as Dependências

Certifique-se de ter o Python 3.10+ instalado e execute:

``pip install -r requirements.txt``

### Execute o Web Scraping

Existem 3 spiders disponíveis:
``players_data.py`` - Spider para coleta dados dos jogadores separados por ano, categoria e temporada.
``scores_data.py`` - Spider para coleta dados dos jogos separados por ano e semana.
``teams_data.py`` - Spider para coleta dados dos times separados por ano, temporada e posição (Ataque e Defesa).
 Estes scripts coletam dados de 2014 até 2024 e pode ser alterado modificando a variável `years`
 
 Para estes 3 spiders, existe um script python para chama-los seguidamente, basta executar este comando no root:
 ``python3 data_collect.py``


Além destes 3 spiders, existe mais um que fara a coleta dos dados de um jogador ao longo de uma temporada específica, trata-se do spider ``player_per_temp.py``.  Atualmente, este script funciona apenas para QuarterBacks, coletando os dados de **passing**, **rushing** e **fumbles** destes. Para configura-lo, precisa alterar as variáveis ``player``, ``team`` (O time precisa ser em sigla) e ``year``.
Exemplo:
``player = "Baker Mayfield"``
``team = "TB"``
``year = "2024"``


Todos os dados retornados serão Jsons e ficaram armazenados no diretório ``data/``.

## Aviso de Propriedade dos Dados 
Todos os dados coletados pertencem ao domínio footballdb.com. Este projeto utiliza técnicas de web scraping apenas para fins de estudo e análise, respeitando os termos de uso do site.


## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções de bugs ou novas funcionalidades.

## Licença

Este projeto está licenciado sob a Licença MIT.

## Contato

Para dúvidas ou sugestões, entre em contato pelo GitHub ou envie um e-mail para lessaconstant@gmail.com.