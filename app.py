import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# ================== ARCHIVOS ==================
ARCHIVO_MEDICIONES = "pases_croupier.xlsx"
CFG_CROUPIERS = "config_croupiers.xlsx"
CFG_JEFES = "config_jefes_mesa.xlsx"
CFG_JUEGOS = "config_juegos.xlsx"

# ================== LISTAS BASE ==================
BASE_JEFES = [
    "Aguado Jaime Omar", "Alvarez Vivian Leslie", "Araya Alex Fernando",
    "Bravo Francisco Andres", "Diaz Raul Humberto",
    "Gonzalez Elizabeth Janet", "Manriquez Rocio Alexsandra",
    "Pardo Freddy", "Recabal Willfredo Alexis",
    "Soto Felix Eduardo", "Villegas Rodrigo"
]

BASE_CROUPIERS = [
    "Avila Leonardo Esteban", "Ayala Carlos Tadeo Benjamin",
    "Barraza Sebastian", "Campillay Nicolas Eduardo",
    "Carvajal Carla Paola", "Castro Lopéz Constanza",
    "Collao Conzuelo Javiera", "Contreras Natalia Alejandra",
    "Cortes Eduardo", "Cortes Marcelo Andres",
    "Cortes Viviana Victoria", "Cuello Dinko Andres",
    "Diaz Guillermo Ignacio", "Dinamarca Sergio Antonio",
    "Flores Sergio", "Godoy Francisca", "Godoy Tommy",
    "Gonzalez Julian Alonso", "Hernandez Teresa Carolina",
    "Jimenez Dafne Lorena", "Milovic Milko Miroslav",
    "Muñoz Francisco Javier", "Olivares Bernardo Jaime",
    "Oyanedel Giovanni Ernesto", "Peña y Lillo Sebastian",
    "Ramirez Nicolas Elias", "Rodriguez Darcy Scarlett",
    "Rojas Adriana Carina", "Rojas Alejandro",
    "Salinas Jose Tomas", "Segovia Alejandra",
    "Tapia Edward Antonio", "Tapia Manuel",
    "Velasquez Felipe Ignacio", "Vivanco Ximena",
    "Zarate Diego", "Zarricueta Angel"
]

BASE_JUEGOS = [
    "Blackjack", "Ruleta Americana", "Draw Poker",
    "Hold'em Poker Plus", "Mini Punto y Banca", "Go Poker"
]

# ================== FUNCIONES ==================
def cargar_config(nombre, base):
    if not os.path.exists(nombre):
        pd.DataFrame({"Nombre": base}).to_excel(nombre, index=False)
    return pd.read_excel(nombre)["Nombre"].tolist()

def guardar_medicion(data):
    df_nuevo = pd.DataFrame([data])
    if os.path.exists(ARCHIVO_MEDICIONES):
        df = pd.read_excel(ARCHIVO_MEDICIONES)
        df = pd.concat([df, df_nuevo], ignore_index=True)
    else:
        df = df_nuevo
    df.to_excel(ARCHIVO_MEDICIONES, index=False)

def formato(seg):
    return f"{int(seg//60):02d}:{int(seg%60):02d}"

# ================== CARGA CONFIG ==================
jefes = cargar_config(CFG_JEFES, BASE_JEFES)
croupiers = cargar_config(CFG_CROUPIERS, BASE_CROUPIERS)
juegos = cargar_config(CFG_JUEGOS, BASE_JUEGOS)

# ================== ESTADO ==================
if "inicio" not in st.session_state:
    st.session_state.inicio = None
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False

# ================== UI ==================
st.set_page_config(page_title="Medición de Pases", layout="centered")
st.title("⏱ Medición de Pases por Croupier")

bloqueado = st.session_state.inicio is not None

jefe = st.selectbox("Jefe de Mesa", jefes, disabled=bloqueado)
croupier = st.selectbox("Croupier", croupiers, disabled=bloqueado)
juego = st.selectbox("Juego", juegos, disabled=bloqueado)
jugadores = st.slider("Cantidad de jugadores", 1, 6, 6, disabled=bloqueado)

# ================== CRONÓMETRO ==================
cronometro = st.empty()

if st.button("⏹ FINALIZAR" if bloqueado else "▶ INICIAR"):
    if not bloqueado:
        st.session_state.inicio = time.time()
        st.session_state.finalizado = False
    else:
        duracion = time.time() - st.session_state.inicio
        registro = {
            "FechaHora": datetime.now(),
            "JefeMesa": jefe,
            "Croupier": croupier,
            "Juego": juego,
            "Jugadores": jugadores,
            "Tiempo_segundos": round(duracion, 2),
            "Tiempo_formato": formato(duracion)
        }
        guardar_medicion(registro)
        st.success(f"Tiempo registrado: {registro['Tiempo_formato']}")
        st.session_state.inicio = None
        st.session_state.finalizado = True

if bloqueado:
    cronometro.markdown(
        f"## ⏱ {formato(time.time() - st.session_state.inicio)}"
    )

# ================== NUEVA MEDICIÓN ==================
if st.session_state.finalizado:
    if st.button("🔁 Nueva medición"):
        st.session_state.finalizado = False
        st.experimental_rerun()

# ================== ESTADÍSTICAS ==================
st.divider()
st.header("📊 Estadísticas")

if os.path.exists(ARCHIVO_MEDICIONES):
    df = pd.read_excel(ARCHIVO_MEDICIONES)

    st.subheader("👤 Promedio por Croupier / Juego / Jugadores")
    st.dataframe(
        df.groupby(["Croupier", "Juego", "Jugadores"])["Tiempo_segundos"]
          .mean().reset_index(),
        use_container_width=True
    )

    st.subheader("🎲 Promedio por Juego y Cantidad de Jugadores")
    st.dataframe(
        df.groupby(["Juego", "Jugadores"])["Tiempo_segundos"]
          .mean().reset_index(),
        use_container_width=True
    )

# ================== ADMIN ==================
st.divider()
st.header("🔐 Acceso Administrativo")

if st.checkbox("Mostrar zona administrativa"):
    st.download_button(
        "📥 Descargar mediciones",
        open(ARCHIVO_MEDICIONES, "rb"),
        file_name="mediciones.xlsx"
    )

    if st.button("🧹 Resetear SOLO mediciones"):
        if os.path.exists(ARCHIVO_MEDICIONES):
            os.remove(ARCHIVO_MEDICIONES)
        st.experimental_rerun()

    if st.button("♻️ Resetear configuración (croupiers / juegos / jefes)"):
        for f in [CFG_CROUPIERS, CFG_JEFES, CFG_JUEGOS]:
            if os.path.exists(f):
                os.remove(f)
        st.experimental_rerun()
