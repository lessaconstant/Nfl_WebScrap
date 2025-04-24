import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "player_per_temp"
    allowed_domains = ["footballdb.com"]
    
    player = "Andy Dalton"  # Nome completo do jogador a ser buscado
    team   = "CIN"          # Sigla do time para filtrar os jogos
    year   = "2011"         # Ano da temporada

    def start_requests(self):
        """
        --- Início do processo de scraping ---
        Monta a URL da página de scores do ano desejado e dispara a requisição.
        """
        print("Iniciando start_requests...")
        url = f"https://www.footballdb.com/games/index.html?yr={self.year}"
        print("URL:", url)

        # Dispara a requisição, levando o 'year' no meta para uso futuro
        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={'year': self.year}
        )

    def parse(self, response):
        """
        --- Parse da lista de jogos ---
        1. Seleciona todas as tabelas na página de scores.
        2. Para cada linha, verifica se a sigla do time aparece.
        3. Extrai e acumula os links individuais de cada jogo.
        """
        tables = response.css("table")
        links = []
        
        for table in tables:
            for row in table.css("tr"):
                # Se a linha contiver a sigla do time, obtemos o link para o boxscore
                if self.team in row.css("td ::text").getall():
                    link = row.css("a::attr(href)").get()
                    if link:
                        full_link = response.urljoin(link)
                        links.append(full_link)
        
        # Dispara parse_details para cada jogo filtrado
        for link in links:
            yield scrapy.Request(
                link,
                callback=self.parse_details,
                meta=response.meta  # repassa o 'year' adiante
            )

    def parse_details(self, response):
        
        #--- Parse dos detalhes de cada jogo ---
        
        # --- Extrai a semana do breadcrumb (terceiro link) ---
        week_sel = response.xpath('/html/body/div[1]/div[1]/div[1]/div[1]/a[3]')
        week_text = (week_sel.xpath('normalize-space(text())').get() or "N/A").strip()
        print("#" * 40)
        print(f"Week: {week_text}")

        # --- Localiza o container que agrupa todas as estatísticas móveis ---
        container = response.xpath('//div[@id="mobToggle_stats" and contains(@class, "mobilehide")]')
        if not container:
            print("Container mobilehide não encontrado.")
            return

        # --- Cada <h2> indica o início de uma nova categoria de estatísticas ---
        sections = container.xpath('.//h2')
        for section in sections:
            # --- Extrai o título da categoria (e.g., Passing, Rushing, Fumbles) ---
            title = section.xpath('normalize-space(text())').get()
            if not title:
                continue
            category = title.strip().lower()
            print(f"\nCategoria: {category}")

            sibling_nodes = section.xpath('following-sibling::*')
            tables = []
            for node in sibling_nodes:
                if node.root.tag.lower() == "h2":
                    break
                if node.root.tag.lower() == "table":
                    tables.append(node)
                else:
                    tables.extend(node.xpath('.//table'))

            # --- Em cada tabela, busca a(s) linha(s) que contenham o nome do jogador ---
            for table in tables:
                rows = table.xpath(f'.//tr[contains(., "{self.player}")]')
                for row in rows:
                    # --- Extrai todos os textos e limpa espaços vazios ---
                    raw = row.xpath('.//text()').getall()
                    data = [t.strip() for t in raw if t.strip()]
                    print("  Linha extraída:", data)

                    # --- Converte a lista 'data' em dicionário conforme a categoria ---
                    data_dict = None
                    if "passing" in category:
                        # Colunas esperadas para passing
                        cols = ["player","att","cmp","yds","ypa","td","int","lg","sack","loss","rate"]
                        if len(data) == len(cols) + 1:  # +1 pois inclui nome completo e sigla
                            vals = [data[0]] + data[2:]
                            data_dict = dict(zip(cols, vals))
                        else:
                            print("  Formato inesperado para passing:", data)

                    elif "rushing" in category:
                        # Colunas para rushing
                        cols = ["player","att","yds","avg","lg","td","fd"]
                        if len(data) == len(cols) + 1:
                            vals = [data[0]] + data[2:]
                            data_dict = dict(zip(cols, vals))
                        else:
                            print("  Formato inesperado para rushing:", data)

                    elif "fumble" in category:
                        # Colunas para fumbles
                        cols = ["player","fum","lost","ff","own","opp","rec","yds","td"]
                        if len(data) >= len(cols) + 1:
                            vals = [data[0]] + data[2:2+len(cols)]
                            data_dict = dict(zip(cols, vals))
                        else:
                            print("  Formato inesperado para fumbles:", data)

                    else:
                        print("  Categoria não tratada:", category)

                    # --- Se montou o dicionário, adiciona metadados e salva ---
                    if data_dict:
                        data_dict.update({
                            "week": week_text,
                            "category": category
                        })
                        print("  Dados convertidos:", data_dict)
                        self.save_data(
                            data_dict,
                            self.player,
                            self.year,
                            week_text,
                            category
                        )

        print("#" * 40 + "\n")

    def save_data(self, data, player, year, week, category):
        """
        --- Salva o dicionário 'data' em disco no formato JSON ---
        Estrutura de diretórios: 
        ../data/Player_Per_Temp/<player>/<year>/<week>/<category>.json
        """
        base_dir = os.path.join(
            os.getcwd(), "..", "data",
            "Player_Per_Temp", player, year, week
        )
        os.makedirs(base_dir, exist_ok=True)

        file_path = os.path.join(base_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"  >> Dados salvos em: {file_path}")
