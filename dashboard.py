from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

st.set_page_config(
    page_title="Agro Telemetry BI Dashboard",
    layout="wide",
)


# =====================================================
# ESTILOS
# =====================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #0E1117;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .dashboard-title {
            font-size: 42px;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0px;
        }

        .dashboard-subtitle {
            font-size: 16px;
            color: #AAB2C0;
            margin-bottom: 25px;
        }

        .section-title {
            font-size: 24px;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .kpi-card {
            background: linear-gradient(135deg, #151A24 0%, #1E2633 100%);
            padding: 20px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        }

        .kpi-label {
            font-size: 13px;
            color: #AAB2C0;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-size: 30px;
            font-weight: 800;
            color: #FFFFFF;
        }

        .kpi-helper {
            font-size: 12px;
            color: #7D8594;
            margin-top: 4px;
        }

        .insight-box {
            background: #111827;
            border-left: 5px solid #22C55E;
            padding: 18px 22px;
            border-radius: 12px;
            color: #E5E7EB;
            margin-bottom: 25px;
        }

        .warning-box {
            background: #111827;
            border-left: 5px solid #F59E0B;
            padding: 18px 22px;
            border-radius: 12px;
            color: #E5E7EB;
            margin-bottom: 25px;
        }

        div[data-testid="stMetric"] {
            background-color: #151A24;
            padding: 15px;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# CARGA DE DATOS
# =====================================================

@st.cache_data
def load_data():
    dealer_summary = pd.read_csv(PROCESSED_DIR / "dealer_summary.csv")
    zone_summary = pd.read_csv(PROCESSED_DIR / "zone_summary.csv")
    machine_summary = pd.read_csv(PROCESSED_DIR / "machine_summary.csv")
    daily_metrics = pd.read_csv(PROCESSED_DIR / "daily_metrics.csv")

    daily_metrics["event_date"] = pd.to_datetime(daily_metrics["event_date"])

    return dealer_summary, zone_summary, machine_summary, daily_metrics


dealer_summary, zone_summary, machine_summary, daily_metrics = load_data()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Filtros")

zonas = ["Todas"] + sorted(daily_metrics["zona"].dropna().unique().tolist())
zona_seleccionada = st.sidebar.selectbox("Zona", zonas, index=0)

if zona_seleccionada != "Todas":
    concesionarios_disponibles = (
        daily_metrics[daily_metrics["zona"] == zona_seleccionada]["concesionario"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    concesionarios_disponibles = (
        daily_metrics["concesionario"]
        .dropna()
        .unique()
        .tolist()
    )

concesionarios = ["Todos"] + sorted(concesionarios_disponibles)

concesionario_seleccionado = st.sidebar.selectbox(
    "Concesionario",
    concesionarios,
    index=0,
)

fecha_min = daily_metrics["event_date"].min().date()
fecha_max = daily_metrics["event_date"].max().date()

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)

st.sidebar.divider()

st.sidebar.info(
    "Este dashboard analiza uso, consumo, alertas y prioridad operativa "
    "de máquinas agrícolas simuladas."
)


# =====================================================
# FILTRADO DE DATOS
# =====================================================

daily_filtered = daily_metrics.copy()

daily_filtered = daily_filtered[
    (daily_filtered["event_date"].dt.date >= fecha_inicio)
    & (daily_filtered["event_date"].dt.date <= fecha_fin)
]

if zona_seleccionada != "Todas":
    daily_filtered = daily_filtered[daily_filtered["zona"] == zona_seleccionada]

if concesionario_seleccionado != "Todos":
    daily_filtered = daily_filtered[
        daily_filtered["concesionario"] == concesionario_seleccionado
    ]


# =====================================================
# MÉTRICAS DERIVADAS
# =====================================================

total_zones = daily_filtered["zona"].nunique()
total_dealers = daily_filtered["concesionario"].nunique()
total_machines = daily_filtered["machine_id"].nunique()
total_hours = daily_filtered["daily_hours_worked"].sum()
total_fuel = daily_filtered["daily_fuel_used"].sum()
total_alerts = daily_filtered["daily_alerts"].sum()
avg_temp = daily_filtered["avg_engine_temp"].mean()

if pd.isna(avg_temp):
    avg_temp = 0

fuel_per_hour = total_fuel / total_hours if total_hours > 0 else 0

dealer_ranking = (
    daily_filtered
    .groupby(["concesionario", "zona"], as_index=False)
    .agg(
        total_machines=("machine_id", "nunique"),
        total_hours_worked=("daily_hours_worked", "sum"),
        total_fuel_used=("daily_fuel_used", "sum"),
        total_alerts=("daily_alerts", "sum"),
        avg_engine_temp=("avg_engine_temp", "mean"),
    )
)

if not dealer_ranking.empty:
    dealer_ranking["operational_score"] = (
        dealer_ranking["total_hours_worked"] * 0.4
        + dealer_ranking["total_fuel_used"] * 0.3
        + dealer_ranking["total_alerts"] * 10
    ).round(2)

    dealer_ranking["total_hours_worked"] = dealer_ranking[
        "total_hours_worked"
    ].round(2)

    dealer_ranking["total_fuel_used"] = dealer_ranking[
        "total_fuel_used"
    ].round(2)

    dealer_ranking["avg_engine_temp"] = dealer_ranking[
        "avg_engine_temp"
    ].round(2)
else:
    dealer_ranking["operational_score"] = []


zone_ranking = (
    daily_filtered
    .groupby("zona", as_index=False)
    .agg(
        total_hours_worked=("daily_hours_worked", "sum"),
        total_fuel_used=("daily_fuel_used", "sum"),
        total_alerts=("daily_alerts", "sum"),
    )
)

machine_ranking = (
    daily_filtered
    .groupby(["machine_id", "modelo", "concesionario", "zona"], as_index=False)
    .agg(
        total_hours_worked=("daily_hours_worked", "sum"),
        total_fuel_used=("daily_fuel_used", "sum"),
        total_alerts=("daily_alerts", "sum"),
        avg_engine_temp=("avg_engine_temp", "mean"),
    )
)

if not machine_ranking.empty:
    machine_ranking["total_hours_worked"] = machine_ranking[
        "total_hours_worked"
    ].round(2)

    machine_ranking["total_fuel_used"] = machine_ranking[
        "total_fuel_used"
    ].round(2)

    machine_ranking["avg_engine_temp"] = machine_ranking[
        "avg_engine_temp"
    ].round(2)


# =====================================================
# HEADER
# =====================================================

st.markdown(
    """
    <div class="dashboard-title"> Agro Telemetry BI Dashboard</div>
    <div class="dashboard-subtitle">
        Análisis BI de telemetría simulada de maquinaria agrícola:
        uso, consumo, alertas y prioridad operativa por zona y concesionario.
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# KPIS
# =====================================================

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Zonas</div>
            <div class="kpi-value">{total_zones}</div>
            <div class="kpi-helper">Zonas activas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Concesionarios</div>
            <div class="kpi-value">{total_dealers}</div>
            <div class="kpi-helper">Operando</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Máquinas</div>
            <div class="kpi-value">{total_machines}</div>
            <div class="kpi-helper">Monitoreadas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Horas trabajadas</div>
            <div class="kpi-value">{total_hours:,.1f}</div>
            <div class="kpi-helper">Horas acumuladas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Combustible</div>
            <div class="kpi-value">{total_fuel:,.1f} L</div>
            <div class="kpi-helper">{fuel_per_hour:.1f} L por hora</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi6:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Alertas</div>
            <div class="kpi-value">{int(total_alerts)}</div>
            <div class="kpi-helper">Eventos operativos</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")


# =====================================================
# INSIGHT EJECUTIVO
# =====================================================

if not dealer_ranking.empty:
    top_dealer = dealer_ranking.sort_values(
        "operational_score",
        ascending=False,
    ).iloc[0]

    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Insight ejecutivo:</strong>
            el concesionario con mayor prioridad operativa es
            <strong>{top_dealer["concesionario"]}</strong>, ubicado en la zona
            <strong>{top_dealer["zona"]}</strong>, con
            <strong>{top_dealer["total_hours_worked"]:.1f}</strong> horas trabajadas,
            <strong>{top_dealer["total_fuel_used"]:.1f} L</strong> de combustible usado,
            <strong>{int(top_dealer["total_alerts"])}</strong> alertas y un score operativo de
            <strong>{top_dealer["operational_score"]:.1f}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="warning-box">
            No hay datos disponibles para los filtros seleccionados.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# GRÁFICOS PRINCIPALES
# =====================================================

st.markdown('<div class="section-title">Resumen operativo</div>', unsafe_allow_html=True)

left_col, right_col = st.columns(2)

with left_col:
    if not zone_ranking.empty:
        zone_chart_data = zone_ranking.sort_values(
            "total_fuel_used",
            ascending=False,
        )

        fig_zone_fuel = px.bar(
            zone_chart_data,
            x="zona",
            y="total_fuel_used",
            text="total_fuel_used",
            title="Consumo total de combustible por zona",
            labels={
                "zona": "Zona",
                "total_fuel_used": "Combustible usado (L)",
            },
        )

        fig_zone_fuel.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_zone_fuel.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=60, b=40),
        )

        st.plotly_chart(fig_zone_fuel, use_container_width=True)

with right_col:
    if not dealer_ranking.empty:
        alerts_data = dealer_ranking.sort_values(
            "total_alerts",
            ascending=False,
        )

        fig_alerts = px.bar(
            alerts_data,
            x="concesionario",
            y="total_alerts",
            text="total_alerts",
            title="Alertas operativas por concesionario",
            labels={
                "concesionario": "Concesionario",
                "total_alerts": "Total de alertas",
            },
        )

        fig_alerts.update_traces(textposition="outside")
        fig_alerts.update_layout(
            height=430,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=60, b=100),
        )

        st.plotly_chart(fig_alerts, use_container_width=True)


left_col, right_col = st.columns(2)

with left_col:
    if not dealer_ranking.empty:
        usage_data = dealer_ranking.sort_values(
            "total_hours_worked",
            ascending=False,
        )

        fig_usage = px.bar(
            usage_data,
            x="concesionario",
            y="total_hours_worked",
            text="total_hours_worked",
            title="Uso total por concesionario",
            labels={
                "concesionario": "Concesionario",
                "total_hours_worked": "Horas trabajadas",
            },
        )

        fig_usage.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_usage.update_layout(
            height=430,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=60, b=100),
        )

        st.plotly_chart(fig_usage, use_container_width=True)

with right_col:
    if not dealer_ranking.empty:
        score_data = dealer_ranking.sort_values(
            "operational_score",
            ascending=False,
        )

        fig_score = px.bar(
            score_data,
            x="concesionario",
            y="operational_score",
            text="operational_score",
            title="Ranking por score operativo",
            labels={
                "concesionario": "Concesionario",
                "operational_score": "Score operativo",
            },
        )

        fig_score.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_score.update_layout(
            height=430,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=60, b=100),
        )

        st.plotly_chart(fig_score, use_container_width=True)


# =====================================================
# TENDENCIAS DIARIAS
# =====================================================

st.markdown('<div class="section-title">Evolución diaria</div>', unsafe_allow_html=True)

daily_by_date = (
    daily_filtered
    .groupby("event_date", as_index=False)
    .agg(
        daily_fuel_used=("daily_fuel_used", "sum"),
        daily_alerts=("daily_alerts", "sum"),
        daily_hours_worked=("daily_hours_worked", "sum"),
    )
)

tab1, tab2, tab3 = st.tabs(
    [
        "Combustible diario",
        "Alertas diarias",
        "Horas trabajadas",
    ]
)

with tab1:
    fig_daily_fuel = px.line(
        daily_by_date,
        x="event_date",
        y="daily_fuel_used",
        markers=True,
        title="Evolución diaria del consumo de combustible",
        labels={
            "event_date": "Fecha",
            "daily_fuel_used": "Combustible usado (L)",
        },
    )

    fig_daily_fuel.update_layout(height=430)
    st.plotly_chart(fig_daily_fuel, use_container_width=True)

with tab2:
    fig_daily_alerts = px.line(
        daily_by_date,
        x="event_date",
        y="daily_alerts",
        markers=True,
        title="Evolución diaria de alertas operativas",
        labels={
            "event_date": "Fecha",
            "daily_alerts": "Total de alertas",
        },
    )

    fig_daily_alerts.update_layout(height=430)
    st.plotly_chart(fig_daily_alerts, use_container_width=True)

with tab3:
    fig_daily_hours = px.line(
        daily_by_date,
        x="event_date",
        y="daily_hours_worked",
        markers=True,
        title="Evolución diaria de horas trabajadas",
        labels={
            "event_date": "Fecha",
            "daily_hours_worked": "Horas trabajadas",
        },
    )

    fig_daily_hours.update_layout(height=430)
    st.plotly_chart(fig_daily_hours, use_container_width=True)


# =====================================================
# ANÁLISIS POR MÁQUINA
# =====================================================

st.markdown('<div class="section-title">Análisis por máquina</div>', unsafe_allow_html=True)

left_col, right_col = st.columns(2)

with left_col:
    if not machine_ranking.empty:
        machine_fuel_data = machine_ranking.sort_values(
            "total_fuel_used",
            ascending=False,
        )

        fig_machine_fuel = px.bar(
            machine_fuel_data,
            x="machine_id",
            y="total_fuel_used",
            text="total_fuel_used",
            title="Ranking de máquinas por consumo",
            labels={
                "machine_id": "Máquina",
                "total_fuel_used": "Combustible usado (L)",
            },
        )

        fig_machine_fuel.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
        )

        fig_machine_fuel.update_layout(
            height=430,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=60, b=80),
        )

        st.plotly_chart(fig_machine_fuel, use_container_width=True)

with right_col:
    if not machine_ranking.empty:
        temp_data = machine_ranking.sort_values(
            "avg_engine_temp",
            ascending=False,
        )

        fig_temp = px.bar(
            temp_data,
            x="machine_id",
            y="avg_engine_temp",
            text="avg_engine_temp",
            title="Temperatura promedio por máquina",
            labels={
                "machine_id": "Máquina",
                "avg_engine_temp": "Temperatura promedio (°C)",
            },
        )

        fig_temp.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
        )

        fig_temp.update_layout(
            height=430,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=60, b=80),
        )

        st.plotly_chart(fig_temp, use_container_width=True)


# =====================================================
# TABLAS EJECUTIVAS
# =====================================================

st.markdown('<div class="section-title">Tablas ejecutivas</div>', unsafe_allow_html=True)

tab_dealers, tab_machines, tab_zones = st.tabs(
    [
        "Concesionarios",
        "Máquinas",
        "Zonas",
    ]
)

with tab_dealers:
    st.dataframe(
        dealer_ranking.sort_values("operational_score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tab_machines:
    st.dataframe(
        machine_ranking.sort_values("total_alerts", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tab_zones:
    st.dataframe(
        zone_ranking.sort_values("total_fuel_used", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "El score operativo combina horas trabajadas, combustible consumido y alertas "
    "para identificar concesionarios con mayor prioridad operativa."
)