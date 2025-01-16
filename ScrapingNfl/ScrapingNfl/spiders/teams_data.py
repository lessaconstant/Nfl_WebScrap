import scrapy
import os
import json


class NflSpider(scrapy.Spider):
    name = "teams_data"
    allowed_domains = ["footballdb.com"]
    
    # Definindo as categorias e anos
    categories = [
        'overall', 'passing', 'rushing', 'kickoff return',
          'punt return', 'punting', 'scoring', 'downs'
        ]
    
    codes = ['T&group', 'P&group', 'R&group', 'KR&group', 
             'PR&group', 'U&group', 'S&group', 'W&group']
    
    years = [2024, 2023, 2022, 2021, 2020]

    # Mapeamento dos sorts por categoria
    category_sorts = {
        'passing': ['passrate'],
        'rushing': ['rushyds'],
        'receiving': ['recnum'],
        'kickoff-returns': ['kryds'],
        'punt-returns': ['pryds'],
        'defense': ['deftot'],
        'punting': ['puntavg'],
        'kicking': ['kickpts'],
        'kickoff': ['koyds'],
        'yards-from-scrimmage': ['scrimyds'],
        'all-purpose-yards': ['apyds'],
        'fumbles': ['fumnum'],
        'scoring': ['totpts']
    }
    

    # Mapeamento das colunas para cada categoria
    category_columns = {
        'T&group': ['team', 'gms', 'Tot Pts', 'Pts/G', 'RushYds', 'RYds/g', 'PassYds', 'PYds/G', 'TotYds', 'Yds/G'],
        'P&group': ["Team", "Gms", "Att", "Cmp", "Pct", "Yds", "YPA", "TD", "Int", "Sack", "Loss", "Rate", "NetYds", "Yds/G"],
        'R&group': ["Team", "Gms", "Att", "Yds", "Avg", "TD", "FD", "Yds/G"],
        'KR&group': ["Team", "Gms", "Num", "Yds", "Avg", "Lg", "TD", "Yds/G"],
        'PR&group': ["Team", "Gms", "Num", "Yds", "Avg", "FC", "Lg", "TD", "Yds/G"],
        'U&group': ["Team",	"Gms",	"Punts", "Yds",	"Avg", "Lg", "TB", "In20", "Blk", "Net"],
        'S&group': ["Team",	"Tot", "R",	"P", "KR", "PR", "IR", "FR", "BK", "BP", "FGR", "PAT", "FG", "Conv", "Saf", "Pts"],
        'W&group': ["Team",	"Gms", "Rush", "Pass", "Pen", "Tot", "T-Att", "T-Made", "T-Pct", "4-Att", "4-Made", "4-Pct"],
    }

    def start_requests(self):
        # Gerar URLs para cada categoria e ano
        for year in self.years:
            for category in self.categories:
                valid_sorts = self.category_sorts.get(category, [])
                for sort in valid_sorts:
                    url = f"https://www.footballdb.com/statistics/nfl/player-stats/{category}/{year}/regular-season?sort={sort}&limit=all"
                    yield scrapy.Request(url, callback=self.parse, meta={'category': category, 'year': year, 'sort': sort})

    def parse(self, response):
        category = response.meta['category']
        year = response.meta['year']
        rows = response.css('tr:not(.header)')  # Ignora cabeçalhos da tabela

        columns = self.category_columns.get(category, [])
        
        data = []
        for row in rows:
            player_data = {}
            for idx, column in enumerate(columns, start=1):
                if column == 'player':
                    player_data[column] = row.css(f'td:nth-child({idx}) a::text').get()
                elif column == 'team':
                    player_data[column] = row.css(f'td:nth-child({idx}) a::text').get()
                else:
                    player_data[column] = row.css(f'td:nth-child({idx})::text').get()

            player_data['category'] = category
            player_data['year'] = year
            data.append(player_data)
        
        self.save_data(data, year, category)

    def save_data(self, data, year, category):
        # Criar o diretório para os dados em 'nfl/data' se ainda não existir
        base_dir = os.path.join(os.getcwd(), "..", "data")  # Caminho relativo para o diretório 'nfl/data'
        year_dir = os.path.join(base_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)

        # Salvar os dados em um arquivo JSON
        file_path = os.path.join(year_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)




