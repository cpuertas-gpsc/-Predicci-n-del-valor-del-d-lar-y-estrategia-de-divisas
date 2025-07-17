![Logo Grupo Procourval](logo%20grupo.JPG)

> Este proyecto ha sido desarrollado por el equipo de Grupo Procourval con el objetivo de optimizar la gestión de riesgos y fortalecer la toma de decisiones estratégicas en operaciones de divisas. Se implementan técnicas avanzadas de modelado predictivo y análisis de escenarios para anticipar la evolución del valor del dólar en horizontes de 1 a 3 años, en respuesta a variables macroeconómicas clave.

#  Proyecto: Predicción del valor del dólar y estrategia de divisas

##  Grupo Procourval

###  Objetivo General

Desarrollar un modelo económico y predictivo capaz de estimar el valor del dólar a futuro y definir una estrategia óptima de conversión de divisas, considerando tres escenarios contrastantes:

- **Neutro:** evolución proyectada sin shocks relevantes.
- **Negativo:** condiciones macroeconómicas adversas (presión inflacionaria, política monetaria contractiva, riesgos geopolíticos).
- **Positivo:** factores que fortalecen el dólar (crecimiento económico sostenido, política monetaria expansiva, estabilidad global).

###  Metodología Aplicada

1. **Recolección** de series temporales desde fuentes económicas oficiales.
2. **Limpieza estructural** y estandarización de datos.
3. **Exploración visual** y estadística de variables clave (EDA).
4. **Modelado** mediante algoritmos de series temporales y/o aprendizaje automático.
5. **Simulación de escenarios** con proyecciones ajustadas.
6. **Diseño estratégico** según perfil de riesgo y objetivos operativos.

###  Estructura del Proyecto

| Notebook                   | Propósito                                         |
|---------------------------|--------------------------------------------------|
| `00_carga_datos.ipynb`    | Obtención de datos desde fuentes web/API         |
| `01_exploracion_datos.ipynb` | Limpieza, análisis exploratorio, visualización  |
| `02_modelado_predictivo.ipynb` | Entrenamiento del modelo, generación de escenarios |
| `03_estrategia_divisas.ipynb` | Evaluación de resultados y recomendación estratégica |

###  Entregables

- Dataset limpio y documentado (`dataset_final_economico.csv`)
- Notebooks explicativos y reproducibles
- Informe ejecutivo en PDF
- Dosier técnico para presentación institucional

###  Equipo

- **Responsable:** Cristina Puertas  
- **Colaboradores:** Grupo Procourval  
---
# Fuentes de Datos Económicos

El proyecto se fundamenta sobre series temporales oficiales que permiten modelar la dinámica cambiaria del dólar frente al euro, contextualizado dentro de movimientos macroeconómicos globales.

##  Variables Recopiladas

###  USD/EUR — Tipo de Cambio Diario

- **Fuente:** Yahoo Finance  
- **Ticker:** `EURUSD=X`  
- **Frecuencia:** Diaria (2010–2025)  
- **Descripción:** Precio de cierre del dólar estadounidense respecto al euro. Indicador directo de la paridad cambiaria bilateral.

###  DXY — Índice del Dólar

- **Fuente:** Yahoo Finance  
- **Ticker:** `DX-Y.NYB`  
- **Frecuencia:** Diaria  
- **Descripción:** Índice ponderado que mide la fortaleza del dólar frente a una cesta de seis monedas principales (EUR, JPY, GBP, CAD, SEK, CHF).

### Inflación USA

- **Fuente:** FRED (Federal Reserve Bank of St. Louis)  
- **Serie:** `CPIAUCSL`  
- **Frecuencia:** Mensual  
- **Descripción:** Índice de Precios al Consumidor para consumidores urbanos. Mide la evolución del coste de vida en EE.UU., clave para interpretar política monetaria.

###  Tasa de Interés Fed

- **Fuente:** FRED  
- **Serie:** `FEDFUNDS`  
- **Frecuencia:** Mensual  
- **Descripción:** Tasa de fondos federales efectiva. Instrumento principal de la Reserva Federal para ajustar liquidez y controlar la inflación.

## Justificación de las variables

- Permiten capturar **interacciones clave** entre política monetaria, inflación, fuerza relativa del dólar y comportamiento del mercado cambiario.
- Son utilizadas por instituciones financieras globales para análisis de riesgo, cobertura cambiaria y planificación financiera.
- Representan elementos esenciales para generar escenarios realistas y recomendables.

---

Los datos han sido tratados, depurados y unificados en un único archivo consolidado (`dataset_final_economico.csv`), listo para modelado y simulación de estrategias.

