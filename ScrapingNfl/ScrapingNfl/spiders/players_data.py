import scrapy      
import os          
import json        

class NflSpider(scrapy.Spider):
    name = "players_data"
    allowed_domains = ["footballdb.com"]  

    # --- Definições de quais estatísticas e anos serão coletados ---
    categories = [  # Tipos de estatísticas disponíveis no site
        'passing', 'rushing', 'receiving', 'kickoff-returns', 'punt-returns',
        'defense', 'punting', 'kicking', 'kickoffs', 'yards-from-scrimmage',
        'all-purpose-yards', 'fumbles', 'scoring'
    ]
    years = [year for year in range(2024, 2006, -1)]  # De 2024 a 2007
    seasons = ['regular-season', 'postseason']        # Temporadas

    # --- Mapeamento de cada categoria para suas colunas na página ---
    category_columns = {
        'passing':             ['player','gms','att','cmp','pct','yds','ypa','td','td_pct','int','int_pct','lg','sack','loss','rate'],
        'rushing':             ['player','gms','att','yds','avg','ypg','lg','td','fd'],
        'receiving':           ['player','gms','rec','yds','avg','ypg','lg','td','fd','tar','yac'],
        'kickoff-returns':     ['player','gms','num','yds','avg','fc','lg','td'],
        'punt-returns':        ['player','gms','num','yds','avg','fc','lg','td'],
        'defense':             ['player','gms','int','avg','lg','td','solo','ast','tot','sack','ydsl'],
        'punting':             ['player','gms','punts','yds','avg','lg','tb','in20','ob','fc','dwn','blk','net','ret','ryds','td'],
        'kicking':             ['player','gms','pat','fg','0-19','20-29','30-39','40-49','50+','lg','pts'],
        'kickoffs':            ['player','gms','num','yds','avg','lg','tb','ob','short','tblz','ret','ryds','td','osk','osr'],
        'yards-from-scrimmage':['player','gms','touch','yds_total','ypg','att','yds_rush','ypg_rush','rec','yds_rec','ypg_rec'],
        'all-purpose-yards':   ['player','gms','total','rush','rec','kr','pr','int','fum'],
        'fumbles':             ['player','gms','fum','lost','forced','own','opp','tot','yds','td'],
        'scoring':             ['player','gms','pts','tot','r','p','kr','pr','ir','fr','bk','bp','fgr','pat','fg','2pt','saf']
    }

    def start_requests(self):
        """
        --- Início do scraping ---
        Itera sobre anos, categorias e temporadas,
        monta a URL de estatísticas e dispara a requisição.
        """
        print("Iniciando coleta de dados dos players...")
        for year in self.years:
            for category in self.categories:
                for season in self.seasons:
                    url = f"https://www.footballdb.com/statistics/nfl/player-stats/{category}/{year}/{season}"
                    print(f"URL: {url}")
                    # Passa junto no meta a categoria, ano e temporada
                    yield scrapy.Request(
                        url,
                        callback=self.parse,
                        meta={'category': category, 'year': year, 'season': season}
                    )

    def parse(self, response):
        """
        --- Parse das linhas de estatísticas ---
        1. Recupera categoria, ano e temporada do meta.
        2. Seleciona todas as linhas de dados (excluindo cabeçalhos).
        3. Para cada linha, mapeia coluna a coluna conforme category_columns.
        4. Acumula em lista e chama save_data ao final.
        """
        category = response.meta['category']
        year     = response.meta['year']
        season   = response.meta['season']
        rows     = response.css('tr:not(.header)')  # Todas as linhas de estatística

        columns = self.category_columns.get(category, [])
        data = []

        for row in rows:
            player_data = {}
            # Percorre as colunas conhecidas, obtendo texto de cada célula
            for idx, column in enumerate(columns, start=1):
                if column == 'player':
                    # Nome do jogador e sigla do time estão juntas no primeiro <td>
                    player_name = row.css(f'td:nth-child({idx}) a::text').get()
                    team_abbr   = row.css(f'td:nth-child({idx}) span.statplayer-team::text').get()
                    player_data['player'] = player_name
                    player_data['team']   = team_abbr
                else:
                    # Obtém valor bruto de texto para as demais colunas
                    player_data[column] = row.css(f'td:nth-child({idx})::text').get()

            # Adiciona metadados
            player_data['category'] = category
            player_data['year']     = year
            player_data['season']   = season
            print("jogador:", player_data)
            data.append(player_data)

        # Chama o salvamento em disco
        self.save_data(data, year, category, season)

    def save_data(self, data, year, category, season):
        """
        --- Salva os dados coletados ---
        Diretório de saída: ../data/Players/<year>/<season>/<category>.json
        """
        base_dir   = os.path.join(os.getcwd(), "..", "data", "Players")
        season_dir = os.path.join(base_dir, str(year), season)
        os.makedirs(season_dir, exist_ok=True)

        file_path = os.path.join(season_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos em {file_path}")
