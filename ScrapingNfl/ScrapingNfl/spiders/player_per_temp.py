import scrapy
import os
import json

class NflSpider(scrapy.Spider):
    name = "player_per_temp"
    allowed_domains = ["footballdb.com"]
    player = "Mac Jones" 
    team = "NE"  # O time precisa ser em sigla
    year = "2021"

    def start_requests(self):
        print("Iniciando start_requests...")
        url = f"https://www.footballdb.com/games/index.html?yr={self.year}"
        print("URL:", url)
        yield scrapy.Request(url, callback=self.parse, meta={'year': str(self.year)})

    def parse(self, response):
        tables = response.css("table")  
        links = []
        for table in tables:
            rows = table.css("tr")
            for row in rows:
                if self.team in row.css("td ::text").getall():
                    link = row.css("a::attr(href)").get()
                    if link:
                        full_link = f"https://www.footballdb.com{link}"
                        links.append(full_link)
        for link in links:
            yield response.follow(link, callback=self.parse_details, meta=response.meta)

    def parse_details(self, response):
        # Extrai a semana
        week_selector = response.xpath('/html/body/div[1]/div[1]/div[1]/div[1]/a[3]')
        week_text = week_selector.css("::text").get() or "N/A"
        week_text = week_text.strip()
        
        print("#" * 20)
        print("Week:", week_text)
        
        # Seleciona o container principal de estatísticas
        container = response.xpath('//div[@id="mobToggle_stats" and contains(@class, "mobilehide")]')
        if not container:
            print("Container mobilehide não encontrado.")
            return

        # Seleciona todas as seções (cada seção inicia com um <h2>)
        sections = container.xpath('.//h2')
        
        for section in sections:
            # Extrai o título da categoria
            cat_title = section.xpath('normalize-space(text())').get()
            if not cat_title:
                continue
            category = cat_title.strip().lower()  # Ex.: "passing", "rushing", "fumbles"
            print("Categoria:", category)
            
            # Seleciona os elementos irmãos que pertencem a esta seção até o próximo <h2>
            sibling_nodes = section.xpath('following-sibling::*')
            tables = []
            for node in sibling_nodes:
                if node.root.tag.lower() == "h2":
                    break  # Chegamos à próxima seção
                # Se o nó é uma tabela ou contém tabelas, adiciona à lista
                if node.root.tag.lower() == "table":
                    tables.append(node)
                else:
                    node_tables = node.xpath('.//table')
                    if node_tables:
                        tables.extend(node_tables)
            
            # Para cada tabela, busca as linhas que contenham o nome do jogador
            for table in tables:
                rows = table.xpath(f'.//tr[contains(., "{self.player}")]')
                for row in rows:
                    raw_data = row.xpath('.//text()').getall()
                    data = [text.strip() for text in raw_data if text.strip()]
                    print("Linha extraída:", data)
                    
                    # Agora convertemos a lista em um dicionário com base na categoria
                    data_dict = None
                    if "passing" in category:
                        passing_columns = ["player", "att", "cmp", "yds", "ypa", "td", "int", "lg", "sack", "loss", "rate"]
                        if len(data) == 12:
                            values = [data[0]] + data[2:12]
                            data_dict = dict(zip(passing_columns, values))
                        else:
                            print("Formato inesperado para passing:", data)
                    elif "rushing" in category:
                        rushing_columns = ["player", "att", "yds", "avg", "lg", "td", "fd"]
                        if len(data) == 8:
                            values = [data[0]] + data[2:8]
                            data_dict = dict(zip(rushing_columns, values))
                        else:
                            print("Formato inesperado para rushing:", data)
                    elif "fumble" in category:
                        fumbles_columns = ["player", "fum", "lost", "ff", "own", "opp", "rec", "yds", "td"]
                        if len(data) >= 10:
                            values = [data[0]] + data[2:11]
                            data_dict = dict(zip(fumbles_columns, values))
                        else:
                            print("Formato inesperado para fumbles:", data)
                    else:
                        print("Categoria não tratada:", category)
                    
                    if data_dict:
                        data_dict["week"] = week_text
                        data_dict["category"] = category
                        print(f"Dados convertidos em dicionário para {category}:", data_dict)
                        self.save_data(data_dict, self.player, self.year, week_text, category)
        print("#" * 20, "\n")

    def save_data(self, data, player, year, week, category):
        # Define o caminho: data/Player_Per_Temp/<player>/<year>/<week>/<category>.json
        base_dir = os.path.join(os.getcwd(), "..", "data", "Player_Per_Temp", player, year, week)
        os.makedirs(base_dir, exist_ok=True)
        
        file_path = os.path.join(base_dir, f"{category}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos em {file_path}")
