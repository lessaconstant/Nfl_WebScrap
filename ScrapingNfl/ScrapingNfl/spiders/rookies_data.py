import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "rookies_data"
    allowed_domains = ["footballdb.com"]  

    # --- Configuração de parâmetros: quais rounds, anos e posições capturar ---
    rounds     = list(range(1, 8))                # Rounds de draft de 1 a 7
    years      = list(range(2024, 2006, -1))      # Anos de 2024 a 2007
    categories = ["QB"]                           # Apenas posições de QB

    def start_requests(self):
        """
        --- Início do scraping de rookies ---
        Constrói a URL de cada ano e round de draft, dispara requisição.
        """
        print("Iniciando start_requests...")
        for rnd in self.rounds:
            for yr in self.years:
                url = f"https://www.footballdb.com/draft/draft.html?lg=NFL&yr={yr}&rnd={rnd}"
                print(f"URL: {url}")
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={'year': yr, 'round': rnd}
                )

    def parse(self, response):
        """
        --- Parse da página de draft ---
        1. Recupera year e round de response.meta.
        2. Seleciona todas as linhas úteis (excluindo cabeçalho).
        3. Coleta pick, team, player, pos e college.
        4. Filtra apenas QBs (self.categories) e armazena em lista.
        5. Se houver dados, chama save_data para persistir.
        """
        year  = response.meta['year']
        rnd   = response.meta['round']
        rows  = response.css('tr:not(.header)')
        data  = []

        for row in rows:
            pick    = row.css('td.d-none ::text').get()
            team    = row.css('td a span.d-inline ::text').get()
            player  = row.css('td.nowrap a ::text').get()
            pos     = row.css('td:nth-child(5) ::text').get()
            college = row.css('td:nth-child(6) a::text').get()

            # --- Mantém apenas jogadores na categoria QB ---
            if pos in self.categories:
                rookie_data = {
                    'pick':    pick,
                    'team':    team,
                    'player':  player,
                    'pos':     pos,
                    'college': college,
                    'round':   rnd,
                    'year':    year
                }
                data.append(rookie_data)

        # --- Salva no disco apenas se houver ao menos um QB no round ---
        if data:
            self.save_data(data, year, rnd)

    def save_data(self, data, year, rnd):
        """
        --- Persiste os dados coletados ---
        Estrutura de diretório: ../data/Rookies/<year>/round_<rnd>.json
        """
        base_dir = os.path.join(os.getcwd(), "..", "data", "Rookies")
        year_dir = os.path.join(base_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)

        file_path = os.path.join(year_dir, f"round_{rnd}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos em {file_path}")
