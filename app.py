import io
import re
import unicodedata
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Seguimiento MPAS 2026",
    page_icon="🏫",
    layout="wide",
)

# -------------------------------------------------------------------
# Coordenadas de referencia aportadas por el usuario.
# Se utilizan primero por distrito y luego, como respaldo, por cantón.
# -------------------------------------------------------------------
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
    "SAN JOSE": [9.9281, -84.0907], "ALAJUELA": [10.0162, -84.2116],
    "CARTAGO": [9.8644, -83.9194], "HEREDIA": [10.0024, -84.1165],
    "GUANACASTE": [10.6350, -85.4377], "PUNTARENAS": [9.9763, -84.8384],
    "LIMON": [9.9917, -83.0360],
}

ALIASES = {
    "escuela": [
        "institucion", "institución", "escuela", "centro educativo",
        "nombre institucion", "nombre institución", "nombre escuela",
        "centro", "nombre del centro educativo"
    ],
    "provincia": ["provincia"],
    "canton": ["canton", "cantón"],
    "distrito": ["distrito"],
    "ninos": [
        "niños", "ninos", "cantidad de niños", "cantidad ninos",
        "total niños", "total ninos", "estudiantes", "participantes",
        "cantidad estudiantes", "cantidad participantes", "beneficiarios",
        "poblacion abordada", "población abordada"
    ],
    "codigo": ["codigo presupuestario", "código presupuestario", "codigo", "código"],
}


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"\s+", " ", texto)
    return texto


def normalizar_nombre_columna(valor):
    texto = normalizar_texto(valor).lower()
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def buscar_columna(columnas, tipo):
    columnas_norm = {col: normalizar_nombre_columna(col) for col in columnas}
    aliases = [normalizar_nombre_columna(x) for x in ALIASES[tipo]]

    for col, col_norm in columnas_norm.items():
        if col_norm in aliases:
            return col

    for col, col_norm in columnas_norm.items():
        if any(alias in col_norm or col_norm in alias for alias in aliases if alias):
            return col
    return None


def limpiar_dataframe(df):
    df = df.copy()
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df.columns = [str(c).strip() for c in df.columns]
    return df


@st.cache_data(show_spinner=False)
def leer_excel_bytes(contenido, nombre_archivo):
    extension = Path(nombre_archivo).suffix.lower()
    motor = "xlrd" if extension == ".xls" else "openpyxl"
    hojas = pd.read_excel(io.BytesIO(contenido), sheet_name=None, engine=motor)

    partes = []
    for nombre_hoja, df in hojas.items():
        df = limpiar_dataframe(df)
        if df.empty:
            continue
        df["__HOJA_ORIGEN"] = nombre_hoja
        partes.append(df)

    if not partes:
        return pd.DataFrame()

    return pd.concat(partes, ignore_index=True, sort=False)


def preparar_mep(df):
    col_escuela = buscar_columna(df.columns, "escuela")
    col_provincia = buscar_columna(df.columns, "provincia")
    col_canton = buscar_columna(df.columns, "canton")
    col_distrito = buscar_columna(df.columns, "distrito")
    col_codigo = buscar_columna(df.columns, "codigo")

    obligatorias = {
        "Escuela": col_escuela,
        "Provincia": col_provincia,
        "Cantón": col_canton,
        "Distrito": col_distrito,
    }
    faltantes = [nombre for nombre, col in obligatorias.items() if col is None]
    if faltantes:
        raise ValueError("En la base MEP no se encontraron: " + ", ".join(faltantes))

    salida = pd.DataFrame({
        "ESCUELA_MEP": df[col_escuela].astype(str).str.strip(),
        "PROVINCIA": df[col_provincia].astype(str).str.strip(),
        "CANTON": df[col_canton].astype(str).str.strip(),
        "DISTRITO": df[col_distrito].astype(str).str.strip(),
        "CODIGO_MEP": df[col_codigo].astype(str).str.strip() if col_codigo else "",
    })
    salida = salida.replace({"nan": "", "None": ""})
    salida = salida[salida["ESCUELA_MEP"].ne("")]
    for col in ["ESCUELA_MEP", "PROVINCIA", "CANTON", "DISTRITO"]:
        salida[f"{col}_N"] = salida[col].map(normalizar_texto)

    salida["CLAVE_ESCUELA"] = (
        salida["PROVINCIA_N"] + "|" + salida["CANTON_N"] + "|" +
        salida["DISTRITO_N"] + "|" + salida["ESCUELA_MEP_N"]
    )
    salida = salida.drop_duplicates("CLAVE_ESCUELA")
    return salida


def selector_columna(etiqueta, columnas, sugerida, key, permitir_vacia=False):
    opciones = list(columnas)
    if permitir_vacia:
        opciones = ["— No disponible —"] + opciones

    indice = 0
    if sugerida in opciones:
        indice = opciones.index(sugerida)

    seleccion = st.selectbox(etiqueta, opciones, index=indice, key=key)
    if seleccion == "— No disponible —":
        return None
    return seleccion


def preparar_mpas(df, mapeo):
    salida = pd.DataFrame({
        "ESCUELA_MPAS": df[mapeo["escuela"]].astype(str).str.strip(),
        "PROVINCIA": df[mapeo["provincia"]].astype(str).str.strip(),
        "CANTON": df[mapeo["canton"]].astype(str).str.strip(),
        "DISTRITO": df[mapeo["distrito"]].astype(str).str.strip(),
    })

    if mapeo["ninos"]:
        salida["NINOS"] = pd.to_numeric(df[mapeo["ninos"]], errors="coerce").fillna(0)
    else:
        salida["NINOS"] = 0

    salida = salida.replace({"nan": "", "None": ""})
    salida = salida[salida["ESCUELA_MPAS"].ne("")]

    for col in ["ESCUELA_MPAS", "PROVINCIA", "CANTON", "DISTRITO"]:
        salida[f"{col}_N"] = salida[col].map(normalizar_texto)

    salida["CLAVE_ESCUELA"] = (
        salida["PROVINCIA_N"] + "|" + salida["CANTON_N"] + "|" +
        salida["DISTRITO_N"] + "|" + salida["ESCUELA_MPAS_N"]
    )

    # Una escuela puede aparecer varias veces por actividades distintas.
    # Se suma la cantidad de niños y se considera una sola escuela abordada.
    salida = (
        salida.groupby(
            ["CLAVE_ESCUELA", "ESCUELA_MPAS", "PROVINCIA", "CANTON", "DISTRITO",
             "PROVINCIA_N", "CANTON_N", "DISTRITO_N"],
            as_index=False,
            dropna=False,
        )
        .agg(NINOS=("NINOS", "sum"))
    )
    return salida


def coincidencia_aproximada(mep, mpas):
    """
    Primero empareja por provincia/cantón/distrito/nombre exacto normalizado.
    Luego intenta coincidencia aproximada dentro de la misma ubicación.
    """
    base = mpas.merge(
        mep[["CLAVE_ESCUELA", "ESCUELA_MEP"]],
        on="CLAVE_ESCUELA",
        how="left",
    )
    base["COINCIDENCIA"] = np.where(base["ESCUELA_MEP"].notna(), "Exacta", "No encontrada")

    faltantes = base["ESCUELA_MEP"].isna()
    if faltantes.any():
        try:
            from rapidfuzz import process, fuzz

            catalogos = {}
            for claves, grupo in mep.groupby(["PROVINCIA_N", "CANTON_N", "DISTRITO_N"]):
                catalogos[claves] = grupo[["ESCUELA_MEP_N", "ESCUELA_MEP"]].drop_duplicates()

            for idx, fila in base[faltantes].iterrows():
                ubicacion = (fila["PROVINCIA_N"], fila["CANTON_N"], fila["DISTRITO_N"])
                catalogo = catalogos.get(ubicacion)
                if catalogo is None or catalogo.empty:
                    continue

                opciones = catalogo["ESCUELA_MEP_N"].tolist()
                resultado = process.extractOne(
                    fila["ESCUELA_MPAS_N"], opciones, scorer=fuzz.token_sort_ratio
                )
                if resultado and resultado[1] >= 88:
                    escuela_norm = resultado[0]
                    nombre_real = catalogo.loc[
                        catalogo["ESCUELA_MEP_N"].eq(escuela_norm), "ESCUELA_MEP"
                    ].iloc[0]
                    base.at[idx, "ESCUELA_MEP"] = nombre_real
                    base.at[idx, "COINCIDENCIA"] = f"Aproximada ({resultado[1]:.0f}%)"
        except Exception:
            pass

    return base


def obtener_coordenadas(distrito_n, canton_n, provincia_n):
    for clave in [distrito_n, canton_n]:
        if clave in COORDENADAS_REFERENCIA:
            return COORDENADAS_REFERENCIA[clave]
    return PROVINCE_COORDS.get(provincia_n, [9.7489, -83.7534])


def construir_resumen(mep, mpas_match):
    total_mep = (
        mep.groupby(["PROVINCIA_N", "CANTON_N", "DISTRITO_N"], as_index=False)
        .agg(
            ESCUELAS_MEP=("CLAVE_ESCUELA", "nunique"),
            PROVINCIA=("PROVINCIA", "first"),
            CANTON=("CANTON", "first"),
            DISTRITO=("DISTRITO", "first"),
        )
    )

    abordadas = mpas_match[mpas_match["ESCUELA_MEP"].notna()].copy()
    total_mpas = (
        abordadas.groupby(["PROVINCIA_N", "CANTON_N", "DISTRITO_N"], as_index=False)
        .agg(
            ESCUELAS_ABORDADAS=("ESCUELA_MEP", "nunique"),
            NINOS_ABORDADOS=("NINOS", "sum"),
        )
    )

    resumen = total_mep.merge(
        total_mpas,
        on=["PROVINCIA_N", "CANTON_N", "DISTRITO_N"],
        how="left",
    )
    resumen[["ESCUELAS_ABORDADAS", "NINOS_ABORDADOS"]] = (
        resumen[["ESCUELAS_ABORDADAS", "NINOS_ABORDADOS"]].fillna(0)
    )
    resumen["ESCUELAS_ABORDADAS"] = resumen["ESCUELAS_ABORDADAS"].astype(int)
    resumen["NINOS_ABORDADOS"] = resumen["NINOS_ABORDADOS"].round().astype(int)
    resumen["COBERTURA_PCT"] = np.where(
        resumen["ESCUELAS_MEP"] > 0,
        resumen["ESCUELAS_ABORDADAS"] / resumen["ESCUELAS_MEP"] * 100,
        0,
    ).round(1)

    coords = resumen.apply(
        lambda r: obtener_coordenadas(r["DISTRITO_N"], r["CANTON_N"], r["PROVINCIA_N"]),
        axis=1,
    )
    resumen["LAT"] = [x[0] for x in coords]
    resumen["LON"] = [x[1] for x in coords]
    return resumen


def archivo_descarga(df):
    return df.to_csv(index=False).encode("utf-8-sig")


st.markdown("""
<style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e4e7ec;
        padding: 14px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,.04);
    }
    .titulo {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: .15rem;
    }
    .subtitulo {color: #667085; margin-bottom: 1rem;}
    .detalle {
        border-left: 5px solid #d97706;
        background: #fff8eb;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 8px 0 16px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">🏫 Seguimiento MPAS 2026</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitulo">Comparación entre la base oficial de centros educativos MEP '
    'y las escuelas abordadas por MPAS.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Carga de archivos")
    archivo_mep = st.file_uploader(
        "Base de datos de escuelas MEP",
        type=["xlsx", "xls"],
        help="Puede contener varias hojas; se consolidan automáticamente.",
    )
    archivo_mpas = st.file_uploader(
        "Base de datos MPAS 2026",
        type=["xlsx", "xls"],
        help="Debe incluir escuela, provincia, cantón, distrito y cantidad de niños.",
    )

if not archivo_mep or not archivo_mpas:
    st.info(
        "Cargue en el panel lateral la base MEP y la base MPAS para generar el seguimiento."
    )
    st.stop()

try:
    with st.spinner("Leyendo y consolidando las bases..."):
        mep_raw = leer_excel_bytes(archivo_mep.getvalue(), archivo_mep.name)
        mpas_raw = leer_excel_bytes(archivo_mpas.getvalue(), archivo_mpas.name)
        mep = preparar_mep(mep_raw)
except Exception as exc:
    st.error(f"No fue posible preparar los archivos: {exc}")
    st.stop()

st.sidebar.divider()
st.sidebar.subheader("Columnas de la base MPAS")

columnas_mpas = list(mpas_raw.columns)
auto = {
    "escuela": buscar_columna(columnas_mpas, "escuela"),
    "provincia": buscar_columna(columnas_mpas, "provincia"),
    "canton": buscar_columna(columnas_mpas, "canton"),
    "distrito": buscar_columna(columnas_mpas, "distrito"),
    "ninos": buscar_columna(columnas_mpas, "ninos"),
}

mapeo = {
    "escuela": selector_columna("Escuela o institución", columnas_mpas, auto["escuela"], "map_escuela"),
    "provincia": selector_columna("Provincia", columnas_mpas, auto["provincia"], "map_provincia"),
    "canton": selector_columna("Cantón", columnas_mpas, auto["canton"], "map_canton"),
    "distrito": selector_columna("Distrito", columnas_mpas, auto["distrito"], "map_distrito"),
    "ninos": selector_columna(
        "Cantidad de niños", columnas_mpas, auto["ninos"], "map_ninos", permitir_vacia=True
    ),
}

try:
    mpas = preparar_mpas(mpas_raw, mapeo)
    mpas_match = coincidencia_aproximada(mep, mpas)
    resumen = construir_resumen(mep, mpas_match)
except Exception as exc:
    st.error(f"No fue posible procesar la base MPAS: {exc}")
    st.stop()

# ---------------------------------------------------------
# Filtros jerárquicos
# ---------------------------------------------------------
st.subheader("Filtros territoriales")
f1, f2, f3 = st.columns(3)

provincias = ["Todas"] + sorted(resumen["PROVINCIA"].dropna().unique().tolist())
provincia_sel = f1.selectbox("Provincia", provincias)

base_filtro = resumen.copy()
if provincia_sel != "Todas":
    base_filtro = base_filtro[base_filtro["PROVINCIA"].eq(provincia_sel)]

cantones = ["Todos"] + sorted(base_filtro["CANTON"].dropna().unique().tolist())
canton_sel = f2.selectbox("Cantón", cantones)

if canton_sel != "Todos":
    base_filtro = base_filtro[base_filtro["CANTON"].eq(canton_sel)]

distritos = ["Todos"] + sorted(base_filtro["DISTRITO"].dropna().unique().tolist())
distrito_sel = f3.selectbox("Distrito", distritos)

if distrito_sel != "Todos":
    base_filtro = base_filtro[base_filtro["DISTRITO"].eq(distrito_sel)]

# ---------------------------------------------------------
# Indicadores
# ---------------------------------------------------------
escuelas_mep = int(base_filtro["ESCUELAS_MEP"].sum())
escuelas_abordadas = int(base_filtro["ESCUELAS_ABORDADAS"].sum())
ninos = int(base_filtro["NINOS_ABORDADOS"].sum())
cobertura = (escuelas_abordadas / escuelas_mep * 100) if escuelas_mep else 0
pendientes = max(escuelas_mep - escuelas_abordadas, 0)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Escuelas MEP", f"{escuelas_mep:,}")
m2.metric("Escuelas abordadas", f"{escuelas_abordadas:,}")
m3.metric("Escuelas pendientes", f"{pendientes:,}")
m4.metric("Niños abordados", f"{ninos:,}")
m5.metric("Cobertura", f"{cobertura:.1f}%")

territorio = "Costa Rica"
if provincia_sel != "Todas":
    territorio = provincia_sel
if canton_sel != "Todos":
    territorio = f"{canton_sel}, {provincia_sel}"
if distrito_sel != "Todos":
    territorio = f"{distrito_sel}, {canton_sel}, {provincia_sel}"

st.markdown(
    f"""
    <div class="detalle">
      Según la base de datos MEP, en <b>{territorio}</b> hay
      <b>{escuelas_mep:,} escuelas</b>. Según la base MPAS 2026,
      se abordaron <b>{escuelas_abordadas:,} escuelas</b>, con un total de
      <b>{ninos:,} niños abordados</b>. La cobertura corresponde al
      <b>{cobertura:.1f}%</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["🗺️ Mapa", "📊 Comparativa territorial", "🏫 Escuelas abordadas", "⚠️ Revisión de coincidencias"]
)

with tab1:
    st.caption(
        "Cada marcador representa un distrito. El tamaño refleja la cantidad de escuelas "
        "MEP y el color indica el nivel de cobertura."
    )
    centro = [
        float(base_filtro["LAT"].mean()) if not base_filtro.empty else 9.7489,
        float(base_filtro["LON"].mean()) if not base_filtro.empty else -83.7534,
    ]
    zoom = 8 if provincia_sel == "Todas" else 10
    if canton_sel != "Todos":
        zoom = 12

    mapa = folium.Map(location=centro, zoom_start=zoom, tiles="CartoDB positron")

    for _, fila in base_filtro.iterrows():
        cobertura_fila = float(fila["COBERTURA_PCT"])
        color = "green" if cobertura_fila >= 70 else "orange" if cobertura_fila >= 40 else "red"
        popup = folium.Popup(
            f"""
            <div style="width:270px">
              <b>{fila['DISTRITO']}</b><br>
              Cantón: {fila['CANTON']}<br>
              Provincia: {fila['PROVINCIA']}<hr>
              Escuelas MEP: <b>{int(fila['ESCUELAS_MEP'])}</b><br>
              Escuelas abordadas: <b>{int(fila['ESCUELAS_ABORDADAS'])}</b><br>
              Niños abordados: <b>{int(fila['NINOS_ABORDADOS'])}</b><br>
              Cobertura: <b>{cobertura_fila:.1f}%</b>
            </div>
            """,
            max_width=320,
        )
        folium.CircleMarker(
            location=[fila["LAT"], fila["LON"]],
            radius=max(6, min(18, 5 + float(fila["ESCUELAS_MEP"]) ** 0.5)),
            color=color,
            fill=True,
            fill_opacity=0.78,
            weight=2,
            tooltip=f"{fila['DISTRITO']} · {int(fila['ESCUELAS_ABORDADAS'])}/{int(fila['ESCUELAS_MEP'])}",
            popup=popup,
        ).add_to(mapa)

    st_folium(mapa, use_container_width=True, height=590, returned_objects=[])

with tab2:
    nivel = st.radio(
        "Agrupar por",
        ["Provincia", "Cantón", "Distrito"],
        horizontal=True,
    )
    columnas_grupo = {
        "Provincia": ["PROVINCIA"],
        "Cantón": ["PROVINCIA", "CANTON"],
        "Distrito": ["PROVINCIA", "CANTON", "DISTRITO"],
    }[nivel]

    comparativa = (
        base_filtro.groupby(columnas_grupo, as_index=False)
        .agg(
            ESCUELAS_MEP=("ESCUELAS_MEP", "sum"),
            ESCUELAS_ABORDADAS=("ESCUELAS_ABORDADAS", "sum"),
            NINOS_ABORDADOS=("NINOS_ABORDADOS", "sum"),
        )
    )
    comparativa["PENDIENTES"] = (
        comparativa["ESCUELAS_MEP"] - comparativa["ESCUELAS_ABORDADAS"]
    ).clip(lower=0)
    comparativa["COBERTURA_PCT"] = np.where(
        comparativa["ESCUELAS_MEP"] > 0,
        comparativa["ESCUELAS_ABORDADAS"] / comparativa["ESCUELAS_MEP"] * 100,
        0,
    ).round(1)
    comparativa = comparativa.sort_values(
        ["COBERTURA_PCT", "ESCUELAS_MEP"], ascending=[False, False]
    )

    st.dataframe(
        comparativa.rename(columns={
            "PROVINCIA": "Provincia",
            "CANTON": "Cantón",
            "DISTRITO": "Distrito",
            "ESCUELAS_MEP": "Escuelas MEP",
            "ESCUELAS_ABORDADAS": "Escuelas abordadas",
            "PENDIENTES": "Pendientes",
            "NINOS_ABORDADOS": "Niños abordados",
            "COBERTURA_PCT": "Cobertura %",
        }),
        use_container_width=True,
        hide_index=True,
    )

    grafico = comparativa.copy()
    grafico["Territorio"] = grafico[columnas_grupo].astype(str).agg(" - ".join, axis=1)
    st.bar_chart(
        grafico.set_index("Territorio")[["ESCUELAS_MEP", "ESCUELAS_ABORDADAS"]],
        use_container_width=True,
    )

    st.download_button(
        "Descargar comparativa CSV",
        data=archivo_descarga(comparativa),
        file_name="comparativa_mpas.csv",
        mime="text/csv",
    )

with tab3:
    abordadas = mpas_match[mpas_match["ESCUELA_MEP"].notna()].copy()

    if provincia_sel != "Todas":
        abordadas = abordadas[abordadas["PROVINCIA"].eq(provincia_sel)]
    if canton_sel != "Todos":
        abordadas = abordadas[abordadas["CANTON"].eq(canton_sel)]
    if distrito_sel != "Todos":
        abordadas = abordadas[abordadas["DISTRITO"].eq(distrito_sel)]

    lista = abordadas[[
        "PROVINCIA", "CANTON", "DISTRITO", "ESCUELA_MEP",
        "ESCUELA_MPAS", "NINOS", "COINCIDENCIA"
    ]].sort_values(["PROVINCIA", "CANTON", "DISTRITO", "ESCUELA_MEP"])

    st.dataframe(
        lista.rename(columns={
            "PROVINCIA": "Provincia",
            "CANTON": "Cantón",
            "DISTRITO": "Distrito",
            "ESCUELA_MEP": "Escuela MEP",
            "ESCUELA_MPAS": "Nombre registrado en MPAS",
            "NINOS": "Niños abordados",
            "COINCIDENCIA": "Coincidencia",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Descargar escuelas abordadas CSV",
        data=archivo_descarga(lista),
        file_name="escuelas_abordadas_mpas.csv",
        mime="text/csv",
    )

with tab4:
    no_encontradas = mpas_match[mpas_match["ESCUELA_MEP"].isna()].copy()
    st.metric("Registros MPAS sin coincidencia MEP", len(no_encontradas))

    if no_encontradas.empty:
        st.success("Todos los centros registrados en MPAS fueron asociados con la base MEP.")
    else:
        st.warning(
            "Estos registros no se contabilizan como escuelas MEP abordadas hasta corregir "
            "el nombre o la ubicación en la base MPAS."
        )
        st.dataframe(
            no_encontradas[[
                "PROVINCIA", "CANTON", "DISTRITO", "ESCUELA_MPAS", "NINOS"
            ]].rename(columns={
                "PROVINCIA": "Provincia",
                "CANTON": "Cantón",
                "DISTRITO": "Distrito",
                "ESCUELA_MPAS": "Escuela registrada en MPAS",
                "NINOS": "Niños",
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Descargar registros sin coincidencia",
            data=archivo_descarga(no_encontradas),
            file_name="mpas_sin_coincidencia_mep.csv",
            mime="text/csv",
        )
