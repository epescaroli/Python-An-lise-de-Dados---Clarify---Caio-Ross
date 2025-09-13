import pandas as pd
import numpy as np
import plotly.graph_objs as go

folder = C:\Users\noturno\Desktop\Python 2 Evandro\Airbnb/
t_ny = 

def standartize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    lat_candidate = ['lat','latitude','Latitude','LAT','Lat','LATITUDE']
    lon_candidates = ['lon', 'LON', 'Lon', 'Longitude', 'LONGITUDE', 'lONG', 'lng']
    cost_candidates = ["cost", "custo", "preco", "price", "valor","amount", "amt", "vl", "vlt", "vlr","COST", "CUSTO", "PRECO", "PRICE", "VALOR",]
    name_candidates = ['nome', 'name', 'titulo', 'title', 'local', 'place', 'descrcao']

    def pick(colnames, candidates):
        for c in candidates:
            if c in colnames
                return c
        for c in candidates
            for col in colnames
                if c.lower() in col.lower():
                    return col
        return None
        
