import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Análisis Bancario Interactivo",
    layout="wide"
)

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

h1 {
    text-align: center;
}

[data-testid="metric-container"] {
    background-color: #262730;
    border: 1px solid #3c3f44;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

df = pd.read_csv(
    "data/processed/dataset_limpio1.csv"
)

df["Monto USD"] = pd.to_numeric(
    df["Monto USD"],
    errors="coerce"
)

coordenadas = {
    "Montevideo": (-34.9011, -56.1645),
    "Canelones": (-34.5228, -56.2778),
    "Maldonado": (-34.9000, -54.9500),
    "Colonia": (-34.4626, -57.8398),
    "San José": (-34.3375, -56.7136),
    "Florida": (-34.0956, -56.2142),
    "Durazno": (-33.4132, -56.5007),
    "Soriano": (-33.2524, -58.0305),
    "Paysandú": (-32.3171, -58.0807),
    "Salto": (-31.3833, -57.9667),
    "Artigas": (-30.4000, -56.4667),
    "Rivera": (-30.9053, -55.5508),
    "Tacuarembó": (-31.7169, -55.9811),
    "Cerro Largo": (-32.3703, -54.1675),
    "Treinta y Tres": (-33.2333, -54.3833),
    "Rocha": (-34.4833, -54.3333),
    "Lavalleja": (-34.3759, -55.2377),
    "Río Negro": (-33.1325, -58.2956),
    "Flores": (-33.5447, -56.8886)
}

st.title("Análisis Bancario Interactivo")

st.write(
    "Esta aplicación permite explorar el dataset mediante filtros y visualizaciones dinámicas."
)

st.sidebar.header("Filtros")

min_monto = int(df["Monto USD"].min(skipna=True))
max_monto = int(df["Monto USD"].max(skipna=True))

mostrar_nulos = st.sidebar.checkbox(
    "Incluir entradas con monto nulo",
    value=True
)

rango_monto = st.sidebar.slider(
    "Rango de Monto USD",
    min_monto,
    max_monto,
    (min_monto, max_monto)
)

sucursales = sorted(
    df["Sucursal"].dropna().unique()
)

sucursal = st.sidebar.selectbox(
    "Sucursal",
    ["Todas"] + sucursales
)

productos = sorted(
    df["Producto"].dropna().unique()
)

producto = st.sidebar.selectbox(
    "Producto",
    ["Todos"] + productos
)

if mostrar_nulos:
    filtro_monto = (
        (
            (df["Monto USD"] >= rango_monto[0]) &
            (df["Monto USD"] <= rango_monto[1])
        )
        |
        (df["Monto USD"].isna())
    )
else:
    filtro_monto = (
        (df["Monto USD"] >= rango_monto[0]) &
        (df["Monto USD"] <= rango_monto[1])
    )

df_filtrado = df[filtro_monto]

if sucursal != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["Sucursal"] == sucursal
    ]

if producto != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Producto"] == producto
    ]

df_graficos = df_filtrado.dropna(
    subset=["Monto USD"]
)

if df_graficos.empty:
    media = 0
    mediana = 0
    desv = 0
else:
    media = df_graficos["Monto USD"].mean()
    mediana = df_graficos["Monto USD"].median()
    desv = df_graficos["Monto USD"].std()

registros = len(df_filtrado)
nulos = df_filtrado["Monto USD"].isna().sum()

st.subheader("Indicadores Principales")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Media", f"{media:,.0f}")
col2.metric("Mediana", f"{mediana:,.0f}")
col3.metric("Desv. Est.", f"{desv:,.0f}")
col4.metric("Registros", registros)
col5.metric("Montos Nulos", nulos)

st.subheader("Resumen Descriptivo")

if not df_graficos.empty:

    resumen = pd.DataFrame({
        "Métrica": [
            "Media",
            "Mediana",
            "Rango",
            "Desviación Estándar",
            "Q1",
            "Q2",
            "Q3"
        ],
        "Valor": [
            df_graficos["Monto USD"].mean(),
            df_graficos["Monto USD"].median(),
            df_graficos["Monto USD"].max() - df_graficos["Monto USD"].min(),
            df_graficos["Monto USD"].std(),
            df_graficos["Monto USD"].quantile(0.25),
            df_graficos["Monto USD"].quantile(0.50),
            df_graficos["Monto USD"].quantile(0.75)
        ]
    })

    st.dataframe(resumen)

else:
    st.warning(
        "No existen registros con Monto USD para generar estadísticas."
    )

st.subheader("Visualizaciones")

if df_graficos.empty:

    st.warning(
        "No existen registros con Monto USD para generar visualizaciones."
    )

else:

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:

        fig_hist = px.histogram(
            df_graficos,
            x="estado_mora",
            title="Distribución de Estado de Mora"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True,
            key="histograma_mora"
        )

    with col_graf2:

        fig_scatter = px.scatter(
            df_graficos,
            x="Dias_Registro",
            y="Monto USD",
            color="estado_mora",
            size="Monto USD",
            hover_data=[
                "Sucursal",
                "Producto"
            ],
            title="Relación entre Monto USD y Días de Registro"
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True,
            key="scatter_montos"
        )

    st.subheader("Distribución Geográfica")

    mapa_df = (
        df_graficos
        .groupby("Sucursal")
        .agg(
            Monto_Total=("Monto USD", "sum"),
            Cantidad_Operaciones=("Monto USD", "count"),
            Monto_Promedio=("Monto USD", "mean")
        )
        .reset_index()
    )

    mapa_df["lat"] = mapa_df["Sucursal"].map(
        lambda x: coordenadas.get(x, (None, None))[0]
    )

    mapa_df["lon"] = mapa_df["Sucursal"].map(
        lambda x: coordenadas.get(x, (None, None))[1]
    )

    mapa_df = mapa_df.dropna(
        subset=["lat", "lon"]
    )

    mapa_df["Monto_Escala"] = np.log1p(
        mapa_df["Monto_Total"]
    )

    fig_mapa = px.scatter_map(
        mapa_df,
        lat="lat",
        lon="lon",
        size="Monto_Escala",
        color="Monto_Total",
        color_continuous_scale="Cividis",
        size_max=80,
        zoom=6,
        hover_name="Sucursal",
        hover_data={
            "Monto_Total": ":,.0f",
            "Cantidad_Operaciones": True,
            "Monto_Promedio": ":,.0f",
            "lat": False,
            "lon": False
        },
        title="Monto Total Gestionado por Sucursal"
    )

    fig_mapa.update_layout(
        height=750,
        map=dict(
            center=dict(
                lat=-32.8,
                lon=-56.0
            )
        )
    )

    st.plotly_chart(
        fig_mapa,
        use_container_width=True,
        key="mapa_sucursales"
    )

    st.subheader("Cantidad de Registros por Producto")

    productos_df = (
        df_filtrado["Producto"]
        .value_counts()
        .reset_index()
    )

    productos_df.columns = [
        "Producto",
        "Cantidad"
    ]

    fig_bar = px.bar(
        productos_df,
        x="Producto",
        y="Cantidad",
        color="Cantidad",
        color_continuous_scale="Cividis",
        title="Cantidad de Registros por Producto"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        key="barra_productos"
    )

st.subheader("Datos Filtrados")

st.dataframe(
    df_filtrado,
    use_container_width=True
)


