import subprocess
import sys
import requests

def check_access(url):
    """
    --- Verifica se a URL está acessível antes de rodar o spider ---
    1. Tenta um GET com timeout de 5s.
    2. Se retornar 403, encerra o script (acesso bloqueado).
    3. Para outros códigos >=400, apenas avisa e continua.
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 403:
            print(f"\n❌ Acesso bloqueado (403) para {url}. Cancelando execução...\n")
            sys.exit(1)
        elif response.status_code >= 400:
            print(f"\n⚠️ Aviso: Código {response.status_code} para {url}, mas continuando...\n")
    except requests.RequestException as e:
        print(f"\n⚠️ Erro ao verificar {url}: {e}. Continuando...\n")

def run_spider(spider_name, description, test_url):
    """
    --- Executa uma spider Scrapy após checar acesso opcionalmente ---
    1. check_access(test_url)
    2. Exibe cabeçalho gráfico com a descrição.
    3. Chama 'scrapy crawl <spider_name>' via subprocess.
    4. Imprime stdout e stderr para debug.
    """
    check_access(test_url)
    
    print(f"\n{'='*40}")
    print(description)
    print(f"{'='*40}\n")
    
    result = subprocess.run(
        ["scrapy", "crawl", spider_name],
        capture_output=True,
        text=True
    )
    
    # --- Saída padrão da execução Scrapy ---
    print(result.stdout)
    
    # --- Se houver erros, exibe stderr ---
    if result.stderr:
        print(f"Erro ao executar {spider_name}:")
        print(result.stderr)

if __name__ == "__main__":
    # --- Mapeamento de spiders para URLs de teste ---
    test_urls = {
        "scores_data":  "https://www.footballdb.com/games/index.html",
        "players_data": "https://www.footballdb.com/statistics/nfl/player-stats/passing",
        "teams_data":   "https://www.footballdb.com/statistics/nfl/team-stats/offense-totals",
        "rookies_data": "https://www.footballdb.com/draft/draft.html?lg=NFL&yr=2024&rnd=1"
    }

    # --- Executa cada spider em sequência ---
    run_spider("scores_data",  "🔹 Coletando dados dos jogos...",   test_urls["scores_data"])
    run_spider("players_data", "🔹 Coletando dados dos jogadores...", test_urls["players_data"])
    run_spider("teams_data",   "🔹 Coletando dados dos times...",    test_urls["teams_data"])
    run_spider("rookies_data","🔹 Coletando dados dos calouros...", test_urls["rookies_data"])

    print("\n✅ Coleta de dados concluída!")
