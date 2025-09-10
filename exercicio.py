from flask import Flask, render_template_string, request
import pandas as pd
import sqlite3
import random
import plotly.express as px

app = Flask(__name__)

# Caminho do banco de dados
caminhoBanco = r"C:\Users\noturno\Desktop\Python 2 Evandro\filmes.db"

# Página inicial
@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>Catálogo de Filmes</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <style>
            body {
                background: linear-gradient(160deg, #f0f2f5 0%, #ffffff 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                color: #333;
            }
            h1 {
                font-weight: 700;
                color: #1f2937;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                margin: 3rem 0 2rem 0;
            }
            .card-container {
                display: flex;
                justify-content: center;
                gap: 2rem;
                flex-wrap: wrap;
            }
            .card {
                background: #ffffff;
                border-radius: 1rem;
                box-shadow: 0 12px 24px rgba(0,0,0,0.08);
                width: 280px;
                padding: 2rem 1.5rem;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .card:hover {
                transform: translateY(-10px) scale(1.05);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            .card h2 {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: #111827;
            }
            .card p {
                font-size: 1rem;
                color: #4b5563;
                margin-bottom: 1.5rem;
            }
            .btn-card {
                border-radius: 50px;
                font-weight: 600;
                padding: 0.7rem 1.8rem;
                background: linear-gradient(90deg, #6366f1, #818cf8);
                color: white;
                border: none;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .btn-card:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 20px rgba(99,102,241,0.4);
            }
        </style>
    </head>
    <body>
        <h1>🎬 Bem-vindo ao Catálogo de Filmes</h1>
        <div class="card-container">
            <div class="card">
                <h2>📊 Gráfico Interativo</h2>
                <p>Visualize as notas dos filmes de forma moderna e animada.</p>
                <a href="/grafico" class="btn btn-card">Ver Gráfico</a>
            </div>
            <div class="card">
                <h2>📜 Lista de Filmes</h2>
                <p>Confira todos os filmes cadastrados no banco de dados.</p>
                <a href="/filmes" class="btn btn-card">Lista de Filmes</a>
            </div>
        </div>
    </body>
    </html>
    """)

# Lista de filmes
@app.route("/filmes")
def listar_filmes():
    conexao = sqlite3.connect(caminhoBanco)
    df = pd.read_sql("SELECT * FROM filmes", conexao)
    conexao.close()

    tabela_html = df.to_html(classes="table table-striped", index=False) if not df.empty else "<p>Nenhum filme encontrado.</p>"

    return render_template_string("""
    <html>
    <head>
        <title>Lista de Filmes</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <style>
            body { background: #f9fafb; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color:#333; }
            h1 { text-align:center; margin:2rem 0; font-weight:700; }
        </style>
    </head>
    <body class="container mt-4">
        <h1>📜 Lista de Filmes</h1>
        <a href="/" class="btn btn-secondary mb-3">Voltar</a>
        {{ tabela|safe }}
    </body>
    </html>
    """, tabela=tabela_html)

# Gráfico com filtro e animação
@app.route("/grafico")
def grafico():
    nota_selecionada = request.args.get("nota")

    conexao = sqlite3.connect(caminhoBanco)
    df = pd.read_sql("SELECT Titulo, Nota FROM filmes", conexao)
    conexao.close()

    if nota_selecionada:
        try:
            nota_valor = float(nota_selecionada)
            df = df[df['Nota'] == nota_valor]
        except:
            pass

    if df.empty:
        return """<h3>Nenhum filme encontrado para esta nota.</h3><br><a href='/'>Voltar</a>"""

    cores = [f"rgba({random.randint(100,255)},{random.randint(100,255)},{random.randint(100,255)},0.8)" for _ in range(len(df))]

    fig = px.scatter(
        df,
        x=df['Titulo'],
        y='Nota',
        hover_name='Titulo',
        title='📊 Notas dos Filmes',
        color=df['Titulo'],
        color_discrete_sequence=cores
    )

    fig.update_layout(
        transition=dict(duration=700, easing='cubic-in-out'),
        xaxis_title="Filmes",
        yaxis_title="Nota",
        xaxis_tickangle=-45
    )

    grafico_html = fig.to_html(full_html=False)

    # Notas disponíveis para filtro
    conexao = sqlite3.connect(caminhoBanco)
    df_total = pd.read_sql("SELECT DISTINCT Nota FROM filmes", conexao)
    conexao.close()
    notas_disponiveis = sorted(df_total['Nota'].tolist())

    return render_template_string("""
    <html>
    <head>
        <title>Gráfico de Filmes</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <style>
            body { background: linear-gradient(160deg, #f0f2f5 0%, #ffffff 100%); font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color:#333; min-height:100vh; }
            h1 { font-weight:700; text-align:center; margin:2rem 0; color:#1f2937; text-shadow:1px 1px 3px rgba(0,0,0,0.1);}
            .form-select, .btn { border-radius:0.5rem; transition: all 0.3s ease;}
            .form-select:focus, .btn:focus { outline:none; box-shadow:0 0 0 3px rgba(99,102,241,0.3);}
            a.btn-secondary { background:#e5e7eb; color:#111827; border:none; transition: all 0.3s ease;}
            a.btn-secondary:hover { background:#d1d5db; color:#1f2937;}
        </style>
    </head>
    <body class="container mt-4">
        <h1>📊 Gráfico de Notas dos Filmes</h1>

        <form method="get" class="mb-3">
            <label for="nota">Filtrar por Nota:</label>
            <select name="nota" id="nota" class="form-select w-auto d-inline-block">
                <option value="">Todas</option>
                {% for n in notas %}
                    <option value="{{ n }}" {% if request.args.get('nota') == n|string %}selected{% endif %}>{{ n }}</option>
                {% endfor %}
            </select>
            <button type="submit" class="btn btn-primary">Filtrar</button>
            <a href="/grafico" class="btn btn-secondary">Resetar</a>
        </form>

        <div id="grafico" style="opacity:0; transition: opacity 1s ease;">
            {{ grafico|safe }}
        </div>
        <script>
            window.onload = function() {
                document.getElementById('grafico').style.opacity = 1;
            }
        </script>

        <br>
        <a href="/" class="btn btn-secondary mt-3">Voltar</a>
    </body>
    </html>
    """, grafico=grafico_html, notas=notas_disponiveis)

if __name__ == "__main__":
    app.run(debug=True)
