import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import yfinance as yf

# 1. Descargar historial del tipo de cambio USD/EUR desde Yahoo Finance
def obtener_usd_eur(desde='2010-01-01', hasta='2025-07-17'):
    par = 'EURUSD=X'
    datos = yf.download(par, start=desde, end=hasta)
    datos = datos[['Close']].rename(columns={'Close': 'USD/EUR'})
    return datos

# 2. Descargar índice del dólar (DXY)
def obtener_dxy(desde='2010-01-01', hasta='2025-07-17'):
    dxy = yf.download('DX-Y.NYB', start=desde, end=hasta)
    dxy = dxy[['Close']].rename(columns={'Close': 'DXY'})
    return dxy

# 3. Descargar indicadores macro (ejemplo: inflación mensual de EE.UU.)
def obtener_inflacion_usa():
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL'
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))
    print("Columnas disponibles en el archivo de inflación:", df.columns)
    return df


# 4. Unir todos los datos
def unir_datos():
    usd_eur = obtener_usd_eur()
    dxy = obtener_dxy()
    inflacion = obtener_inflacion_usa()

    df = usd_eur.join(dxy, how='outer').join(inflacion, how='outer')
    df = df.dropna()
    return df

# Ejecutar
if __name__ == "__main__":
    datos_completos = unir_datos()
    print(datos_completos.tail())
    datos_completos.to_csv('datos_dolar_predictivo.csv')
