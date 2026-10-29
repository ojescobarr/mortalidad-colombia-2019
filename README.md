<<<<<<< HEAD
# Análisis de Mortalidad en Colombia - 2019

## Introducción

Este proyecto consiste en el desarrollo de una aplicación web interactiva para el análisis de la mortalidad en Colombia durante el año 2019, utilizando datos abiertos publicados por el Departamento Administrativo Nacional de Estadística (DANE).

La aplicación permite explorar patrones geográficos, temporales y demográficos mediante visualizaciones interactivas desarrolladas con Python, Streamlit y Plotly.


## Objetivo

Analizar el comportamiento de la mortalidad en Colombia durante el año 2019 mediante una aplicación web interactiva que facilite la exploración de patrones por departamento, municipio, sexo, edad y causa de muerte.

## Estructura del proyecto

```text
Mortalidad-Colombia-2019/

│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│ └── co_2018_MGN_DPTO_POLITICO.geojson
│
└── data/
├── Anexo1.NoFetal2019_CE_15-03-23.xlsx
├── Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx
└── Divipola_CE_.xlsx
```

## Requisitos

```txt
streamlit
pandas
plotly
openpyxl
numpy
```

## Software utilizado

- Python
- Streamlit
- Plotly
- Pandas
- Json
- Visual Studio Code
- GitHub
- Render

## Instalación

Clonar repositorio:

```bash
git clone URL_DEL_REPOSITORIO
```

Ingresar al proyecto:

```bash
cd Mortalidad-Colombia-2019
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar aplicación:

```bash
streamlit run app.py
```


## Despliegue

La aplicación fue desplegada en Render utilizando un servicio web conectado directamente al repositorio de GitHub.

Comando de construcción:

pip install -r requirements.txt

Comando de inicio:

streamlit run app.py --server.port $PORT --server.address 0.0.0.0


## Visualizaciones

### Mapa de mortalidad por departamento

CAPTURAS

Permite identificar los departamentos con mayor concentración de defunciones registradas durante 2019.
=======
# mortalidad-colombia-2019
>>>>>>> 82ac5d0b3e5de2fbb9daa431536f6546c5eedb17
