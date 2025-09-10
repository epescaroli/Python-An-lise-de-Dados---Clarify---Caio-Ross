from flask import Flask, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px

app = Flask(__name__)

DB_PATH = r"C:\Users\noturno\Desktop\Python 2 Evandro\filmes.db"

def get_df():
    """Lê a tabela de filmes do banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM filmes", conn)
    except Exception as e:
        df = pd.DataFrame()  # retorna DataFrame vazio em caso de erro
    finally:
        conn.close()
    return df

@app.route("/")
def index():
    df = get_df()
    if df.empty:
        return "Erro: não foi possível carregar os filmes."

    if 'Direcao' not in df.columns:
        return "Erro: coluna 'Direcao' não encontrada no banco de dados."

    # Contagem de filmes por Direcao
    contagem = df.groupby('Direcao').size().reset_index(name='Qtd')
    contagem = contagem.sort_values(by='Qtd', ascending=True)  # ordenar crescente para barras horizontais

    # Gráfico de barras horizontal
    fig = px.bar(
        contagem,
        x='Direcao',
        y='Qtd',
        text='Qtd',
        color='Qtd',
        template = "plotly_dark",
        title='Quantidade de filmes por Direcao',
        labels={'Direcao': 'Direcao', 'Qtd': 'Quantidade de filmes'},
        width=900,
        height=600
    )

    # Mostrar valores fora das barras
    fig.update_traces(textposition='outside', hovertemplate='%{y}: %{x}<extra></extra>')

    # Layout fixo para evitar que hover altere o tamanho das barras
    fig.update_layout(
        yaxis=dict(autorange="reversed"),  # maior no topo
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        title_x = 0.5,
        height = 520,
        bargap = 0.3,
        margin = dict(l=30, r=30, t=60, b=120),
        paper_bgcolor = "#111",
        plot_bgcolor = "#111",
        xaxis_tickangle = -45
    )

    grafico_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    html = """
        <stile>
            body{margin:0 background: #111; color: #eee;}
            #bloquinho{max-width:1200px; margin:0 auto}
            .blocao{margin:0;}
        </stile>
        <div id='bloquinho'>
            <div class='blocao'>
                {{grafico|safe}}
            </div>
        </div>
"""

    return render_template_string(f"""
        <h1>Gráfico de Filmes por Direcao</h1>
        {grafico_html}
    """)

if __name__ == "__main__":
    app.run(debug=True)
