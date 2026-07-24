import io
import re
import unicodedata
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from rapidfuzz import fuzz, process
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Seguimiento MPAS 2026",
    page_icon="🏫",
    layout="wide",
)

# ============================================================
# COORDENADAS DE REFERENCIA
# ============================================================
COORDENADAS_REFERENCIA = {
    "CARMEN": [9.9365, -84.0750], "MERCED": [9.9386, -84.0828],
    "HOSPITAL": [9.9274, -84.0918], "CATEDRAL": [9.9289, -84.0740],
    "ZAPOTE": [9.9198, -84.0553], "SAN FRANCISCO": [9.9136, -84.0724],
    "URUCA": [9.9567, -84.1060], "MATA REDONDA": [9.9352, -84.1047],
    "PAVAS": [9.9488, -84.1342], "HATILLO": [9.9160, -84.1010],
    "SAN SEBASTIAN": [9.9121, -84.0909], "ESCAZU": [9.9180, -84.1399],
    "SANTA ANA": [9.9326, -84.1825], "ALAJUELITA": [9.9016, -84.1000],
    "VASQUEZ DE CORONADO": [9.9760, -84.0070], "CORONADO": [9.9760, -84.0070],
    "ACOSTA": [9.8003, -84.1604], "TIBAS": [9.9580, -84.0790],
    "MORAVIA": [9.9610, -84.0480], "MONTES DE OCA": [9.9369, -84.0500],
    "CURRIDABAT": [9.9136, -84.0405], "GOICOECHEA": [9.9480, -84.0430],
    "DESAMPARADOS": [9.8982, -84.0626], "ASERRI": [9.8587, -84.0917],
    "MORA": [9.9182, -84.2411], "PURISCAL": [9.8469, -84.3149],
    "TARRAZU": [9.6596, -84.0206], "DOTA": [9.6500, -83.9600],
    "LEON CORTES": [9.6830, -84.0500], "TURRUBARES": [9.9050, -84.4520],
    "ALAJUELA": [10.0162, -84.2116], "SAN RAMON": [10.0887, -84.4702],
    "GRECIA": [10.0739, -84.3112], "SAN MATEO": [9.9365, -84.5247],
    "ATENAS": [9.9787, -84.3801], "NARANJO": [10.0987, -84.3782],
    "PALMARES": [10.0567, -84.4370], "POAS": [10.0800, -84.2450],
    "OROTINA": [9.9111, -84.5230], "SAN CARLOS": [10.3290, -84.4310],
    "ZARCERO": [10.1852, -84.3900], "SARCHI": [10.0883, -84.3473],
    "UPALA": [10.8986, -85.0155], "LOS CHILES": [11.0350, -84.7130],
    "GUATUSO": [10.6667, -84.8167], "RIO CUARTO": [10.3410, -84.2140],
    "CARTAGO": [9.8644, -83.9194], "PARAISO": [9.8383, -83.8656],
    "LA UNION": [9.9084, -83.9886], "JIMENEZ": [9.9048, -83.6834],
    "TURRIALBA": [9.9050, -83.6830], "ALVARADO": [9.9333, -83.8000],
    "OREAMUNO": [9.9100, -83.9000], "EL GUARCO": [9.8472, -83.9460],
    "HEREDIA": [10.0024, -84.1165], "BARVA": [10.0208, -84.1233],
    "SANTO DOMINGO": [10.0639, -84.1547], "SANTA BARBARA": [10.0400, -84.1600],
    "SAN RAFAEL": [10.0138, -84.1002], "SAN ISIDRO": [10.0186, -84.0569],
    "BELEN": [9.9852, -84.1810], "FLORES": [10.0000, -84.1600],
    "SAN PABLO": [9.9953, -84.0966], "SARAPIQUI": [10.4522, -84.0166],
    "LIBERIA": [10.6350, -85.4377], "NICOYA": [10.1483, -85.4520],
    "SANTA CRUZ": [10.2600, -85.5850], "BAGACES": [10.5250, -85.2550],
    "CARRILLO": [10.4750, -85.5850], "CANAS": [10.4310, -85.0980],
    "ABANGARES": [10.2820, -84.9590], "TILARAN": [10.4670, -84.9670],
    "NANDAYURE": [9.9990, -85.2060], "LA CRUZ": [11.0730, -85.6320],
    "HOJANCHA": [10.0550, -85.4200], "PUNTARENAS": [9.9763, -84.8384],
    "CHOMES": [10.0950, -84.9250], "JUDAS": [10.0510, -84.8870],
    "ESPARZA": [9.9940, -84.6640], "BUENOS AIRES": [9.1667, -83.3333],
    "MONTES DE ORO": [10.0870, -84.7300], "OSA": [8.9590, -83.5230],
    "QUEPOS": [9.4319, -84.1617], "GOLFITO": [8.6390, -83.1660],
    "COTO BRUS": [8.8830, -82.9660], "PARRITA": [9.5200, -84.3200],
    "CORREDORES": [8.6420, -82.9460], "GARABITO": [9.6150, -84.6300],
    "LIMON": [9.9917, -83.0360], "POCOCI": [10.2150, -83.7870],
    "SIQUIRRES": [10.0970, -83.5060], "TALAMANCA": [9.6240, -82.8440],
    "MATINA": [10.0760, -83.2890], "GUACIMO": [10.2100, -83.6900],
    "PEREZ ZELEDON": [9.3540, -83.6340], "LOS SANTOS": [9.6550, -84.0300],
}

PROVINCE_COORDS = {
    "SAN JOSE": [9.9281, -84.0907],
    "ALAJUELA": [10.0162, -84.2116],
    "CARTAGO": [9.8644, -83.9194],
    "HEREDIA": [10.0024, -84.1165],
    "GUANACASTE": [10.6350, -85.4377],
    "PUNTARENAS": [9.9763, -84.8384],
    "LIMON": [9.9917, -83.0360],
}


# ============================================================
# UTILIDADES
# ============================================================
def normalizar(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"\s+", " ", texto)
    return texto


def normalizar_codigo(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip()
    texto = re.sub(r"\.0$", "", texto)
    texto = re.sub(r"[^0-9A-Za-z]", "", texto)
    return texto.upper()


def buscar_columna(columnas, opciones):
    mapa = {c: normalizar(c) for c in columnas}
    opciones_n = [normalizar(x) for x in opciones]

    for col, col_n in mapa.items():
        if col_n in opciones_n:
            return col

    for col, col_n in mapa.items():
        if any(op in col_n or col_n in op for op in opciones_n if op):
            return col
    return None


def detectar_fila_encabezado(df_sin_header):
    """
    Busca la fila real de encabezados dentro de cada hoja.
    En la base MPAS normalmente está en la fila 4.
    """
    palabras = [
        "PROVINCIA", "CANTON", "DISTRITO",
        "NOMBRE DEL CENTRO EDUCATIVO", "CENTRO EDUCATIVO",
        "CODIGO MEP", "TOTAL NINOS"
    ]

    mejor_fila = 0
    mejor_puntaje = -1

    limite = min(20, len(df_sin_header))
    for i in range(limite):
        fila = " | ".join(normalizar(x) for x in df_sin_header.iloc[i].tolist())
        puntaje = sum(1 for p in palabras if p in fila)
        if puntaje > mejor_puntaje:
            mejor_fila = i
            mejor_puntaje = puntaje

    return mejor_fila


@st.cache_data(show_spinner=False)
def leer_libro(contenido, nombre_archivo):
    extension = Path(nombre_archivo).suffix.lower()
    engine = "xlrd" if extension == ".xls" else "openpyxl"

    libro = pd.ExcelFile(io.BytesIO(contenido), engine=engine)
    hojas_limpias = []

    for hoja in libro.sheet_names:
        bruto = pd.read_excel(
            io.BytesIO(contenido),
            sheet_name=hoja,
            header=None,
            engine=engine
        )

        if bruto.dropna(how="all").empty:
            continue

        fila_header = detectar_fila_encabezado(bruto)

        df = pd.read_excel(
            io.BytesIO(contenido),
            sheet_name=hoja,
            header=fila_header,
            engine=engine
        )

        df = df.dropna(how="all")
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
        df.columns = [str(c).strip() for c in df.columns]
        df["HOJA_ORIGEN"] = hoja

        hojas_limpias.append(df)

    if not hojas_limpias:
        return pd.DataFrame()

    return pd.concat(hojas_limpias, ignore_index=True, sort=False)



def preparar_mep(df):
    """
    Lee únicamente las hojas regionales de la base MEP.

    Reglas:
    - Incluye las hojas regionales y la hoja Preescolar.
    - Excluye únicamente las filas finales de totales.
    - Conserva centros con o sin código presupuestario para que el total
      coincida con el total visible de cada hoja regional.
    - La región se toma de HOJA_ORIGEN.
    """
    if "HOJA_ORIGEN" not in df.columns:
        raise ValueError("La base MEP no conserva el nombre de la hoja de origen.")

    df = df.copy()

    col_escuela = buscar_columna(df.columns, [
        "Institución", "Nombre del centro educativo", "Escuela"
    ])
    col_provincia = buscar_columna(df.columns, ["Provincia"])
    col_canton = buscar_columna(df.columns, ["Cantón", "Canton"])
    col_distrito = buscar_columna(df.columns, ["Distrito"])
    col_codigo = buscar_columna(df.columns, [
        "Código presupuestario", "Codigo presupuestario", "Código MEP", "Codigo MEP"
    ])

    requeridas = {
        "institución": col_escuela,
        "provincia": col_provincia,
        "cantón": col_canton,
        "distrito": col_distrito,
    }
    faltantes = [k for k, v in requeridas.items() if v is None]
    if faltantes:
        raise ValueError(
            "No se encontraron en la base MEP las columnas: " + ", ".join(faltantes)
        )

    salida = pd.DataFrame({
        "REGION_MEP": df["HOJA_ORIGEN"].astype(str).str.strip(),
        "ESCUELA_MEP": df[col_escuela],
        "PROVINCIA": df[col_provincia],
        "CANTON": df[col_canton],
        "DISTRITO": df[col_distrito],
        "CODIGO_MEP": df[col_codigo] if col_codigo else "",
    })

    # Una escuela válida debe tener nombre y ubicación territorial.
    # Esto elimina automáticamente las filas finales que solo contienen 312, 397, etc.
    salida = salida.dropna(subset=["ESCUELA_MEP", "PROVINCIA", "CANTON", "DISTRITO"])
    salida["ESCUELA_MEP"] = salida["ESCUELA_MEP"].astype(str).str.strip()

    for col in ["REGION_MEP", "PROVINCIA", "CANTON", "DISTRITO"]:
        salida[col] = salida[col].fillna("").astype(str).str.strip()
        salida[col + "_N"] = salida[col].map(normalizar)

    salida["ESCUELA_MEP_N"] = salida["ESCUELA_MEP"].map(normalizar)
    salida["CODIGO_N"] = salida["CODIGO_MEP"].map(normalizar_codigo)

    salida["CLAVE_NOMBRE"] = (
        salida["REGION_MEP_N"] + "|" +
        salida["PROVINCIA_N"] + "|" +
        salida["CANTON_N"] + "|" +
        salida["DISTRITO_N"] + "|" +
        salida["ESCUELA_MEP_N"]
    )

    salida["ID_ESCUELA"] = np.where(
        salida["CODIGO_N"].ne(""),
        "COD|" + salida["CODIGO_N"],
        "NOM|" + salida["CLAVE_NOMBRE"]
    )

    # No se eliminan centros sin código. Solo se elimina un duplicado exacto
    # dentro de la misma hoja regional.
    return salida.drop_duplicates(
        ["REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N", "ESCUELA_MEP_N"]
    )

def preparar_mpas(df):
    """
    Utiliza únicamente la hoja resumen principal "MPAS".
    Cada fila válida representa un centro educativo abordado según la base MPAS.
    El Código MEP es la llave principal de comparación.
    """
    if "HOJA_ORIGEN" in df.columns:
        mascara_hoja = df["HOJA_ORIGEN"].map(normalizar).eq("MPAS")
        principal = df[mascara_hoja].copy()
        if principal.empty:
            principal = df.copy()
    else:
        principal = df.copy()

    col_escuela = buscar_columna(principal.columns, [
        "Nombre del centro educativo", "Institución", "Escuela"
    ])
    col_provincia = buscar_columna(principal.columns, ["Provincia"])
    col_canton = buscar_columna(principal.columns, ["Cantón", "Canton"])
    col_distrito = buscar_columna(principal.columns, ["Distrito"])
    col_codigo = buscar_columna(principal.columns, ["Código MEP", "Codigo MEP"])
    col_ninos = buscar_columna(principal.columns, [
        "Total niños capacitados", "Total ninos capacitados",
        "Cantidad de niños", "Cantidad ninos", "Niños", "Ninos"
    ])

    requeridas = {
        "nombre del centro educativo": col_escuela,
        "código MEP": col_codigo,
        "total de niños capacitados": col_ninos,
    }
    faltantes = [k for k, v in requeridas.items() if v is None]
    if faltantes:
        raise ValueError(
            "No se encontraron en la hoja resumen MPAS las columnas: "
            + ", ".join(faltantes)
        )

    salida = pd.DataFrame({
        "ESCUELA_MPAS": principal[col_escuela],
        "PROVINCIA_MPAS": principal[col_provincia] if col_provincia else "",
        "CANTON_MPAS": principal[col_canton] if col_canton else "",
        "DISTRITO_MPAS": principal[col_distrito] if col_distrito else "",
        "CODIGO_MEP_ORIGINAL": principal[col_codigo],
        "NINOS": principal[col_ninos],
        "HOJAS": principal["HOJA_ORIGEN"] if "HOJA_ORIGEN" in principal.columns else "MPAS",
    })

    salida = salida.dropna(subset=["ESCUELA_MPAS"])
    salida["ESCUELA_MPAS"] = salida["ESCUELA_MPAS"].astype(str).str.strip()

    # Excluye filas de totales y filas vacías; conserva cada registro real MPAS.
    salida = salida[
        ~salida["ESCUELA_MPAS"].map(normalizar).str.contains("TOTAL NINOS", na=False)
    ]
    salida = salida[salida["ESCUELA_MPAS"].ne("")]

    salida["CODIGO_N"] = salida["CODIGO_MEP_ORIGINAL"].map(normalizar_codigo)
    salida["ESCUELA_MPAS_N"] = salida["ESCUELA_MPAS"].map(normalizar)
    salida["NINOS"] = pd.to_numeric(salida["NINOS"], errors="coerce").fillna(0)

    for col in ["PROVINCIA_MPAS", "CANTON_MPAS", "DISTRITO_MPAS"]:
        salida[col] = salida[col].fillna("").astype(str).str.strip()

    salida = salida.reset_index(drop=True)
    salida["REGISTRO_MPAS_ID"] = np.arange(1, len(salida) + 1)
    return salida


def relacionar_bases(mep, mpas):
    """
    Relación segura:
    1. Código MEP de MPAS = Código presupuestario de MEP.
    2. Solo cuando el código está vacío o mal digitado, se intenta recuperar
       la institución por nombre para fines de revisión.

    El conteo MPAS conserva todos los registros válidos de la hoja resumen.
    """
    catalogo_codigo = (
        mep[mep["CODIGO_N"].ne("")]
        .sort_values("ID_ESCUELA")
        .drop_duplicates("CODIGO_N")[[
            "CODIGO_N", "ID_ESCUELA", "ESCUELA_MEP", "REGION_MEP",
            "PROVINCIA", "CANTON", "DISTRITO",
            "REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N"
        ]]
    )

    resultado = mpas.merge(catalogo_codigo, on="CODIGO_N", how="left")
    resultado["TIPO_COINCIDENCIA"] = np.where(
        resultado["ID_ESCUELA"].notna(),
        "Código MEP / Código presupuestario",
        "Código no encontrado"
    )

    # Respaldo por nombre únicamente para identificar posibles errores de digitación.
    catalogo_nombres = mep[[
        "ID_ESCUELA", "ESCUELA_MEP", "ESCUELA_MEP_N", "REGION_MEP",
        "PROVINCIA", "CANTON", "DISTRITO",
        "REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N", "CODIGO_N"
    ]].drop_duplicates("ID_ESCUELA")

    faltantes = resultado["ID_ESCUELA"].isna()
    opciones = catalogo_nombres["ESCUELA_MEP_N"].tolist()

    for idx, fila in resultado[faltantes].iterrows():
        nombre = fila["ESCUELA_MPAS_N"]
        if not nombre:
            continue

        match = process.extractOne(nombre, opciones, scorer=fuzz.token_sort_ratio)
        if not match or match[1] < 88:
            continue

        candidato = catalogo_nombres[
            catalogo_nombres["ESCUELA_MEP_N"].eq(match[0])
        ].iloc[0]

        for campo in [
            "ID_ESCUELA", "ESCUELA_MEP", "REGION_MEP",
            "PROVINCIA", "CANTON", "DISTRITO",
            "REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N"
        ]:
            resultado.at[idx, campo] = candidato[campo]

        resultado.at[idx, "CODIGO_MEP_CORRECTO"] = candidato["CODIGO_N"]
        resultado.at[idx, "TIPO_COINCIDENCIA"] = (
            f"Revisión por nombre ({match[1]:.0f}%)"
        )

    if "CODIGO_MEP_CORRECTO" not in resultado.columns:
        resultado["CODIGO_MEP_CORRECTO"] = ""
    resultado["CODIGO_MEP_CORRECTO"] = resultado["CODIGO_MEP_CORRECTO"].fillna("")

    # Para códigos exactos, el código correcto es el mismo ingresado.
    exactos = resultado["TIPO_COINCIDENCIA"].eq(
        "Código MEP / Código presupuestario"
    )
    resultado.loc[exactos, "CODIGO_MEP_CORRECTO"] = resultado.loc[exactos, "CODIGO_N"]

    # Si no se pudo identificar en MEP, conserva ubicación MPAS solo para revisión.
    if "REGION_MEP" not in resultado.columns:
        resultado["REGION_MEP"] = "Código no localizado en MEP"
    resultado["REGION_MEP"] = resultado["REGION_MEP"].fillna("Código no localizado en MEP")
    resultado["REGION_MEP_N"] = resultado["REGION_MEP"].map(normalizar)

    resultado["PROVINCIA"] = resultado["PROVINCIA"].fillna(resultado["PROVINCIA_MPAS"])
    resultado["CANTON"] = resultado["CANTON"].fillna(resultado["CANTON_MPAS"])
    resultado["DISTRITO"] = resultado["DISTRITO"].fillna(resultado["DISTRITO_MPAS"])
    resultado["PROVINCIA_N"] = resultado["PROVINCIA"].map(normalizar)
    resultado["CANTON_N"] = resultado["CANTON"].map(normalizar)
    resultado["DISTRITO_N"] = resultado["DISTRITO"].map(normalizar)

    return resultado


def obtener_coordenadas(distrito, canton, provincia):
    for clave in [distrito, canton]:
        if clave in COORDENADAS_REFERENCIA:
            return COORDENADAS_REFERENCIA[clave]
    return PROVINCE_COORDS.get(provincia, [9.7489, -83.7534])



def crear_resumen(mep, relacionados):
    # El universo MEP se cuenta por hoja regional + provincia + cantón + distrito.
    # Así R2 Alajuela conserva exactamente sus 312 centros.
    total_mep = (
        mep.groupby(
            ["REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N"],
            as_index=False
        )
        .agg(
            REGION_MEP=("REGION_MEP", "first"),
            PROVINCIA=("PROVINCIA", "first"),
            CANTON=("CANTON", "first"),
            DISTRITO=("DISTRITO", "first"),
            ESCUELAS_MEP=("ID_ESCUELA", "count"),
        )
    )

    # Solo los registros que pudieron ubicarse en MEP se distribuyen territorialmente.
    ubicados = relacionados[
        relacionados["REGION_MEP_N"].ne("CODIGO NO LOCALIZADO EN MEP")
    ].copy()

    total_mpas = (
        ubicados.groupby(
            ["REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N"],
            as_index=False,
            dropna=False
        )
        .agg(
            ESCUELAS_ABORDADAS=("REGISTRO_MPAS_ID", "count"),
            CENTROS_UNICOS_CODIGO=("CODIGO_MEP_CORRECTO", lambda s: s[s.ne("")].nunique()),
            NINOS_ABORDADOS=("NINOS", "sum"),
        )
    )

    resumen = total_mep.merge(
        total_mpas,
        on=["REGION_MEP_N", "PROVINCIA_N", "CANTON_N", "DISTRITO_N"],
        how="left"
    )

    for col in ["ESCUELAS_ABORDADAS", "CENTROS_UNICOS_CODIGO", "NINOS_ABORDADOS"]:
        resumen[col] = resumen[col].fillna(0)

    resumen["ESCUELAS_ABORDADAS"] = resumen["ESCUELAS_ABORDADAS"].astype(int)
    resumen["CENTROS_UNICOS_CODIGO"] = resumen["CENTROS_UNICOS_CODIGO"].astype(int)
    resumen["NINOS_ABORDADOS"] = resumen["NINOS_ABORDADOS"].round().astype(int)

    resumen["PENDIENTES"] = (
        resumen["ESCUELAS_MEP"] - resumen["ESCUELAS_ABORDADAS"]
    ).clip(lower=0)

    resumen["COBERTURA"] = np.where(
        resumen["ESCUELAS_MEP"] > 0,
        resumen["ESCUELAS_ABORDADAS"] / resumen["ESCUELAS_MEP"] * 100,
        0
    ).round(1)

    coords = resumen.apply(
        lambda r: obtener_coordenadas(
            r["DISTRITO_N"], r["CANTON_N"], r["PROVINCIA_N"]
        ),
        axis=1
    )
    resumen["LAT"] = [c[0] for c in coords]
    resumen["LON"] = [c[1] for c in coords]
    return resumen

def color_cobertura(pct):
    if pct >= 70:
        return "#16a34a"
    if pct >= 40:
        return "#f59e0b"
    if pct > 0:
        return "#ef4444"
    return "#64748b"


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


# ============================================================
# ESTILO
# ============================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 14px;
    border-radius: 14px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.06);
}
.titulo {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
}
.subtitulo {
    color: #475569;
    margin-bottom: 1rem;
}
.resumen {
    border-left: 6px solid #f59e0b;
    background: #fff7ed;
    padding: 16px 20px;
    border-radius: 10px;
    margin: 16px 0;
}
.leyenda {
    background: white;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="titulo">🏫 Seguimiento MPAS 2026</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitulo">Comparación de centros educativos MEP y escuelas abordadas por MPAS.</div>',
    unsafe_allow_html=True
)


# ============================================================
# CARGA DE ARCHIVOS
# ============================================================
with st.sidebar:
    st.header("Carga de archivos")

    archivo_mep = st.file_uploader(
        "Base de datos de escuelas MEP",
        type=["xlsx", "xls"]
    )

    archivo_mpas = st.file_uploader(
        "Base de datos MPAS 2026",
        type=["xlsx", "xls"]
    )

    st.divider()
    st.caption(
        "La aplicación detecta automáticamente la fila real de encabezados "
        "en cada hoja del archivo MPAS."
    )


if not archivo_mep or not archivo_mpas:
    st.info("Cargue ambos archivos desde el panel lateral.")
    st.stop()


try:
    with st.spinner("Leyendo y relacionando las bases..."):
        mep_raw = leer_libro(archivo_mep.getvalue(), archivo_mep.name)
        mpas_raw = leer_libro(archivo_mpas.getvalue(), archivo_mpas.name)

        mep = preparar_mep(mep_raw)
        mpas = preparar_mpas(mpas_raw)
        relacionados = relacionar_bases(mep, mpas)
        resumen = crear_resumen(mep, relacionados)

except Exception as exc:
    st.error(f"No fue posible procesar los archivos: {exc}")
    st.stop()


# ============================================================
# INFORMACIÓN DE LECTURA
# ============================================================
with st.sidebar:
    st.success(f"MEP regional: {len(mep):,} centros leídos")
    st.success(f"MPAS: {len(mpas):,} centros registrados")

    coincidencias = relacionados["TIPO_COINCIDENCIA"].eq("Código MEP / Código presupuestario").sum()
    sin_coincidencia = (~relacionados["TIPO_COINCIDENCIA"].eq("Código MEP / Código presupuestario")).sum()

    st.metric("Coincidencias encontradas", f"{coincidencias:,}")
    st.metric("Sin coincidencia", f"{sin_coincidencia:,}")

    st.caption(
        "Se incluyen todas las hojas, incluida Preescolar. "
        "Solo se excluyen las filas finales que contienen totales y no centros educativos."
    )


# ============================================================
# FILTROS
# ============================================================
st.subheader("Filtros territoriales")

c0, c1, c2, c3 = st.columns(4)

regiones = ["Todas"] + sorted(
    resumen["REGION_MEP"].dropna().unique().tolist()
)
region = c0.selectbox("Región MEP", regiones)

filtrado = resumen.copy()
if region != "Todas":
    filtrado = filtrado[filtrado["REGION_MEP"].eq(region)]

provincias = ["Todas"] + sorted(
    filtrado["PROVINCIA"].dropna().unique().tolist()
)
provincia = c1.selectbox("Provincia", provincias)

if provincia != "Todas":
    filtrado = filtrado[filtrado["PROVINCIA"].eq(provincia)]

cantones = ["Todos"] + sorted(
    filtrado["CANTON"].dropna().unique().tolist()
)
canton = c2.selectbox("Cantón", cantones)

if canton != "Todos":
    filtrado = filtrado[filtrado["CANTON"].eq(canton)]

distritos = ["Todos"] + sorted(
    filtrado["DISTRITO"].dropna().unique().tolist()
)
distrito = c3.selectbox("Distrito", distritos)

if distrito != "Todos":
    filtrado = filtrado[filtrado["DISTRITO"].eq(distrito)]

# Filtro específico para identificar dónde hubo o no actividad MPAS.
filtro_actividad = st.radio(
    "Estado de actividad en el distrito",
    ["Todos", "Con actividad", "Sin actividad"],
    horizontal=True,
    help=(
        "Con actividad: el distrito tiene al menos una escuela abordada. "
        "Sin actividad: no registra escuelas abordadas en la base MPAS."
    )
)

if filtro_actividad == "Con actividad":
    filtrado = filtrado[filtrado["ESCUELAS_ABORDADAS"] > 0]
elif filtro_actividad == "Sin actividad":
    filtrado = filtrado[filtrado["ESCUELAS_ABORDADAS"] == 0]


# ============================================================
# MÉTRICAS
# ============================================================
total_mep = int(filtrado["ESCUELAS_MEP"].sum())
total_abordadas_ubicadas = int(filtrado["ESCUELAS_ABORDADAS"].sum())
total_ninos_ubicados = int(filtrado["NINOS_ABORDADOS"].sum())

# Cuando no hay filtros territoriales ni filtro de actividad, se conserva
# íntegramente el total reportado por MPAS, aunque existan códigos pendientes.
vista_nacional_completa = (
    region == "Todas"
    and provincia == "Todas"
    and canton == "Todos"
    and distrito == "Todos"
    and filtro_actividad == "Todos"
)

if vista_nacional_completa:
    total_abordadas = int(len(mpas))
    total_ninos = int(mpas["NINOS"].sum())
else:
    total_abordadas = total_abordadas_ubicadas
    total_ninos = total_ninos_ubicados

total_pendientes = max(total_mep - total_abordadas, 0)
cobertura = (total_abordadas / total_mep * 100) if total_mep else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Centros MEP válidos", f"{total_mep:,}")
m2.metric("Centros abordados MPAS", f"{total_abordadas:,}")
m3.metric("Centros pendientes", f"{total_pendientes:,}")
m4.metric("Niños reportados MPAS", f"{total_ninos:,}")
m5.metric("Cobertura", f"{cobertura:.1f}%")

territorio = "Costa Rica"
if region != "Todas":
    territorio = region
if provincia != "Todas":
    territorio = provincia
if canton != "Todos":
    territorio = f"{canton}, {provincia}"
if distrito != "Todos":
    territorio = f"{distrito}, {canton}, {provincia}"

pendientes_codigo = int(
    ~relacionados["TIPO_COINCIDENCIA"].eq(
        "Código MEP / Código presupuestario"
    )
).sum()

st.markdown(
    f"""
    <div class="resumen">
    Según la base MEP, en <b>{territorio}</b> existen
    <b>{total_mep:,} centros educativos válidos</b>. La base MPAS reporta
    <b>{total_abordadas:,} centros abordados</b> y
    <b>{total_ninos:,} niños</b>. La cobertura corresponde al
    <b>{cobertura:.1f}%</b>.
    </div>
    """,
    unsafe_allow_html=True
)

if vista_nacional_completa and pendientes_codigo > 0:
    st.info(
        f"MPAS contiene {len(mpas):,} registros. "
        f"{total_abordadas_ubicadas:,} ya están ubicados territorialmente mediante "
        f"el Código MEP y {pendientes_codigo:,} están pendientes de corregir o validar. "
        "Los pendientes sí se mantienen incluidos en el total nacional."
    )

with st.expander("Control de cifras de las bases"):
    st.write(
        f"**Base MEP:** {len(mep):,} filas válidas de centros educativos. "
        "Las filas finales que solo muestran el total de cada hoja no se cuentan como escuelas."
    )
    st.write(
        f"**Base MPAS:** {len(mpas):,} centros reportados y "
        f"{int(mpas['NINOS'].sum()):,} niños reportados."
    )
    st.write(
        f"**Georreferenciados por Código MEP:** {total_abordadas_ubicadas:,} centros "
        f"y {total_ninos_ubicados:,} niños para la vista territorial actual."
    )


# ============================================================
# PESTAÑAS
# ============================================================
tab_mapa, tab_comp, tab_lista, tab_revision = st.tabs([
    "🗺️ Mapa",
    "📊 Comparativa territorial",
    "🏫 Escuelas abordadas",
    "⚠️ Revisión de coincidencias"
])


with tab_mapa:
    st.markdown("""
    <div class="leyenda">
    <b>Leyenda del mapa blanco:</b>
    🟢 Distrito con actividad MPAS &nbsp;&nbsp;
    🔴 Distrito sin actividad MPAS
    </div>
    """, unsafe_allow_html=True)

    if filtrado.empty:
        st.warning("No existen datos para los filtros seleccionados.")
    else:
        centro = [
            float(filtrado["LAT"].mean()),
            float(filtrado["LON"].mean())
        ]

        zoom = 8
        if provincia != "Todas":
            zoom = 10
        if canton != "Todos":
            zoom = 11
        if distrito != "Todos":
            zoom = 13

        mapa = folium.Map(
            location=centro,
            zoom_start=zoom,
            tiles="CartoDB positron",
            control_scale=True,
            prefer_canvas=True
        )

        for _, fila in filtrado.iterrows():
            tiene_actividad = int(fila["ESCUELAS_ABORDADAS"]) > 0
            color_pin = "green" if tiene_actividad else "red"
            icono_pin = "ok" if tiene_actividad else "remove"
            estado = "CON ACTIVIDAD" if tiene_actividad else "SIN ACTIVIDAD"

            popup = folium.Popup(
                f"""
                <div style="width:305px;font-family:Arial">
                    <h4 style="margin-bottom:5px">{fila['DISTRITO']}</h4>
                    <b>Estado:</b> {estado}<br>
                    <b>Región MEP:</b> {fila['REGION_MEP']}<br>
                    <b>Provincia:</b> {fila['PROVINCIA']}<br>
                    <b>Cantón:</b> {fila['CANTON']}<br><hr>
                    <b>Escuelas MEP:</b> {int(fila['ESCUELAS_MEP'])}<br>
                    <b>Centros MPAS ubicados:</b> {int(fila['ESCUELAS_ABORDADAS'])}<br>
                    <b>Escuelas pendientes:</b> {int(fila['PENDIENTES'])}<br>
                    <b>Niños abordados:</b> {int(fila['NINOS_ABORDADOS'])}<br>
                    <b>Cobertura:</b> {float(fila['COBERTURA']):.1f}%
                </div>
                """,
                max_width=350
            )

            folium.Marker(
                location=[fila["LAT"], fila["LON"]],
                icon=folium.Icon(
                    color=color_pin,
                    icon=icono_pin,
                    prefix="glyphicon"
                ),
                tooltip=(
                    f"{fila['DISTRITO']} · {estado}: "
                    f"{int(fila['ESCUELAS_ABORDADAS'])}/"
                    f"{int(fila['ESCUELAS_MEP'])} escuelas"
                ),
                popup=popup
            ).add_to(mapa)

        st_folium(
            mapa,
            use_container_width=True,
            height=620,
            returned_objects=[]
        )


with tab_comp:
    nivel = st.radio(
        "Agrupar información por",
        ["Región MEP", "Provincia", "Cantón", "Distrito"],
        horizontal=True
    )

    grupos = {
        "Región MEP": ["REGION_MEP"],
        "Provincia": ["PROVINCIA"],
        "Cantón": ["PROVINCIA", "CANTON"],
        "Distrito": ["PROVINCIA", "CANTON", "DISTRITO"]
    }[nivel]

    comparativa = (
        filtrado.groupby(grupos, as_index=False)
        .agg(
            ESCUELAS_MEP=("ESCUELAS_MEP", "sum"),
            ESCUELAS_ABORDADAS=("ESCUELAS_ABORDADAS", "sum"),
            PENDIENTES=("PENDIENTES", "sum"),
            NINOS_ABORDADOS=("NINOS_ABORDADOS", "sum")
        )
    )

    comparativa["COBERTURA_PCT"] = np.where(
        comparativa["ESCUELAS_MEP"] > 0,
        comparativa["ESCUELAS_ABORDADAS"] /
        comparativa["ESCUELAS_MEP"] * 100,
        0
    ).round(1)

    comparativa = comparativa.sort_values(
        ["COBERTURA_PCT", "ESCUELAS_MEP"],
        ascending=[False, False]
    )

    mostrar = comparativa.rename(columns={
        "REGION_MEP": "Región MEP",
        "PROVINCIA": "Provincia",
        "CANTON": "Cantón",
        "DISTRITO": "Distrito",
        "ESCUELAS_MEP": "Escuelas MEP",
        "ESCUELAS_ABORDADAS": "Escuelas abordadas",
        "PENDIENTES": "Pendientes",
        "NINOS_ABORDADOS": "Niños abordados",
        "COBERTURA_PCT": "Cobertura %"
    })

    st.dataframe(
        mostrar,
        use_container_width=True,
        hide_index=True
    )

    grafico = comparativa.copy()
    grafico["Territorio"] = grafico[grupos].astype(str).agg(" - ".join, axis=1)

    st.bar_chart(
        grafico.set_index("Territorio")[
            ["ESCUELAS_MEP", "ESCUELAS_ABORDADAS"]
        ],
        use_container_width=True
    )

    st.download_button(
        "Descargar comparativa CSV",
        data=csv_bytes(mostrar),
        file_name="comparativa_territorial_mpas.csv",
        mime="text/csv"
    )


with tab_lista:
    abordadas = relacionados[
        relacionados["ID_ESCUELA"].notna()
    ].copy()

    if region != "Todas":
        abordadas = abordadas[
            abordadas["REGION_MEP"].eq(region)
        ]

    if provincia != "Todas":
        abordadas = abordadas[
            abordadas["PROVINCIA"].map(normalizar).eq(normalizar(provincia))
        ]

    if canton != "Todos":
        abordadas = abordadas[
            abordadas["CANTON"].map(normalizar).eq(normalizar(canton))
        ]

    if distrito != "Todos":
        abordadas = abordadas[
            abordadas["DISTRITO"].map(normalizar).eq(normalizar(distrito))
        ]

    columnas = [
        "REGION_MEP", "PROVINCIA", "CANTON", "DISTRITO",
        "ESCUELA_MEP", "ESCUELA_MPAS",
        "CODIGO_N", "CODIGO_MEP_CORRECTO", "NINOS", "TIPO_COINCIDENCIA"
    ]

    lista = abordadas[columnas].sort_values(
        ["PROVINCIA", "CANTON", "DISTRITO", "ESCUELA_MEP"]
    )

    lista = lista.rename(columns={
        "REGION_MEP": "Región MEP",
        "PROVINCIA": "Provincia",
        "CANTON": "Cantón",
        "DISTRITO": "Distrito",
        "ESCUELA_MEP": "Escuela según MEP",
        "ESCUELA_MPAS": "Escuela registrada en MPAS",
        "CODIGO_N": "Código registrado en MPAS",
        "CODIGO_MEP_CORRECTO": "Código presupuestario MEP",
        "NINOS": "Niños abordados",
        "TIPO_COINCIDENCIA": "Tipo de coincidencia"
    })

    st.dataframe(
        lista,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Descargar escuelas abordadas CSV",
        data=csv_bytes(lista),
        file_name="escuelas_abordadas_mpas.csv",
        mime="text/csv"
    )


with tab_revision:
    sin_match = relacionados[
        relacionados["ID_ESCUELA"].isna()
    ].copy()

    st.metric(
        "Registros MPAS sin coincidencia con MEP",
        f"{len(sin_match):,}"
    )

    if sin_match.empty:
        st.success(
            "Todas las escuelas registradas en MPAS fueron relacionadas "
            "con la base MEP."
        )
    else:
        st.warning(
            "Estos registros no se contabilizan como escuelas abordadas "
            "hasta que el nombre, código o ubicación coincida con la base MEP."
        )

        columnas_revision = [
            "PROVINCIA", "CANTON", "DISTRITO",
            "ESCUELA_MPAS", "CODIGO_N", "NINOS", "HOJAS"
        ]

        # reindex evita que la aplicación se detenga si una columna opcional
        # no está presente en una futura versión del archivo.
        revision = sin_match.reindex(columns=columnas_revision).copy()
        revision["HOJAS"] = revision["HOJAS"].fillna("MPAS")

        revision = revision.rename(columns={
            "PROVINCIA": "Provincia",
            "CANTON": "Cantón",
            "DISTRITO": "Distrito",
            "ESCUELA_MPAS": "Escuela registrada en MPAS",
            "CODIGO_N": "Código MEP registrado",
            "NINOS": "Niños",
            "HOJAS": "Hoja de origen"
        })

        st.dataframe(
            revision,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Descargar registros sin coincidencia",
            data=csv_bytes(revision),
            file_name="registros_mpas_sin_coincidencia.csv",
            mime="text/csv"
        )
