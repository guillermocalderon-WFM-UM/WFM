import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard WFM – Uniminuto",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPERVISOR_COLORS = px.colors.qualitative.Bold

# ─────────────────────────────────────────────
# CARGA Y PREPARACIÓN DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos(path):
    df = pd.read_excel(path, sheet_name="Detalle")
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    def a_seg(col):
        return pd.to_timedelta(df[col], errors="coerce").dt.total_seconds()

    df["adh_s"]  = a_seg("ADH aplicada")
    df["prog_s"] = a_seg("Tiempo programado")
    df["tard_s"] = a_seg("Tiempo de tardanza")
    df["aus_s"]  = a_seg("Tiempo de ausencia")

    excesos = ["Exceso Almuerzo","Exceso Descanso","Exceso Seguimiento",
               "Exceso Toilette","Exceso Entrenamiento","Exceso Feedback","Exceso Calidad"]
    for c in excesos:
        df[c + "_min"] = pd.to_timedelta(df[c], errors="coerce").dt.total_seconds() / 60

    df["Semana"]    = df["Fecha"].dt.to_period("W").apply(lambda p: f"Sem {p.start_time.strftime('%d/%m')}")
    df["Mes"]       = df["Fecha"].dt.to_period("M").astype(str)
    df["DiaSemana"] = df["Fecha"].dt.day_name()
    df["FechaStr"]  = df["Fecha"].dt.strftime("%d/%m")

    mask = (df["prog_s"] > 0) & (df["Validador Llegada"] != "Ausente")
    df["ADH_pct"] = None
    df.loc[mask, "ADH_pct"] = df.loc[mask, "adh_s"] / df.loc[mask, "prog_s"]

    return df

df = cargar_datos("Consolidado_MAYO.xlsx")

# ─────────────────────────────────────────────
# SIDEBAR – FILTROS + COLORES
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 WFM Dashboard")
    st.markdown("**Uniminuto · Scala Learning**")
    st.markdown("---")

    st.markdown("### Período")
    tipo_periodo = st.selectbox("Agrupar por", ["Día","Semana","Mes"], index=0)

    fechas = sorted(df["Fecha"].dt.date.unique())
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_ini = st.date_input("Desde", value=fechas[0], min_value=fechas[0], max_value=fechas[-1])
    with col_f2:
        fecha_fin = st.date_input("Hasta", value=fechas[-1], min_value=fechas[0], max_value=fechas[-1])

    st.markdown("---")
    st.markdown("### Filtros")

    supervisores = ["Todos"] + sorted(df["Supervisor"].dropna().unique().tolist())
    sup_sel = st.selectbox("Supervisor", supervisores)

    campanas = ["Todas"] + sorted(df["Campana"].dropna().unique().tolist())
    camp_sel = st.selectbox("Campaña", campanas)

    st.markdown("---")
    st.markdown("### 🎨 Colores")
    with st.expander("Personalizar colores"):
        COLOR_PRIMARY = st.color_picker("Sidebar / Primario", "#226B1B")
        COLOR_ACCENT  = st.color_picker("Acento (azul claro)", "#0EA5E9")
        COLOR_SUCCESS = st.color_picker("Éxito (verde)",       "#10B981")
        COLOR_WARNING = st.color_picker("Alerta (amarillo)",   "#F59E0B")
        COLOR_DANGER  = st.color_picker("Peligro (rojo)",      "#EF4444")
        COLOR_BG      = st.color_picker("Fondo",               "#F0F4F8")

    st.markdown("---")
    st.caption("Adherencia = ADH aplicada / Tiempo programado · Excluye ausentes")

# ─────────────────────────────────────────────
# CSS DINÁMICO (usa los colores del sidebar)
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    .main {{ background-color: {COLOR_BG}; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 1rem; }}
    .kpi-card {{
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid {COLOR_PRIMARY};
    }}
    .kpi-label {{ font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: {COLOR_PRIMARY}; line-height: 1.2; }}
    .kpi-sub   {{ font-size: 12px; color: #9CA3AF; margin-top: 2px; }}
    .section-title {{ font-size: 16px; font-weight: 700; color: {COLOR_PRIMARY}; margin-bottom: 4px; }}
    div[data-testid="stSidebarContent"] {{ background: {COLOR_PRIMARY}; }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}
    div[data-testid="stSidebarContent"] .stSelectbox label,
    div[data-testid="stSidebarContent"] .stMultiSelect label {{ color: #CBD5E1 !important; font-size: 12px !important; }}
    div[data-testid="stSidebarContent"] hr {{ border-color: rgba(255,255,255,0.15); }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────
mask = (
    (df["Fecha"].dt.date >= fecha_ini) &
    (df["Fecha"].dt.date <= fecha_fin)
)
if sup_sel != "Todos":
    mask &= df["Supervisor"] == sup_sel
if camp_sel != "Todas":
    mask &= df["Campana"] == camp_sel

dff = df[mask].copy()

if tipo_periodo == "Día":
    dff["_periodo"] = dff["FechaStr"]
elif tipo_periodo == "Semana":
    dff["_periodo"] = dff["Semana"]
else:
    dff["_periodo"] = dff["Mes"]

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
st.markdown(f"## 📊 Dashboard de Adherencia · Mayo 2026")
rango = f"{fecha_ini.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
filtro_txt = f"{'Todos los supervisores' if sup_sel == 'Todos' else sup_sel}  ·  {'Todas las campañas' if camp_sel == 'Todas' else camp_sel}"
st.caption(f"📅 {rango}   |   👤 {filtro_txt}")
st.markdown("---")

# ─────────────────────────────────────────────
# KPIs GLOBALES
# ─────────────────────────────────────────────
dff_validos = dff[(dff["prog_s"] > 0) & (dff["Validador Llegada"] != "Ausente")]
total_agentes   = dff["Nombre"].nunique()
total_registros = len(dff_validos)

adh_global = dff_validos["adh_s"].sum() / dff_validos["prog_s"].sum() if dff_validos["prog_s"].sum() > 0 else 0

llegada_counts = dff["Validador Llegada"].value_counts()
total_prog_valid = llegada_counts.get("Llegada a tiempo", 0) + llegada_counts.get("Llegada tarde", 0) + llegada_counts.get("Llegada antes", 0) + llegada_counts.get("Ausente", 0)
pct_ausentes = llegada_counts.get("Ausente", 0) / total_prog_valid * 100 if total_prog_valid > 0 else 0
pct_tarde    = llegada_counts.get("Llegada tarde", 0) / total_prog_valid * 100 if total_prog_valid > 0 else 0
pct_tiempo   = llegada_counts.get("Llegada a tiempo", 0) / total_prog_valid * 100 if total_prog_valid > 0 else 0

adh_color = COLOR_SUCCESS if adh_global >= 0.90 else (COLOR_WARNING if adh_global >= 0.80 else COLOR_DANGER)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class='kpi-card' style='border-color:{adh_color}'>
        <div class='kpi-label'>Adherencia Global</div>
        <div class='kpi-value' style='color:{adh_color}'>{adh_global:.1%}</div>
        <div class='kpi-sub'>ADH aplicada / Tiempo programado</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='kpi-card' style='border-color:{COLOR_PRIMARY}'>
        <div class='kpi-label'>Agentes</div>
        <div class='kpi-value'>{total_agentes}</div>
        <div class='kpi-sub'>{total_registros} registros con turno</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class='kpi-card' style='border-color:{COLOR_SUCCESS}'>
        <div class='kpi-label'>Llegada a tiempo</div>
        <div class='kpi-value' style='color:{COLOR_SUCCESS}'>{pct_tiempo:.1f}%</div>
        <div class='kpi-sub'>{llegada_counts.get("Llegada a tiempo",0)} registros</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class='kpi-card' style='border-color:{COLOR_WARNING}'>
        <div class='kpi-label'>Llegadas tarde</div>
        <div class='kpi-value' style='color:{COLOR_WARNING}'>{pct_tarde:.1f}%</div>
        <div class='kpi-sub'>{llegada_counts.get("Llegada tarde",0)} registros</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class='kpi-card' style='border-color:{COLOR_DANGER}'>
        <div class='kpi-label'>Ausentes</div>
        <div class='kpi-value' style='color:{COLOR_DANGER}'>{pct_ausentes:.1f}%</div>
        <div class='kpi-sub'>{llegada_counts.get("Ausente",0)} registros</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TENDENCIA + DISTRIBUCIÓN LLEGADAS
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📈 Tendencia de Adherencia</div>", unsafe_allow_html=True)

tend = (
    dff_validos
    .groupby("_periodo")
    .apply(lambda g: g["adh_s"].sum() / g["prog_s"].sum() if g["prog_s"].sum() > 0 else 0)
    .reset_index(name="ADH")
)

c1, c2 = st.columns([2, 1])
with c1:
    fig_tend = go.Figure()
    fig_tend.add_trace(go.Scatter(
        x=tend["_periodo"], y=tend["ADH"],
        mode="lines+markers",
        line=dict(color=COLOR_ACCENT, width=2.5),
        marker=dict(size=7, color=COLOR_PRIMARY),
        fill="tozeroy",
        fillcolor="rgba(14,165,233,0.08)",
        hovertemplate="%{x}<br><b>%{y:.1%}</b><extra></extra>"
    ))
    fig_tend.add_hline(y=0.90, line_dash="dot", line_color=COLOR_SUCCESS,
                       annotation_text="Meta 90%", annotation_position="top right")
    fig_tend.update_layout(
        height=280, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="white", plot_bgcolor="white",
        yaxis=dict(tickformat=".0%", gridcolor="#F3F4F6", range=[0, 1.1]),
        xaxis=dict(gridcolor="#F3F4F6"),
        font=dict(family="sans-serif", size=11)
    )
    st.plotly_chart(fig_tend, use_container_width=True)

with c2:
    llegadas_plot = dff["Validador Llegada"].value_counts().reset_index()
    llegadas_plot.columns = ["Estado","Cantidad"]
    llegadas_plot = llegadas_plot[llegadas_plot["Estado"] != "No programado"]
    color_map = {
        "Llegada a tiempo": COLOR_SUCCESS,
        "Llegada antes":    COLOR_ACCENT,
        "Llegada tarde":    COLOR_WARNING,
        "Ausente":          COLOR_DANGER
    }
    fig_pie = px.pie(
        llegadas_plot, values="Cantidad", names="Estado",
        color="Estado", color_discrete_map=color_map,
        hole=0.55
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                          hovertemplate="%{label}<br><b>%{value}</b> registros<extra></extra>")
    fig_pie.update_layout(
        height=280, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family="sans-serif", size=10)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────────────────────────────
# COMPARATIVO POR SUPERVISOR
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-title'>👥 Comparativo por Supervisor</div>", unsafe_allow_html=True)

sup_stats = (
    dff_validos.groupby("Supervisor")
    .apply(lambda g: pd.Series({
        "ADH":      g["adh_s"].sum() / g["prog_s"].sum() if g["prog_s"].sum() > 0 else 0,
        "Agentes":  g["Nombre"].nunique(),
        "Registros": len(g)
    }))
    .reset_index()
    .sort_values("ADH", ascending=True)
)

aus_sup = dff[dff["Validador Llegada"] == "Ausente"].groupby("Supervisor").size().reset_index(name="Ausentes")
tarde_sup = dff[dff["Validador Llegada"] == "Llegada tarde"].groupby("Supervisor").size().reset_index(name="Tardes")
sup_stats = sup_stats.merge(aus_sup, on="Supervisor", how="left").merge(tarde_sup, on="Supervisor", how="left")
sup_stats["Ausentes"] = sup_stats["Ausentes"].fillna(0).astype(int)
sup_stats["Tardes"]   = sup_stats["Tardes"].fillna(0).astype(int)

c_bar, c_gauge = st.columns([3, 2])

with c_bar:
    sup_stats["Color"] = sup_stats["ADH"].apply(
        lambda x: COLOR_SUCCESS if x >= 0.90 else (COLOR_WARNING if x >= 0.80 else COLOR_DANGER)
    )
    sup_short = sup_stats.copy()
    sup_short["Supervisor"] = sup_short["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))

    fig_bar = go.Figure(go.Bar(
        x=sup_stats["ADH"], y=sup_short["Supervisor"],
        orientation="h",
        marker_color=sup_stats["Color"],
        text=sup_stats["ADH"].apply(lambda x: f"{x:.1%}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Adherencia: %{x:.1%}<extra></extra>"
    ))
    fig_bar.add_vline(x=0.90, line_dash="dot", line_color=COLOR_PRIMARY,
                      annotation_text="Meta 90%")
    fig_bar.update_layout(
        height=380, margin=dict(l=0,r=60,t=10,b=0),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(tickformat=".0%", range=[0, 1.15], gridcolor="#F3F4F6"),
        yaxis=dict(gridcolor="#F3F4F6"),
        font=dict(family="sans-serif", size=11)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c_gauge:
    st.markdown("**Tabla resumen por supervisor**")
    tabla_sup = sup_stats.sort_values("ADH", ascending=False)[
        ["Supervisor","ADH","Agentes","Ausentes","Tardes"]
    ].copy()
    tabla_sup["ADH"] = tabla_sup["ADH"].apply(lambda x: f"{x:.1%}")
    tabla_sup["Supervisor"] = tabla_sup["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
    tabla_sup.columns = ["Supervisor","ADH%","Agentes","Ausentes","Tardes"]
    st.dataframe(tabla_sup, use_container_width=True, hide_index=True, height=360)

# ─────────────────────────────────────────────
# GRÁFICAS POR SUPERVISOR (TENDENCIA)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-title'>📉 Tendencia por Supervisor</div>", unsafe_allow_html=True)

tend_sup = (
    dff_validos
    .groupby(["_periodo","Supervisor"])
    .apply(lambda g: g["adh_s"].sum() / g["prog_s"].sum() if g["prog_s"].sum() > 0 else 0)
    .reset_index(name="ADH")
)

sup_lista = sorted(tend_sup["Supervisor"].unique())
colores_sup = {s: SUPERVISOR_COLORS[i % len(SUPERVISOR_COLORS)] for i, s in enumerate(sup_lista)}

fig_sup = go.Figure()
for sup in sup_lista:
    sub = tend_sup[tend_sup["Supervisor"] == sup]
    nombre_corto = " ".join(sup.split()[:2])
    fig_sup.add_trace(go.Scatter(
        x=sub["_periodo"], y=sub["ADH"],
        name=nombre_corto,
        mode="lines+markers",
        line=dict(color=colores_sup[sup], width=1.8),
        marker=dict(size=5),
        hovertemplate=f"<b>{nombre_corto}</b><br>%{{x}}: %{{y:.1%}}<extra></extra>"
    ))
fig_sup.add_hline(y=0.90, line_dash="dot", line_color="#9CA3AF",
                  annotation_text="Meta 90%", annotation_position="top right")
fig_sup.update_layout(
    height=320, margin=dict(l=0,r=0,t=10,b=0),
    paper_bgcolor="white", plot_bgcolor="white",
    yaxis=dict(tickformat=".0%", gridcolor="#F3F4F6", range=[0, 1.2]),
    xaxis=dict(gridcolor="#F3F4F6"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
    font=dict(family="sans-serif", size=11)
)
st.plotly_chart(fig_sup, use_container_width=True)

# ─────────────────────────────────────────────
# DETALLE POR AGENTE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-title'>🔍 Detalle por Agente</div>", unsafe_allow_html=True)

excesos_min = [c for c in dff.columns if c.endswith("_min")]
agente_stats = (
    dff_validos.groupby(["Nombre","Supervisor","Campana"])
    .agg(
        ADH=("ADH_pct", "mean"),
        Dias=("Fecha", "nunique"),
        **{e.replace("_min",""): (e, lambda x: round(x.sum(), 1)) for e in excesos_min}
    )
    .reset_index()
    .sort_values("ADH", ascending=False)
)
agente_stats["ADH"] = agente_stats["ADH"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "-")

tard_ag = dff[dff["Validador Llegada"] == "Llegada tarde"].groupby("Nombre").size().reset_index(name="Tardanzas")
agente_stats = agente_stats.merge(tard_ag, on="Nombre", how="left")
agente_stats["Tardanzas"] = agente_stats["Tardanzas"].fillna(0).astype(int)

exceso_cols = [c.replace("_min","") for c in excesos_min]
cols_mostrar = ["Nombre","Supervisor","Campana","ADH","Dias","Tardanzas"] + exceso_cols

st.dataframe(
    agente_stats[cols_mostrar].rename(columns={
        "Nombre": "Agente", "Dias": "Días", "Campana": "Campaña",
        "Exceso Almuerzo": "Ex.Almuerzo", "Exceso Descanso": "Ex.Descanso",
        "Exceso Seguimiento": "Ex.Seguim.", "Exceso Toilette": "Ex.Toilette",
        "Exceso Entrenamiento": "Ex.Entrena.", "Exceso Feedback": "Ex.Feedback",
        "Exceso Calidad": "Ex.Calidad"
    }),
    use_container_width=True,
    hide_index=True,
    height=420
)

st.caption(f"📋 {len(agente_stats)} agentes · Excesos en minutos acumulados del período · Adherencia promedio de días trabajados")
