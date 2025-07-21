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
# Mostrar valores estimados de entrada
st.markdown("###  Variables estimadas para la fecha seleccionada")
st.dataframe(entrada_macro.T.rename(columns={fecha_str: "Valor estimado"}))

# Métricas visuales personalizadas
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="background-color:#e6f2ff; padding:20px; border-radius:10px;">
            <h4 style="color:#0b6cb7;">Promedio modelo combinado</h4>
            <p style="font-size:24px; color:black;"><strong>{resultado['Promedio']} USD/EUR</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color:#fff5e6; padding:20px; border-radius:10px;">
            <h4 style="color:#b76c0b;">Desviación entre modelos</h4>
            <p style="font-size:24px; color:black;"><strong>{resultado['Desviación (%)']}%</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )
# 📅 Extraer clave de mes y año
fecha_clave = fecha_input.strftime("%Y-%m")

# 🌐 Predicciones externas por mes (simuladas manualmente)
# Basadas en fuentes como Traders Union, FXStreet y LiteFinance
predicciones_externas_mensuales = {
    "2025-07": 1.155,
    "2025-08": 1.148,
    "2025-09": 1.182,
    "2025-10": 1.183,
    "2025-11": 1.218,
    "2025-12": 1.255,
    "2026-01": 1.257,
    "2026-02": 1.258,
    "2026-03": 1.231,
    "2026-04": 1.197,
    "2026-05": 1.170,
    "2026-06": 1.179,
    "2026-07": 1.203,
    "2026-08": 1.213,
    "2026-09": 1.201,
    "2026-10": 1.221,
    "2026-11": 1.207,
    "2026-12": 1.206,
    "2027-01": 1.205,
    "2027-02": 1.181,
    "2027-03": 1.197,
    "2027-04": 1.232,
    "2027-05": 1.233,
    "2027-06": 1.202,
    "2027-07": 1.185,
    "2027-08": 1.195,
    "2027-09": 1.220,
    "2027-10": 1.184,
    "2027-11": 1.203,
    "2027-12": 1.233,
    "2028-01": 1.201,
    "2028-02": 1.218,
    "2028-03": 1.252,
    "2028-04": 1.290,
    "2028-05": 1.301,
    "2028-06": 1.268,
    "2028-07": 1.247,
    "2028-08": 1.216,
    "2028-09": 1.187,
    "2028-10": 1.208,
    "2028-11": 1.172,
    "2028-12": 1.156
}



# 🔍 Buscar predicción externa para el mes seleccionado
prediccion_externa = predicciones_externas_mensuales.get(fecha_clave, None)

# 📊 Comparativa visual
if resultado and prediccion_externa:
    diferencia_ext = round(abs(resultado["Promedio"] - prediccion_externa), 4)
    delta_ext_pct = round((resultado["Promedio"] - prediccion_externa) / prediccion_externa * 100, 2)

    st.subheader("🌐 Comparativa con predicciones externas mensuales")
    st.markdown("""
**Fuentes utilizadas**:
- [Traders Union](https://tradersunion.com/es/currencies/forecast/eur-usd/): modelo técnico con indicadores como RSI, MACD, medias móviles y análisis de ondas.
- [FXStreet](https://www.fxstreet.es/rates-charts/eurusd/forecast): encuesta semanal entre analistas, con distribución de precios esperados.
- [LiteFinance](https://www.litefinance.org/es/blog/analysts-opinions/eurusd/): análisis técnico y fundamental diario, con proyecciones a medio plazo.

Estas fuentes utilizan modelos estadísticos, indicadores técnicos y análisis de sentimiento para estimar el comportamiento del EUR/USD en horizontes mensuales.
""")

st.markdown(f"""
<div style="background-color:#f2f2f2; padding:18px; border-radius:10px; margin-bottom:10px;">
    <h4 style="color:#0b6cb7;">📊 Promedio modelo combinado</h4>
    <p style="font-size:24px; color:#000;"><strong>{resultado["Promedio"]}</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background-color:#f2f2f2; padding:18px; border-radius:10px; margin-bottom:10px;">
    <h4 style="color:#b76c0b;">🌐 Predicción externa para el mes</h4>
    <p style="font-size:24px; color:#000;"><strong>{prediccion_externa}</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background-color:#fff5f5; padding:18px; border-radius:10px; margin-bottom:10px;">
    <h4 style="color:#8B0000;">📐 Diferencia absoluta</h4>
    <p style="font-size:24px; color:#000;"><strong>{diferencia_ext}</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background-color:#e6f0ff; padding:18px; border-radius:10px; margin-bottom:10px;">
    <h4 style="color:#0b6cb7;">📉 Diferencia porcentual</h4>
    <p style="font-size:24px; color:#000;"><strong>{delta_ext_pct}%</strong></p>
</div>
""", unsafe_allow_html=True)

  

   # Diagnóstico visual de alineación con predicción externa
if abs(delta_ext_pct) < 2:
        st.markdown("""
         <div style="background-color:#e6f7e6; padding:15px; border-radius:8px;">
         <strong style="color:#006400;">✅ Tu modelo está alineado con las previsiones externas para ese mes.</strong>
        </div>
     """, unsafe_allow_html=True)
   
elif resultado["Promedio"] > prediccion_externa:
     st.markdown("""
     <div style="background-color:#fff0f0; padding:15px; border-radius:8px;">
           <strong style="color:#8B0000;"> Tu modelo sobreestima el USD frente al EUR según fuentes externas.</strong>
     </div>
     """, unsafe_allow_html=True)
else:
        st.markdown("""
        <div style="background-color:#f0f7ff; padding:15px; border-radius:8px;">
         <strong style="color:#0b6cb7;"> Tu modelo subestima el USD frente al EUR según fuentes externas.</strong>
        </div>
     """, unsafe_allow_html=True)


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

