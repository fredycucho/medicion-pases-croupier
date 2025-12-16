import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# ================= CONFIG =================
ARCHIVO_EXCEL = "pases_croupier.xlsx"
CODIGOS_ADMIN = ["JMESA01", "ADMINVIP"]

CFG_JEFES = "config_jefes_mesa.xlsx"
CFG_CROUPIERS = "config_croupiers.xlsx"
CFG_JUEGOS = "config_juegos.xlsx"

# ================= FUNCIONES CONFIG =================
def cargar_config(archivo, valores_iniciales):
    if not os.path.exists(archivo):
        pd.DataFrame({"Nombre": valores_iniciales}).to_excel(archivo, index=False)
    return pd.read_excel(archivo)["Nombre"].dropna().tolist()

def guardar_config(archivo, lista):
    pd.DataFrame({"Nombre": lista}).to_excel(archivo, index=False)

# ================= DATOS BASE =================
jefes_mesa_base = [
    "Aguado Jaime Omar", "Alvarez Vivian Leslie", "Araya Alex Fernando",
    "Bravo Francisco Andres", "Diaz Raul Humberto", "Gonzalez Elizabeth Janet",
    "Manriquez Rocio Alexsandra", "Pardo Freddy", "Recabal Willfredo Alexis",
    "Soto Felix Eduardo", "Villegas Rodrigo"
]

croupiers_base = [
    "Avila Leonardo Esteban", "Ayala Carlos Tadeo Benjamin",
    "Barraza Sebastian", "Campillay Nicolas Eduardo",
    "Carvajal Carla Paola", "Castro Lopéz Constanza",
    "Collao Conzuelo Javiera", "Contreras Natalia Alejandra"
]

juegos_base = [
    "Blackjack", "Ruleta Americana", "Draw Poker",
    "Hold'em Poker Plus", "Mini Punto y Banca", "Go Poker"
]

# ================= CARGA CONFIG =================
jefes_mesa = cargar_config(CFG_JEFES, jefes_mesa_base)
croupiers = cargar_config(CFG_CROUPIERS, croupiers_base)
juegos = cargar_config(CFG_JUEGOS, juegos_base)

# ================= FUNCIONES =================
def guardar_registro(data):
    df_nuevo = pd.DataFrame([data])
    if os.path.exists(ARCHIVO_EXCEL):
        df = pd.read_excel(ARCHIVO_EXCEL)
        df = pd.concat([df, df_nuevo], ignore_index=True)
    else:
        df = df_nuevo
    df.to_excel(ARCHIVO_EXCEL, index=False)

def formato_tiempo(segundos):
    return f"{int(segundos//60):02d}:{int(segundos%60):02d}"

# ================= SESSION STATE =================
for k in ["inicio","confirmar_nueva","ultimo_registro","confirmar_reset","modo_config"]:
    if k not in st.session_state:
        st.session_state[k] = None if k=="inicio" else False

# ================= UI =================
st.set_page_config(page_title="Medición de Pases", layout="centered")
st.title("⏱ Medición de Pases por Croupier")

bloqueado = st.session_state.inicio is not None

jefe_mesa = st.selectbox("Jefe de mesa", jefes_mesa, disabled=bloqueado)
croupier = st.selectbox("Croupier", croupiers, disabled=bloqueado)
juego = st.selectbox("Juego", juegos, disabled=bloqueado)
jugadores = st.slider("Cantidad de jugadores", 1, 6, 6, disabled=bloqueado)

st.divider()

cronometro = st.empty()

# ================= CRONÓMETRO =================
if st.session_state.inicio is None and not st.session_state.confirmar_nueva:
    if st.button("▶ INICIAR", use_container_width=True):
        st.session_state.inicio = time.time()
        st.rerun()

elif st.session_state.inicio is not None:
    cronometro.info(f"⏱ Tiempo: {formato_tiempo(time.time()-st.session_state.inicio)}")

    if st.button("⏹ FINALIZAR", use_container_width=True):
        t = time.time() - st.session_state.inicio
        guardar_registro({
            "FechaHora": datetime.now(),
            "JefeMesa": jefe_mesa,
            "Croupier": croupier,
            "Juego": juego,
            "Jugadores": jugadores,
            "Tiempo_segundos": round(t,2),
            "Tiempo_formato": formato_tiempo(t)
        })
        st.session_state.inicio = None
        st.session_state.confirmar_nueva = True
        st.rerun()

    time.sleep(1)
    st.rerun()

# ================= ADMIN =================
st.divider()
st.subheader("🔐 Acceso administrativo")

codigo = st.text_input("Código", type="password")

if codigo in CODIGOS_ADMIN:

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 Descargar Excel",
            open(ARCHIVO_EXCEL,"rb"),
            file_name=ARCHIVO_EXCEL
        )

    with col2:
        if st.button("⚙ Configuración"):
            st.session_state.modo_config = not st.session_state.modo_config

    # ================= CONFIGURACIÓN =================
    if st.session_state.modo_config:
        st.divider()
        st.subheader("⚙ Configuración del sistema")

        for titulo, archivo, lista in [
            ("Jefes de mesa", CFG_JEFES, jefes_mesa),
            ("Croupiers", CFG_CROUPIERS, croupiers),
            ("Juegos", CFG_JUEGOS, juegos)
        ]:
            st.markdown(f"### {titulo}")

            st.dataframe(pd.DataFrame({"Nombre": lista}), use_container_width=True)

            nuevo = st.text_input(f"Agregar nuevo {titulo[:-1]}", key=titulo)
            if st.button(f"➕ Agregar {titulo}", key=f"add_{titulo}") and nuevo:
                if nuevo not in lista:
                    lista.append(nuevo)
                    guardar_config(archivo, lista)
                    st.rerun()

            eliminar = st.selectbox(
                f"Eliminar {titulo[:-1]}",
                [""] + lista,
                key=f"del_{titulo}"
            )
            if eliminar and st.button(f"🗑 Eliminar {titulo}", key=f"delbtn_{titulo}"):
                lista.remove(eliminar)
                guardar_config(archivo, lista)
                st.rerun()
