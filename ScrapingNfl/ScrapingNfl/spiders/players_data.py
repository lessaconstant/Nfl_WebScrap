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
    years = [year for year in range(2024, 2013, -1)]
    seasons = ['regular-season', 'postseason']

    # Colunas de cada tabela
    category_columns = {
        'passing': ['player', 'gms', 'att', 'cmp', 'pct', 'yds', 'ypa', 'td', 'td_pct', 'int', 'int_pct', 'lg', 'sack', 'loss', 'rate'],
        'rushing': ['player', 'gms', 'att', 'yds', 'avg', 'ypg', 'lg', 'td', 'fd'],
        'receiving': ['player', 'gms', 'rec', 'yds', 'avg', 'ypg', 'lg', 'td', 'fd', 'tar', 'yac'],
        'kickoff-returns': ['player', 'gms', 'num', 'yds', 'avg', 'fc', 'lg', 'td'],
        'punt-returns': ['player', 'gms', 'num', 'yds', 'avg', 'fc', 'lg', 'td'],
        'defense': ['player', 'gms', 'int', 'avg', 'lg', 'td', 'solo', 'ast', 'tot', 'sack', 'ydsl'],
        'punting': ['player', 'gms', 'punts', 'yds', 'avg', 'lg', 'tb', 'in20', 'ob', 'fc', 'dwn', 'blk', 'net', 'ret', 'ryds', 'td'],
        'kicking': ['player', 'gms', 'pat', 'fg', '0-19', '20-29', '30-39', '40-49', '50+', 'lg', 'pts'],
        'kickoffs': ['player', 'gms', 'num', 'yds', 'avg', 'lg', 'tb', 'ob', 'short', 'tblz', 'ret', 'ryds', 'td', 'osk', 'osr'],
        'yards-from-scrimmage': ['player', 'gms', 'touch', 'yds_total', 'ypg', 'att', 'yds_rush', 'ypg_rush', 'rec', 'yds_rec', 'ypg_rec'],
        'all-purpose-yards': ['player', 'gms', 'total', 'rush', 'rec', 'kr', 'pr', 'int', 'fum'],
        'fumbles': ['player', 'gms', 'fum', 'lost', 'forced', 'own', 'opp', 'tot', 'yds', 'td'],
        'scoring': ['player', 'gms', 'pts', 'tot', 'r', 'p', 'kr', 'pr', 'ir', 'fr', 'bk', 'bp', 'fgr', 'pat', 'fg', '2pt', 'saf']
    }

    def start_requests(self):
        #Montando a URL
        print("Iniciando start_requests...")
        for year in self.years:
            for category in self.categories:
                for season in self.seasons:
                    url = f"https://www.footballdb.com/statistics/nfl/player-stats/{category}/{year}/{season}"
                    print("URL: ", url)
                    yield scrapy.Request(url, callback=self.parse, meta={'category': category, 'year': year, 'season':season})

    def parse(self, response):
        category = response.meta['category']
        year = response.meta['year']
        season = response.meta['season']
        rows = response.css('tr:not(.header)')

        columns = self.category_columns.get(category, [])
        
        data = []
        #Coleta dos dados
        for row in rows:
            player_data = {}
            for idx, column in enumerate(columns, start=1):
                if column == 'player':
                    player_name = row.css(f'td:nth-child({idx}) a::text').get()
                    team = row.css(f'td:nth-child({idx}) span.statplayer-team::text').get()
                    player_data['player'] = player_name
                    player_data['team'] = team
                else:
                    player_data[column] = row.css(f'td:nth-child({idx})::text').get()
            print(f"jogador: {player_data}")

            player_data['category'] = category
            player_data['year'] = year
            player_data['season'] = season
            data.append(player_data)
        
        self.save_data(data, year, category, season)

    #Salvando os dados coletados no diretório nfl/data/players
    def save_data(self, data, year, category, season):
        base_dir = os.path.join(os.getcwd(), "..", "data", "Players")  
        season_dir = os.path.join(base_dir, str(year), season)  
        os.makedirs(season_dir, exist_ok=True)  

        file_path = os.path.join(season_dir, f"{category}.json")  
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

