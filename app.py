import os
from flask import Flask, render_template, request, jsonify  
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def fetch_info_projetos(link):
    driver = None
    try:
        base_url = "https://editor.p5js.org/"
        nome_usuario = link.split("/")[3]
        user_sketches_url = f"{base_url}{nome_usuario}/sketches"

        options = Options()
        options.binary_location = "/app/.apt/usr/bin/google-chrome" 
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')  # Necessário em alguns ambientes
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--user-data-dir=/tmp/user-data')
        options.add_argument('--data-path=/tmp/data-path')
        options.add_argument('--homedir=/tmp')
        options.add_argument('--disk-cache-dir=/tmp/cache-dir')
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
            return info_projetos
        else:
            return {"error": "Projeto não encontrado."}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if driver:
            driver.quit()

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
