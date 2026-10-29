import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import unicodedata

# --------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Mortalidad Colombia 2019",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ENCABEZADO
# --------------------------------------------------

st.title("📊 Análisis de Mortalidad en Colombia - 2019")

st.markdown("""
### Aplicación web interactiva para el análisis de mortalidad en Colombia

La aplicación permite explorar patrones geográficos, demográficos y epidemiológicos mediante visualizaciones interactivas desarrolladas con Plotly y Streamlit.


**Autores:**

- Oscar Julián Escobar Rodríguez
- Mariana Rojas Romero

**Tecnologías utilizadas:**
Python | Streamlit | Plotly | Pandas | Json

---
""")

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------

@st.cache_data
def cargar_datos():

    mortalidad = pd.read_excel(
        "data/Anexo1.NoFetal2019_CE_15-03-23.xlsx"
    )

    causas = pd.read_excel(
    "data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx",
    header=8
)
    
    divipola = pd.read_excel(
        "data/Divipola_CE_.xlsx"
    )

    return mortalidad, causas, divipola


df, causas_df, divipola_df = cargar_datos()

divipola_df = divipola_df[
    [
        "COD_DEPARTAMENTO",
        "DEPARTAMENTO",
        "COD_MUNICIPIO",
        "MUNICIPIO"
    ]
].drop_duplicates()

df = df.merge(
    divipola_df,
    on=[
        "COD_DEPARTAMENTO",
        "COD_MUNICIPIO"
    ],
    how="left"
)

causas_df = causas_df.rename(
    columns={
        "Código de la CIE-10 tres caracteres":"COD_CIE3",
        "Descripción  de códigos mortalidad a tres caracteres":"DESC_MUERTE3",
        "Código de la CIE-10 cuatro caracteres": "COD_MUERTE",
        "Descripcion  de códigos mortalidad a cuatro caracteres": "DESCRIPCION_MUERTE"
    }
)


causas_df = causas_df[
    [
        "COD_CIE3",
        "DESC_MUERTE3",
        "COD_MUERTE",
        "DESCRIPCION_MUERTE"
    ]
]

df = df.merge(
    causas_df,
    on="COD_MUERTE",
    how="left"
)

departamentos = sorted(
    df["DEPARTAMENTO"]
    .dropna()
    .unique()
)


# =====================================
# TRANSFORMACIÓN DE VARIABLES
# =====================================

sexo_dict = {
    1: "Masculino",
    2: "Femenino",
    3: "Indeterminado"
}

df["SEXO_DESC"] = df["SEXO"].map(sexo_dict)

meses_dict = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

df["MES_DESC"] = df["MES"].map(meses_dict)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.image(
    "https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png",
    width=200
)

st.sidebar.title("Filtros")

st.sidebar.info(
    """
    Dashboard interactivo para el análisis
    de mortalidad en Colombia durante 2019.
    """
)

# =====================================
# FILTROS
# =====================================

sexo = st.sidebar.multiselect(
    "Sexo",
    options=[
        "Masculino",
        "Femenino",
        "Indeterminado"
    ]
)

orden_meses = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre"
]

mes = st.sidebar.multiselect(
    "Mes",
    options=orden_meses
)

departamento = st.sidebar.multiselect(
    "Departamento",
    options=departamentos
)


df_filtrado = df.copy()

if sexo:
    df_filtrado = df_filtrado[
        df_filtrado["SEXO_DESC"].isin(sexo)
    ]

if mes:
    df_filtrado = df_filtrado[
        df_filtrado["MES_DESC"].isin(mes)
    ]

if departamento:

    df_filtrado = df_filtrado[
        df_filtrado["DEPARTAMENTO"]
        .isin(departamento)
    ]


df_homicidios = df_filtrado[
    df_filtrado["COD_CIE3"] == "X95"
]
# =====================================
# KPIs
# =====================================

st.subheader("📌 Indicadores Generales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Muertes",
        f"{len(df_filtrado):,}"
    )

with col2:
    st.metric(
        "Departamentos",
        df_filtrado["DEPARTAMENTO"].nunique()
    )

with col3:
    st.metric(
        "Municipios",
        df_filtrado["MUNICIPIO"].nunique()
    )

with col4:
    st.metric(
        "Promedio mensual",
        f"{len(df_filtrado)/12:,.0f}"
    )

# =====================================
# Grafico1 Mapa muertes x depto
# =====================================
def normalizar_texto(texto):

    if pd.isna(texto):
        return texto

    texto = str(texto).upper()

    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

    return texto.strip()

muertes_departamento = (
    df_filtrado
    .groupby("DEPARTAMENTO")
    .size()
    .reset_index(name="TOTAL_MUERTES")
)


muertes_departamento["DEPARTAMENTO"] = (
    muertes_departamento["DEPARTAMENTO"]
    .apply(normalizar_texto)
)


with open(
    "assets/co_2018_MGN_DPTO_POLITICO.geojson",
    encoding="utf-8"
) as f:

    geojson_colombia = json.load(f)


for feature in geojson_colombia["features"]:

    nombre = feature["properties"]["DPTO_CNMBR"]

    feature["properties"]["DPTO_CNMBR"] = (
        normalizar_texto(nombre)
    )


# =====================================
# MAPA DEPARTAMENTAL
# =====================================

st.markdown("---")
st.subheader("🗺️ Distribución Geográfica de la Mortalidad en Colombia (2019)")

fig_mapa = px.choropleth(
    muertes_departamento,
    geojson=geojson_colombia,
    locations="DEPARTAMENTO",
    featureidkey="properties.DPTO_CNMBR",
    color="TOTAL_MUERTES",
    hover_name="DEPARTAMENTO",
    hover_data={
        "TOTAL_MUERTES": True
    },
    color_continuous_scale="Reds"
)

fig_mapa.update_geos(
    fitbounds="locations",
    visible=False
)

fig_mapa.update_layout(
    template="plotly_white",
    height=750,
    margin={
        "r": 0,
        "t": 30,
        "l": 0,
        "b": 0
    },
    coloraxis_colorbar=dict(
        title="Muertes"
    )
)

st.plotly_chart(
    fig_mapa,
    use_container_width=True
)

# =====================================
# Grafico2 Líneas muertes x mes
# =====================================
st.markdown("---")
st.subheader("📈 Evolución Mensual de las Defunciones Registradas en Colombia")

muertes_mes = (
    df_filtrado
    .groupby(["MES", "MES_DESC"])
    .size()
    .reset_index(name="TOTAL")
    .sort_values("MES")
)

fig_mes = px.line(
    muertes_mes,
    x="MES_DESC",
    y="TOTAL",
    markers=True,
    title="Total de Defunciones por Mes en Colombia"
)

fig_mes.update_layout(
    template="plotly_white",
    xaxis_title="Mes",
    yaxis_title="Número de Muertes",
    height=500
)

st.plotly_chart(
    fig_mes,
    use_container_width=True
)

# =====================================
# Grafico3 Barras Top5 violencia
# =====================================

st.markdown("---")
st.subheader("🔫 Top 5 Ciudades con Mayor Número de Homicidios por arma de fuego (X95)")

ciudades_violentas = (
    df_homicidios
    .groupby("MUNICIPIO")
    .size()
    .reset_index(name="TOTAL_HOMICIDIOS")
    .sort_values(
        "TOTAL_HOMICIDIOS",
        ascending=False
    )
    .head(5)
)

fig_homicidios = px.bar(
    ciudades_violentas,
    x="MUNICIPIO",
    y="TOTAL_HOMICIDIOS",
    color="TOTAL_HOMICIDIOS",
    color_continuous_scale="Reds",
    title="Ciudades con Mayor Número de Homicidios por Arma de Fuego (X95)"
)

fig_homicidios.update_layout(
    template="plotly_white",
    xaxis_title="Municipio",
    yaxis_title="Número de Homicidios",
    height=500,
    showlegend=False
)

st.plotly_chart(
    fig_homicidios,
    use_container_width=True
)

# =====================================
# Grafico4 Circular top 10 menor mortalidad
# =====================================

st.markdown("---")
st.subheader("🏙️ 10 Municipios con Menor Número de Defunciones Registradas")

menor_mortalidad = (
    df_filtrado
    .groupby("MUNICIPIO")
    .size()
    .reset_index(name="TOTAL")
    .sort_values("TOTAL")
    .head(10)
)

fig_pie = px.pie(
    menor_mortalidad,
    names="MUNICIPIO",
    values="TOTAL",
    hole=0.35,
    title="Participación de las 10 Ciudades con Menor Mortalidad"
)

fig_pie.update_layout(
    template="plotly_white",
    height=600
)

st.plotly_chart(
    fig_pie,
    use_container_width=True
)

st.success(f"""
Los municipios con menor número de defunciones registradas en el conjunto de datos
presentaron entre {menor_mortalidad['TOTAL'].min()} y
{menor_mortalidad['TOTAL'].max()} casos durante 2019.
""")

#st.info(
#    """
#    Nota: Debido a que los datos suministrados no incluyen
#    población municipal, el análisis se realiza utilizando
#    el número absoluto de defunciones registradas por municipio.
#    """
#)

with st.expander("Limitaciones del análisis"):
    st.write("""
    El conjunto de datos no incluye población municipal,
    por lo que no fue posible calcular tasas o índices
    de mortalidad ajustados por habitantes.

    Los resultados corresponden al número absoluto de
    defunciones registradas por municipio.
    """)

# =====================================
# Grafico5 Tabla top 10 causas
# =====================================
st.markdown("---")
st.subheader("🏥 Top 10 Causas de Muerte3")

top_causas = (
    df_filtrado
    .groupby(
        [
            "COD_CIE3",
            "DESC_MUERTE3"
        ]
    )
    .size()
    .reset_index(name="TOTAL_CASOS")
    .sort_values(
        "TOTAL_CASOS",
        ascending=False
    )
    .head(10)
)

top_causas.columns = [
    "Código CIE-10",
    "Causa de muerte",
    "Casos"
]

st.dataframe(
    top_causas,
    use_container_width=True,
    hide_index=True
)


#st.markdown("---")
#st.subheader("🏥 Top 10 Causas de Muerte")

#top_causas = (
#    df_filtrado
#    .groupby(
#        [
#            "COD_MUERTE",
#            "DESCRIPCION_MUERTE"
#        ]
#    )
#    .size()
#    .reset_index(name="TOTAL_CASOS")
#    .sort_values(
#        "TOTAL_CASOS",
#        ascending=False
#    )
#    .head(10)
#)

#top_causas.columns = [
#    "Código CIE-10",
#    "Causa de muerte",
#    "Casos"
#]

#st.dataframe(
#    top_causas,
#    use_container_width=True,
#    hide_index=True
#)

# =====================================
# Grafico6 Barras Apiladas por sexo en cada dpto
# =====================================

st.markdown("---")
st.subheader("👥 Comparación de Defunciones por Sexo y Departamento")

sexo_depto = (
    df_filtrado
    .groupby(
        [
            "DEPARTAMENTO",
            "SEXO_DESC"
        ]
    )
    .size()
    .reset_index(name="TOTAL")
)

fig_sexo = px.bar(
    sexo_depto,
    x="DEPARTAMENTO",
    y="TOTAL",
    color="SEXO_DESC",
    barmode="stack",
    color_discrete_map={
        "Masculino":"#1565C0",
        "Femenino":"#D81B60",
        "Indeterminado":"#757575"
    }
)

fig_sexo.update_layout(
    template="plotly_white",
    xaxis_title="Departamento",
    yaxis_title="Total de Muertes",
    legend_title_text="Sexo",
    height=650
)

st.plotly_chart(
    fig_sexo,
    use_container_width=True
)

# =====================================
# Grafico7 Histograma por grupo de edad
# =====================================

def clasificar_edad(grupo):

    if 0 <= grupo <= 4:
        return "Mortalidad neonatal"

    elif 5 <= grupo <= 6:
        return "Mortalidad infantil"

    elif 7 <= grupo <= 8:
        return "Primera infancia"

    elif 9 <= grupo <= 10:
        return "Niñez"

    elif grupo == 11:
        return "Adolescencia"

    elif 12 <= grupo <= 13:
        return "Juventud"

    elif 14 <= grupo <= 16:
        return "Adultez temprana"

    elif 17 <= grupo <= 19:
        return "Adultez intermedia"

    elif 20 <= grupo <= 24:
        return "Vejez"

    elif 25 <= grupo <= 28:
        return "Longevidad"

    else:
        return "Edad desconocida"

df_filtrado["CATEGORIA_EDAD"] = (
    df_filtrado["GRUPO_EDAD1"]
    .apply(clasificar_edad)
)

st.markdown("---")
st.subheader("👶🧑👴 Distribución de la Mortalidad Según el Ciclo de Vida")

orden_edades = [
    "Mortalidad neonatal",
    "Mortalidad infantil",
    "Primera infancia",
    "Niñez",
    "Adolescencia",
    "Juventud",
    "Adultez temprana",
    "Adultez intermedia",
    "Vejez",
    "Longevidad",
    "Edad desconocida"
]

edad = (
    df_filtrado
    .groupby("CATEGORIA_EDAD")
    .size()
    .reset_index(name="TOTAL")
)

edad["CATEGORIA_EDAD"] = pd.Categorical(
    edad["CATEGORIA_EDAD"],
    categories=orden_edades,
    ordered=True
)

edad = edad.sort_values(
    "CATEGORIA_EDAD"
)

fig_hist = px.histogram(
    edad,
    x="CATEGORIA_EDAD",
    y="TOTAL",
    color="CATEGORIA_EDAD"
)

fig_hist.update_layout(
    template="plotly_white",
    xaxis_title="Grupo Etario",
    yaxis_title="Número de Muertes",
    showlegend=False,
    height=550
)

st.plotly_chart(
    fig_hist,
    use_container_width=True
)