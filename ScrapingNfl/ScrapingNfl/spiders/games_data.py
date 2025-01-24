import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "games_data"
    allowed_domains = ["footballdb.com"]
    years = [2024, 2023, 2022, 2021, 2020]


    def start_requests(self):
        for year in self.years:
            url = f"https://www.footballdb.com/games/index.html?yr={year}"
            yield scrapy.Request(url, callback=self.parse, meta={'year': year})


    def parse(self, response):
        year = response.meta['year']
        tables = response.css("table")  # Seleciona todas as tabelas na página
        weeks = response.css("div.ltbluediv span::text").getall()  # Coleta os nomes das semanas

        for week, table in zip(weeks, tables):  # Itera por cada semana e sua tabela correspondente
            games_week = []

            # Itera sobre todas as linhas da tabela (cada linha representa um jogo)
            rows = table.css("tr:not(.header)")
            for row in rows:
                game = {
                    "date": row.css("td:nth-child(1) span.d-none::text").get(),
                    "visitor": row.css("td:nth-child(2) span.d-inline::text").get(),
                    "v_score": row.css("td:nth-child(3)::text").get(),
                    "home": row.css("td:nth-child(4) span.d-inline::text").get(),
                    "h_score": row.css("td:nth-child(5)::text").get(),
                    "week": week
                }
                print(game)
                games_week.append(game)

            # Salvar os jogos da semana
            self.save_data(games_week, year, week)

            

    # Função para salvar os dados coletados no diretório nfl/data/Games
    def save_data(self, data, year, week):
        # Define o diretório base
        base_dir = os.path.join(os.getcwd(), "..", "data", "Games")  
        year_dir = os.path.join(base_dir, str(year))  # Diretório para o ano específico
        os.makedirs(year_dir, exist_ok=True)  # Cria o diretório, se não existir

        # Define o nome do arquivo para a semana
        file_name = week.replace(" ", "_").replace("/", "_") + ".json"  # Trata espaços e barras no nome
        file_path = os.path.join(year_dir, file_name)

        # Salva os dados no arquivo JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
