from flask import Flask, render_template_string
import pandas as pd
import sqlite3
import random
import plotly.express as px

app = Flask(__name__)

# Caminho do banco de dados
caminhoBanco = r"C:\Users\noturno\Desktop\Python 2 Evandro\filmes.db"

# Página inicial com visual moderno e cards animados
@app.route("/")
def home():
    return render_template_string("""
        <html>
        <head>
            <title>Catálogo de Filmes</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
            <style>
                body {
                    background: linear-gradient(135deg, #f0f2f5 0%, #ffffff 100%);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                h1 {
                    font-weight: bold;
                    color: #333;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                    margin-top: 4rem;
                    margin-bottom: 4rem;
                }
                .card-container {
                    display: flex;
                    justify-content: center;
                    gap: 2rem;
                    flex-wrap: wrap;
                }
                .card {
                    background: #ffffff;
                    border-radius: 20px;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.08);
                    width: 260px;
                    padding: 2rem 1rem;
                    text-align: center;
                    opacity: 0;
                    transform: translateY(30px);
                    animation: fadeSlide 0.8s forwards;
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                .card:nth-child(1) { animation-delay: 0.2s; }
                .card:nth-child(2) { animation-delay: 0.4s; }
                .card:hover { transform: translateY(-8px) scale(1.03); box-shadow: 0 15px 30px rgba(0,0,0,0.15); }
                @keyframes fadeSlide { to { opacity: 1; transform: translateY(0); } }
                .card h2 { font-size: 1.4rem; margin-bottom: 1rem; color: #555; }
                .card p { font-size: 0.95rem; color: #777; margin-bottom: 1.5rem; }
                .btn-card {
                    border-radius: 50px;
                    font-weight: 600;
                    padding: 0.6rem 1.5rem;
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                .btn-card:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <h1>🎬 Bem-vindo ao Catálogo de Filmes</h1>
            <div class="card-container">
                <div class="card">
                    <h2>📊 Gráfico</h2>
                    <p>Visualize as notas dos filmes de forma interativa e moderna.</p>
                    <a href="/grafico" class="btn btn-primary btn-card">Ver Gráfico</a>
                </div>
                <div class="card">
                    <h2>📜 Lista de Filmes</h2>
                    <p>Confira todos os filmes cadastrados no banco de dados.</p>
                    <a href="/filmes" class="btn btn-success btn-card">Lista de Filmes</a>
                </div>
            </div>
        </body>
        </html>
    """)

# Rota para a lista de filmes
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
        </head>
        <body class="container mt-4">
            <h1 class="mb-3">📜 Lista de Filmes</h1>
            <a href="/" class="btn btn-secondary mb-3">Voltar</a>
            {{ tabela|safe }}
        </body>
        </html>
    """, tabela=tabela_html)

# Rota para o gráfico - Scatter com cores vivas e botão voltar
@app.route("/grafico")
def grafico():
    conexao = sqlite3.connect(caminhoBanco)
    df = pd.read_sql("SELECT Titulo, Nota FROM filmes", conexao)
    conexao.close()

    # cores vivas
    cores = [f"rgba({random.randint(100,255)},{random.randint(100,255)},{random.randint(100,255)},0.8)" for _ in range(len(df))]

    # Gráfico scatter usando índice do DataFrame diretamente
    fig = px.scatter(
        df,
        x=df.index,
        y='Nota',
        hover_name='Titulo',
        title='📊 Notas dos Filmes',
        color=df['Titulo'],  # cores diferentes para cada ponto
        color_discrete_sequence=cores
    )

    # Renderiza o gráfico como HTML e adiciona botão de voltar
    grafico_html = fig.to_html(full_html=False)
    return render_template_string("""
        <html>
        <head>
            <title>Gráfico de Filmes</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        </head>
        <body class="container mt-4">
            <h1 class="mb-3">📊 Gráfico de Notas dos Filmes</h1>
            <a href="/" class="btn btn-secondary mb-3">Voltar</a>
            {{ grafico|safe }}
        </body>
        </html>
    """, grafico=grafico_html)

if __name__ == "__main__":
    app.run(debug=True)
