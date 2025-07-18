import streamlit as st
import pandas as pd
import joblib
import datetime
from dateutil.relativedelta import relativedelta
import os

# Configurar Streamlit
st.set_page_config(
    page_title="Sistema Predictivo USD/EUR",
    layout="wide",
    initial_sidebar_state="auto",
)

# Estilos corporativos
st.markdown("""
<style>
    body {
        background-color: white;
        color: black;
    }
    .main, .block-container {
        background-color: white;
        color: black;
    }
    h1, h2, h3 {
        color: #0b6cb7;
    }
    .stApp {
        font-family: 'Segoe UI', sans-serif;
        color: black;
    }
    .css-18ni7ap, .css-1kyxreq, .css-1v3fvcr {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo institucional
st.image("logo grupo.JPG", width=180)

# Título
st.title("Sistema Predictivo USD/EUR")
st.subheader("Herramienta inteligente para la gestión de divisas")

# Cargar sistema
sistema = joblib.load("sistema_usdeur.pkl")
modelo_xgb = sistema["xgb"]
modelo_prophet = sistema["prophet"]
forecast = sistema["forecast_prophet"]

# Introducción
st.header("Sobre el proyecto")
st.markdown("""
Este sistema predictivo ha sido diseñado para anticipar la evolución del tipo de cambio USD/EUR en contextos económicos variables.

**¿Por qué dos modelos?**  
- Prophet analiza patrones históricos internos del tipo de cambio.  
- XGBoost incorpora variables exógenas: inflación, tasas, índice DXY...

**¿Qué aporta la combinación?**  
- Mejora la precisión.  
- Detecta incoherencias entre fuentes.  
- Ayuda a tomar mejores decisiones de cobertura en divisa.
""")

# Fechas disponibles (primer día del mes de 2025 a 2027)
fechas_validas = [datetime.date(2025, 1, 1) + relativedelta(months=i) for i in range(36)]

fecha_input = st.selectbox("Selecciona una fecha (mes y año)", fechas_validas)
fecha_str = fecha_input.strftime("%Y-%m-%d")

# Simulación de entrada macro (ajustar según variables reales)
entrada_macro = pd.DataFrame({
    "DXY": [104.2],
    "Inflación USA": [2.5],
    "Tasa Fed": [4.75],
    "USD_EUR_lag1": [0.935],
    "USD_EUR_lag3": [0.927],
    "DXY_lag1": [103.7],
    "DXY_lag3": [102.4]
}, index=[fecha_str])

# Evaluación de la fecha
def evaluar_fecha(fecha, entrada_macro):
    fila = forecast[forecast["ds"] == fecha]
    if fila.empty:
        return None
    valor_prophet = fila["yhat"].values[0]
    valor_xgb = modelo_xgb.predict(entrada_macro)[0]
    valor_promedio = (valor_prophet + valor_xgb) / 2
    desviacion = abs(valor_prophet - valor_xgb) / valor_promedio * 100

    # Recomendación general
    if desviacion < 2:
        mensaje = "✅ Alta coherencia entre modelos: predicción confiable."
    elif valor_xgb > valor_prophet:
        mensaje = "⚠️ XGBoost estima presión externa alcista sobre el dólar."
    else:
        mensaje = "⚠️ Prophet detecta patrón de subida interna."

    # Recomendación estratégica en divisa
    if desviacion < 2:
        riesgo_texto = "🟢 Baja volatilidad. Podría ser un momento estable para cambiar divisa."
    elif valor_xgb > valor_prophet:
        riesgo_texto = "🔴 Riesgo exógeno: el entorno económico anticipa subida del dólar. Evalúa si conviene esperar."
    else:
        riesgo_texto = "🟡 Riesgo histórico: patrones pasados indican apreciación. Considera cobertura."

    return {
        "XGBoost": round(valor_xgb, 4),
        "Prophet": round(valor_prophet, 4),
        "Promedio": round(valor_promedio, 4),
        "Desviación (%)": round(desviacion, 2),
        "Diagnóstico": mensaje,
        "Recomendación estratégica": riesgo_texto
    }

resultado = evaluar_fecha(fecha_str, entrada_macro)

# Mostrar resultado
if resultado:
    st.subheader(f"Predicción para {fecha_str}")
    st.markdown(f"**XGBoost:** {resultado['XGBoost']}")
    st.markdown(f"**Prophet:** {resultado['Prophet']}")
    st.markdown(f"**Promedio combinado:** {resultado['Promedio']}")
    st.markdown(f"**Desviación entre modelos:** {resultado['Desviación (%)']}%")
    st.markdown(f"<p style='color:black; font-size:18px;'>{resultado['Diagnóstico']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:black; font-size:18px;'><strong>{resultado['Recomendación estratégica']}</strong></p>", unsafe_allow_html=True)
else:
    st.warning("La fecha seleccionada no está disponible en las proyecciones.")

# Evaluación gráfica
st.header("Evaluación comparativa de modelos")
st.markdown("""
Este gráfico muestra las métricas técnicas obtenidas al evaluar los modelos individuales y el sistema combinado:

- MAE: Error absoluto medio  
- RMSE: Error cuadrático medio  
- MAPE: Error porcentual  
- R²: capacidad explicativa
""")

if os.path.exists("output.png"):
    st.image("output.png", use_container_width=True)
else:
    st.warning("La imagen de evaluación no está disponible.")

# Cierre
st.header("Aplicación operativa")
st.markdown("""
Este sistema puede integrarse en:

- Paneles financieros
- Estrategias de cobertura
- Estudios de riesgo por divisa
- Decisiones mensuales de cambio

Su estructura permite evaluar fechas, predecir comportamientos, y orientar decisiones críticas en entornos cambiantes.
""")

st.markdown("---")
st.caption("© Grupo Corporativo · Sistema híbrido desarrollado con Python, Streamlit, Prophet & XGBoost")

