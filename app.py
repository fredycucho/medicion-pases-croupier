import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# ---------------- CONFIG ----------------
ARCHIVO_EXCEL = "pases_croupier.xlsx"

jefes_mesa = [
    "Aguado Jaime Omar",
    "Alvarez Vivian Leslie",
    "Araya Alex Fernando",
    "Bravo Francisco Andres",
    "Diaz Raul Humberto",
    "Gonzalez Elizabeth Janet",
    "Manriquez Rocio Alexsandra",
    "Pardo Freddy",
    "Recabal Willfredo Alexis",
    "Soto Felix Eduardo",
    "Villegas Rodrigo"
]

croupiers = [
    "Avila Leonardo Esteban",
    "Ayala Carlos Tadeo Benjamin",
    "Barraza Sebastian",
    "Campillay Nicolas Eduardo",
    "Carvajal Carla Paola",
    "Castro Lopéz Constanza",
    "Collao Conzuelo Javiera",
    "Contreras Natalia Alejandra",
    "Cortes Eduardo",
    "Cortes Marcelo Andres",
    "Cortes Viviana Victoria",
    "Cuello Dinko Andres",
    "Diaz Guillermo Ignacio",
    "Dinamarca Sergio Antonio",
    "Flores Sergio",
    "Godoy Francisca",
    "Godoy Tommy",
    "Gonzalez Julian Alonso",
    "Hernandez Teresa Carolina",
    "Jimenez Dafne Lorena",
    "Milovic Milko Miroslav",
    "Muñoz Francisco Javier",
    "Olivares Bernardo Jaime",
    "Oyanedel Giovanni Ernesto",
    "Peña y Lillo Sebastian",
    "Ramirez Nicolas Elias",
    "Rodriguez Darcy Scarlett",
    "Rojas Adriana Carina",
    "Rojas Alejandro",
    "Salinas Jose Tomas",
    "Segovia Alejandra",
    "Tapia Edward Antonio",
    "Tapia Manuel",
    "Velasquez Felipe Ignacio",
    "Vivanco Ximena",
    "Zarate Diego",
    "Zarricueta Angel"
]

juegos = [
    "Blackjack",
    "Ruleta Americana",
    "Draw Poker",
    "Hod'em Poker Plus",
    "Mini Punto y Banca",
    "Go Poker"
]

# ---------------- FUNCIONES ----------------
def guardar_registro(data):
    df_nuevo = pd.DataFrame([data])

    if os.path.exists(ARCHIVO_EXCEL):
        df = pd.read_excel(ARCHIVO_EXCEL)
        df = pd.concat([df, df_nuevo], ignore_index=True)
    else:
        df = df_nuevo

    df.to_excel(ARCHIVO_EXCEL, index=False)

def formato_tiempo(segundos):
    m = int(segundos // 60)
    s = int(segundos % 60)
    return f"{m:02d}:{s:02d}"

# ---------------- UI ----------------
st.set_page_config(
    page_title="Medición de Pases",
    layout="centered"
)

st.title("⏱ Medición de Pases por Croupier")

jefe_mesa = st.selectbox("Jefe de mesa (quien mide)", jefes_mesa)
croupier = st.selectbox("Croupier", croupiers)
juego = st.selectbox("Juego", juegos)
jugadores = st.slider("Cantidad de jugadores", 1, 6, 6)

# ---------------- CRONÓMETRO ----------------
if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "ultimo_registro" not in st.session_state:
    st.session_state.ultimo_registro = None

# Texto dinámico del botón
boton_texto = "▶ INICIAR" if st.session_state.inicio is None else "⏹ FINALIZAR"

if st.button(boton_texto, use_container_width=True):

    # -------- INICIAR --------
    if st.session_state.inicio is None:
        st.session_state.inicio = time.time()
        st.session_state.ultimo_registro = None
        st.rerun()   # ← 🔴 ESTO ES LA CLAVE

    # -------- FINALIZAR --------
    else:
        tiempo_final = time.time() - st.session_state.inicio

        registro = {
            "FechaHora": datetime.now(),
            "JefeMesa": jefe_mesa,
            "Croupier": croupier,
            "Juego": juego,
            "Jugadores": jugadores,
            "Tiempo_segundos": round(tiempo_final, 2),
            "Tiempo_formato": formato_tiempo(tiempo_final)
        }

        guardar_registro(registro)

        st.session_state.ultimo_registro = registro
        st.session_state.inicio = None
        st.rerun()   # ← 🔴 Y AQUÍ TAMBIÉN

# Mostrar tiempo en curso
cronometro_placeholder = st.empty()

if st.session_state.inicio is not None:
    tiempo_actual = time.time() - st.session_state.inicio
    cronometro_placeholder.markdown(
        f"## ⏱ {formato_tiempo(tiempo_actual)}"
    )
    time.sleep(0.5)  # refresca cada medio segundo
    st.rerun()

# Mostrar último registro guardado
if st.session_state.ultimo_registro is not None:
    st.success("Registro guardado correctamente")
    st.json(st.session_state.ultimo_registro)

