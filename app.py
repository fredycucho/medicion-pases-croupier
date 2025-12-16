import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# ================= CONFIG =================
ARCHIVO_EXCEL = "pases_croupier.xlsx"
CODIGOS_ADMIN = ["jmesa01", "adminvip"]

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

# ================= LISTAS BASE COMPLETAS =================
jefes_mesa_base = [
    "Aguado Jaime Omar", "Alvarez Vivian Leslie", "Araya Alex Fernando",
    "Bravo Francisco Andres", "Diaz Raul Humberto", "Gonzalez Elizabeth Janet",
    "Manriquez Rocio Alexsandra", "Pardo Freddy", "Recabal Willfredo Alexis",
    "Soto Felix Eduardo", "Villegas Rodrigo"
]

croupiers_base = [
    "Avila Leonardo Esteban","Ayala Carlos Tadeo Benjamin","Barraza Sebastian",
    "Campillay Nicolas Eduardo","Carvajal Carla Paola","Castro Lopéz Constanza",
    "Collao Conzuelo Javiera","Contreras Natalia Alejandra","Cortes Eduardo",
    "Cortes Marcelo Andres","Cortes Viviana Victoria","Cuello Dinko Andres",
    "Diaz Guillermo Ignacio","Dinamarca Sergio Antonio","Flores Sergio",
    "Godoy Francisca","Godoy Tommy","Gonzalez Julian Alonso",
    "Hernandez Teresa Carolina","Jimenez Dafne Lorena","Milovic Milko Miroslav",
    "Muñoz Francisco Javier","Olivares Bernardo Jaime","Oyanedel Giovanni Ernesto",
    "Peña y Lillo Sebastian","Ramirez Nicolas Elias","Rodriguez Darcy Scarlett",
    "Rojas Adriana Carina","Rojas Alejandro","Salinas Jose Tomas",
    "Segovia Alejandra","Tapia Edward Antonio","Tapia Manuel",
    "Velasquez Felipe Ignacio","Vivanco Ximena","Zarate Diego","Zarricueta Angel"
]

juegos_base = [
    "Blackjack","Ruleta Americana","Draw Poker",
    "Hold'em Poker Plus","Mini Punto y Banca","Go Poker"
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
for k in ["inicio","confirmar_nueva","modo_config","confirmar_reset"]:
    if k not in st.session_state:
        st.session_state[k] = False if k!="inicio" else None

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
if st.session_state.inicio is None:
    if st.button("▶ INICIAR", use_container_width=True):
        st.session_state.inicio = time.time()
        st.rerun()
else:
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
        st.success("✅ Medición guardada")
        st.rerun()

    time.sleep(1)
    st.rerun()

# ================= ADMIN =================
st.divider()
st.subheader("🔐 Acceso administrativo")

codigo = st.text_input("Código", type="password")

if codigo in CODIGOS_ADMIN:

    col1, col2, col3 = st.columns(3)

    with col1:
        if os.path.exists(ARCHIVO_EXCEL):
            st.download_button(
                "📥 Descargar Excel",
                open(ARCHIVO_EXCEL,"rb"),
                file_name=ARCHIVO_EXCEL
            )

    with col2:
        if not st.session_state.confirmar_reset:
            if st.button("🧨 Resetear mediciones"):
                st.session_state.confirmar_reset = True
                st.rerun()
        else:
            st.warning("¿Borrar TODAS las mediciones?")
            if st.button("✅ Confirmar reset"):
                columnas = [
                    "FechaHora","JefeMesa","Croupier",
                    "Juego","Jugadores",
                    "Tiempo_segundos","Tiempo_formato"
                ]
                pd.DataFrame(columns=columnas).to_excel(ARCHIVO_EXCEL, index=False)
                st.session_state.confirmar_reset = False
                st.success("Base de mediciones reiniciada")
                st.rerun()

    with col3:
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

            df_cfg = pd.DataFrame({"Nombre": lista})
            df_cfg.index = df_cfg.index + 1
            st.dataframe(df_cfg, use_container_width=True)

            nuevo = st.text_input(f"Agregar nuevo {titulo[:-1]}", key=f"new_{titulo}")
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

# ================= ESTADÍSTICAS =================
st.divider()
st.subheader("📊 Estadísticas")

if os.path.exists(ARCHIVO_EXCEL):
    df = pd.read_excel(ARCHIVO_EXCEL)

    if not df.empty:

        st.markdown("### 🎲 Tiempo promedio por juego y cantidad de jugadores")
        tabla_juego_jugadores = (
            df
            .groupby(["Juego", "Jugadores"])["Tiempo_segundos"]
            .mean()
            .reset_index()
            .round(2)
            .sort_values(["Juego", "Jugadores"])
        )
        tabla_juego_jugadores.index = tabla_juego_jugadores.index + 1
        st.dataframe(tabla_juego_jugadores, use_container_width=True)

        st.markdown("### 👤 Tiempo promedio por croupier, juego y jugadores")
        tabla_croupier = (
            df
            .groupby(["Croupier", "Juego", "Jugadores"])["Tiempo_segundos"]
            .mean()
            .reset_index()
            .round(2)
            .sort_values(["Croupier", "Juego", "Jugadores"])
        )
        tabla_croupier.index = tabla_croupier.index + 1
        st.dataframe(tabla_croupier, use_container_width=True)

    else:
        st.info("ℹ️ Aún no hay mediciones registradas.")
else:
    st.info("ℹ️ El archivo de mediciones todavía no existe.")


