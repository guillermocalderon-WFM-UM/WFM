import streamlit as st

st.set_page_config(
    page_title="WFM Dashboard – Uniminuto",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# NAVEGACIÓN (todas por ruta de archivo → navegación confiable)
# ─────────────────────────────────────────────
home_pg = st.Page("home.py",               title="Inicio",       icon="🏠", default=True)
adh_pg  = st.Page("pages/1_Adherencia.py", title="Adherencia",   icon="🎯")
ocu_pg  = st.Page("pages/2_Ocupacion.py",  title="Ocupación",    icon="📊")
tip_pg  = st.Page("pages/4_Tipificacion.py", title="Tipificación", icon="🏷️")
nov_pg  = st.Page("pages/3_Novedades.py",  title="Novedades",    icon="📢")

pg = st.navigation([home_pg, adh_pg, ocu_pg, tip_pg, nov_pg])
pg.run()
