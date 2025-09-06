from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random
import config_PythonsDeElite as config
import consultas

caminhoBanco = config.DB_PATH
pio.renderers.default = "browser"
nomeBanco = config.NOMEBANCO
rotas = config.ROTAS
tabelaA = config.TABELA_A
tabelaB = config.TABELA_B

#arquivos a serem carregados
dfDrinks = pd.read_csv(f'{caminhoBanco}{tabelaA}')
dfavengers = pd.read_csv(f'{caminhoBanco}{tabelaB}', encoding='latin1')
# outros exemplos de encodings: utf-8, cp1256, iso8859-1

# criamos o banco d edados em SQL caso nao exista
conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')

dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)
dfavengers.to_sql("vingadores", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

html_template = f'''
<h1>Dashboards</h1>
<h2>Parte 01</h2>
<ul>
<li> <a href="{rotas[1]}">Top 10 Paises em consumo<a/a> </li>
<li> <a href="{rotas[2]}">Media de consumo por tipo <a/a> </li>
<li> <a href="{rotas[3]}">Consumo por regiao<a/a> </li>
<li> <a href="{rotas[4]}">Comparativo entre Tipos<a/a> </li>
<li> 
</ul>
<h1> </h1>
<h2>Parte 02</h2>
<ul>
<li> <a href="{rotas[5]}">Comparar<a/a> </li>
<li> <a href="{rotas[6]}">Upload<a/a> </li>
<li> <a href="{rotas[7]}">Apagar tabela<a/a> </li>
<li> <a href="{rotas[8]}">Ver tabela<a/a> </li>
<li> <a href="{rotas[9]}">V.A.A<a/a> </li>
</ul>
'''

#iniciar o flask
app = Flask(__name__)

def getDbConnect():
    conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}') 
    conn.row_factory = sqlite3.Row
    return conn

@app.route(rotas[0])
def index():
   return render_template_string(html_template)

@app.route(rotas[1])
def grafico1():
   with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta01, conn)
   figuraGrafico1 = px.bar(
       df, 
       x = 'country',
       y = 'total_litres_of_pure_alcohol',
       title = 'Top 10 paises em consumo de alcool!'
   )
   return figuraGrafico1.to_html()

@app.route(rotas[2])
def grafico2():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
      df = pd.read_sql_query(consultas.consultas02, conn)   

      # transforma as colunas cerveja destilados e vinhos s linhas criando no fim duas colunas, uma chamada bebidas com os nome originais das colunas e outra com a media de porçoes com seus valores correspondentes
      df_melted = df.melt(var_name='Bebidas', 
      value_name='Média de porções')
      figuraGrafico2 = px.bar(
         df_melted,
         x = 'Bebidas',
         y = 'Média de porções',
         title = 'Média de consumo Global por litro'
   )
      return figuraGrafico2.to_html()

@app.route(rotas[3])
def graficos3():
   regioes = {
        "Europa":['France','Germany','Spain','Italy', 'Portugal'],
        "Asia":['China','Japan', 'India', 'Thailand'],
        "Africa":['Angola','Nigeria', 'Egypt', 'Algeria'],
        "Americas":['USA','Brasil', 'Canada', 'Argentina', 'Mexico']
    }
   dados = []
   with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        # itera sobre dicionario de regioes onde cada chave (regiao tem uma lista de paises)
      for regiao, paises in regioes.items():
         # criando a lista de placeholders para os paises dessa região 
         # isso vai ser usadi na consulta sql para filtrar o pais da regiao
            placeholders = ",".join([f"'{p}'" for p in paises])
            query = f"""
               SELECT SUM(total_litres_of_pure_alcohol) AS total
               FROM bebidas
               WHERE country IN ({placeholders})
            """
            # iloc trata os nossos dados
            total = pd.read_sql_query(query, conn).iloc[0,0]
            dados.append(
                {
                    "Região": regiao,
                    "Consumo Total": total
                }
            )
   dfRegioes = pd.DataFrame(dados)
   figuraGrafico3 = px.pie(
         dfRegioes,
         names = "Região",
         values = "Consumo Total",
         title = "Consumo Total por Região"
      )
   return figuraGrafico3.to_html() + f"<br><a href='{rotas[0]}'>voltar</a>"


@app.route(rotas[4])
def grafico4():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta03, conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo', 'Média']
        figuraGrafico4 = px.pie(
            medias,
            names = "Tipo",
            values = "Média",
            title = "Proporção média entre os tipos de bebidas!"
        )
        return figuraGrafico4.to_html() + f"<br><a href='{rotas[0]}'>Voltar</a>"

@app.route(rotas[5], methods=["POST", "GET"])
def comparar():
   opcoes = [
      'beer_servings',
      'spirit_servings',
      'wine_servings'
   ]
   if request.method == "POST":
       eixoX = request.form.get('eixo_x')
       eixoY = request.form.get('eixo_y')
       if eixoX == eixoY:
           return f"<h3> Selecione campos diferentes! </h3><br><a href='{rotas[5]}'>Voltar</a>"
       conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
       df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixoX, eixoY), conn)
       conn.close()
       figuraComparar = px.scatter(
           df,
           x = eixoX,
           y = eixoY,
           title = f"Comparação entre {eixoX} VS {eixoY}"
       )
       figuraComparar.update_traces(textposition = 'top center')
       return figuraComparar.to_html() + f"<br><a href='{rotas[5]}'>Voltar</a>"
         


   return render_template_string('''
      <h2> Comparar campos </h2>
      <form method="POST">
            <label> Eixo X: </label>
            <select name="eixo_x">
                     {% for opcao in opcoes %}
                           <option value='{{opcao}}'>{{opcao}}</option>
                     {% endfor %}
            </select>
            <br><br>
                                 
            <label> Eixo Y: </label>
            <select name="eixo_y">
                     {% for opcao in opcoes %}
                           <option value='{{opcao}}'>{{opcao}}</option>
                     {% endfor %}
            </select>
            <br><br>
                                 
            <input type="submit" value="-- Comparar --">
         </form>
         <br><a href="{{rotaInterna}}">Voltar</a>
''', opcoes = opcoes, rotaInterna = rotas[0])

@app.route(rotas[6], methods=['GET', "POST"])
def upload():
    if request.method == "POST":
        recebido = request.files['c_arquivo']
        if not recebido:
            return f"<h3> Nenhum arquivo enviado </h3><br><a href='{rotas[6]}'>Voltar</a>"
        conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
        dfavengers.to_sql("vingadores", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        return f"<h3> Upload Feito com Sucesso! </h3><br><a href='{rotas[6]}'>Voltar</a>"
    return'''
   <h2> Upload da tabela Abengers! </h2>
   <form method="POST" enctype="multipart/form-data">
      <input type="file" name="c_arquivo" accept=".csv">
      <input type="submit" value="-- Carregar --">
   </form>
'''

@app.route('/apagar_tabela/<nome_tabela>', methods=['GET'])
def apapagarTabela(nome_tabela):
    conn = getDbConnect()
    # realiza o apontamento para o banco que será manipulado
    cursor = conn.cursor()
    # Usaremos o try except para controlar possiveis erros
    # Confirmar antes se a tabela existe
    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'")
    # pega o resultado da contagem (0 se não existir e 1 se existir)
    exist = cursor.fetchone()[0]
    if not exist :
        conn.close()
        return "Tabela não encontrada"
    
    try:
        cursor.execute(f'DROP TABLE "{nome_tabela}"')
        conn.commit()
        conn.close()
        return f"tabela {nome_tabela} Apagada com sucesso!!"

    except Exception as erro:
        conn.close()
        return "Não foi possível apagar a tabela erro: {erro}"


@app.route(rotas[8], methods=["POST", "GET"])
def ver_tabela():
    if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas', 'vingadores']:
            return f"<h3>Tabela {nome_tabela} Não encontrada!!</h3><br><a href={rotas[8]}>Voltar</a>"
        
        conn = getDbConnect()
        df = pd.read_sql_query(f"SELECT * FROM {nome_tabela}", conn)
        conn.close()
        tabela_html = df.to_html(classes='table table-striped')  # <- CORRIGIDO AQUI
        return f'''
            <h3>Conteúdo da tabela {nome_tabela}:</h3>
            {tabela_html}
            <br><a href={rotas[8]}>Voltar</a>
        '''

    # FORMULÁRIO HTML CORRIGIDO
    return render_template_string('''
        <marquee>Selecione a tabela a ser visualizada:</marquee>
        <form method="POST">
            <label for="tabela">Escolha a tabela abaixo:</label>
            <select name="tabela">
                <option value="bebidas">Bebidas</option>
                <option value="vingadores">Vingadores</option>
            </select>
            <br><br> 
            <input type="submit" value="Consultar Tabela">    
        </form>
        <br><a href="{{rotas[0]}}">Voltar</a>                      
    ''', rotas=rotas)

@app.route(rotas[7], methods=["POST", "GET"])
def apagar_tabela():
    if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas', 'vingadores']:
            return f"<h3>Tabela '{nome_tabela}' não encontrada!</h3><br><a href='{rotas[7]}'>Voltar</a>"
        confirmacao = request.form.get('confirmacao')
        if confirmacao == "Sim":
            try:
                conn = getDbConnect()
                cursor = conn.cursor()
                cursor.execute(f'DROP TABLE IF EXISTS "{nome_tabela}"')
                conn.commit()
                conn.close()
                return f"<h3>Tabela '{nome_tabela}' apagada com sucesso!</h3><br><a href='{rotas[7]}'>Voltar</a>"
            except Exception as e:
                return f"<h3>Erro ao apagar: {e}</h3><br><a href='{rotas[9]}'>Voltar</a>"

    # Formulário GET para escolher qual tabela apagar
    return render_template_string('''
        <html>
<head>
    <title><marquee>*** CUIDADO *** - Apagar tabela</marquee></title>
    <script type="text/javascript">
        function confirmarExclusao() {
            var ok = confirm('Tem certeza que deseja apagar a tabela selecionada?');
            if (ok) {
                document.getElementById('confirmacao').value = 'Sim';
                return true;
            } else {
                return false;
            }
        }
    </script>
</head>
<body>
    <h3>Selecione a tabela que deseja apagar:</h3>
    <form method="POST" onsubmit="return confirmarExclusao();">
        <select name="tabela">
            <option value="">Selecione</option>
            <option value="bebidas">Bebidas</option>
            <option value="vingadores">Vingadores</option>
        </select>
        <br><br>
        <input type="hidden" name="confirmacao" value="" id="confirmacao">
        <input type="submit" value="Apagar Tabela">
    </form>
    <br><a href="{{ rotas[0] }}">Voltar</a>
</body>
</html>
    ''', rotas=rotas)


@app.route(rotas[9], methods=['GET', 'POST'])
def vaa_mortes_consumo():
    metricas_beb = {
        "Total (L de Alcool)":"total_litles_of_pure_alcohol",
        "Cerveja (Doses)":"beer_servings",
        "Destilados (Doses)":"spirit_servings",
        "Vinho (Doses)":"wine_servings"

    }

    if request.method == "POST":
        met_beb_key = request.form.get("metrica_beb") or "Total (L de Alcool)"
        met_beb = metricas_beb.get(met_beb_key, "total_litles_of_pure_alcohol")

        # Semente opcional para reproduzir a mesma distribuição de países nos vingadores
        try:
            semente = int(request.form.get("semente"))
        except:
            semente = 42
        sementeAleatoria = random.Random(semente) # Gera o valor aleatório baseado na smente escolhida

        # Lê os dados do SQL
        with getDbConnect as conn:
            dfA = pd.read_sql_query('SELECT * FROM vingadores', conn)
            dfB = pd.read_sql_query('SELECT country, beer_servings, apirit_servings, wine_ servings, total_litles_of_pure_alcohol FROM bebidas', conn)
        
        # ---- Mortes dos vingadores
        # estrategia: somar colunas que contenham o death como treu (case-insensitive)
        # contaremos não-nulos como 1, ou seja, death1 tem True? vale 1, não tem nada? vale 0
        death_cols = [c for c in dfA.columns if "death" in c.lower()]
        if death_cols:
            dfA["Mortes"] = dfA["death_cols"].notna().astype(int).sum(axis=1)
        elif "Deaths" in dfA.columns:
        # fallback obvio
            dfA["Mortes"] = pd.to_numeric(dfA["Deaths"], errors="coerse").fillna(0).astype(int)
        else:
            dfA["Mortes"] = 0

        if "Name/Alias" in dfA.columns:
            col_name = "Name/Alias"
        elif "Name" in dfA.columns:
            col_name = "Name"
        elif "Alias" in dfA.columns:
            col_name "Alias"
        else:
            possivel_texto = [c for c in dfA.columns if dfA[c].dtype == "object"]
            col_name = possivel_texto[0] if possivel_texto else dfA.columns[0]

        dfA.rename(columns={col_name: "Personagem"}, inplace=True)

        # --- Sortear um país para cada vingador
        paises = dfB["country"].dropna().astype(str).to_list()
        if not paises:
            return f"<h3>Não há países na tabela de bebidas!</h3><a href={rotas[9]}>Voltar1</a>"
        
        dfA["Pais"] = [sementeAleatoria.choice(paises) for _ in range(len(dfA))]
        dfB_cons = dfB[["country", met_beb]].rename(columns={"country":"Pais",
                        met_beb : "Consumo"
        })
        base = dfA[["Personagem", "Mortes", "Pais"]].merg(dfB_cons, on="Pais", how="left")

        # filtrar apenas linhas validas
        base = base.dropna(subset=['Consumo'])
        base["Mortes"] = pd.to_numeric(base["Mortes"], errors="coerse").fillna(0).astype(int)
        base = base[base["Mortes"] >= 0]

        # Correlação (se possivel)
        corr_text = ""
        if base["Consumo"].notna().sum() >=3 and base["Mortes"].notna().sum() >= 3:
            try:
                corr = base["Consumo"].corr(base["Mortes"])
                corr_txt = f" ♣ r = {corr:.3f} "
            except Exception:
                pass
        # Gráfico Scatter 2D: Consumo X Mortes (cor = pais) ---------
        fig2d = px. Scatter(
            base,
            x = "Consumo",
            y = "Mortes",
            cor = "Pais",
            hover_name = "Personagem",
            hover_data = {
                "Pais": True,
                "Consumo": True,
                "Mortes": True
                },
            title = f"Vingadores - Mortes X Consumo de Alcool do país ({met_beb_key}){corr_text}"           
        )
        fig2D.update_layout(
            xaxis_title = f"{met_beb_key}"
            yaxis_title = "Mortes (contagem)"
            margin = dict(l=40, r=20, t=70, b=40)
        )
        return (
            "<h3> Grafico 2D --- </h3>"
            + fig2D.to_html(full_html= false)
            + "<hr>"
            + "<h3> --- Grafico 3D --- </h3>"
            + "<p> Em Breve </p>"
            + "<hr>"
            + "<h3> --- Preview dos dados --- </h3>"
            + "<p> Em Breve </p>"
            + "<hr>"
            + f"<a href={rotas[9]}>Voltar</a>"
            + "<br>"
            + f"<a href={rotas[9]}>Menu Inicial</a>"
                       

        )

    return render_template_string('''
                 

        <!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>V.A.A - País X Consumo X Mortes</title>
    <style>
        /* Reset e fonte */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f0f4ff, #fdfdfd);
            margin: 0;
            padding: 20px;
            color: #333;
            overflow-x: hidden;
        }

        /* Título */
        h2 {
            text-align: center;
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 20px;
            animation: fadeSlideDown 1s ease both;
        }

        /* Animação para o título */
        @keyframes fadeSlideDown {
            from {
                opacity: 0;
                transform: translateY(-15px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Formulário */
        form {
            max-width: 450px;
            margin: 0 auto;
            background: #fff;
            padding: 25px 30px;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            transition: transform 0.2s ease;
            opacity: 0;
            transform: translateY(25px);
            animation: fadeSlideUp 1s ease forwards;
            animation-delay: 0.3s;
        }

        /* Animação para o form */
        @keyframes fadeSlideUp {
            from {
                opacity: 0;
                transform: translateY(25px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        form:hover {
            transform: translateY(-3px);
        }

        /* Labels */
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #34495e;
        }

        /* Select e Inputs */
        select, input[type="number"] {
            width: 100%;
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid #ccc;
            margin-bottom: 20px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        /* Animação de pulsar */
        @keyframes pulseBorder {
            0% {
                box-shadow: 0 0 0 0 rgba(108, 99, 255, 0.6);
            }
            70% {
                box-shadow: 0 0 10px 5px rgba(108, 99, 255, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(108, 99, 255, 0);
            }
        }

        select:focus, input[type="number"]:focus {
            border-color: #6c63ff;
            outline: none;
            animation: pulseBorder 1.2s infinite;
        }

        /* Botão */
        input[type="submit"] {
            width: 100%;
            padding: 12px 0;
            background: linear-gradient(90deg, #6c63ff, #4facfe);
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease, transform 0.1s ease;
            opacity: 0;
            animation: fadeSlideUp 1s ease forwards;
            animation-delay: 0.6s;
        }

        input[type="submit"]:hover {
            background: linear-gradient(90deg, #4facfe, #6c63ff);
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(108, 99, 255, 0.4);
        }

        /* Efeito press (clicado) */
        input[type="submit"]:active {
            transform: scale(0.96);
            box-shadow: 0 3px 8px rgba(108, 99, 255, 0.3) inset;
        }

        /* Texto explicativo */
        p {
            max-width: 700px;
            margin: 20px auto;
            text-align: center;
            line-height: 1.5;
            color: #555;
            opacity: 0;
            animation: fadeSlideUp 1s ease forwards;
            animation-delay: 0.9s;
        }

        /* Link voltar */
        a {
            display: inline-block;
            margin: 20px auto;
            text-decoration: none;
            padding: 10px 18px;
            border-radius: 10px;
            background: #ecf0f1;
            color: #2c3e50;
            font-weight: bold;
            transition: all 0.3s ease;
            opacity: 0;
            animation: fadeSlideUp 1s ease forwards;
            animation-delay: 1.2s;
        }

        a:hover {
            background: #6c63ff;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
        }

        /* Rodapé */
        footer {
            margin-top: 40px;
            padding: 15px 0;
            border-top: 2px solid #6c63ff;
            text-align: center;
            font-weight: bold;
            font-size: 1rem;
            color: #6c63ff;
            background: #f9f9ff;
            letter-spacing: 2px;
            opacity: 0;
            animation: fadeSlideUp 1s ease forwards;
            animation-delay: 1.5s;
        }
    </style>
</head>
<body>

    <h2>V.A.A - País X Consumo X Mortes</h2>

    <form method="POST">
        <label for="metrica_beb">Selecione a métrica:</label>
        <select name="metrica_beb" id="metrica_beb">
            {% for metrica in metricas_beb.keys() %}
                <option value='{{metrica}}'>{{metrica}}</option>
            {% endfor %}
        </select>

        <label for="semente"><b>semente:</b> (<i>opcional, p/ reprodutubilidade</i>)</label>
        <input type="number" name="semente" id="semente" value="42">

        <input type="submit" value="-- Gerar Graficos --">
    </form>

    <p>
        Esta visão sorteie um país para cada vingador, soma as mortes dos personagens e anexa o consumo de álcool do país, 
        ao fim plota um Scatter 2D (Consumo X Mortes) e um gráfico 3D (País X Mortes).
    </p>

    <a href="{{rotas[0]}}">Voltar</a>

    <footer>
        <p>PYTHONS DE ELITE</p>
    </footer>

</body>
</html>




''', metricas_beb = metricas_beb, rotas=rotas)

#inicia o servidor
if __name__ == '__main__':
    app.run(
      debug = config.FLASK_DEBUG,
      host = config.FLASK_HOST,
      port = config.flask_port
         )