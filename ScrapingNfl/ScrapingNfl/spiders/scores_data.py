import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "scores_data"
    allowed_domains = ["footballdb.com"]

    # --- Anos que serão processados (de 2024 até 2007) ---
    years = list(range(2024, 2006, -1))

    def start_requests(self):
        """
        --- Ponto de entrada ---
        Para cada ano em self.years, monta a URL da página de resultados
        e dispara a requisição, armazenando o 'year' em response.meta.
        """
        print("Iniciando start_requests...")
        for year in self.years:
            url = f"https://www.footballdb.com/games/index.html?yr={year}"
            print(f"URL: {url}")
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'year': year}
            )

    def parse(self, response):
        """
        --- Parse da página de resultados de cada ano ---
        1. Recupera o ano do meta.
        2. Seleciona todas as tabelas (cada tabela = uma semana).
        3. Coleta os nomes das semanas via div.ltbluediv.
        4. Para cada par (semana, tabela), extrai cada linha de jogo.
        """
        year = response.meta['year']
        tables = response.css("table")  
        weeks  = response.css("div.ltbluediv span::text").getall()

        # Itera casado semana
        for week, table in zip(weeks, tables):
            games_week = []  # Lista temporária para esta semana

            # Seleciona todas as linhas de dados (excluindo cabeçalhos)
            rows = table.css("tr:not(.header)")
            for row in rows:
                # Mapeia cada coluna em um campo do dict
                game = {
                    "date":    row.css("td:nth-child(1) span.d-none::text").get(),
                    "visitor": row.css("td:nth-child(2) span.d-inline::text").get(),
                    "v_score": row.css("td:nth-child(3)::text").get(),
                    "home":    row.css("td:nth-child(4) span.d-inline::text").get(),
                    "h_score": row.css("td:nth-child(5)::text").get(),
                    "week":    week
                }
                print(game)            # Debug: imprime cada jogo
                games_week.append(game)

            # --- Salva todos os jogos desta semana em JSON ---
            self.save_data(games_week, year, week)

    def save_data(self, data, year, week):
        """
        --- Persiste em disco ---
        Diretório: ../data/Games/<year>/
        Arquivo:   <week>.json (espaços e barras substituídos por _)
        """
        base_dir = os.path.join(os.getcwd(), "..", "data", "Games")
        year_dir = os.path.join(base_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)

        # Ajusta o nome do arquivo para não conter caracteres inválidos
        file_name = week.replace(" ", "_").replace("/", "_") + ".json"
        file_path = os.path.join(year_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"  >> Jogos da semana '{week}' salvos em: {file_path}")
