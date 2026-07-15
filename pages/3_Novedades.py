# v8
import streamlit as st
import pandas as pd
import base64
import io
import urllib.parse
import plotly.graph_objects as go
import plotly.io as pio
import streamlit.components.v1 as components
import holidays

_CO_FESTIVOS = holidays.country_holidays("CO")

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"

_LOGO_PATH = "logo-scala-learning-transformacion-digital-universidades.webp"

@st.cache_data(show_spinner=False)
def _excel_bytes(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()

def _df_descarga(df, nombre_archivo, **kwargs):
    st.dataframe(df, **kwargs)
    b64 = base64.b64encode(_excel_bytes(df)).decode()
    st.markdown(
        f'<div style="text-align:right;margin-top:-6px;margin-bottom:8px">'
        f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" '
        f'download="{nombre_archivo}" '
        f'style="font-size:0.72rem;color:rgba(255,255,255,0.35);text-decoration:none;letter-spacing:0.03em" '
        f'onmouseover="this.style.color=\'rgba(255,255,255,0.75)\'" '
        f'onmouseout="this.style.color=\'rgba(255,255,255,0.35)\'">'
        f'↓ Exportar Excel</a></div>',
        unsafe_allow_html=True,
    )

@st.cache_data(show_spinner=False)
def _cargar_logo():
    try:
        with open(_LOGO_PATH, "rb") as _f:
            return f"data:image/webp;base64,{base64.b64encode(_f.read()).decode()}"
    except FileNotFoundError:
        return ""

_logo_src = _cargar_logo()

# ─────────────────────────────────────────────
# CONEXIÓN GOOGLE SHEETS
# ─────────────────────────────────────────────
_SHEET_ID = "1-Ld6qxNvCl2g3u7_qmqnvljPoRYr_sgGyovGiOJ_Riw"

@st.cache_data(ttl=60, show_spinner=False)
def _cargar_hoja(nombre_hoja: str) -> pd.DataFrame:
    url = (
        f"https://docs.google.com/spreadsheets/d/{_SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(nombre_hoja)}"
    )
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame({"_error": [str(e)]})

@st.cache_data(ttl=60, show_spinner=False)
def _cargar_maestro_wfm() -> pd.DataFrame:
    """Timestamp de envío del experto y fechas de validación (supervisor y WFM), por ID Novedad."""
    df = _cargar_hoja("Novedades WFM")
    if "_error" in df.columns or df.empty or "ID" not in df.columns:
        return pd.DataFrame()
    out = df[["ID", "Timestamp", "Estado supervisor", "Fecha sup", "Estado WFM", "Fecha WFM"]].copy()
    out = out.rename(columns={"ID": "ID Novedad"})
    out["_ts_envio"] = pd.to_datetime(out["Timestamp"], dayfirst=True, errors="coerce")
    out["_fecha_sup"] = pd.to_datetime(out["Fecha sup"], dayfirst=True, errors="coerce")
    out["_fecha_wfm"] = pd.to_datetime(out["Fecha WFM"], dayfirst=True, errors="coerce")
    return out[["ID Novedad", "_ts_envio", "Estado supervisor", "_fecha_sup", "Estado WFM", "_fecha_wfm"]]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _fmt_fecha(v):
    try:
        return pd.to_datetime(v).strftime("%d/%m/%Y")
    except Exception:
        return str(v) if pd.notna(v) else "-"

def _kpi_bar(pct, color, max_val=100):
    fill = min(pct / max_val * 100, 100) if max_val else 0
    return (f"<div class='kpi-bar-wrap'>"
            f"<div class='kpi-bar-fill' style='width:{fill:.0f}%;background:{color};'></div>"
            f"</div>")

def _horas_habiles(inicio, fin):
    """Horas transcurridas entre dos timestamps, excluyendo domingos y festivos (Colombia)."""
    if pd.isna(inicio) or pd.isna(fin) or fin <= inicio:
        return 0.0
    total = 0.0
    cur = inicio
    fin_dia = cur.normalize() + pd.Timedelta(days=1)
    while fin_dia < fin:
        if cur.weekday() != 6 and cur.date() not in _CO_FESTIVOS:
            total += (fin_dia - cur).total_seconds() / 3600
        cur = fin_dia
        fin_dia = cur + pd.Timedelta(days=1)
    if cur.weekday() != 6 and cur.date() not in _CO_FESTIVOS:
        total += (fin - cur).total_seconds() / 3600
    return total

_MESES_ES = ["Todos","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

_DEMO = pd.DataFrame([
    {"ID Novedad":"WFM-ID-611977","Estado":"Aprobado supervisor","Nombre":"Laura Camila Sanchez Toro",  "Cédula":"1125230546","Supervisor":"Claudia Daniela Arevalo Martinez","Tipo de novedad":"Tiempo real",  "Novedad específica":"Falla de sistema",  "Fecha inicio":"01/07/2026","Hora inicio":"08:15","Fecha fin":"01/07/2026","Hora fin":"09:00","Horas":"0:45","Comentarios":"Equipo sin conectividad"},
    {"ID Novedad":"NOV-002",      "Estado":"Aprobado",           "Nombre":"Carlos Andrés Moreno",        "Cédula":"1098765432","Supervisor":"Johan Sebastian López",           "Tipo de novedad":"Planificación","Novedad específica":"Cambio de turno",    "Fecha inicio":"02/07/2026","Hora inicio":"07:00","Fecha fin":"02/07/2026","Hora fin":"15:00","Horas":"8:00","Comentarios":"Aprobado por coordinación"},
    {"ID Novedad":"NOV-003",      "Estado":"Rechazado",           "Nombre":"María Camila Torres",         "Cédula":"1023456789","Supervisor":"Zully Paola Rodríguez",          "Tipo de novedad":"Históricas",  "Novedad específica":"Permiso médico",     "Fecha inicio":"28/06/2026","Hora inicio":"10:00","Fecha fin":"28/06/2026","Hora fin":"14:00","Horas":"4:00","Comentarios":"Sin soporte adjunto"},
    {"ID Novedad":"NOV-004",      "Estado":"Aprobado",           "Nombre":"Andrés Felipe Gómez",         "Cédula":"1034567890","Supervisor":"Karen Julieth Barreto",           "Tipo de novedad":"Planificación","Novedad específica":"Licencia",           "Fecha inicio":"03/07/2026","Hora inicio":"06:00","Fecha fin":"05/07/2026","Hora fin":"15:00","Horas":"24:00","Comentarios":"Licencia por calamidad"},
    {"ID Novedad":"NOV-005",      "Estado":"Pendiente",           "Nombre":"Valentina Herrera Cruz",      "Cédula":"1045678901","Supervisor":"Camila Maldonado",               "Tipo de novedad":"Tiempo real",  "Novedad específica":"Ausente",            "Fecha inicio":"01/07/2026","Hora inicio":"06:55","Fecha fin":"01/07/2026","Hora fin":"15:00","Horas":"8:05","Comentarios":"No se reportó"},
    {"ID Novedad":"NOV-006",      "Estado":"Aprobado",           "Nombre":"Diego Fernando Ruiz",         "Cédula":"1056789012","Supervisor":"Ana Milena Carvajal",             "Tipo de novedad":"Históricas",  "Novedad específica":"Retiro",             "Fecha inicio":"25/06/2026","Hora inicio":"06:00","Fecha fin":"25/06/2026","Hora fin":"15:00","Horas":"9:00","Comentarios":"Procesado en nómina"},
])

# ─────────────────────────────────────────────
# GRÁFICOS
# ─────────────────────────────────────────────
_ESTADO_COLOR = {
    "Pendiente":           "#F59E0B",
    "Aprobado supervisor": "#10B981",
    "Aprobado":            "#10B981",
    "Rechazado":           "#EF4444",
    "Aprobado WFM":        "#38BDF8",
    "Rechazado supervisor":"#F87171",
}
_ESTADO_ORDER = ["Aprobado WFM", "Aprobado supervisor", "Aprobado", "Pendiente", "Rechazado", "Rechazado supervisor"]

_TIPO_COLOR = {
    "Tiempo real":   "#EF4444",
    "Planificación": "#38BDF8",
    "Históricas":    "#34D399",
}

_DARK_BG = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")


def _chart_por_supervisor(df):
    if "Supervisor" not in df.columns or "Estado" not in df.columns or df.empty:
        return
    grp   = df.groupby(["Supervisor", "Estado"]).size().reset_index(name="n")
    tot_por_sup = grp.groupby("Supervisor")["n"].sum()
    sups  = tot_por_sup.sort_values(ascending=True).index.tolist()
    uniq  = grp["Estado"].unique().tolist()
    orden = [e for e in _ESTADO_ORDER if e in uniq] + [e for e in uniq if e not in _ESTADO_ORDER]

    # Cada supervisor ocupa 30px → barras delgadas y juntas; iframe fijo 350px con scroll
    fig_h = max(320, len(sups) * 30 + 70)
    x_max = tot_por_sup.max() * 1.22 if not tot_por_sup.empty else 1

    fig = go.Figure()
    for estado in orden:
        sub  = grp[grp["Estado"] == estado].set_index("Supervisor")["n"]
        vals = [int(sub.get(s, 0)) for s in sups]
        fig.add_trace(go.Bar(
            name=estado, y=sups, x=vals, orientation="h",
            marker=dict(
                color=_ESTADO_COLOR.get(estado, "#64748B"),
                line=dict(color="rgba(8,6,15,0.85)", width=1.4),
                opacity=0.90,
                cornerradius=4,
            ),
            width=0.55,
            hovertemplate="<b>%{y}</b><br>" + estado + ": <b>%{x}</b><extra></extra>",
        ))

    # Etiqueta de total al final de cada barra apilada
    for s, t in tot_por_sup.items():
        fig.add_annotation(
            x=t, y=s, xref="x", yref="y", xanchor="left", yanchor="middle", xshift=8,
            text=f"<b>{int(t)}</b>", showarrow=False,
            font=dict(family="Space Grotesk, sans-serif", size=11, color="rgba(255,255,255,0.72)"),
        )

    fig.update_layout(
        **_DARK_BG,
        barmode="stack",
        bargap=0.42,
        height=fig_h,
        margin=dict(l=180, r=120, t=10, b=10),
        font=dict(family="Inter, sans-serif"),
        legend=dict(
            orientation="v",
            yanchor="top", y=1.0,
            xanchor="left", x=1.02,
            font=dict(size=10, color="rgba(255,255,255,0.55)"),
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.08)", borderwidth=1,
            traceorder="reversed",
        ),
        xaxis=dict(
            range=[0, x_max],
            showgrid=True, gridcolor="rgba(255,255,255,0.05)", gridwidth=1,
            zeroline=False,
            tickfont=dict(color="rgba(255,255,255,0.32)", size=9),
            showline=False, fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color="rgba(255,255,255,0.70)", size=10),
            automargin=False,
        ),
    )

    plot_div = pio.to_html(
        fig, include_plotlyjs="cdn", full_html=False,
        config={"displayModeBar": False},
    )
    components.html(
        f"""<!DOCTYPE html><html><head>
        <style>
          html,body{{margin:0;padding:0;background:transparent;overflow-x:hidden;}}
          ::-webkit-scrollbar{{width:5px;}}
          ::-webkit-scrollbar-track{{background:rgba(255,255,255,0.04);}}
          ::-webkit-scrollbar-thumb{{background:rgba(56,189,248,0.40);border-radius:99px;}}
        </style></head>
        <body>{plot_div}</body></html>""",
        height=350,
        scrolling=True,
    )


_ESTADO_GLOW = {
    "Pendiente":            "rgba(245,158,11,0.72)",
    "Aprobado supervisor":  "rgba(16,185,129,0.72)",
    "Aprobado":             "rgba(16,185,129,0.72)",
    "Aprobado WFM":         "rgba(56,189,248,0.72)",
    "Rechazado":            "rgba(239,68,68,0.72)",
    "Rechazado supervisor": "rgba(248,113,113,0.68)",
}

def _chart_por_tipo(df):
    if "Estado" not in df.columns or df.empty:
        return

    grp   = df.groupby("Estado").size().reset_index(name="n")
    grp   = grp.sort_values("n", ascending=False)
    total = int(grp["n"].sum()) or 1
    labels = grp["Estado"].tolist()
    vals   = grp["n"].tolist()
    colors = [_ESTADO_GLOW.get(e, "rgba(100,116,139,0.65)") for e in labels]

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[""] * len(labels),
        values=vals,
        marker=dict(
            colors=colors,
            line=dict(color="rgba(6,4,12,1)", width=4),
            pad=dict(t=28, l=4, r=4, b=4),
        ),
        texttemplate=(
            "<b style='font-size:14px'>%{label}</b><br>"
            "<span style='font-size:20px;font-weight:900'>%{value}</span>"
            "<span style='font-size:11px'>  ·  %{percentRoot:.0%}</span>"
        ),
        textposition="middle center",
        textfont=dict(color="rgba(255,255,255,0.92)", family="Inter, sans-serif"),
        hovertemplate="<b>%{label}</b><br>%{value} novedades · %{percentRoot:.1%}<extra></extra>",
        tiling=dict(packing="squarify", pad=4),
    ))

    fig.update_layout(
        **_DARK_BG,
        height=320,
        margin=dict(l=0, r=0, t=0, b=0),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


_SLA_ZONAS = [
    (0, 24, COLOR_SUCCESS, "A tiempo"),
    (24, 48, COLOR_WARNING, "Alerta"),
    (48, None, COLOR_DANGER, "Crítico"),
]
_PCT_ZONAS = [
    (0, 10, COLOR_SUCCESS, "Bajo"),
    (10, 25, COLOR_WARNING, "Moderado"),
    (25, None, COLOR_DANGER, "Alto"),
]


def _sla_meta(horas):
    """(color, icono, etiqueta) para horas hábiles transcurridas. SLA óptimo: 24 h."""
    if horas <= 0:
        return COLOR_SUCCESS, "🆕", "Hoy"
    elif horas <= 24:
        return COLOR_WARNING, "⏳", f"{horas:.0f} h"
    return COLOR_DANGER, "🚨", f"{horas:.0f} h"


def _pct_meta(pct):
    """(color, icono, etiqueta) para una tasa de rechazo (%)."""
    if pct <= 10:
        return COLOR_SUCCESS, "✅", f"{pct:.0f}%"
    elif pct <= 25:
        return COLOR_WARNING, "⚠️", f"{pct:.0f}%"
    return COLOR_DANGER, "🔴", f"{pct:.0f}%"


def _kpis_tiempo(df, col_dias, col_pendiente, col_dias_pendiente=None, titulo_prom="Promedio validación",
                 titulo_criticos="Envejecimiento crítico", desc_criticos="Pendientes con 48+ horas"):
    """col_dias_pendiente permite usar una base distinta para el envejecimiento de los pendientes
    (p. ej. el reloj de una cola empieza a correr en un momento distinto al de la métrica de cierre)."""
    col_dias_pendiente = col_dias_pendiente or col_dias
    if col_dias not in df.columns:
        return
    validadas = df.loc[~df[col_pendiente], col_dias].dropna()
    pendientes = df.loc[df[col_pendiente], col_dias_pendiente].dropna()
    if validadas.empty and pendientes.empty:
        return

    total_val = len(validadas)
    a_tiempo = int((validadas <= 24).sum()) if total_val else 0
    pct_sla = (a_tiempo / total_val * 100) if total_val else 0.0
    prom_horas = validadas.mean() if total_val else 0.0
    criticos = int((pendientes >= 48).sum())

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_ACCENT}'>
            <div class='kpi-bg-icon'>🎯</div>
            <div>
                <div class='kpi-label'>SLA cumplido</div>
                <div class='kpi-value' style='color:#7DD3FC'>{pct_sla:.0f}%</div>
                <div class='kpi-sub'>Validadas dentro de SLA (24 h)</div>
            </div>
            {_kpi_bar(pct_sla, COLOR_ACCENT, 100)}
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_WARNING}'>
            <div class='kpi-bg-icon'>⏱️</div>
            <div>
                <div class='kpi-label'>{titulo_prom}</div>
                <div class='kpi-value' style='color:{COLOR_WARNING}'>{prom_horas:.1f}<span style='font-size:16px'>h</span></div>
                <div class='kpi-sub'>Horas hábiles · casos ya validados</div>
            </div>
            {_kpi_bar(prom_horas, COLOR_WARNING, max(prom_horas, 48))}
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_DANGER}'>
            <div class='kpi-bg-icon'>🚨</div>
            <div>
                <div class='kpi-label'>{titulo_criticos}</div>
                <div class='kpi-value' style='color:{COLOR_DANGER}'>{criticos}</div>
                <div class='kpi-sub'>{desc_criticos}</div>
            </div>
            {_kpi_bar(criticos, COLOR_DANGER, max(len(pendientes), 1))}
        </div>""", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)


def _chart_ranking_zonas(valores, zonas, meta_fn, eje_titulo, value_fmt, alto_fila=36):
    """Ranking horizontal genérico: barras delgadas redondeadas + zonas de contexto sombreadas."""
    if valores is None or valores.empty:
        return
    valores = valores.sort_values(ascending=True)
    cats = valores.index.tolist()
    vals = valores.tolist()
    colors = [meta_fn(v)[0] for v in vals]
    tope = zonas[-1][1] if zonas[-1][1] is not None else zonas[-1][0] + 1
    x_max = max(vals + [tope]) * 1.22

    fig = go.Figure(go.Bar(
        y=cats, x=vals, orientation="h",
        marker=dict(color=colors, opacity=0.92, line=dict(width=0), cornerradius=6),
        width=0.55,
        text=[value_fmt(v) for v in vals],
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.78)", size=11, family="Space Grotesk, sans-serif"),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>" + eje_titulo + ": <b>%{x}</b><extra></extra>",
    ))

    # Zonas de contexto como washes de fondo (~8% opacidad), dibujadas antes que las barras
    for x0, x1, color, _ in zonas:
        fig.add_vrect(
            x0=x0, x1=x1 if x1 is not None else x_max,
            fillcolor=color, opacity=0.07, line_width=0, layer="below",
        )
    for x0, x1, color, label in zonas:
        centro = (x0 + (x1 if x1 is not None else x_max)) / 2
        fig.add_annotation(
            x=centro, y=1.06, xref="x", yref="paper", showarrow=False,
            text=label.upper(), font=dict(size=8, color=color, family="Inter, sans-serif"),
            opacity=0.55,
        )

    fig_h = max(260, len(cats) * alto_fila + 70)
    fig.update_layout(
        **_DARK_BG,
        height=fig_h,
        margin=dict(l=190, r=60, t=34, b=10),
        font=dict(family="Inter, sans-serif"),
        showlegend=False,
        bargap=0.42,
        xaxis=dict(
            range=[0, x_max],
            showgrid=True, gridcolor="rgba(255,255,255,0.045)", gridwidth=1, zeroline=False,
            tickfont=dict(color="rgba(255,255,255,0.32)", size=9), fixedrange=True,
            title=dict(text=eje_titulo, font=dict(size=10, color="rgba(255,255,255,0.35)")),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(color="rgba(255,255,255,0.72)", size=10.5), fixedrange=True),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _iniciales(nombre):
    partes = str(nombre).strip().split()
    if not partes:
        return "?"
    return (partes[0][0] + (partes[1][0] if len(partes) > 1 else "")).upper()


def _lista_pendientes(df, col_pendiente, col_dias, meta_fn=_sla_meta):
    if col_pendiente not in df.columns:
        return
    pend = df[df[col_pendiente]].copy()
    if pend.empty:
        return
    pend = pend.sort_values(col_dias, ascending=False).head(8)

    filas = []
    for i, (_, row) in enumerate(pend.iterrows(), start=1):
        nombre = row.get("Nombre", "—")
        supervisor = row.get("Supervisor", "—")
        id_nov = row.get("ID Novedad", "—")
        color, icono, etiqueta = meta_fn(row[col_dias])
        filas.append(f"""
        <div class='verif-row' style='--vc:{color}'>
            <span class='verif-rank'>{i:02d}</span>
            <div class='verif-avatar'>{_iniciales(nombre)}</div>
            <div class='verif-body'>
                <div class='verif-name'>{nombre}</div>
                <div class='verif-sup'>👤 {supervisor}</div>
            </div>
            <span class='verif-id'>{id_nov}</span>
            <span class='verif-badge' style='background:{color}22;color:{color};border:1px solid {color}55'>
                {icono} {etiqueta}
            </span>
        </div>""")

    st.markdown(f"<div class='verif-list'>{''.join(filas)}</div>", unsafe_allow_html=True)


def _chart_tendencia(df):
    """Línea semanal comparando el tiempo de verificación del supervisor vs. el ciclo completo (WFM)."""
    if "_ts_envio" not in df.columns:
        return
    base = df.dropna(subset=["_ts_envio"]).copy()
    if base.empty:
        return
    base["_semana"] = base["_ts_envio"].dt.to_period("W").apply(lambda p: p.start_time)

    serie_sup = (base.dropna(subset=["_horas_verif"]).groupby("_semana")["_horas_verif"].mean()
                 if "_horas_verif" in base.columns else pd.Series(dtype=float))
    serie_ciclo = (base.dropna(subset=["_horas_ciclo"]).groupby("_semana")["_horas_ciclo"].mean()
                   if "_horas_ciclo" in base.columns else pd.Series(dtype=float))
    if serie_sup.empty and serie_ciclo.empty:
        return

    fig = go.Figure()
    if not serie_sup.empty:
        fig.add_trace(go.Scatter(
            x=serie_sup.index, y=serie_sup.values, mode="lines+markers", name="Verificación supervisor",
            line=dict(color=COLOR_ACCENT, width=2),
            marker=dict(size=8, color=COLOR_ACCENT, line=dict(color="rgba(8,6,15,0.85)", width=1.5)),
            hovertemplate="Semana %{x|%d/%m}<br>Supervisor: <b>%{y:.0f} h</b><extra></extra>",
        ))
    if not serie_ciclo.empty:
        fig.add_trace(go.Scatter(
            x=serie_ciclo.index, y=serie_ciclo.values, mode="lines+markers", name="Ciclo completo (WFM)",
            line=dict(color=COLOR_DANGER, width=2),
            marker=dict(size=8, color=COLOR_DANGER, line=dict(color="rgba(8,6,15,0.85)", width=1.5)),
            hovertemplate="Semana %{x|%d/%m}<br>Ciclo completo: <b>%{y:.0f} h</b><extra></extra>",
        ))
    fig.update_layout(
        **_DARK_BG,
        height=300,
        margin=dict(l=50, r=20, t=10, b=40),
        font=dict(family="Inter, sans-serif"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
            font=dict(size=10, color="rgba(255,255,255,0.60)"), bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=False, tickfont=dict(color="rgba(255,255,255,0.35)", size=9), fixedrange=True, tickformat="%d/%m"),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False,
            tickfont=dict(color="rgba(255,255,255,0.32)", size=9), fixedrange=True,
            title=dict(text="Horas promedio", font=dict(size=10, color="rgba(255,255,255,0.35)")),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _tasa_rechazo(df, columna, min_casos=3):
    """% de rechazo por categoría (solo casos ya finalizados), descartando categorías con pocos casos."""
    if "_finalizada" not in df.columns or columna not in df.columns:
        return None
    base = df[df["_finalizada"]]
    if base.empty:
        return None
    g = base.groupby(columna)["_rechazada"].agg(["mean", "size"])
    g = g[g["size"] >= min_casos]
    if g.empty:
        return None
    return (g["mean"] * 100).rename(None)


# ─────────────────────────────────────────────
# RENDER TAB
# ─────────────────────────────────────────────
def _render_tab(df: pd.DataFrame, sup_sel, exp_sel, buscar, fecha_desde, fecha_hasta, agrupar, periodo_sel):
    if "_error" in df.columns:
        st.error(f"No se pudo cargar la hoja: {df['_error'].iloc[0]}")
        return

    es_demo = df.empty
    if es_demo:
        df = _DEMO.copy()
        st.markdown(
            "<div style='background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.30);"
            "border-radius:12px;padding:10px 16px;margin-bottom:16px;font-size:12px;"
            "color:rgba(255,255,255,0.70);display:flex;align-items:center;gap:8px'>"
            "<span style='font-size:16px'>👁️</span>"
            "<span><b style='color:#F59E0B'>Vista previa</b> — datos de muestra. "
            "Cuando registres novedades en el Sheet aparecerán aquí automáticamente.</span>"
            "</div>",
            unsafe_allow_html=True
        )

    df = df.copy()
    if not es_demo and not df_maestro.empty and "ID Novedad" in df.columns:
        df = df.merge(df_maestro, on="ID Novedad", how="left")
        _hoy = pd.Timestamp.now()
        _env = df["_ts_envio"]
        _estado_sup = df["Estado supervisor"].astype(str).str.strip()
        _validado = (
            _estado_sup.str.contains("Aprobado", case=False, na=False)
            | _estado_sup.str.contains("Rechazado", case=False, na=False)
        )
        df["_pendiente_sup"] = (~_validado) & _env.notna()
        df["_horas_verif"] = pd.NA
        _mask_val = _validado & df["_fecha_sup"].notna() & _env.notna()
        df.loc[_mask_val, "_horas_verif"] = df.loc[_mask_val].apply(
            lambda r: _horas_habiles(r["_ts_envio"], r["_fecha_sup"]), axis=1)
        _mask_pend = df["_pendiente_sup"]
        df.loc[_mask_pend, "_horas_verif"] = df.loc[_mask_pend, "_ts_envio"].apply(
            lambda t: _horas_habiles(t, _hoy))
        df["_horas_verif"] = pd.to_numeric(df["_horas_verif"], errors="coerce")

        # Ciclo completo (envío → decisión final de WFM)
        _estado_wfm = df["Estado WFM"].astype(str).str.strip()
        _validado_wfm = (
            _estado_wfm.str.contains("Aprobado", case=False, na=False)
            | _estado_wfm.str.contains("Rechazado", case=False, na=False)
        )
        _aprobada_sup = _estado_sup.str.contains("Aprobado", case=False, na=False)
        df["_pendiente_wfm"] = _aprobada_sup & (~_validado_wfm) & _env.notna()
        df["_horas_ciclo"] = pd.NA
        _mask_ciclo_val = _validado_wfm & df["_fecha_wfm"].notna() & _env.notna()
        df.loc[_mask_ciclo_val, "_horas_ciclo"] = df.loc[_mask_ciclo_val].apply(
            lambda r: _horas_habiles(r["_ts_envio"], r["_fecha_wfm"]), axis=1)
        _mask_ciclo_pend = df["_pendiente_wfm"]
        df.loc[_mask_ciclo_pend, "_horas_ciclo"] = df.loc[_mask_ciclo_pend, "_ts_envio"].apply(
            lambda t: _horas_habiles(t, _hoy))
        df["_horas_ciclo"] = pd.to_numeric(df["_horas_ciclo"], errors="coerce")

        # Horas en cola de WFM: se cuentan desde que el supervisor respondió (Fecha sup),
        # no desde el envío original del experto — así refleja el tiempo real de espera en WFM.
        _inicio_cola = df["_fecha_sup"].where(df["_fecha_sup"].notna(), _env)
        df["_horas_cola_wfm"] = pd.NA
        _mask_cola = df["_pendiente_wfm"] & _inicio_cola.notna()
        df.loc[_mask_cola, "_horas_cola_wfm"] = _inicio_cola[_mask_cola].apply(
            lambda t: _horas_habiles(t, _hoy))
        df["_horas_cola_wfm"] = pd.to_numeric(df["_horas_cola_wfm"], errors="coerce")

        # Rechazo final (en cualquiera de las dos etapas)
        _rechazada_sup = _estado_sup.str.contains("Rechazado", case=False, na=False)
        _rechazada_wfm = _estado_wfm.str.contains("Rechazado", case=False, na=False)
        df["_rechazada"] = _rechazada_sup | _rechazada_wfm
        df["_finalizada"] = df["_rechazada"] | _validado_wfm

    if "Fecha inicio" in df.columns:
        # Intentar ISO (2026-07-01) y USA (7/1/2026) — ambos sin dayfirst
        _parsed = pd.to_datetime(df["Fecha inicio"], errors="coerce", dayfirst=False)
        # Para celdas que no se parsearon, intentar con dayfirst=True (DD/MM/YYYY)
        _null = _parsed.isna()
        if _null.any():
            _parsed[_null] = pd.to_datetime(df.loc[_null, "Fecha inicio"], errors="coerce", dayfirst=True)
        df["_fecha_dt"] = _parsed
    else:
        df["_fecha_dt"] = pd.NaT

    if fecha_desde:
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.date >= fecha_desde)]
    if fecha_hasta:
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.date <= fecha_hasta)]

    if agrupar == "Mes" and periodo_sel and periodo_sel != "Todos":
        mes_num = _MESES_ES.index(periodo_sel)
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.month == mes_num)]
    elif agrupar == "Semana" and periodo_sel and periodo_sel != "Todas":
        try:
            sem_n = int(periodo_sel.split()[-1])
            df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.isocalendar().week == sem_n)]
        except Exception:
            pass
    elif agrupar == "Trimestre" and periodo_sel and periodo_sel != "Todos":
        _tri_map = {"T1 (Ene–Mar)": [1,2,3], "T2 (Abr–Jun)": [4,5,6],
                    "T3 (Jul–Sep)": [7,8,9],  "T4 (Oct–Dic)": [10,11,12]}
        meses_tri = _tri_map.get(periodo_sel, [])
        if meses_tri:
            df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.month.isin(meses_tri))]
    elif agrupar == "Semestre" and periodo_sel and periodo_sel != "Todos":
        meses_sem = [1,2,3,4,5,6] if "S1" in periodo_sel else [7,8,9,10,11,12]
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.month.isin(meses_sem))]

    if sup_sel != "Todos" and "Supervisor" in df.columns:
        df = df[df["Supervisor"] == sup_sel]
    if exp_sel != "Todos" and "Nombre" in df.columns:
        df = df[df["Nombre"] == exp_sel]
    if buscar and "ID Novedad" in df.columns:
        df = df[df["ID Novedad"].astype(str).str.strip().str.upper() == buscar.strip().upper()]

    for c in ["Fecha inicio", "Fecha fin", "Fecha procesamiento"]:
        if c in df.columns:
            df[c] = df[c].apply(_fmt_fecha)
    df = df.drop(columns=["_fecha_dt"], errors="ignore")

    # ── KPIs ─────────────────────────────────────────
    total = len(df)
    if "Estado" in df.columns:
        estados = df["Estado"].astype(str).str.strip()
        pend = estados.str.contains("Pendiente", case=False).sum()
        apro = estados.str.contains("Aprobado", case=False).sum()
        rech = estados.str.contains("Rechazado", case=False).sum()
    else:
        pend = apro = rech = 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_ACCENT}'>
            <div class='kpi-bg-icon'>📋</div>
            <div>
                <div class='kpi-label'>Total</div>
                <div class='kpi-value' style='color:#7DD3FC'>{total}</div>
                <div class='kpi-sub'>Novedades registradas</div>
            </div>
            {_kpi_bar(total, COLOR_ACCENT, max(total, 1))}
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_WARNING}'>
            <div class='kpi-bg-icon'>⏳</div>
            <div>
                <div class='kpi-label'>Pendientes</div>
                <div class='kpi-value' style='color:{COLOR_WARNING}'>{pend}</div>
                <div class='kpi-sub'>Sin gestionar</div>
            </div>
            {_kpi_bar(pend, COLOR_WARNING, max(total, 1))}
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_SUCCESS}'>
            <div class='kpi-bg-icon'>✅</div>
            <div>
                <div class='kpi-label'>Aprobados</div>
                <div class='kpi-value' style='color:{COLOR_SUCCESS}'>{apro}</div>
                <div class='kpi-sub'>Novedad aprobada</div>
            </div>
            {_kpi_bar(apro, COLOR_SUCCESS, max(total, 1))}
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_DANGER}'>
            <div class='kpi-bg-icon'>❌</div>
            <div>
                <div class='kpi-label'>Rechazados</div>
                <div class='kpi-value' style='color:{COLOR_DANGER}'>{rech}</div>
                <div class='kpi-sub'>Novedad rechazada</div>
            </div>
            {_kpi_bar(rech, COLOR_DANGER, max(total, 1))}
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # ── Gráfico 1: novedades por supervisor ───────────
    st.markdown(
        "<div style='font-size:10px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;"
        "color:rgba(255,255,255,0.35);margin-bottom:6px'>"
        "<span style='display:inline-block;width:18px;height:2px;background:#38BDF8;"
        "border-radius:2px;vertical-align:middle;margin-right:8px'></span>"
        "Novedades por supervisor</div>",
        unsafe_allow_html=True,
    )
    _chart_por_supervisor(df)

    # ── Gráfico 2: tiempo de verificación por supervisor ──
    if "_horas_verif" in df.columns:
        st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
        n_sup_verif = df.loc[~df["_horas_verif"].isna(), "Supervisor"].nunique()
        st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_PRIMARY} 0%,{COLOR_WARNING} 100%)'>
            <span class='tbl-hdr-icon'>⏱️</span>
            <div class='tbl-hdr-body'>
                <div class='tbl-hdr-title'>Tiempo de Verificación por Supervisor</div>
                <div class='tbl-hdr-desc'>Horas hábiles desde el envío del experto hasta la validación · SLA: 24 h (excluye domingos y festivos)</div>
            </div>
            <span class='tbl-hdr-badge'>{n_sup_verif} supervisores</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
        _kpis_tiempo(df, "_horas_verif", "_pendiente_sup")
        _chart_ranking_zonas(
            df.dropna(subset=["_horas_verif"]).groupby("Supervisor")["_horas_verif"].mean(),
            _SLA_ZONAS, _sla_meta, "Horas promedio de validación", lambda v: f"{v:.0f} h",
        )

        n_pend = int(df["_pendiente_sup"].sum())
        if n_pend:
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_DANGER} 0%,{COLOR_PRIMARY} 100%)'>
                <span class='tbl-hdr-icon'>🚨</span>
                <div class='tbl-hdr-body'>
                    <div class='tbl-hdr-title'>Pendientes Más Antiguas</div>
                    <div class='tbl-hdr-desc'>Novedades esperando validación del supervisor</div>
                </div>
                <span class='tbl-hdr-badge'>{n_pend} pendientes</span>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
            _lista_pendientes(df, "_pendiente_sup", "_horas_verif", _sla_meta)

    # ── Gráfico 3: ciclo completo (experto → supervisor → WFM) ──
    if "_horas_ciclo" in df.columns:
        st.markdown("<div style='margin-top:26px'></div>", unsafe_allow_html=True)
        n_sup_ciclo = df.loc[~df["_horas_ciclo"].isna(), "Supervisor"].nunique()
        st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_PRIMARY} 0%,{COLOR_ACCENT} 100%)'>
            <span class='tbl-hdr-icon'>🏁</span>
            <div class='tbl-hdr-body'>
                <div class='tbl-hdr-title'>Ciclo Completo · Experto → Supervisor → WFM</div>
                <div class='tbl-hdr-desc'>Horas hábiles desde el envío hasta la decisión final de WFM</div>
            </div>
            <span class='tbl-hdr-badge'>{n_sup_ciclo} supervisores</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
        _kpis_tiempo(
            df, "_horas_ciclo", "_pendiente_wfm", col_dias_pendiente="_horas_cola_wfm",
            titulo_prom="Promedio ciclo completo",
            titulo_criticos="Críticos en cola WFM",
            desc_criticos="En cola WFM con 48+ horas",
        )
        _chart_ranking_zonas(
            df.dropna(subset=["_horas_ciclo"]).groupby("Supervisor")["_horas_ciclo"].mean(),
            _SLA_ZONAS, _sla_meta, "Horas promedio del ciclo completo", lambda v: f"{v:.0f} h",
        )

        n_pend_wfm = int(df["_pendiente_wfm"].sum())
        if n_pend_wfm:
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_DANGER} 0%,{COLOR_ACCENT} 100%)'>
                <span class='tbl-hdr-icon'>📮</span>
                <div class='tbl-hdr-body'>
                    <div class='tbl-hdr-title'>Pendientes en Cola WFM</div>
                    <div class='tbl-hdr-desc'>Ya aprobadas por el supervisor, esperando decisión final</div>
                </div>
                <span class='tbl-hdr-badge'>{n_pend_wfm} pendientes</span>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
            _lista_pendientes(df, "_pendiente_wfm", "_horas_cola_wfm", _sla_meta)

    # ── Gráfico 4: tendencia temporal ──
    if "_horas_verif" in df.columns:
        st.markdown("<div style='margin-top:26px'></div>", unsafe_allow_html=True)
        st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_ACCENT} 0%,{COLOR_SUCCESS} 100%)'>
            <span class='tbl-hdr-icon'>📈</span>
            <div class='tbl-hdr-body'>
                <div class='tbl-hdr-title'>Tendencia Semanal de Verificación</div>
                <div class='tbl-hdr-desc'>¿El tiempo de validación mejora o empeora semana a semana?</div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
        _chart_tendencia(df)

    # ── Gráfico 5: tasa de rechazo ──
    if "_rechazada" in df.columns:
        rechazo_sup = _tasa_rechazo(df, "Supervisor")
        rechazo_tipo = _tasa_rechazo(df, "Novedad específica") if "Novedad específica" in df.columns else None
        if rechazo_sup is not None or rechazo_tipo is not None:
            st.markdown("<div style='margin-top:26px'></div>", unsafe_allow_html=True)
            n_final = int(df["_finalizada"].sum())
            pct_global = (df.loc[df["_finalizada"], "_rechazada"].mean() * 100) if n_final else 0.0
            st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_DANGER} 0%,{COLOR_WARNING} 100%)'>
                <span class='tbl-hdr-icon'>🚫</span>
                <div class='tbl-hdr-body'>
                    <div class='tbl-hdr-title'>Tasa de Rechazo</div>
                    <div class='tbl-hdr-desc'>% de novedades rechazadas sobre casos ya finalizados</div>
                </div>
                <span class='tbl-hdr-badge'>{pct_global:.0f}% global</span>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

            if rechazo_sup is not None:
                st.markdown(_sec_label("Por supervisor", COLOR_DANGER), unsafe_allow_html=True)
                _chart_ranking_zonas(rechazo_sup, _PCT_ZONAS, _pct_meta, "% de rechazo", lambda v: f"{v:.0f}%")
            if rechazo_tipo is not None:
                st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
                st.markdown(_sec_label("Por tipo de novedad · mín. 3 casos", COLOR_WARNING), unsafe_allow_html=True)
                _chart_ranking_zonas(rechazo_tipo, _PCT_ZONAS, _pct_meta, "% de rechazo", lambda v: f"{v:.0f}%")

    st.markdown("<div style='margin-top:26px'></div>", unsafe_allow_html=True)
    # ── Tabla ─────────────────────────────────────────
    _COLS = [c for c in [
        "ID Novedad", "Estado", "Nombre", "Cédula", "Supervisor",
        "Tipo de novedad", "Novedad específica",
        "Fecha inicio", "Hora inicio", "Fecha fin", "Hora fin",
        "Horas", "Comentarios",
    ] if c in df.columns]

    st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_PRIMARY} 0%,{COLOR_ACCENT} 100%)'>
        <span class='tbl-hdr-icon'>📋</span>
        <div class='tbl-hdr-body'>
            <div class='tbl-hdr-title'>Registro de Novedades</div>
            <div class='tbl-hdr-desc'>Detalle completo · filtros aplicados desde el panel lateral</div>
        </div>
        <span class='tbl-hdr-badge'>{total} registros</span>
    </div>""", unsafe_allow_html=True)

    _df_descarga(
        df[_COLS].reset_index(drop=True),
        "novedades_operativas.xlsx",
        use_container_width=True,
        hide_index=True,
        height=350,
    )
    if es_demo:
        st.caption("👁️ Vista previa con datos de muestra — conectado a Google Sheets")
    else:
        st.caption(f"📋 {len(df)} registros · Google Sheets · recarga la página para actualizar")

    # ── Gráfico 3: novedades por tipo ─────────────────
    st.markdown(
        "<div style='font-size:10px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;"
        "color:rgba(255,255,255,0.35);margin-top:18px;margin-bottom:6px'>"
        "<span style='display:inline-block;width:18px;height:2px;background:#34D399;"
        "border-radius:2px;vertical-align:middle;margin-right:8px'></span>"
        "Distribución por tipo de novedad</div>",
        unsafe_allow_html=True,
    )
    _chart_por_tipo(df)

# ─────────────────────────────────────────────
# CARGAR DATOS
# ─────────────────────────────────────────────
df_rt   = _cargar_hoja("Tiempo real")
df_plan = _cargar_hoja("Planificación")
df_hist = _cargar_hoja("Históricas")
df_maestro = _cargar_maestro_wfm()

def _get_opts(col):
    vals = []
    for df in [df_rt, df_plan, df_hist]:
        if not df.empty and "_error" not in df.columns and col in df.columns:
            vals += df[col].dropna().astype(str).unique().tolist()
    return sorted(set(vals)) or (sorted(_DEMO[col].dropna().unique().tolist()) if col in _DEMO.columns else [])

_sups    = _get_opts("Supervisor")
_expertos = _get_opts("Nombre")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sbc'>
        <div class='sbc-orb sbc-orb-1'></div>
        <div class='sbc-orb sbc-orb-2'></div>
        <div class='sbc-orb sbc-orb-3'></div>
        <div class='sbc-live'><span class='sbc-pulse'></span>LIVE</div>
        <div class='sbc-body'>
            <div class='sbc-logo-wrap'><img src='{_logo_src}' class='sbc-logo-img' /></div>
            <div class='sbc-name'>Workforce Management</div>
            <div class='sbc-org'>Uniminuto &nbsp;·&nbsp; Scala Learning</div>
            <div class='sbc-stats'>
                <div class='sbc-stat'><span class='sbc-sv'>2026</span><span class='sbc-sl'>Año</span></div>
                <div class='sbc-sep'></div>
                <div class='sbc-stat'><span class='sbc-sv'>WFM</span><span class='sbc-sl'>Área</span></div>
                <div class='sbc-sep'></div>
                <div class='sbc-stat'><span class='sbc-sv'>COL</span><span class='sbc-sl'>País</span></div>
            </div>
        </div>
        <div class='sbc-bar'></div>
    </div>
    """, unsafe_allow_html=True)

    # ── 01 PERÍODO ──────────────────────────────────
    st.markdown("""<div class='sbh'>
        <div class='sbh-num' style='color:#38BDF8!important;background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.22)'>01</div>
        <div class='sbh-lbl'>Período</div>
        <div class='sbh-rule'></div>
    </div>""", unsafe_allow_html=True)

    agrupar = st.selectbox("Agrupar por", ["Día", "Semana", "Mes", "Trimestre", "Semestre"], key="sb_agrupar")

    periodo_sel = None
    if agrupar == "Mes":
        periodo_sel = st.selectbox("Mes", _MESES_ES, key="sb_mes")
    elif agrupar == "Semana":
        periodo_sel = st.selectbox("Semana", ["Todas"] + [f"Semana {i}" for i in range(1, 53)], key="sb_sem")
    elif agrupar == "Trimestre":
        periodo_sel = st.selectbox("Trimestre", ["Todos","T1 (Ene–Mar)","T2 (Abr–Jun)","T3 (Jul–Sep)","T4 (Oct–Dic)"], key="sb_tri")
    elif agrupar == "Semestre":
        periodo_sel = st.selectbox("Semestre", ["Todos","S1 (Ene–Jun)","S2 (Jul–Dic)"], key="sb_sem2")

    c1, c2 = st.columns(2)
    with c1:
        fecha_desde = st.date_input("Desde", value=None, key="sb_desde")
    with c2:
        fecha_hasta = st.date_input("Hasta", value=None, key="sb_hasta")

    # ── 02 FILTROS ───────────────────────────────────
    st.markdown("""<div class='sbh'>
        <div class='sbh-num' style='color:#34D399!important;background:rgba(52,211,153,0.12);border-color:rgba(52,211,153,0.22)'>02</div>
        <div class='sbh-lbl'>Filtros</div>
        <div class='sbh-rule'></div>
    </div>""", unsafe_allow_html=True)

    sup_sel  = st.selectbox("Supervisor", ["Todos"] + _sups,     key="sb_sup")
    exp_sel  = st.selectbox("Experto",    ["Todos"] + _expertos, key="sb_exp")
    buscar   = st.text_input("Buscar por ID", placeholder="WFM-ID-000000", key="sb_bus")

    if st.button("🔄  Actualizar datos", key="sb_refresh", use_container_width=True):
        _cargar_hoja.clear()
        st.rerun()

    # ── Usuario ──────────────────────────────────────
    st.markdown("""
    <div class='sbf'>
        <div class='sbf-card'>
            <div class='sbf-glow'></div>
            <div class='sbf-row'>
                <div class='sbf-avatar'>GC<span class='sbf-online'></span></div>
                <div class='sbf-info'>
                    <div class='sbf-name'>Guillermo Calderón</div>
                    <div class='sbf-role'>Analista WFM · Scala Learning</div>
                </div>
            </div>
        </div>
        <div class='sbf-credit'><span class='sbf-spark'>⚡</span>Desarrollado por Workforce Management</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS  (idéntico a Adherencia / Ocupación)
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}
    span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    .material-symbols-rounded, .material-symbols-outlined, .material-icons {{
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }}
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    [data-testid="stAppViewContainer"], .main {{
        background:
            radial-gradient(ellipse 90% 55% at 6% -6%,   rgba(14,165,233,0.16) 0%, transparent 55%),
            radial-gradient(ellipse 80% 55% at 100% 0%,  rgba(99,102,241,0.17) 0%, transparent 55%),
            radial-gradient(ellipse 75% 60% at 92% 100%, rgba(52,211,153,0.08) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 0% 100%,  rgba(99,102,241,0.07) 0%, transparent 55%),
            linear-gradient(160deg, #0A0813 0%, #0F0B20 45%, #08060F 100%);
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}

    [data-testid="stSidebarCollapseButton"] button,
    div[data-testid="collapsedControl"] button {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important; transition: all .2s ease !important;
    }}
    div[data-testid="collapsedControl"] button {{
        background: rgba(40,5,63,0.06) !important;
        border: 1px solid rgba(40,5,63,0.15) !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover,
    div[data-testid="collapsedControl"] button:hover {{
        border-color: rgba(14,165,233,0.45) !important;
    }}
    [data-testid="stSidebarCollapseButton"] span {{ color: rgba(255,255,255,0.80) !important; font-size:20px !important; }}
    div[data-testid="collapsedControl"] span {{ color: {COLOR_PRIMARY} !important; font-size:20px !important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important; box-sizing:border-box!important; padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: linear-gradient(160deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 100%);
        border-radius: 20px; padding: 22px 22px 18px;
        box-shadow: 0 20px 44px -18px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        position: relative; overflow: hidden;
        min-height: 148px; display: flex; flex-direction: column; justify-content: space-between;
        border: 1px solid rgba(255,255,255,0.10);
        transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
        cursor: default;
    }}
    .kpi-card:hover {{
        transform: translateY(-6px);
        border-color: var(--kc, {COLOR_ACCENT});
        box-shadow: 0 30px 60px -22px rgba(0,0,0,0.8), 0 0 36px -12px var(--kc, {COLOR_ACCENT}), inset 0 1px 0 rgba(255,255,255,0.10);
    }}
    .kpi-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: var(--kc, {COLOR_PRIMARY}); box-shadow: 0 0 18px -2px var(--kc, {COLOR_PRIMARY});
    }}
    .kpi-card::after {{
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 120px; height: 120px;
        background: radial-gradient(circle, var(--kc, {COLOR_PRIMARY}), transparent 70%);
        opacity: 0.22; border-radius: 50%;
    }}
    .kpi-bg-icon {{
        position: absolute; bottom: 12px; right: 16px;
        font-size: 46px; opacity: 0.10; line-height: 1; pointer-events: none; z-index: 0;
    }}
    .kpi-label {{ font-size: 10px; color: rgba(255,255,255,0.50); font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; position: relative; z-index: 1; }}
    .kpi-value {{ font-family:'Space Grotesk',sans-serif!important; font-size: 34px; font-weight: 700; line-height: 1.1; margin: 10px 0 4px; position: relative; z-index: 1; letter-spacing:-0.5px; text-shadow:0 2px 16px rgba(0,0,0,0.4); }}
    .kpi-sub   {{ font-size: 11px; color: rgba(255,255,255,0.42); position: relative; z-index: 1; }}
    .kpi-bar-wrap {{ background: rgba(255,255,255,0.09); border-radius: 99px; height: 5px; margin-top: 12px; overflow: hidden; position: relative; z-index: 1; }}
    .kpi-bar-fill {{ height: 5px; border-radius: 99px; box-shadow:0 0 10px -1px currentColor; }}

    /* ── Table headers ── */
    .tbl-hdr {{
        padding: 14px 20px; border-radius: 14px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 6px; box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        position: relative; overflow: hidden;
    }}
    .tbl-hdr::before {{ content:''; position:absolute; left:-10px; top:-10px; width:60px; height:60px; background:rgba(255,255,255,0.08); border-radius:50%; }}
    .tbl-hdr::after  {{ content:''; position:absolute; right:-20px; bottom:-20px; width:80px; height:80px; background:rgba(255,255,255,0.10); border-radius:50%; }}
    .tbl-hdr-icon  {{ font-size:24px; flex-shrink:0; position:relative; z-index:1; }}
    .tbl-hdr-body  {{ flex:1; position:relative; z-index:1; }}
    .tbl-hdr-title {{ font-size:14px; font-weight:800; color:white; margin:0 0 2px; letter-spacing:-0.2px; }}
    .tbl-hdr-desc  {{ font-size:11px; color:rgba(255,255,255,0.72); margin:0; }}
    .tbl-hdr-badge {{ font-size:10px; font-weight:700; color:white; background:rgba(255,255,255,0.20); border:1px solid rgba(255,255,255,0.35); padding:4px 12px; border-radius:99px; flex-shrink:0; white-space:nowrap; position:relative; z-index:1; }}

    /* ── Plotly chart ── */
    div[data-testid="stPlotlyChart"] {{
        background: linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015)) !important;
        border-radius: 18px !important; box-shadow: 0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border: 1px solid rgba(255,255,255,0.09) !important; overflow: hidden !important; padding: 10px !important;
    }}

    /* ── Tabla oscura ── */
    div[data-testid="stDataFrame"] {{
        border-radius: 16px !important; overflow: hidden !important;
        box-shadow: 0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] {{
        background: linear-gradient(135deg, #1b1240 0%, #0EA5E9 100%) !important;
        color: white !important; font-weight: 700 !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] span {{ color: white !important; }}
    div[data-testid="stDataFrame"] .ag-root-wrapper {{ background: rgba(16,13,36,0.90) !important; border: none !important; }}
    div[data-testid="stDataFrame"] .ag-body-viewport,
    div[data-testid="stDataFrame"] .ag-center-cols-viewport {{ background: transparent !important; }}
    div[data-testid="stDataFrame"] .ag-row {{ background: rgba(16,13,36,0.85) !important; border-color: rgba(255,255,255,0.045) !important; }}
    div[data-testid="stDataFrame"] .ag-row-odd {{ background: rgba(22,18,48,0.80) !important; }}
    div[data-testid="stDataFrame"] .ag-row:hover,
    div[data-testid="stDataFrame"] .ag-row-hover {{ background: rgba(14,165,233,0.10) !important; }}
    div[data-testid="stDataFrame"] .ag-cell {{ color: rgba(225,232,250,0.90) !important; border-color: rgba(255,255,255,0.04) !important; }}
    div[data-testid="stDataFrame"] .ag-header {{ background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.10) !important; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar {{ width:6px; height:6px; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.04); }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{ background: rgba(56,189,248,0.35); border-radius:99px; }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%, transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%, transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%, transparent 55%),
            linear-gradient(160deg, #0B0518 0%, #14082b 45%, #0A0414 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
        display:flex!important; flex-direction:column!important; min-height:100vh!important;
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}
    [data-testid="stSidebarHeader"] {{ padding-top:0.6rem!important; padding-bottom:0!important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top:0!important; flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] > div {{ flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{ margin-top:auto!important; }}
    div[data-testid="stSidebarContent"] hr {{ border-color: rgba(255,255,255,0.08); margin-top:4px!important; margin-bottom:4px!important; }}
    div[data-testid="collapsedControl"] {{ background:transparent!important; border:none!important; box-shadow:none!important; }}
    div[data-testid="collapsedControl"] * {{ color:transparent!important; background:transparent!important; border:none!important; }}

    @keyframes sbcBar   {{ 0%{{background-position:0% 0%;}} 100%{{background-position:200% 0%;}} }}
    @keyframes sbcPulse {{ 0%,100%{{opacity:1;transform:scale(1);}} 50%{{opacity:.3;transform:scale(.6);}} }}

    .sbc {{ position:relative;border-radius:20px;overflow:hidden;margin:0 0 20px;padding:20px 18px 18px;
        background:linear-gradient(145deg,rgba(56,189,248,0.12),rgba(129,140,248,0.09),rgba(52,211,153,0.07)),rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.12); }}
    .sbc-orb {{ position:absolute;border-radius:50%;pointer-events:none; }}
    .sbc-orb-1 {{ width:140px;height:140px;background:radial-gradient(circle,rgba(56,189,248,0.18),transparent 70%);top:-50px;right:-40px; }}
    .sbc-orb-2 {{ width:90px;height:90px;background:radial-gradient(circle,rgba(129,140,248,0.16),transparent 70%);bottom:-30px;left:-25px; }}
    .sbc-orb-3 {{ width:60px;height:60px;background:radial-gradient(circle,rgba(52,211,153,0.14),transparent 70%);top:50%;right:12px; }}
    .sbc-live {{ position:absolute;top:14px;right:14px;display:flex;align-items:center;gap:5px;
        font-size:8px!important;font-weight:800!important;color:#34D399!important;
        background:rgba(52,211,153,0.13);border:1px solid rgba(52,211,153,0.30);
        padding:3px 9px 3px 7px;border-radius:99px;letter-spacing:0.10em;z-index:2; }}
    .sbc-pulse {{ width:5px;height:5px;background:#34D399;border-radius:50%;display:inline-block;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .sbc-body {{ position:relative;z-index:1;text-align:center; }}
    .sbc-logo-wrap {{ margin-bottom:10px;display:flex;justify-content:center; }}
    .sbc-logo-img {{ max-width:150px!important;height:auto!important;filter:drop-shadow(0 4px 14px rgba(56,189,248,0.45)) brightness(1.05); }}
    .sbc-name {{ font-size:13px!important;font-weight:700!important;color:rgba(255,255,255,0.88)!important;margin-bottom:4px!important; }}
    .sbc-org  {{ font-size:10px!important;color:rgba(255,255,255,0.35)!important;margin-bottom:16px!important; }}
    .sbc-stats {{ display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.22);border-radius:12px;padding:10px 8px;border:1px solid rgba(255,255,255,0.07); }}
    .sbc-stat {{ flex:1;text-align:center; }}
    .sbc-sv {{ display:block;font-size:14px!important;font-weight:900!important;color:white!important;line-height:1;margin-bottom:3px; }}
    .sbc-sl {{ display:block;font-size:8px!important;font-weight:700!important;color:rgba(255,255,255,0.28)!important;letter-spacing:0.10em;text-transform:uppercase; }}
    .sbc-sep {{ width:1px;height:28px;background:rgba(255,255,255,0.09);flex-shrink:0; }}
    .sbc-bar {{ position:absolute;bottom:0;left:0;right:0;height:3px;
        background:linear-gradient(90deg,#38BDF8,#818CF8,#34D399,#F59E0B,#38BDF8);
        background-size:300% 100%;animation:sbcBar 4s linear infinite; }}

    .sbh {{ display:flex;align-items:center;gap:10px;margin:24px 0 12px; }}
    .sbh-num {{ font-size:10px!important;font-weight:900!important;width:28px;height:22px;border-radius:7px;border:1px solid;display:flex;align-items:center;justify-content:center;flex-shrink:0;letter-spacing:0.04em; }}
    .sbh-lbl {{ font-size:10px!important;font-weight:800!important;color:rgba(255,255,255,0.60)!important;letter-spacing:0.14em!important;text-transform:uppercase!important;white-space:nowrap!important; }}
    .sbh-rule {{ flex:1;height:1px;background:rgba(255,255,255,0.08); }}

    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *,
    ul[role="listbox"] *, li[role="option"], li[role="option"] * {{ color: #1E293B !important; }}
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{ background: #F1F5F9 !important; }}

    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] span,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] *,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] input {{ color: white !important; }}
    div[data-testid="stSidebarContent"] input[type="text"] {{ color: white !important; }}
    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] span {{
        font-size:11px!important; font-weight:500!important; color:rgba(255,255,255,0.50)!important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput label,
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"] p {{
        font-size:11px!important; font-weight:600!important; color:#38BDF8!important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div,
    div[data-testid="stSidebarContent"] .stSelectbox > label + div > div {{
        background:rgba(255,255,255,0.05)!important; border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:9px!important; transition:border-color .18s, box-shadow .18s!important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div:hover {{
        border-color:rgba(56,189,248,0.50)!important; box-shadow:0 0 0 3px rgba(56,189,248,0.10)!important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input {{
        background:rgba(255,255,255,0.05)!important; border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:9px!important; color:white!important; font-size:11px!important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input:focus {{
        border-color:rgba(56,189,248,0.50)!important; box-shadow:0 0 0 3px rgba(56,189,248,0.10)!important;
    }}
    div[data-testid="stSidebarContent"] .stTextInput > div > div > input {{
        background:rgba(255,255,255,0.05)!important; border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:9px!important; color:white!important; font-size:11px!important;
    }}

    .sbf {{ margin-top:26px; }}
    .sbf-card {{ position:relative;overflow:hidden;border-radius:16px;padding:14px;
        background:linear-gradient(150deg,rgba(56,189,248,0.10),rgba(129,140,248,0.06));
        border:1px solid rgba(255,255,255,0.10);box-shadow:inset 0 1px 0 rgba(255,255,255,0.08); }}
    .sbf-glow {{ position:absolute;width:120px;height:120px;border-radius:50%;top:-50px;right:-40px;
        background:radial-gradient(circle,rgba(56,189,248,0.20),transparent 70%);pointer-events:none; }}
    .sbf-row {{ display:flex;align-items:center;gap:12px;position:relative;z-index:1; }}
    .sbf-avatar {{ position:relative;width:42px;height:42px;border-radius:13px;flex-shrink:0;
        background:linear-gradient(135deg,#38BDF8,#818CF8);
        display:flex;align-items:center;justify-content:center;
        font-size:14px!important;font-weight:900!important;color:white!important;
        box-shadow:0 6px 18px rgba(56,189,248,0.45),inset 0 1px 0 rgba(255,255,255,0.3); }}
    .sbf-online {{ position:absolute;bottom:-2px;right:-2px;width:12px;height:12px;border-radius:50%;
        background:#34D399;border:2.5px solid #130A2B;box-shadow:0 0 8px rgba(52,211,153,0.8);
        animation:sbcPulse 2s ease-in-out infinite; }}
    .sbf-info {{ flex:1; }}
    .sbf-name {{ font-size:12px!important;font-weight:700!important;color:rgba(255,255,255,0.92)!important;margin-bottom:3px!important; }}
    .sbf-role {{ font-size:10px!important;color:rgba(255,255,255,0.42)!important;line-height:1.3; }}
    .sbf-credit {{ display:flex;align-items:center;justify-content:center;gap:5px;margin-top:12px;
        font-size:9px!important;font-weight:600!important;color:rgba(255,255,255,0.30)!important;letter-spacing:0.06em; }}
    .sbf-spark {{ font-size:10px; }}

    /* ── Header banner (idéntico a los otros módulos) ── */
    .st-key-hdrbanner {{
        position:relative; overflow:hidden; border-radius:20px; padding:18px 30px; margin-bottom:18px;
        background:
            radial-gradient(ellipse 70% 130% at 2% -15%,   rgba(14,165,233,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 65% 130% at 100% 120%, rgba(129,140,248,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 55% 110% at 72% 130%,  rgba(52,211,153,0.16) 0%, transparent 60%),
            linear-gradient(155deg, #0B0518 0%, #14082b 50%, #0A0414 100%);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 18px 46px -18px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    .hb-eyebrow {{ display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.16);
        border-radius:99px;padding:5px 13px;margin-bottom:11px;
        font-size:10px;font-weight:700;color:rgba(255,255,255,0.78);letter-spacing:0.12em;text-transform:uppercase; }}
    .hb-dot {{ width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 9px #34D399;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .hb-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:29px;font-weight:700;color:white;margin:0 0 9px;letter-spacing:-0.8px; }}
    .hb-meta {{ display:flex;flex-wrap:wrap;gap:8px;margin:0 0 2px; }}
    .hb-chip {{ display:inline-flex;align-items:center;gap:6px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.13);
        border-radius:9px;padding:5px 11px;font-size:11px;font-weight:600;color:rgba(255,255,255,0.74); }}
    .hb-chip b {{ color:#fff;font-weight:700; }}
    .nav-lbl {{ font-size:9px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;
        color:rgba(255,255,255,0.40);margin:3px 0 7px; }}
    .st-key-hdrbanner [data-testid="stVerticalBlock"] {{ gap:0.5rem!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button {{
        position:relative; z-index:2; white-space:nowrap!important; color:#CBD3F2!important;
        border-radius:9px!important; font-size:10px!important; font-weight:700!important;
        height:32px!important; min-height:32px!important; padding:0 11px!important;
        border:1px solid rgba(255,255,255,0.12)!important; border-top-color:rgba(255,255,255,0.18)!important;
        background:linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.025))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.10), 0 4px 12px -8px rgba(8,3,24,0.60)!important;
        transition:all .16s ease!important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button p {{ white-space:nowrap!important; margin:0!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:hover {{
        color:#EAF2FF!important; transform:translateY(-1px)!important;
        border-color:rgba(125,211,252,0.42)!important;
        background:linear-gradient(180deg, rgba(125,211,252,0.15), rgba(255,255,255,0.04))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.16), 0 8px 20px -10px rgba(56,189,248,0.38)!important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"] {{
        color:#F4F9FF!important; padding-left:20px!important;
        border:1px solid rgba(56,189,248,0.55)!important; border-top-color:rgba(186,225,255,0.62)!important;
        background:linear-gradient(180deg, rgba(56,189,248,0.30), rgba(59,130,246,0.16))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.22), 0 8px 22px -10px rgba(56,189,248,0.50)!important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]::before {{
        content:""; position:absolute; left:8px; top:50%; transform:translateY(-50%);
        width:5px; height:5px; border-radius:50%; background:#7DD3FC; box-shadow:0 0 8px rgba(125,211,252,0.9);
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]:hover {{
        transform:translateY(-1px)!important;
        background:linear-gradient(180deg, rgba(56,189,248,0.36), rgba(59,130,246,0.20))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.24), 0 10px 26px -10px rgba(56,189,248,0.58)!important;
    }}

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tablist"] {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background:
            radial-gradient(ellipse 90% 160% at 2% 50%,  rgba(14,165,233,0.22) 0%, transparent 60%),
            radial-gradient(ellipse 90% 160% at 98% 50%, rgba(129,140,248,0.22) 0%, transparent 60%),
            radial-gradient(ellipse 70% 130% at 50% 120%,rgba(52,211,153,0.10) 0%, transparent 60%),
            linear-gradient(155deg, #0B0518 0%, #14082b 55%, #0A0414 100%) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-top-color: rgba(255,255,255,0.16) !important;
        border-radius: 22px !important;
        padding: 6px !important;
        gap: 5px !important;
        box-shadow:
            0 12px 40px -12px rgba(0,0,0,0.55),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
    }}
    [data-testid="stTabs"] [role="tab"] {{
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        color: rgba(255,255,255,0.32) !important;
        padding: 13px 36px !important;
        transition: all .22s ease !important;
        border: 1px solid transparent !important;
        position: relative !important;
        letter-spacing: 0.03em !important;
        white-space: nowrap !important;
        background: transparent !important;
    }}
    [data-testid="stTabs"] [role="tab"]:hover {{
        color: rgba(255,255,255,0.70) !important;
        background: rgba(255,255,255,0.055) !important;
        border-color: rgba(255,255,255,0.10) !important;
    }}
    /* Tiempo real — rojo */
    [data-testid="stTabs"] [role="tab"]:nth-child(1)[aria-selected="true"] {{
        background: linear-gradient(150deg, rgba(239,68,68,0.26) 0%, rgba(239,68,68,0.08) 100%) !important;
        border-color: rgba(239,68,68,0.50) !important;
        border-top-color: rgba(252,165,165,0.55) !important;
        color: #FCA5A5 !important;
        box-shadow:
            0 0 32px -8px rgba(239,68,68,0.65),
            0 6px 20px -10px rgba(239,68,68,0.50),
            inset 0 1px 0 rgba(255,180,180,0.18) !important;
        text-shadow: 0 0 16px rgba(252,165,165,0.60) !important;
    }}
    /* Planificación — azul */
    [data-testid="stTabs"] [role="tab"]:nth-child(2)[aria-selected="true"] {{
        background: linear-gradient(150deg, rgba(56,189,248,0.26) 0%, rgba(56,189,248,0.08) 100%) !important;
        border-color: rgba(56,189,248,0.50) !important;
        border-top-color: rgba(125,211,252,0.55) !important;
        color: #7DD3FC !important;
        box-shadow:
            0 0 32px -8px rgba(56,189,248,0.65),
            0 6px 20px -10px rgba(56,189,248,0.50),
            inset 0 1px 0 rgba(125,211,252,0.18) !important;
        text-shadow: 0 0 16px rgba(125,211,252,0.60) !important;
    }}
    /* Históricas — verde */
    [data-testid="stTabs"] [role="tab"]:nth-child(3)[aria-selected="true"] {{
        background: linear-gradient(150deg, rgba(52,211,153,0.26) 0%, rgba(52,211,153,0.08) 100%) !important;
        border-color: rgba(52,211,153,0.50) !important;
        border-top-color: rgba(110,231,183,0.55) !important;
        color: #6EE7B7 !important;
        box-shadow:
            0 0 32px -8px rgba(52,211,153,0.65),
            0 6px 20px -10px rgba(52,211,153,0.50),
            inset 0 1px 0 rgba(110,231,183,0.18) !important;
        text-shadow: 0 0 16px rgba(110,231,183,0.60) !important;
    }}
    [data-testid="stTabPanel"] {{ padding-top:28px !important; }}

    /* ── Botón Actualizar datos ── */
    .st-key-sb_refresh button {{
        background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(99,102,241,0.14)) !important;
        border: 1px solid rgba(56,189,248,0.35) !important;
        border-radius: 10px !important;
        color: #7DD3FC !important;
        font-size: 11px !important; font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        transition: all .2s ease !important;
        box-shadow: 0 0 14px -6px rgba(56,189,248,0.40), inset 0 1px 0 rgba(255,255,255,0.10) !important;
    }}
    .st-key-sb_refresh button:hover {{
        background: linear-gradient(135deg, rgba(56,189,248,0.28), rgba(99,102,241,0.20)) !important;
        border-color: rgba(56,189,248,0.60) !important;
        box-shadow: 0 0 22px -4px rgba(56,189,248,0.55), inset 0 1px 0 rgba(255,255,255,0.14) !important;
        transform: translateY(-1px) !important;
    }}
    .st-key-sb_refresh button p {{ color: #7DD3FC !important; }}

    /* ── Lista de envejecimiento (pendientes de validación) ── */
    .verif-list {{ display:flex; flex-direction:column; gap:7px; margin-top:2px; }}
    .verif-row {{
        position:relative; display:flex; align-items:center; gap:14px;
        background: linear-gradient(160deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.018) 100%);
        border:1px solid rgba(255,255,255,0.09);
        border-radius:14px; padding:10px 18px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }}
    .verif-row:hover {{
        transform: translateX(4px);
        border-color: var(--vc, rgba(255,255,255,0.20));
        box-shadow: 0 10px 26px -14px rgba(0,0,0,0.65), 0 0 22px -12px var(--vc, transparent), inset 0 1px 0 rgba(255,255,255,0.07);
    }}
    .verif-rank {{
        font-family:'Space Grotesk',sans-serif!important; font-size:11px!important; font-weight:800!important;
        color:rgba(255,255,255,0.24)!important; width:20px; flex-shrink:0; text-align:center;
    }}
    .verif-avatar {{
        width:36px; height:36px; border-radius:11px; flex-shrink:0;
        background: linear-gradient(135deg, rgba(255,255,255,0.14), rgba(255,255,255,0.04));
        border:1px solid rgba(255,255,255,0.14);
        display:flex; align-items:center; justify-content:center;
        font-size:11px!important; font-weight:800!important; color:rgba(255,255,255,0.85)!important;
    }}
    .verif-body {{ flex:1; min-width:0; }}
    .verif-name {{
        font-size:12.5px!important; font-weight:700!important; color:rgba(255,255,255,0.90)!important;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }}
    .verif-sup {{
        font-size:10.5px!important; color:rgba(255,255,255,0.40)!important;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:1px;
    }}
    .verif-id {{
        font-size:9.5px!important; color:rgba(255,255,255,0.26)!important;
        font-family:'Space Grotesk',sans-serif!important; flex-shrink:0; white-space:nowrap;
    }}
    .verif-badge {{
        flex-shrink:0; font-size:10.5px!important; font-weight:800!important;
        padding:5px 12px; border-radius:99px; white-space:nowrap; letter-spacing:0.01em;
    }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
_home_pg = st.Page("home.py",               title="Inicio",     icon="🏠", default=True)
_adh_pg  = st.Page("pages/1_Adherencia.py", title="Adherencia", icon="🎯")
_ocu_pg  = st.Page("pages/2_Ocupacion.py",  title="Ocupación",  icon="📊")

with st.container(key="hdrbanner"):
    st.markdown("""
    <div class='hb-eyebrow'><span class='hb-dot'></span>Centro de Control · Uniminuto 2026</div>
    <div class='hb-title'>Novedades Operativas</div>
    <div class='hb-meta'>
        <span class='hb-chip'>📢 <b>Google Sheets en vivo</b></span>
    </div>
    <div class='nav-lbl'>⚡ Navegación</div>
    """, unsafe_allow_html=True)
    nb1, nb2, nb3, nb4, _nsp = st.columns([1.0, 1.35, 1.3, 1.35, 1.6], vertical_alignment="center")
    with nb1:
        if st.button("🏠 Inicio",     key="hdr_home", use_container_width=True):
            st.switch_page(_home_pg)
    with nb2:
        if st.button("🎯 Adherencia", key="hdr_adh",  use_container_width=True):
            st.switch_page(_adh_pg)
    with nb3:
        if st.button("📊 Ocupación",  key="hdr_ocu",  use_container_width=True):
            st.switch_page(_ocu_pg)
    with nb4:
        st.button("📢 Novedades", key="hdr_nov", use_container_width=True, type="primary")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
def _sec_label(texto, color):
    return (
        f"<div style='font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;"
        f"color:rgba(255,255,255,0.38);display:flex;align-items:center;gap:10px;margin-bottom:18px'>"
        f"<span style='width:22px;height:2px;background:{color};border-radius:2px;display:inline-block'></span>"
        f"{texto}</div>"
    )

_filter_args = dict(
    sup_sel=sup_sel, exp_sel=exp_sel, buscar=buscar,
    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
    agrupar=agrupar, periodo_sel=periodo_sel,
)

tab_rt, tab_plan, tab_hist = st.tabs([
    "🚨  Tiempo real",
    "🗓️  Planificación",
    "📁  Históricas",
])

with tab_rt:
    st.markdown(_sec_label("Novedades activas · turno en curso", "#EF4444"), unsafe_allow_html=True)
    _render_tab(df_rt, **_filter_args)

with tab_plan:
    st.markdown(_sec_label("Novedades planificadas · próximos días", "#38BDF8"), unsafe_allow_html=True)
    _render_tab(df_plan, **_filter_args)

with tab_hist:
    st.markdown(_sec_label("Registro histórico · novedades cerradas", "#34D399"), unsafe_allow_html=True)
    _render_tab(df_hist, **_filter_args)
