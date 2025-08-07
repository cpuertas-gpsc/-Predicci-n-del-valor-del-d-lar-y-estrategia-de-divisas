import streamlit as st
import pandas as pd
import requests
import pickle
from datetime import datetime

# 🖼️ Configuración visual
st.set_page_config(page_title="Predicción USD/EUR", layout="wide")
st.image("logo grupo.JPG", width=180)
st.title("Sistema Predictivo USD/EUR Mejorado")

# 🔗 Función para obtener valor USD/EUR desde FRED
def obtener_valor_dolar_fred(api_key):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "DEXUSEU",
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    valor = float(data["observations"][0]["value"])
    fecha = data["observations"][0]["date"]
    return valor, fecha

# 🔑 Clave API FRED
api_key = "437ffc22620f0fe3615350b1764f112b"
valor_dolar, fecha_dato = obtener_valor_dolar_fred(api_key)

# 📆 Formatear fecha como Año-Mes
fecha_formateada = pd.to_datetime(fecha_dato).strftime("%Y-%m")

# 💬 Mostrar valor actual con protagonismo
st.markdown("""
<div style='
    background-color:#e6f2ff;
    padding:25px;
    border-radius:10px;
    border-left:8px solid #0b6cb7;
    color:#0b6cb7;
    text-align:center;
'>
    <div style='font-size:26px; font-weight:bold;'>Valor del dólar HOY</div>
    <div style='font-size:14px; margin-bottom:10px;'>Fecha: {fecha}</div>
    <div style='font-size:48px; font-weight:bold;'>{valor}</div>
    <div style='font-size:14px; margin-top:10px;'>
        Fuente: <a href="https://fred.stlouisfed.org/series/DEXUSEU" target="_blank" style='color:#0b6cb7;'>FRED - Reserva Federal</a>
    </div>
</div>
""".format(fecha=fecha_formateada, valor=round(valor_dolar, 4)), unsafe_allow_html=True)

# 📦 Cargar modelo Prophet entrenado
with open("modelo_prophet_mejorado.pkl", "rb") as f:
    modelo_prophet = pickle.load(f)

# 📥 Cargar forecast generado
forecast = pd.read_csv("forecast_mejorado.csv")
forecast["ds"] = pd.to_datetime(forecast["ds"])
import plotly.express as px

# 📅 Selector de fecha
st.markdown("### 🔮 Predicción futura del USD/EUR")
fecha_seleccionada = st.date_input(
    "Selecciona una fecha para ver los tres escenarios:",
    value=forecast["ds"].max().date(),
    min_value=forecast["ds"].min().date(),
    max_value=forecast["ds"].max().date()
)

# 🔍 Buscar la fecha más cercana
fecha_objetivo = pd.to_datetime(fecha_seleccionada)
fechas_disponibles = forecast["ds"]
fecha_mas_cercana = fechas_disponibles.iloc[(fechas_disponibles - fecha_objetivo).abs().argsort()[0]]

# 🔍 Obtener predicción para esa fecha
prediccion = forecast[forecast["ds"] == fecha_mas_cercana]

if not prediccion.empty:
    neutro = round(prediccion["escenario_neutro"].values[0], 4)
    positivo = round(prediccion["escenario_positivo"].values[0], 4)
    negativo = round(prediccion["escenario_negativo"].values[0], 4)

    st.markdown(f"""
    <div style='background-color:#f9f9f9; padding:20px; border-left:6px solid #0b6cb7; border-radius:6px; color:#0b6cb7;'>
        <strong>Predicción más cercana ({fecha_mas_cercana.strftime('%Y-%m-%d')}):</strong><br>
        <ul style='list-style:none; padding-left:0; font-size:16px;'>
            <li>🔵 Escenario neutro: <strong>{neutro}</strong></li>
            <li>🟢 Escenario positivo: <strong>{positivo}</strong></li>
            <li>🔴 Escenario negativo: <strong>{negativo}</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No se encontró ninguna predicción cercana.")


# 📥 Cargar datos reales desde el CSV económico
datos_reales = pd.read_csv("dataset_final_economico.csv")
datos_reales["Fecha"] = pd.to_datetime(datos_reales["Fecha"])
datos_reales = datos_reales.rename(columns={"Fecha": "ds", "USD_EUR": "valor_real"})

# 🔄 Asegurar que las fechas coincidan con el forecast
datos_reales_filtrados = datos_reales[datos_reales["ds"].isin(forecast["ds"])]

# 📊 Gráfico con escenarios + valor real desde CSV
import plotly.graph_objects as go

fig = go.Figure()

# Escenarios
fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["escenario_neutro"], mode='lines', name='Neutro', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["escenario_positivo"], mode='lines', name='Positivo', line=dict(color='green')))
fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["escenario_negativo"], mode='lines', name='Negativo', line=dict(color='red')))

# 🔶 Valor real desde el CSV
fig.add_trace(go.Scatter(
    x=datos_reales_filtrados["ds"],
    y=datos_reales_filtrados["valor_real"],
    mode='lines',
    name='Valor real',
    line=dict(color='gold', width=2, dash='dot')
))

fig.update_layout(
    title="Proyección USD/EUR por escenarios vs. valor real",
    xaxis_title="Fecha",
    yaxis_title="Valor USD/EUR",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
# 🔍 Buscar valor real para la fecha más cercana
valor_real_fila = datos_reales[datos_reales["ds"] == fecha_mas_cercana]

if not valor_real_fila.empty:
    valor_real = round(valor_real_fila["valor_real"].values[0], 4)

    # 📉 Calcular diferencias
    dif_neutro = round((neutro - valor_real) / valor_real * 100, 2)
    dif_positivo = round((positivo - valor_real) / valor_real * 100, 2)
    dif_negativo = round((negativo - valor_real) / valor_real * 100, 2)

    # 🧾 Mostrar tabla comparativa
    st.markdown("### 📊 Comparativa con valor real")
    comparativa = pd.DataFrame({
        "Escenario": ["Real", "Neutro", "Positivo", "Negativo"],
        "Valor USD/EUR": [valor_real, neutro, positivo, negativo],
        "Diferencia (%) vs. Real": [0.0, dif_neutro, dif_positivo, dif_negativo]
    })
    st.dataframe(comparativa.style.format({"Valor USD/EUR": "{:.4f}", "Diferencia (%) vs. Real": "{:+.2f}%"}))

else:
    # 🧾 Mostrar tabla solo con escenarios
    st.markdown("### 📊 Predicción")
    comparativa = pd.DataFrame({
        "Escenario": ["Neutro", "Positivo", "Negativo"],
        "Valor USD/EUR": [neutro, positivo, negativo]
    })
    st.dataframe(comparativa.style.format({"Valor USD/EUR": "{:.4f}"}))
import io

# Convertir tabla a CSV
csv_buffer = io.StringIO()
comparativa.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

# Botón de descarga
st.download_button(
    label="📥 Descargar tabla como CSV",
    data=csv_data,
    file_name="comparativa_usdeur.csv",
    mime="text/csv"
)
# Mostrar texto plano para copiar
st.markdown("### 📋 Copiar tabla")
st.text(comparativa.to_string(index=False))
st.markdown("### 🧠 Resumen de la predicción")
st.markdown(f"""
<div style='background-color:#e6f2ff; padding:15px; border-radius:6px; color:#0b6cb7; font-size:16px;'>
Para la fecha <strong>{fecha_mas_cercana.strftime('%Y-%m-%d')}</strong>, el modelo predice:<br>
🔵 Escenario neutro: <strong>{neutro}</strong><br>
🟢 Escenario positivo: <strong>{positivo}</strong><br>
🔴 Escenario negativo: <strong>{negativo}</strong><br><br>

📊 <strong>Análisis experto:</strong><br>
• Rango total entre escenarios: <strong>{round(positivo - negativo, 4)}</strong><br>
• Desviación estimada: <strong>{round(((positivo - negativo)/2), 4)}</strong><br>
• Distancia al neutro: Positivo: <strong>{round(positivo - neutro, 4)}</strong> / Negativo: <strong>{round(neutro - negativo, 4)}</strong><br><br>

🧭 <strong>Recomendación estratégica:</strong><br>
{f"El modelo muestra una dispersión significativa (>10%), lo que sugiere alta volatilidad. Se recomienda cobertura parcial si hay exposición al USD." if (positivo - negativo) > 0.1 else "La dispersión es moderada. Puede mantenerse la posición actual, pero se recomienda monitoreo activo."}
</div>
""", unsafe_allow_html=True)


# Valores predichos
neutro = 1.1569
positivo = 1.2147
negativo = 1.0990
valor_actual = 1.1555
fecha_mas_cercana = datetime(2028, 6, 30)

# Cálculos
rango = round(positivo - negativo, 4)
desviacion = round(rango / 2, 4)
dist_pos = round(positivo - neutro, 4)
dist_neg = round(neutro - negativo, 4)
riesgo = "🔴 Alto" if rango > 0.1 else "🟡 Moderado" if rango > 0.05 else "🟢 Bajo"
st.markdown("### 📚 Metodología y fuentes del modelo")
st.markdown("""
<div style='background-color:#f0f8ff; padding:20px; border-radius:10px; color:#0b6cb7; font-size:16px;'>

🔍 <strong>Métricas utilizadas:</strong><br>
• <strong>USD/EUR:</strong> Tipo de cambio diario<br>
• <strong>DXY:</strong> Índice de fortaleza del dólar<br>
• <strong>Inflación USA:</strong> Índice de Precios al Consumidor (CPI)<br>
• <strong>Tasa de interés Fed:</strong> Tasa de fondos federales efectiva<br><br>

📈 <strong>Modelo aplicado:</strong><br>
• Algoritmo Prophet entrenado sobre series temporales desde 2010<br>
• Simulación de tres escenarios: neutro, positivo y negativo<br>
• Análisis de dispersión y recomendación estratégica<br><br>

🌐 <strong>Fuentes oficiales:</strong><br>
• <a href="https://fred.stlouisfed.org/series/DEXUSEU" target="_blank">FRED - Reserva Federal</a><br>
• <a href="https://finance.yahoo.com/quote/EURUSD=X" target="_blank">Yahoo Finance - EUR/USD</a><br><br>

📦 <strong>Repositorio del proyecto:</strong><br>
• <a href="https://github.com/cpuertas-gpsc/-Predicci-n-del-valor-del-d-lar-y-estrategia-de-divisas" target="_blank">Grupo Procourval – Predicción del valor del dólar y estrategia de divisas</a><br><br>

🧠 <strong>Objetivo:</strong><br>
Optimizar la toma de decisiones en operaciones de divisas mediante inteligencia predictiva, simulación de escenarios y análisis financiero especializado.

</div>
""", unsafe_allow_html=True)
