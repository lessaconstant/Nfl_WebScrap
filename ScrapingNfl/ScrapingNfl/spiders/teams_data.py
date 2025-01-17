import scrapy
import os
import json


class NflSpider(scrapy.Spider):
    name = "teams_data"
    allowed_domains = ["footballdb.com"]
    
    # Definindo as categorias e anos
    categories = ["totals", "passing", "rushing", "kickoff-returns", 
             "punt-returns", "punting", "scoring", "downs"]
    
    years = [2024, 2023, 2022, 2021, 2020]

    positions = ["offense", "defense"]

    # Mapeamento das colunas para cada categoria
    category_columns = {
        'totals': ["Team", "Gms", "Tot Pts", "Pts/G", "RushYds", "RYds/G", "PassYds", "PYds/G", "TotYds", "Yds/G"],
        'passing': ["Team", "Gms", "Att", "Cmp", "Pct", "Yds", "YPA", "TD", "Int", "Sack", "Loss", "Rate", "NetYds", "Yds/G"],
        'rushing': ["Team", "Gms", "Att", "Yds", "Avg", "TD", "FD", "Yds/G"],
        'kickoff-returns': ["Team", "Gms", "Num", "Yds", "Avg", "Lg", "TD", "Yds/G"],
        'punt-returns': ["Team", "Gms", "Num", "Yds", "Avg", "FC", "Lg", "TD", "Yds/G"],
        'punting': ["Team",	"Gms",	"Punts", "Yds",	"Avg", "Lg", "TB", "In20", "Blk", "Net"],
        'scoring': ["Team",	"Tot", "R",	"P", "KR", "PR", "IR", "FR", "BK", "BP", "FGR", "PAT", "FG", "Conv", "Saf", "Pts"],
        'downs': ["Team",	"Gms", "Rush", "Pass", "Pen", "Tot", "3-Att", "3-Made", "3-Pct", "4-Att", "4-Made", "4-Pct"],
    }

    def start_requests(self):
        # Gerar URLs para cada categoria e ano
        for year in self.years:
            for category in self.categories:
                for position in self.positions:
                    url = f"https://www.footballdb.com/statistics/nfl/team-stats/{position}-{category}/{year}/regular-season"
                    yield scrapy.Request(url, callback=self.parse, meta={'position': position, 'category': category, 'year': year})

    def parse(self, response):
        position = response.meta['position']
        category = response.meta['category']
        year = response.meta['year']
        rows = response.css('tr:not(.header)')  # Ignora cabeçalhos da tabela

        columns = self.category_columns.get(category, [])
        
        data = []
        for row in rows:
            team_data = {}
            for idx, column in enumerate(columns, start=1):
                if column == 'Team':
                    team_data[column] = row.css(f'td:nth-child({idx}) a::text').get()
                else:
                    team_data[column] = row.css(f'td:nth-child({idx})::text').get()

            team_data['position'] = position
            team_data['category'] = category
            team_data['year'] = year
            data.append(team_data)
        
        self.save_data(data, position, year, category)

    def save_data(self, data, position, year, category):
        # Criar o diretório para os dados em 'nfl/data' se ainda não existir
        base_dir = os.path.join(os.getcwd(), "..", "data", "Teams")  # Caminho relativo para o diretório 'nfl/data'
        year_dir = os.path.join(base_dir, str(year))
        posi_dir = os.path.join(year_dir, position)
        os.makedirs(posi_dir, exist_ok=True)

        # Salvar os dados em um arquivo JSON
        file_path = os.path.join(posi_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)




