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
st.subheader("Herramienta para la gestión de divisas")

# Cargar sistema
sistema = joblib.load("sistema_usdeur.pkl")
modelo_xgb = sistema["xgb"]
modelo_prophet = sistema["prophet"]
forecast = sistema["forecast_prophet"]

# Introducción
st.header("Sobre el proyecto")
st.markdown("""
La gestión eficiente del tipo de cambio USD/EUR es una tarea crítica para empresas que operan en mercados internacionales. Esta aplicación ha sido desarrollada como herramienta predictiva estratégica, orientada específicamente a evaluar **cuándo conviene convertir dólares a euros** de forma inteligente y respaldada por datos.

---

###  ¿Cómo funciona el sistema?

El modelo predictivo combina dos enfoques analíticos complementarios:

- **Prophet (Meta/Facebook)**  
  Un modelo de series temporales capaz de identificar patrones históricos, estacionalidades y tendencias internas del mercado cambiario.  
  Ideal para estudiar la evolución natural del tipo de cambio sin variables externas.

- **XGBoost (Extreme Gradient Boosting)**  
  Algoritmo de aprendizaje supervisado que incorpora variables macroeconómicas clave como inflación en EE.UU., tasa de interés de la Reserva Federal, índice DXY y rezagos históricos.  
  Permite capturar el impacto de factores externos sobre el valor del dólar.

---

###  ¿Por qué usar ambos?

La combinación de Prophet y XGBoost permite:
- **Mejorar la precisión** de la predicción.
- Detectar discrepancias entre patrones históricos y señales económicas del entorno.
- Generar una estimación más equilibrada y confiable para el tipo de cambio.
- Emitir recomendaciones estratégicas de conversión de divisa con respaldo técnico.

Este enfoque se considera **conservador**: prioriza coherencia entre modelos internos y tiende a proyectar el valor del dólar de forma estructural, sin incorporar expectativas de mercado o eventos especulativos.

---

###  Comparación en línea con fuentes externas

Para validar las estimaciones y fortalecer la toma de decisiones, el sistema compara sus resultados con predicciones publicadas por fuentes externas especializadas.

Estas fuentes utilizan modelos técnicos, encuestas de sentimiento y proyecciones del mercado para estimar el comportamiento del USD/EUR en horizontes mensuales.

 El sistema alerta si existe una **divergencia significativa entre el modelo interno y el consenso externo**, lo que puede indicar un momento óptimo (o de riesgo) para realizar el cambio de divisa.

---

Este proyecto busca transformar la incertidumbre cambiaria en un recurso estratégico, aportando predicciones y visualizaciones claras  directamente a la gestión financiera.
""")
# 📅 Instrucción antes del selector
st.markdown("""
<div style="background-color:#f9f9f9; padding:12px; border-left:5px solid #0b6cb7; border-radius:6px; margin-top:15px;">
<strong style="color:#0b6cb7;">Selecciona una fecha a partir de este mes para consultar la predicción del tipo de cambio USD/EUR, SELECCIONA AÑO Y MES .</strong>
</div>
""", unsafe_allow_html=True)


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

    # 🚦 Recomendación general según coherencia entre modelos
    if desviacion < 2:
     mensaje = "🟢 Los modelos se parecen mucho: puedes confiar en la predicción."
    elif valor_xgb > valor_prophet:
     mensaje = "🔴 El modelo económico dice que el dólar podría subir. Atención si estás pensando en cambiar."
    else:
        mensaje = "🟡 El modelo histórico muestra una subida del dólar basada en su comportamiento pasado."

# 💱 Recomendación sobre cuándo cambiar dólares a euros
    if desviacion < 2:
     riesgo_texto = "🟢 Es un mes estable: podrías cambiar tus dólares con confianza."
    elif valor_xgb > valor_prophet:
        riesgo_texto = "🔴 Riesgo externo: el dólar podría subir. Si puedes esperar, quizá recibas más euros."
    else:
     riesgo_texto = "🟡 El pasado indica que el dólar puede subir. Considera si te conviene esperar un poco."


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
         <strong style="color:#006400;">✅ El modelo está alineado con las previsiones externas para ese mes.</strong>
        </div>
     """, unsafe_allow_html=True)
   
elif resultado["Promedio"] > prediccion_externa:
     st.markdown("""
     <div style="background-color:#fff0f0; padding:15px; border-radius:8px;">
           <strong style="color:#8B0000;"> El modelo sobreestima el USD frente al EUR según fuentes externas.</strong>
     </div>
     """, unsafe_allow_html=True)
else:
        st.markdown("""
        <div style="background-color:#f0f7ff; padding:15px; border-radius:8px;">
         <strong style="color:#0b6cb7;"> El modelo subestima el USD frente al EUR según fuentes externas.</strong>
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

st.header("Cierre del proyecto")
st.markdown("""
Este sistema es el resultado de un trabajo técnico y estratégico realizado por el equipo de Grupo Procourval, orientado a fortalecer la toma de decisiones en operaciones de divisas a través de un modelo híbrido de predicción USD/EUR.

Durante el desarrollo:

- Se recopilaron y limpiaron series temporales y datos macroeconómicos clave.
- Se entrenaron dos modelos complementarios: Prophet (patrones históricos) y XGBoost (variables externas).
- Se construyó una arquitectura combinada, que mejora precisión y estabilidad frente a enfoques individuales.
- Se diseñó una aplicación interactiva que permite consultar predicciones por fecha y comparar con fuentes externas del mercado.

Este sistema ofrece recomendaciones operativas claras, alertas visuales y métricas de confianza, siendo una herramienta valiosa para:

- Paneles financieros internos  
- Estrategias de cobertura y cambio  
- Estudios técnicos de riesgo cambiario  
- Simulación de escenarios futuros

---

###  ¿Qué sigue?

Este es solo un primer borrador. Hay oportunidade de mejora como:

- Integrar nuevas variables geopolíticas y financieras.
- Automatizar la actualización de datos y predicciones en tiempo real.
- Explorar modelos de red neuronal (LSTM, RNN) para mayor profundidad.

El feedback  proporcionado será clave para seguir iterando y hacer de esta herramienta un sistema más completo y adaptado al entorno cambiante.

Gracias.
""")


st.markdown("---")
st.caption("© Cristina Puertas · Sistema híbrido desarrollado con Python, Streamlit, Prophet & XGBoost")

