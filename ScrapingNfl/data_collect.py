import subprocess

def run_spider(spider_name, description):
    print(f"\n{'='*40}")
    print(f"{description}")
    print(f"{'='*40}\n")
    
    result = subprocess.run(["scrapy", "crawl", spider_name], capture_output=True, text=True)
    
    print(result.stdout)  # Exibe a saída do Scrapy
    if result.stderr:
        print(f"Erro ao executar {spider_name}:")
        print(result.stderr)

if __name__ == "__main__":
    run_spider("games_data", "🔹 Coletando dados dos jogos...")
    run_spider("players_data", "🔹 Coletando dados dos jogadores...")
    run_spider("teams_data", "🔹 Coletando dados dos times...")

    print("\n✅ Coleta de dados concluída!")
