import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Cargar datos
df = pd.read_excel("Base_envios_final.xlsx")

# Renombrar columnas
df.columns = [
    "Fecha", "Tiempo_envio", "Distancia", "Indice_ocupacion",
    "Barrio", "Tipo_via", "Semaforos", "Hora_salida",
    "Horario_salida", "Clima"
]

# División de datos
X = df[["Distancia", "Indice_ocupacion", "Tipo_via", "Semaforos", "Hora_salida", "Horario_salida", "Clima"]]
y = df["Tiempo_envio"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Función de predicción basada en fórmula fija
def predecir_tiempo(distancia, indice_ocupacion, tipo_via, semaforos, hora_salida, horario_salida, clima):
    return round(30.98 + 1.61*distancia + 0.34*indice_ocupacion - 1.38*tipo_via +
                 0.44*semaforos - 0.06*hora_salida + 0.44*horario_salida + 5.75*clima, 2)

# Diccionario de destinos y distancias
destinos = {
    "Blas de Lezo (15 km)": ("Blas de Lezo", 15),
    "Castillo Grande (20 km)": ("Castillo Grande", 20),
    "La Castellana (17 km)": ("La Castellana", 17),
    "Torices (18 km)": ("Torices", 18),
    "Zaragocilla (16 km)": ("Zaragocilla", 16)
}

# Número de semáforos por destino
semaforos_por_destino = {
    "Blas de Lezo": 6,
    "Castillo Grande": 9,
    "La Castellana": 7,
    "Torices": 8,
    "Zaragocilla": 7
}

# Título de la app
st.title("🚚 Estimador de Tiempo de Envío desde Mamonal")

# Panel lateral
st.sidebar.header("🛠️ Parámetros de Entrada")

# Segmentadores
indice_ocupacion = st.sidebar.slider("Índice de Ocupación (veh/km)", 0.0, 100.0, 50.0)
hora_salida = st.sidebar.slider("Hora de salida", 0, 23, 8)

# Destino y distancia
destino_opcion = st.sidebar.selectbox("Destino", list(destinos.keys()))
destino_nombre, distancia = destinos[destino_opcion]

# Obtener automáticamente número de semáforos
semaforos = semaforos_por_destino[destino_nombre]

# Tipo de vía
tipo_via_opciones = {
    "Vía principal (1)": 1,
    "Vía secundaria (2)": 2,
    "Vía local (3)": 3
}
tipo_via_str = st.sidebar.selectbox("Tipo de vía", list(tipo_via_opciones.keys()))
tipo_via = tipo_via_opciones[tipo_via_str]

# Franja horaria
franja_horaria_opciones = {
    "Mañana (1)": 1,
    "Tarde (2)": 2,
    "Noche (3)": 3
}
franja_str = st.sidebar.selectbox("Franja horaria", list(franja_horaria_opciones.keys()))
horario_salida = franja_horaria_opciones[franja_str]

# Clima
clima_opciones = {
    "Soleado (1)": 1,
    "Nublado (2)": 2,
    "Lluvia (3)": 3,
    "Tormenta (4)": 4
}
clima_str = st.sidebar.selectbox("Clima", list(clima_opciones.keys()))
clima = clima_opciones[clima_str]

# Predicción
tiempo_estimado = predecir_tiempo(distancia, indice_ocupacion, tipo_via, semaforos, hora_salida, horario_salida, clima)
st.subheader(f"🕒 Tiempo estimado de envío: **{tiempo_estimado} minutos**")

# Congestión por hora
st.subheader("📊 Congestión promedio por hora")
hora_congestion = df.groupby("Hora_salida")["Indice_ocupacion"].mean()
fig, ax = plt.subplots()
hora_congestion.plot(kind="bar", ax=ax, color='salmon')
ax.set_xlabel("Hora del día")
ax.set_ylabel("Índice de ocupación promedio")
ax.set_title("Ocupación vehicular promedio por hora")
ax.set_yticks(range(0, 101, 20))  # Saltos de 20 en eje Y
st.pyplot(fig)

# Mejor hora para salir
mejor_hora = hora_congestion.idxmin()
st.subheader(f"✅ Mejor hora para salir: **{mejor_hora}:00 hrs** (menor ocupación vehicular)")

# Gráfico de congestión por destino
st.subheader("🚧 Rutas con mayor congestión esperada (Mamonal → Destino)")

# Filtrar solo por hora_salida
df_filtrado = df[df["Hora_salida"] == hora_salida]

# Lista de barrios
barrios_objetivo = ["Blas de Lezo", "Castillo Grande", "La Castellana", "Torices", "Zaragocilla"]

# Agrupar por barrio
congestion_por_barrio = df_filtrado.groupby("Barrio")["Indice_ocupacion"].mean().reindex(barrios_objetivo)

# Rellenar NaN con el promedio válido
promedio_valido = congestion_por_barrio[congestion_por_barrio.notna()].mean()
congestion_por_barrio = congestion_por_barrio.fillna(promedio_valido)

# Gráfico de barras horizontal
fig3, ax3 = plt.subplots()
congestion_por_barrio.sort_values().plot(kind='barh', ax=ax3, color='orange')
ax3.set_xlabel("Índice de ocupación promedio")
ax3.set_ylabel("Destino")
ax3.set_title(f"Congestión esperada a las {hora_salida}:00 hrs")
st.pyplot(fig3)

# Mostrar la ruta más congestionada
barrio_max = congestion_por_barrio.idxmax()
valor_max = congestion_por_barrio.max()
st.warning(f"⚠️ Mayor congestión esperada a las {hora_salida}:00 hrs: **{barrio_max}** (Índice: {valor_max:.2f})")
