import subprocess
import sys
import requests

def check_access(url):
    """Verifica se a URL está acessível antes de rodar o spider."""
    try:
        response = requests.get(url, timeout=5)  # Timeout de 5 segundos
        if response.status_code == 403:
            print(f"\n❌ Acesso bloqueado (403) para {url}. Cancelando execução...\n")
            sys.exit(1)  # Encerra o script com código de erro
        elif response.status_code >= 400:
            print(f"\n⚠️ Aviso: Código {response.status_code} para {url}, mas continuando...\n")
    except requests.RequestException as e:
        print(f"\n⚠️ Erro ao verificar {url}: {e}. Continuando...\n")

def run_spider(spider_name, description, test_url):
    """Executa o spider após verificar se a URL está acessível."""
    # check_access(test_url)  # Testa a URL antes de rodar o spider
    
    print(f"\n{'='*40}")
    print(f"{description}")
    print(f"{'='*40}\n")
    
    result = subprocess.run(["scrapy", "crawl", spider_name], capture_output=True, text=True)
    
    print(result.stdout)  # Exibe a saída do Scrapy
    
    if result.stderr:
        print(f"Erro ao executar {spider_name}:")
        print(result.stderr)

if __name__ == "__main__":
    # URLs de teste correspondentes aos spiders
    test_urls = {
        "games_data": "https://www.footballdb.com/games/index.html",
        "players_data": "https://www.footballdb.com/statistics/nfl/player-stats/passing",
        "teams_data": "https://www.footballdb.com/statistics/nfl/team-stats/offense-totals"
    }

    run_spider("games_data", "🔹 Coletando dados dos jogos...", test_urls["games_data"])
    run_spider("players_data", "🔹 Coletando dados dos jogadores...", test_urls["players_data"])
    run_spider("teams_data", "🔹 Coletando dados dos times...", test_urls["teams_data"])

    print("\n✅ Coleta de dados concluída!")
