import scrapy
import os
import json


class NflSpider(scrapy.Spider):
    name = "teams_data"
    allowed_domains = ["footballdb.com"]
    
    # Definindo as categorias e anos
    categories = ["totals", "passing", "rushing", "kickoff-returns", 
             "punt-returns", "punting", "scoring", "downs"]
    
    years = [year for year in range(2024, 2013, -1)]

    seasons = ['regular-season', 'postseason']

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
        print("Iniciando start_requests...")
        for year in self.years:
            for category in self.categories:
                for position in self.positions:
                    for season in self.seasons:
                        url = f"https://www.footballdb.com/statistics/nfl/team-stats/{position}-{category}/{year}/{season}"
                        print("URL: ", url)
                        yield scrapy.Request(url, callback=self.parse, meta={'position': position, 'category': category, 'year': year})

    def parse(self, response):
        position = response.meta['position']
        category = response.meta['category']
        year = response.meta['year']
        season = response.meta['season']
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
            
            print(team_data)

            team_data['position'] = position
            team_data['category'] = category
            team_data['year'] = year
            team_data['season'] = season
            data.append(team_data)
        
        self.save_data(data, position, year, category)

    def save_data(self, data, year, season, position, category):
        # Criar o diretório para os dados em 'nfl/data' se ainda não existir
        base_dir = os.path.join(os.getcwd(), "..", "data", "Teams")  
        position_dir = os.path.join(base_dir, str(year), season, position)  # Adiciona season e position
        os.makedirs(position_dir, exist_ok=True)  # Garante que o diretório exista

        # Salvar os dados em um arquivo JSON
        file_path = os.path.join(position_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)





