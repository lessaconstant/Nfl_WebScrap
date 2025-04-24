import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "teams_data"
    allowed_domains = ["footballdb.com"]
    
    # --- Parâmetros de iteração: categorias, anos, temporadas e lado do time ---
    categories = [         
        "totals", "passing", "rushing",
        "kickoff-returns", "punt-returns",
        "punting", "scoring", "downs"
    ]
    years = list(range(2024, 2013, -1))  
    seasons = ['regular-season', 'postseason']
    positions = ["offense", "defense"]  

    # --- Mapeamento de colunas esperadas para cada categoria ---
    category_columns = {
        'totals':         ["Team","Gms","Tot Pts","Pts/G","RushYds","RYds/G","PassYds","PYds/G","TotYds","Yds/G"],
        'passing':        ["Team","Gms","Att","Cmp","Pct","Yds","YPA","TD","Int","Sack","Loss","Rate","NetYds","Yds/G"],
        'rushing':        ["Team","Gms","Att","Yds","Avg","TD","FD","Yds/G"],
        'kickoff-returns':["Team","Gms","Num","Yds","Avg","Lg","TD","Yds/G"],
        'punt-returns':   ["Team","Gms","Num","Yds","Avg","FC","Lg","TD","Yds/G"],
        'punting':        ["Team","Gms","Punts","Yds","Avg","Lg","TB","In20","Blk","Net"],
        'scoring':        ["Team","Tot","R","P","KR","PR","IR","FR","BK","BP","FGR","PAT","FG","Conv","Saf","Pts"],
        'downs':          ["Team","Gms","Rush","Pass","Pen","Tot","3-Att","3-Made","3-Pct","4-Att","4-Made","4-Pct"],
    }

    def start_requests(self):
        """
        --- Dispara as requisições iniciais ---
        Para cada combinação de ano, categoria, posição e temporada,
        gera a URL e chama parse() com esses parâmetros em response.meta.
        """
        print("Iniciando start_requests...")
        for year in self.years:
            for category in self.categories:
                for position in self.positions:
                    for season in self.seasons:
                        url = f"https://www.footballdb.com/statistics/nfl/team-stats/{position}-{category}/{year}/{season}"
                        print(f"URL: {url}")
                        yield scrapy.Request(
                            url,
                            callback=self.parse,
                            meta={
                                'year': year,
                                'category': category,
                                'position': position,
                                'season': season
                            }
                        )

    def parse(self, response):
        """
        --- Extrai estatísticas de times ---
        1. Lê os parâmetros do season, category, position e year.
        2. Itera em cada linha de dados da tabela (tr sem a classe .header).
        3. Para cada coluna definida em category_columns, extrai o texto correto.
        4. Adiciona metadados (posição, categoria, ano, temporada) e armazena na lista.
        5. Chama save_data() para persistir em JSON.
        """
        year     = response.meta['year']
        category = response.meta['category']
        position = response.meta['position']
        season   = response.meta['season']
        
        # Seleciona todas as linhas de dados (excluindo o cabeçalho)
        rows = response.css('tr:not(.header)')
        columns = self.category_columns.get(category, [])
        data = []

        for row in rows:
            team_data = {}
            # Para cada coluna esperada, extrai nome ou valor
            for idx, column in enumerate(columns, start=1):
                if column == 'Team':
                    # Link com nome do time está em <a>
                    team_data[column] = row.css(f'td:nth-child({idx}) a::text').get()
                else:
                    team_data[column] = row.css(f'td:nth-child({idx})::text').get()

            # --- Adiciona metadados ao registro ---
            team_data['position'] = position
            team_data['category'] = category
            team_data['year']     = year
            team_data['season']   = season

            print(team_data)  # Debug: imprime o dicionário
            data.append(team_data)

        # --- Persiste se houver dados coletados ---
        if data:
            self.save_data(data, year, season, position, category)

    def save_data(self, data, year, season, position, category):
        """
        --- Persiste os dados em disco ---
        Estrutura: ../data/Teams/<year>/<season>/<position>/<category>.json
        """
        base_dir    = os.path.join(os.getcwd(), "..", "data", "Teams")
        position_dir = os.path.join(base_dir, str(year), season, position)
        os.makedirs(position_dir, exist_ok=True)

        file_path = os.path.join(position_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos em {file_path}")
