import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "players_data"
    allowed_domains = ["footballdb.com"]
    
    # Categorias e ano
    categories = [
        'passing', 'rushing', 'receiving', 'kickoff-returns', 'punt-returns',
        'defense', 'punting', 'kicking', 'kickoffs', 'yards-from-scrimmage',
        'all-purpose-yards', 'fumbles', 'scoring'
    ]
    years = [2024, 2023, 2022, 2021, 2020]

    # Colunas de cada tabela
    category_columns = {
        'passing': ['player', 'team', 'gms', 'att', 'cmp', 'pct', 'yds', 'ypa', 'td', 'td_pct', 'int', 'int_pct', 'lg', 'sack', 'loss', 'rate'],
        'rushing': ['player', 'team', 'gms', 'att', 'yds', 'avg', 'ypg', 'lg', 'td', 'fd'],
        'receiving': ['player', 'team', 'gms', 'rec', 'yds', 'avg', 'ypg', 'lg', 'td', 'fd', 'tar', 'yac'],
        'kickoff-returns': ['player', 'team', 'gms', 'num', 'yds', 'avg', 'fc', 'lg', 'td'],
        'punt-returns': ['player', 'team', 'gms', 'num', 'yds', 'avg', 'fc', 'lg', 'td'],
        'defense': ['player', 'team', 'gms', 'int', 'avg', 'lg', 'td', 'solo', 'ast', 'tot', 'sack', 'ydsl'],
        'punting': ['player', 'team', 'gms', 'punts', 'yds', 'avg', 'lg', 'tb', 'in20', 'ob', 'fc', 'dwn', 'blk', 'net', 'ret', 'ryds', 'td'],
        'kicking': ['player', 'team', 'gms', 'pat', 'fg', '0-19', '20-29', '30-39', '40-49', '50+', 'lg', 'pts'],
        'kickoff': ['player', 'team', 'gms', 'num', 'yds', 'avg', 'lg', 'tb', 'ob', 'short', 'tblz', 'ret', 'ryds', 'td', 'osk', 'osr'],
        'yards-from-scrimmage': ['player', 'team', 'gms', 'touch', 'yds_total', 'ypg', 'att', 'yds_rush', 'ypg_rush', 'rec', 'yds_rec', 'ypg_rec'],
        'all-purpose-yards': ['player', 'team', 'gms', 'total', 'rush', 'rec', 'kr', 'pr', 'int', 'fum'],
        'fumbles': ['player', 'team', 'gms', 'fum', 'lost', 'forced', 'own', 'opp', 'tot', 'yds', 'td'],
        'scoring': ['player', 'team', 'gms', 'pts', 'tot', 'r', 'p', 'kr', 'pr', 'ir', 'fr', 'bk', 'bp', 'fgr', 'pat', 'fg', '2pt', 'saf']
    }

    def start_requests(self):
        #Montando a URL
        for year in self.years:
            for category in self.categories:
                url = f"https://www.footballdb.com/statistics/nfl/player-stats/{category}/{year}/regular-season"
                yield scrapy.Request(url, callback=self.parse, meta={'category': category, 'year': year})

    def parse(self, response):
        category = response.meta['category']
        year = response.meta['year']
        rows = response.css('tr:not(.header)')

        columns = self.category_columns.get(category, [])
        
        data = []
        #Coleta dos dados
        for row in rows:
            print(row.get())
            player_data = {}
            for idx, column in enumerate(columns, start=1):
                if column == 'player':
                    player_name = row.css(f'td:nth-child({idx}) a::text').get()
                    team = row.css(f'td:nth-child({idx}) span.statplayer-team::text').get()
                    player_data['player'] = player_name
                    player_data['team'] = team
                else:
                    player_data[column] = row.css(f'td:nth-child({idx})::text').get()

            player_data['category'] = category
            player_data['year'] = year
            data.append(player_data)
        
        self.save_data(data, year, category)

    #Salvando os dados coletados no diretório nfl/data/players
    def save_data(self, data, year, category):
        base_dir = os.path.join(os.getcwd(), "..", "data", "Players")  
        year_dir = os.path.join(base_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)

        file_path = os.path.join(year_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
