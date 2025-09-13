import pandas as pd
import numpy as np
import plotly.graph_objs as go

folder = 'C:/Users/noturno/Desktop/Python 2 Evandro/Airbnb/'
t_ny = 'ny.csv'
t_rj = 'rj.csv'

def standartize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    lat_candidates = ['lat','latitude','Latitude','LAT','Lat','LATITUDE']
    lon_candidates = ['lon','LON','Lon', 'Longitude', 'LONGITUDE', 'Long', 'Lng']
    cost_candidates = ['custo','valor','coust','cost','price','preço']
    name_candidates = ['nome','name','titulo','title','local','place', 'descricao']

    def pick(colnames, candidates):
    # colnames: lista de nomes das colunas da tabela
    #candidates : lista de possiveis nomes das colunas a serem encontradas
        for c in candidates:
        #percorre cada candidato (c) dentro da lista de candidatos
            if c in colnames:
            # se o candidato for exatamente igual a um dos nomes em colnames (tabela)
                return c
                # retorna esse candidato imediatamente
        for c in candidates:
        #se nao encontrou a correspondencia
            # percorre novamente cada coluna
            for col in colnames:
            #aqui percorre cada nome de coluna
                if c.lower() in col.lower():
                #faz igual o de cima, mas trabalhando em minusculas apenas
                    return col
                    # retorna a coluna imediatamente
        return None
        #se nao encontrou nenhuma coluna, nem exato nem parcial, retorna none (nenhum match encontrado)


    lat_col = pick(df.columns, lat_candidates)
    lon_col = pick(df.columns, lat_candidates)
    cost_col = pick(df.columns, lat_candidates)
    name_col = pick(df.columns, lat_candidates)

    if lat_col is None or lon_col is None:
        raise ValueError(f"Não encontrei a Latitude e longitude: {list(df.columns)}")
    
    out =pd.DataFrame()
    out['lat'] =    pd.to_numeric(df[lat_col],  errors='coerce')
    out['lon'] =    pd.to_numeric(df[lon_col],  errors='coerce')
    out['custo'] =  pd.to_numeric(df[cost_col], errors='coerce')
    out['nome'] =   pd.to_numeric(df[name_col], errors='coerce')
    
    # remove as linhas sem coordenadas
    out = out.dropna(subset=['lat', 'lon']).reset_index(drop=True)

    # preenche o custo se for ausente 
    if out['custo'].notna().any():
        med = float(out['custo'].median())
        if not np.isfinite(med):
            med = 1.0
        out['custo'] = out['custo'].fillna(med)
    else:
        out['custo'] = 1.0
    return out

def city_center(df: pd.DataFrame) -> dict:
    '''
    Define a função citycenter que encontra a latitude e
    longitude media de um grande volume de dados
    --- recebe como parametro um dataframe pandas
    --- deve retornar um dicionario (-> dict)

    '''

    return dict(
        lat = float(df['lat'].mean()),
        lon = float(df['lat'].mean()),
    )

# -------------- traces ---------------------

def make_point_trace(df:pd.DataFrame, name:str) -> go.Scattermapbox:
    hover = (
        "<b>     %{customdata[0]}</b><br>"
        "Custo:  %{customdata[1]}<br>"
        "Lat:    %{lat:.5f}<br>"
        "lon:    %{lon:.5f}"
    )  

    # tamanho dos marcadores (normalizados pelo custo)
    c = df['custo'].astype(float).values
    c_min, c_max = float(np.min(c)), float(np.max(c))

    # CASO ESPECIAL: Se não existorem valores numericos 
    # validos ou se todos os custos forem praticamente iguais (diferença <1e-9)
    # cria uma array de tamanho fixo 10 para todos os pontos 
    if not np.isfinite(c_min) or not np.isfinite(c_max) or abs(c_max - c_min) < 1e-9:
        size = np.full_like(c, 10.0, dtype=float)
    else:
    #CASO NORMAL: Normalizar os custos para um intervalo de [0,1] e a escala
    # pode variar entre 6 e 26 (20 de amplitude mais deslocamento de 6)
    # Pontos de custos baixos ~6 pontos de custo alto ~26
        size = (c - c_min) / (c_max - c_min) * 20 + 6
    # Mesmo que os dados estejam fora da faixa de 6 a 26 ele evita sua
    # apresentação, forçando a ficar entre o intervalo
        sizes = np.clip(size, 6,26)
        # axis1 empilha as colunas lado a lado
        custom = np.stack([df['nome'].values, df['custo'].values], axis=1)

        return go.Scattermapbox(
            lat = df['lat'],
            lon = df['lon'],
            mode = 'markers',
            marker = dict(
                size = sizes,
                color = df['custo'],
                colorscale = "Plasma",
                colorbar = dict(title='custo')
            ),
            name = f'{name} ♥ Pontos',
            hovertemplate = hover,
            customdata = custom
        )

def make_density_trace(df: pd.DataFrame, name: str) -> go.Densitymapbox:
    return go.Densitymapbox(
        lat = df['lat'],
        lon = df['lon'],
        z = df['custo'],
        radius = 20,
        colorscale = "inferno",
        name = f'{name} ♥ Pontos',
        showscale = True,
        colorbar = dict(title='custo')
    )

# ------------ MAIN -------------------
def main():
    ny = standartize_columns(pd.read_csv(f'{folder}{t_ny}'))
    rj = standartize_columns(pd.read_csv(f'{folder}{t_rj}'))

    # cria os quatro traces (NY pontos de calor, RJ pontos de calor)
    ny_point = make_point_trace(ny, 'Nova York')
    ny_heat = make_density_trace(ny, 'Nova York')
    rj_point = make_point_trace(rj, 'Rio de Janeiro')
    rj_heat = make_density_trace(rj, 'Rio de Janeiro')

    fig = go.Figure([ny_point, ny_heat, rj_point, rj_heat])

    def center_zoom(df, zoom):
        return dict(
            center = city_center(df),
            zoom = zoom
        )

    buttons = [
        dict(
            label = 'Nova York ♥ Pontos',
            method = "update",
            args = [
                {'visible':[True, False, False, False]},
                {'mapbox': center_zoom(ny, 9)}
                ]
        ),
        dict(
            label = 'Nova York ♥ Calor',
            method = "update",
            args = [
                {'visible':[False, True, False, False]},
                {'mapbox': center_zoom(ny, 9)}
                ]
        ),
        dict(
            label = 'Rio de Janeiro ♥ Pontos',
            method = "update",
            args = [
                {'visible':[False, False, True, False]},
                {'mapbox': center_zoom(rj, 10)}
                ]
        ),
        dict(
            label = 'Rio de Janeiro ♥ Calor',
            method = "update",
            args = [
                {'visible':[False, False, False, True]},
                {'mapbox': center_zoom(rj, 10)}
                ]
        )


    ]

    fig.update_layout(
        title = 'Mapa interativo de Custos ○ Pontos e mapa de Calor',
        mapbox_style = "open-street-map", # Satellite-streets
        mapbox = dict(center=city_center(rj), zoom=10),
        margin = dict(l=10, r=10, t=50, b=10),
        updatemenus = [dict(
            buttons = buttons,
            direction = 'down',
            x = 0.01,
            y = 0.99,
            xanchor = 'left',
            yanchor = 'top',
            bgcolor = 'white',
            bordercolor = 'purple'
        )],
        legend = dict(
            orientation = 'h',
            yanchor = 'bottom',
            xanchor = 'right',
            y = 0.01,
            x = 0.99
        )
    
    )

    # Vamos salvar em HTML criando uma página com dados sem precisar de um servidor para rodar

    fig.write_html(f'{folder}mapa_interativos.html', full_html = True, include_plotlyjs = 'cdn')
    print(f'Arquivo gerado com sucesso!!! \nSalvo em: {folder}mapa_interativos.html')

    # Inicia o servidor
if __name__ == '__main__':
    main()


