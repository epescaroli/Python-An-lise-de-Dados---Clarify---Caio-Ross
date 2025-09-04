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


#inicia o servidor
if __name__ == '__main__':
    app.run(
      debug = config.FLASK_DEBUG,
      host = config.FLASK_HOST,
      port = config.flask_port
         )