from flask import Flask, render_template, request, jsonify  

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return jsonify({"message": "Funcionando"})
    return render_template("index.html")

# Adicionando um log simples
if __name__ == "__main__":
    print("Iniciando aplicação Flask...")
    app.run()
