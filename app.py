import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# ================= CONFIG =================
ARCHIVO_EXCEL = "pases_croupier.xlsx"
CODIGOS_ADMIN = ["jmesa01", "adminvip"]

jefes_mesa = [
    "Aguado Jaime Omar", "Alvarez Vivian Leslie", "Araya Alex Fernando",
    "Bravo Francisco Andres", "Diaz Raul Humberto", "Gonzalez Elizabeth Janet",
    "Manriquez Rocio Alexsandra", "Pardo Freddy", "Recabal Willfredo Alexis",
    "Soto Felix Eduardo", "Villegas Rodrigo"
]

croupiers = [
    "Avila Leonardo Esteban", "Ayala Carlos Tadeo Benjamin",
    "Barraza Sebastian", "Campillay Nicolas Eduardo",
    "Carvajal Carla Paola", "Castro Lopéz Constanza",
    "Collao Conzuelo Javiera", "Contreras Natalia Alejandra",
    "Cortes Eduardo", "Cortes Marcelo Andres", "Cortes Viviana Victoria",
    "Cuello Dinko Andres", "Diaz Guillermo Ignacio",
    "Dinamarca Sergio Antonio", "Flores Sergio",
    "Godoy Francisca", "Godoy Tommy", "Gonzalez Julian Alonso",
    "Hernandez Teresa Carolina", "Jimenez Dafne Lorena",
    "Milovic Milko Miroslav", "Muñoz Francisco Javier",
    "Olivares Bernardo Jaime", "Oyanedel Giovanni Ernesto",
    "Peña y Lillo Sebastian", "Ramirez Nicolas Elias",
    "Rodriguez Darcy Scarlett", "Rojas Adriana Carina",
    "Rojas Alejandro", "Salinas Jose Tomas", "Segovia Alejandra",
    "Tapia Edward Antonio", "Tapia Manuel",
    "Velasquez Felipe Ignacio", "Vivanco Ximena",
    "Zarate Diego", "Zarricueta Angel"
]

juegos = [
    "Blackjack", "Ruleta Americana", "Draw Poker",
    "Hold'em Poker Plus", "Mini Punto y Banca", "Go Poker"
]

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
    m = int(segundos // 60)
    s = int(segundos % 60)
    return f"{m:02d}:{s:02d}"

# ================= ESTADO =================
if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "confirmar_nueva" not in st.session_state:
    st.session_state.confirmar_nueva = False

if "ultimo_registro" not in st.session_state:
    st.session_state.ultimo_registro = None

if "confirmar_reset" not in st.session_state:
    st.session_state.confirmar_reset = False

# ================= UI =================
st.set_page_config(page_title="Medición de Pases", layout="centered")
st.title("⏱ Medición de Pases hora por Croupier")

# -------- Selectores --------
jefe_mesa = st.selectbox("Jefe de mesa (quien mide)", jefes_mesa)
croupier = st.selectbox("Croupier", croupiers)
juego = st.selectbox("Juego", juegos)
jugadores = st.slider("Cantidad de jugadores", 1, 6, 6)

st.divider()

# Placeholder del cronómetro
cronometro_placeholder = st.empty()

# ================= CRONÓMETRO =================
if st.session_state.inicio is None and not st.session_state.confirmar_nueva:
    if st.button("▶ INICIAR", use_container_width=True):
        st.session_state.inicio = time.time()
        st.rerun()

elif st.session_state.inicio is not None:
    tiempo_actual = time.time() - st.session_state.inicio
    cronometro_placeholder.info(
        f"⏱ Tiempo en curso: {formato_tiempo(tiempo_actual)}"
    )

    if st.button("⏹ FINALIZAR", use_container_width=True):
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
        st.session_state.confirmar_nueva = True
        st.rerun()

    # 🔁 refresco automático del cronómetro
    time.sleep(1)
    st.rerun()

# ================= CONFIRMACIÓN NUEVA MEDICIÓN =================
if st.session_state.confirmar_nueva:
    st.success(
        f"✅ Tiempo registrado: {st.session_state.ultimo_registro['Tiempo_formato']}"
    )

    st.markdown("### ¿Desea realizar una nueva medición?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Sí"):
            st.session_state.confirmar_nueva = False
            st.session_state.ultimo_registro = None
            st.rerun()

    with col2:
        if st.button("❌ No"):
            st.info("Puede revisar estadísticas o cerrar la aplicación.")

# ================= ESTADÍSTICAS =================
st.divider()
st.subheader("📊 Estadísticas internas")

if os.path.exists(ARCHIVO_EXCEL):
    df = pd.read_excel(ARCHIVO_EXCEL)

    if not df.empty:
        st.markdown("### ⏱ Tiempo promedio por juego")
        st.dataframe(
            df.groupby("Juego")["Tiempo_segundos"].mean().reset_index(),
            use_container_width=True
        )

        st.markdown("### 👤 Tiempo promedio por croupier")
        st.dataframe(
            df.groupby("Croupier")["Tiempo_segundos"].mean().reset_index(),
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total mediciones", len(df))
        col2.metric("Mínimo", formato_tiempo(df["Tiempo_segundos"].min()))
        col3.metric("Máximo", formato_tiempo(df["Tiempo_segundos"].max()))
    else:
        st.info("El archivo existe, pero no tiene datos.")
else:
    st.info("Aún no hay registros.")

# ================= ADMIN =================
st.divider()
st.subheader("🔐 Acceso administrativo")

codigo = st.text_input("Código de acceso", type="password")

if codigo:
    if codigo in CODIGOS_ADMIN:
        st.success("Acceso autorizado")

        if os.path.exists(ARCHIVO_EXCEL):
            col1, col2 = st.columns(2)

            # ---- Descargar ----
            with col1:
                with open(ARCHIVO_EXCEL, "rb") as f:
                    st.download_button(
                        "📥 Descargar Excel",
                        f,
                        file_name="pases_croupier.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            # ---- Reset ----
            with col2:
                if not st.session_state.confirmar_reset:
                    if st.button("🧨 Resetear registros"):
                        st.session_state.confirmar_reset = True
                        st.rerun()
                else:
                    st.warning("⚠️ ¿Seguro que desea borrar TODOS los registros?")

                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Sí, borrar todo"):
                            columnas = [
                                "FechaHora", "JefeMesa", "Croupier",
                                "Juego", "Jugadores",
                                "Tiempo_segundos", "Tiempo_formato"
                            ]
                            df_vacio = pd.DataFrame(columns=columnas)
                            df_vacio.to_excel(ARCHIVO_EXCEL, index=False)

                            st.session_state.confirmar_reset = False
                            st.success("🧹 Registros eliminados. Archivo reiniciado.")
                            st.rerun()

                    with c2:
                        if st.button("❌ Cancelar"):
                            st.session_state.confirmar_reset = False
                            st.rerun()
        else:
            st.info("Aún no existe archivo.")
    else:
        st.error("Código incorrecto")


