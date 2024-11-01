import os
from flask import Flask, render_template, request, jsonify  
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
from flask_cors import CORS
import chromedriver_binary 

app = Flask(__name__)
CORS(app)

def fetch_info_projetos(link):
    driver = None
    try:
        print("Iniciando o Selenium...")
        
        base_url = "https://editor.p5js.org/"
        nome_usuario = link.split("/")[3]
        user_sketches_url = f"{base_url}{nome_usuario}/sketches"

        # Configuração do Chrome
        options = Options()
        options.binary_location = os.getenv('GOOGLE_CHROME_SHIM', "/app/.apt/usr/bin/google-chrome")
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920x1080')

        # Inicializa o ChromeDriver
        driver = webdriver.Chrome(options=options)
        driver.get(user_sketches_url)
        time.sleep(3)

        tabela = driver.find_element(By.CLASS_NAME, 'sketches-table')
        linha_projeto = None

        for linha in tabela.find_elements(By.CLASS_NAME, 'sketches-table__row'):
            link_projeto = linha.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if link_projeto == link:
                linha_projeto = linha
                break

        if linha_projeto:
            nome_projeto = linha_projeto.find_element(By.TAG_NAME, 'a').text
            data_criacao_texto = linha_projeto.find_elements(By.TAG_NAME, 'td')[0].text
            data_modificacao_texto = linha_projeto.find_elements(By.TAG_NAME, 'td')[1].text

            data_criacao = datetime.strptime(data_criacao_texto, "%b %d, %Y, %I:%M:%S %p") - timedelta(hours=3)
            data_modificacao = datetime.strptime(data_modificacao_texto, "%b %d, %Y, %I:%M:%S %p") - timedelta(hours=3)

            info_projetos = {
                'nome': nome_projeto,
                'link': link_projeto,
                'data_criacao': data_criacao.strftime("%b %d, %Y, %I:%M:%S %p"),
                'data_modificacao': data_modificacao.strftime("%b %d, %Y, %I:%M:%S %p"),
            }
            print("Informações do projeto capturadas com sucesso.")
            return info_projetos
        else:
            print("Projeto não encontrado.")
            return {"error": "Projeto não encontrado."}

    except Exception as e:
        print(f"Erro ao utilizar o Selenium: {e}")
        return {"error": str(e)}

    finally:
        if driver:
            driver.quit()
            print("Driver finalizado.")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()  # Captura os dados JSON enviados
        link = data.get("link", "")
        if link:
            info_projetos = fetch_info_projetos(link)
            return jsonify(info_projetos)
        else:
            return jsonify({"error": "Link inválido"}), 400
    return render_template("index.html")

if __name__ == "__main__":
    print("Iniciando aplicação Flask...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
