import io, math, re, unicodedata
from pathlib import Path
import folium, numpy as np, pandas as pd, streamlit as st
from rapidfuzz import fuzz, process
from streamlit_folium import st_folium
st.set_page_config(page_title="Seguimiento MPAS y GREAT 2026",page_icon="🏫",layout="wide")
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

def normalizar(v):
    if pd.isna(v): return ""
    t=unicodedata.normalize("NFD",str(v).strip().upper())
    return re.sub(r"\s+"," ","".join(c for c in t if unicodedata.category(c)!="Mn"))
def normalizar_codigo(v):
    if pd.isna(v): return ""
    return re.sub(r"[^0-9A-Za-z]","",re.sub(r"\.0$","",str(v).strip())).upper()
def buscar_columna(cols,ops):
    m={c:normalizar(c) for c in cols}; o=[normalizar(x) for x in ops]
    for c,n in m.items():
        if n in o:return c
    for c,n in m.items():
        if any(x in n or n in x for x in o if x):return c
    return None
def detectar_header(b):
    keys=["PROVINCIA","CANTON","DISTRITO","CENTRO EDUCATIVO","INSTITUCION","CODIGO MEP","CODIGO PRESUPUESTARIO"]
    best,score=0,-1
    for i in range(min(20,len(b))):
        s=" | ".join(normalizar(x) for x in b.iloc[i].tolist()); p=sum(k in s for k in keys)
        if p>score:best,score=i,p
    return best
@st.cache_data(show_spinner=False)
@st.cache_data(show_spinner=False)
def leer_libro(data,nombre):
    eng='xlrd' if Path(nombre).suffix.lower()=='.xls' else 'openpyxl'
    xl=pd.ExcelFile(io.BytesIO(data),engine=eng)
    out=[]
    for h in xl.sheet_names:
        b=pd.read_excel(io.BytesIO(data),sheet_name=h,header=None,engine=eng)
        if b.dropna(how='all').empty:
            continue
        d=pd.read_excel(io.BytesIO(data),sheet_name=h,header=detectar_header(b),engine=eng).dropna(how='all')
        d.columns=[str(c).strip() for c in d.columns]
        d['HOJA_ORIGEN']=h
        out.append(d)
    return pd.concat(out,ignore_index=True,sort=False) if out else pd.DataFrame()


def _nombre_hoja_real(data,nombre,hoja_buscada):
    eng='xlrd' if Path(nombre).suffix.lower()=='.xls' else 'openpyxl'
    xl=pd.ExcelFile(io.BytesIO(data),engine=eng)
    objetivo=normalizar(hoja_buscada)
    for h in xl.sheet_names:
        if normalizar(h)==objetivo:
            return h,eng
    return None,eng


@st.cache_data(show_spinner=False)
def leer_totales_hoja(data,nombre,hoja_buscada):
    hoja,eng=_nombre_hoja_real(data,nombre,hoja_buscada)
    if hoja is None:
        return {'centros':0,'primaria':0,'intermedia':0,'ninos':0}
    b=pd.read_excel(io.BytesIO(data),sheet_name=hoja,header=None,engine=eng)
    labels={'TOTAL ESCUELAS':'centros','TOTAL CENTROS':'centros','TOTAL PRIMARIA':'primaria','TOTAL INTERMEDIA':'intermedia','TOTAL NINOS':'ninos'}
    candidatos={k:[] for k in ['centros','primaria','intermedia','ninos']}
    for i in range(len(b)):
        for j in range(len(b.columns)):
            etiqueta=normalizar(b.iat[i,j])
            if etiqueta not in labels:
                continue
            clave=labels[etiqueta]
            for q in range(j+1,min(j+9,len(b.columns))):
                v=pd.to_numeric(b.iat[i,q],errors='coerce')
                if pd.notna(v):
                    candidatos[clave].append(int(round(float(v))))
                    break
    return {k:(max(v) if v else 0) for k,v in candidatos.items()}


def preparar_mep(d):
    ci=buscar_columna(d.columns,['Institución','Institucion','Nombre del centro educativo','Escuela'])
    cp=buscar_columna(d.columns,['Provincia'])
    cc=buscar_columna(d.columns,['Cantón','Canton'])
    cd=buscar_columna(d.columns,['Distrito'])
    ck=buscar_columna(d.columns,['Código presupuestario','Codigo presupuestario','Código MEP','Codigo MEP'])
    if not all([ci,cp,cc,cd]):
        raise ValueError('La base MEP no contiene Institución, Provincia, Cantón y Distrito.')
    x=pd.DataFrame({'REGION_MEP':d.HOJA_ORIGEN,'CENTRO_MEP':d[ci],'PROVINCIA':d[cp],'CANTON':d[cc],'DISTRITO':d[cd],'CODIGO_MEP':d[ck] if ck else ''}).dropna(subset=['CENTRO_MEP','PROVINCIA','CANTON','DISTRITO'])
    x['CENTRO_MEP']=x.CENTRO_MEP.astype(str).str.strip()
    x=x[x.CENTRO_MEP.ne('') & ~x.CENTRO_MEP.map(normalizar).str.startswith('TOTAL')]
    for c in ['REGION_MEP','PROVINCIA','CANTON','DISTRITO']:
        x[c]=x[c].astype(str).str.strip();x[c+'_N']=x[c].map(normalizar)
    x['CENTRO_MEP_N']=x.CENTRO_MEP.map(normalizar)
    x['CODIGO_N']=x.CODIGO_MEP.map(normalizar_codigo)
    x=x.reset_index(drop=True)
    x['ID_FILA_MEP']=x.index.astype(str)
    x['ID_NOMBRE']=x.PROVINCIA_N+'|'+x.CANTON_N+'|'+x.DISTRITO_N+'|'+x.CENTRO_MEP_N
    return x


def preparar_programa(d,hoja,fuente,grupo):
    if d is None or d.empty:
        return pd.DataFrame()
    q=d[d.HOJA_ORIGEN.map(normalizar).eq(normalizar(hoja))].copy()
    if q.empty:
        return pd.DataFrame()
    cn=buscar_columna(q.columns,['Nombre del centro educativo','Institución','Escuela'])
    ck=buscar_columna(q.columns,['Código MEP','Codigo MEP'])
    cp=buscar_columna(q.columns,['Provincia'])
    cc=buscar_columna(q.columns,['Cantón','Canton'])
    cd=buscar_columna(q.columns,['Distrito'])
    cr=buscar_columna(q.columns,['Región','Region'])
    c1=buscar_columna(q.columns,['Primaria'])
    c2=buscar_columna(q.columns,['Intermedia'])
    ct=buscar_columna(q.columns,['Total niños capacitados','Total ninos capacitados','Cantidad de niños','Cantidad ninos','Niños','Ninos'])
    if cn is None or ct is None:
        return pd.DataFrame()
    x=pd.DataFrame({'FUENTE':fuente,'GRUPO':grupo,'CENTRO_ORIGEN':q[cn],'CODIGO_ORIGINAL':q[ck] if ck else '','PROVINCIA_ORIGEN':q[cp] if cp else '','CANTON_ORIGEN':q[cc] if cc else '','DISTRITO_ORIGEN':q[cd] if cd else '','REGION_ORIGEN':q[cr] if cr else '','PRIMARIA':q[c1] if c1 else 0,'INTERMEDIA':q[c2] if c2 else 0,'NINOS':q[ct]})
    x=x.dropna(subset=['CENTRO_ORIGEN'])
    x['CENTRO_ORIGEN']=x.CENTRO_ORIGEN.astype(str).str.strip()
    x=x[x.CENTRO_ORIGEN.ne('') & ~x.CENTRO_ORIGEN.map(normalizar).str.contains('TOTAL NINOS|TOTAL ESCUELAS|TOTAL CENTROS',regex=True)]
    x['CODIGO_N']=x.CODIGO_ORIGINAL.map(normalizar_codigo)
    x['CENTRO_ORIGEN_N']=x.CENTRO_ORIGEN.map(normalizar)
    for c in ['PRIMARIA','INTERMEDIA','NINOS']:
        x[c]=pd.to_numeric(x[c],errors='coerce').fillna(0)
    for c in ['PROVINCIA_ORIGEN','CANTON_ORIGEN','DISTRITO_ORIGEN','REGION_ORIGEN']:
        x[c]=x[c].fillna('').astype(str).str.strip()
    return x.reset_index(drop=True)


def totales_desde_detalle(d):
    if d is None or d.empty:
        return {'centros':0,'primaria':0,'intermedia':0,'ninos':0}
    return {'centros':int(len(d)),'primaria':int(d.PRIMARIA.sum()),'intermedia':int(d.INTERMEDIA.sum()),'ninos':int(d.NINOS.sum())}


def relacionar(m,d):
    if d is None or d.empty:
        return pd.DataFrame()
    if m is None or m.empty:
        r=d.copy()
        r['CENTRO_MEP']=r['CENTRO_ORIGEN']
        r['REGION_MEP']=r['REGION_ORIGEN'].replace('',np.nan).fillna(r['FUENTE'])
        r['PROVINCIA']=r['PROVINCIA_ORIGEN'];r['CANTON']=r['CANTON_ORIGEN'];r['DISTRITO']=r['DISTRITO_ORIGEN']
        for c in ['PROVINCIA','CANTON','DISTRITO']:
            r[c+'_N']=r[c].map(normalizar)
        r['ID_NOMBRE']=r.PROVINCIA_N+'|'+r.CANTON_N+'|'+r.DISTRITO_N+'|'+r.CENTRO_ORIGEN_N
        r['ID_FILA_MEP']=np.nan
        r['COINCIDENCIA']='Base MEP no cargada'
        r['UBICADO']=r.PROVINCIA_N.ne('') & r.CANTON_N.ne('') & r.DISTRITO_N.ne('')
        return r
    cat=m[m.CODIGO_N.ne('')].drop_duplicates('CODIGO_N')
    cols=['CODIGO_N','ID_FILA_MEP','ID_NOMBRE','CENTRO_MEP','REGION_MEP','PROVINCIA','CANTON','DISTRITO','PROVINCIA_N','CANTON_N','DISTRITO_N']
    r=d.merge(cat[cols],on='CODIGO_N',how='left')
    r['COINCIDENCIA']=np.where(r.ID_FILA_MEP.notna(),'Código MEP / presupuestario','No localizado')
    ops=m.CENTRO_MEP_N.tolist()
    for i,f in r[r.ID_FILA_MEP.isna()].iterrows():
        z=process.extractOne(f.CENTRO_ORIGEN_N,ops,scorer=fuzz.token_sort_ratio)
        if z and z[1]>=92:
            c=m[m.CENTRO_MEP_N.eq(z[0])].iloc[0]
            for k in ['ID_FILA_MEP','ID_NOMBRE','CENTRO_MEP','REGION_MEP','PROVINCIA','CANTON','DISTRITO','PROVINCIA_N','CANTON_N','DISTRITO_N']:
                r.at[i,k]=c[k]
            r.at[i,'COINCIDENCIA']=f'Revisión por nombre ({z[1]:.0f}%)'
    falt=r.ID_NOMBRE.isna()
    r.loc[falt,'CENTRO_MEP']=r.loc[falt,'CENTRO_ORIGEN']
    r.loc[falt,'REGION_MEP']=r.loc[falt,'REGION_ORIGEN']
    r.loc[falt,'PROVINCIA']=r.loc[falt,'PROVINCIA_ORIGEN'];r.loc[falt,'CANTON']=r.loc[falt,'CANTON_ORIGEN'];r.loc[falt,'DISTRITO']=r.loc[falt,'DISTRITO_ORIGEN']
    for c in ['PROVINCIA','CANTON','DISTRITO']:
        r[c+'_N']=r[c].map(normalizar)
    r.loc[falt,'ID_NOMBRE']=r.loc[falt,'PROVINCIA_N']+'|'+r.loc[falt,'CANTON_N']+'|'+r.loc[falt,'DISTRITO_N']+'|'+r.loc[falt,'CENTRO_ORIGEN_N']
    r['UBICADO']=r.PROVINCIA_N.ne('') & r.CANTON_N.ne('') & r.DISTRITO_N.ne('')
    return r


def coord(d,c,p):
    for k in [d,c]:
        if k in COORDENADAS_REFERENCIA:return COORDENADAS_REFERENCIA[k]
    return PROVINCE_COORDS.get(p,[9.7489,-83.7534])


def resumen(m,a):
    if m is not None and not m.empty:
        b=m.groupby(['REGION_MEP','PROVINCIA','CANTON','DISTRITO','PROVINCIA_N','CANTON_N','DISTRITO_N'],as_index=False).agg(INSTITUCIONES_MEP=('ID_FILA_MEP','count'))
        ok=a[a.UBICADO] if a is not None and not a.empty else pd.DataFrame()
        if ok.empty:
            act=pd.DataFrame(columns=['REGION_MEP','PROVINCIA','CANTON','DISTRITO','CENTROS_ACTIVOS','NINOS'])
        else:
            act=ok.groupby(['REGION_MEP','PROVINCIA','CANTON','DISTRITO'],as_index=False).agg(CENTROS_ACTIVOS=('ID_NOMBRE','nunique'),NINOS=('NINOS','sum'))
        z=b.merge(act,on=['REGION_MEP','PROVINCIA','CANTON','DISTRITO'],how='left').fillna({'CENTROS_ACTIVOS':0,'NINOS':0});z.CENTROS_ACTIVOS=z.CENTROS_ACTIVOS.astype(int)
    else:
        ok=a[a.UBICADO].copy() if a is not None and not a.empty else pd.DataFrame()
        if ok.empty:
            return pd.DataFrame(columns=['REGION_MEP','PROVINCIA','CANTON','DISTRITO','INSTITUCIONES_MEP','CENTROS_ACTIVOS','NINOS','LAT','LON'])
        z=ok.groupby(['REGION_MEP','PROVINCIA','CANTON','DISTRITO'],as_index=False).agg(CENTROS_ACTIVOS=('ID_NOMBRE','nunique'),NINOS=('NINOS','sum'))
        z['INSTITUCIONES_MEP']=np.nan
        z['PROVINCIA_N']=z.PROVINCIA.map(normalizar);z['CANTON_N']=z.CANTON.map(normalizar);z['DISTRITO_N']=z.DISTRITO.map(normalizar)
    cs=z.apply(lambda r:coord(r.DISTRITO_N,r.CANTON_N,r.PROVINCIA_N),axis=1);z['LAT']=[v[0] for v in cs];z['LON']=[v[1] for v in cs]
    return z


def csv_bytes(d):return d.to_csv(index=False).encode('utf-8-sig')

st.markdown('<style>.block-container{padding-top:1.2rem}div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;padding:12px;border-radius:13px}.resumen{background:#fff7ed;border-left:5px solid #f59e0b;padding:14px;border-radius:9px;margin:14px 0}</style>',unsafe_allow_html=True)
st.title('🏫 Seguimiento MPAS, GREAT y Policía Municipal 2026')
st.caption('Carga flexible: la aplicación trabaja con uno, dos o los tres archivos disponibles.')
with st.sidebar:
    st.header('Carga de archivos')
    fm=st.file_uploader('Base MEP',type=['xlsx','xls'])
    fp=st.file_uploader('Base MPAS 2026',type=['xlsx','xls'])
    fg=st.file_uploader('Base GREAT 2026',type=['xlsx','xls'])
    st.caption('Puede cargar 1, 2 o 3 archivos. No es obligatorio cargar los tres.')
if not any([fm,fp,fg]):
    st.info('Cargue al menos uno de los archivos para iniciar.');st.stop()

mep=None;mpas=pd.DataFrame();great_fp=pd.DataFrame();policia_municipal=pd.DataFrame()
tm={'centros':0,'primaria':0,'intermedia':0,'ninos':0};tg=tm.copy();tpm=tm.copy();errores=[]
if fm:
    try:mep=preparar_mep(leer_libro(fm.getvalue(),fm.name))
    except Exception as e:errores.append(f'MEP: {e}');mep=None
if fp:
    try:
        raw=leer_libro(fp.getvalue(),fp.name);detalle=preparar_programa(raw,'MPAS','MPAS','MPAS');mpas=relacionar(mep,detalle);tm=leer_totales_hoja(fp.getvalue(),fp.name,'MPAS')
        if not tm['centros']:tm=totales_desde_detalle(detalle)
    except Exception as e:errores.append(f'MPAS: {e}');mpas=pd.DataFrame()
if fg:
    try:
        raw=leer_libro(fg.getvalue(),fg.name)
        dg=preparar_programa(raw,'GREAT','GREAT Fuerza Pública','GREAT')
        if not dg.empty:
            great_fp=relacionar(mep,dg);tg=leer_totales_hoja(fg.getvalue(),fg.name,'GREAT')
            if not tg['centros']:tg=totales_desde_detalle(dg)
        dp=preparar_programa(raw,'POLICIA MUNICIPAL','Policía Municipal','GREAT')
        if not dp.empty:
            policia_municipal=relacionar(mep,dp);tpm=leer_totales_hoja(fg.getvalue(),fg.name,'POLICIA MUNICIPAL')
            if not tpm['centros']:tpm=totales_desde_detalle(dp)
    except Exception as e:errores.append(f'GREAT: {e}');great_fp=pd.DataFrame();policia_municipal=pd.DataFrame()
for e in errores:st.warning(e)

with st.sidebar:
    st.divider();st.subheader('Archivos reconocidos')
    if mep is not None and not mep.empty:st.success(f'MEP: {len(mep):,} instituciones')
    if not mpas.empty:st.success(f'MPAS: {len(mpas):,} registros')
    if not great_fp.empty:st.success(f'GREAT Fuerza Pública: {len(great_fp):,} registros')
    if not policia_municipal.empty:st.success(f'Policía Municipal: {len(policia_municipal):,} registros')

fuentes=[]
if not mpas.empty:fuentes.append(mpas)
if not great_fp.empty:fuentes.append(great_fp)
if not policia_municipal.empty:fuentes.append(policia_municipal)
if not fuentes and (mep is None or mep.empty):st.error('No fue posible obtener información válida de los archivos cargados.');st.stop()

if fuentes:
    opciones=[]
    if len(fuentes)>=2:opciones.append('Todos los datos cargados')
    if not mpas.empty:opciones.append('MPAS')
    if not great_fp.empty:opciones.append('GREAT Fuerza Pública')
    if not policia_municipal.empty:opciones.append('Policía Municipal')
    if not great_fp.empty and not policia_municipal.empty:opciones.append('GREAT unificado')
    if not mpas.empty and (not great_fp.empty or not policia_municipal.empty):opciones.append('MPAS y GREAT en el mismo centro')
    st.subheader('Visualización de información');vista=st.radio('Seleccione la vista',opciones,horizontal=True)
    great_total=pd.concat([x for x in [great_fp,policia_municipal] if not x.empty],ignore_index=True) if (not great_fp.empty or not policia_municipal.empty) else pd.DataFrame()
    todos=pd.concat(fuentes,ignore_index=True)
    if vista=='MPAS':act=mpas.copy()
    elif vista=='GREAT Fuerza Pública':act=great_fp.copy()
    elif vista=='Policía Municipal':act=policia_municipal.copy()
    elif vista=='GREAT unificado':act=great_total.copy()
    elif vista=='MPAS y GREAT en el mismo centro':
        ids=set(mpas.ID_NOMBRE.dropna()).intersection(set(great_total.ID_NOMBRE.dropna()));act=todos[todos.ID_NOMBRE.isin(ids)].copy()
    else:act=todos.copy()
else:
    vista='Base MEP';act=pd.DataFrame();st.subheader('Visualización de información');st.info('Solo está cargada la base MEP. Se muestra el universo territorial MEP.')

r=resumen(mep,act)
if r.empty:st.warning('No hay información territorial disponible para la selección actual.');st.stop()
st.subheader('Filtros territoriales');a,b,c,d=st.columns(4)
reg=a.selectbox('Región MEP / Región',['Todas']+sorted([x for x in r.REGION_MEP.dropna().astype(str).unique() if x.strip()]))
f=r.copy()
if reg!='Todas':f=f[f.REGION_MEP.eq(reg)]
pro=b.selectbox('Provincia',['Todas']+sorted([x for x in f.PROVINCIA.dropna().astype(str).unique() if x.strip()]))
if pro!='Todas':f=f[f.PROVINCIA.eq(pro)]
can=c.selectbox('Cantón',['Todos']+sorted([x for x in f.CANTON.dropna().astype(str).unique() if x.strip()]))
if can!='Todos':f=f[f.CANTON.eq(can)]
dis=d.selectbox('Distrito',['Todos']+sorted([x for x in f.DISTRITO.dropna().astype(str).unique() if x.strip()]))
if dis!='Todos':f=f[f.DISTRITO.eq(dis)]
f_territorial=f.copy();opciones_estado=['Todos','Con actividad','Sin actividad'] if mep is not None and not mep.empty else ['Todos','Con actividad']
estado=st.radio('Estado de actividad en el distrito',opciones_estado,horizontal=True,help='Sin actividad requiere la base MEP.')
f_mapa=f_territorial.copy()
if estado=='Con actividad':f_mapa=f_mapa[f_mapa.CENTROS_ACTIVOS>0]
elif estado=='Sin actividad':f_mapa=f_mapa[f_mapa.CENTROS_ACTIVOS==0]

fa=act.copy()
if not fa.empty:
    if reg!='Todas':fa=fa[fa.REGION_MEP.eq(reg)]
    if pro!='Todas':fa=fa[fa.PROVINCIA.eq(pro)]
    if can!='Todos':fa=fa[fa.CANTON.eq(can)]
    if dis!='Todos':fa=fa[fa.DISTRITO.eq(dis)]
if fa.empty:
    centros=pd.DataFrame(columns=['ID_NOMBRE','REGION_MEP','PROVINCIA','CANTON','DISTRITO','CENTRO_MEP','CODIGO_N','PRIMARIA','INTERMEDIA','NINOS','FUENTES','GRUPOS'])
else:
    centros=fa.groupby('ID_NOMBRE',as_index=False).agg(
        REGION_MEP=('REGION_MEP','first'),
        PROVINCIA=('PROVINCIA','first'),
        CANTON=('CANTON','first'),
        DISTRITO=('DISTRITO','first'),
        CENTRO_MEP=('CENTRO_MEP','first'),
        CODIGO_N=('CODIGO_N','first'),
        PRIMARIA=('PRIMARIA','sum'),
        INTERMEDIA=('INTERMEDIA','sum'),
        NINOS=('NINOS','sum'),
        FUENTES=('FUENTE',lambda s:' + '.join(sorted(set(s.astype(str))))),
        GRUPOS=('GRUPO',lambda s:' + '.join(sorted(set(s.astype(str)))))
    )

vista_nacional=(reg=='Todas' and pro=='Todas' and can=='Todos' and dis=='Todos')
nm=int(f_territorial.INSTITUCIONES_MEP.sum()) if mep is not None and not mep.empty else None
if vista_nacional and vista=='MPAS':cent,pri,inter,nin=tm['centros'],tm['primaria'],tm['intermedia'],tm['ninos']
elif vista_nacional and vista=='GREAT Fuerza Pública':cent,pri,inter,nin=tg['centros'],tg['primaria'],tg['intermedia'],tg['ninos']
elif vista_nacional and vista=='Policía Municipal':cent,pri,inter,nin=tpm['centros'],tpm['primaria'],tpm['intermedia'],tpm['ninos']
else:
    cent=len(centros);pri=int(centros.PRIMARIA.sum()) if not centros.empty else 0;inter=int(centros.INTERMEDIA.sum()) if not centros.empty else 0;nin=int(centros.NINOS.sum()) if not centros.empty else 0
if vista=='Base MEP':cent=pri=inter=nin=0
cov=(cent/nm*100) if nm else None
m1,m2,m3,m4,m5,m6=st.columns(6);m1.metric('Instituciones MEP',f'{nm:,}' if nm is not None else 'No cargada');m2.metric('Centros visibles',f'{cent:,}');m3.metric('Primaria',f'{pri:,}');m4.metric('Intermedia',f'{inter:,}');m5.metric('Total niños',f'{nin:,}');m6.metric('Cobertura',f'{cov:.1f}%' if cov is not None else '—')
texto_universo=f'{nm:,} instituciones MEP' if nm is not None else 'sin base MEP cargada'
st.markdown(f'<div class="resumen"><b>{vista}</b>: {cent:,} centros visibles, {nin:,} niños reportados y universo territorial de {texto_universo}. '+(f'Cobertura: <b>{cov:.1f}%</b>.' if cov is not None else 'La cobertura requiere la base MEP.')+'</div>',unsafe_allow_html=True)

st.subheader('Mapa de seguimiento');st.caption('🟢 MPAS · 🔵 GREAT Fuerza Pública · 🟠 Policía Municipal · 🟣 centro presente en más de una fuente · 🔴 sin actividad')
if f_mapa.empty:st.warning('No existen datos para los filtros seleccionados.')
else:
    mapa=folium.Map([float(f_mapa.LAT.mean()),float(f_mapa.LON.mean())],zoom_start=8,tiles='CartoDB positron')
    if mep is not None and not mep.empty and estado in ['Todos','Sin actividad']:
        for _,q in f_mapa[f_mapa.CENTROS_ACTIVOS==0].iterrows():
            folium.Marker([q.LAT,q.LON],icon=folium.Icon(color='red',icon='remove'),tooltip=f'{q.DISTRITO} · Sin actividad',popup=folium.Popup(f'<b>{q.DISTRITO}</b><br>Sin actividad para: {vista}<br>Provincia: {q.PROVINCIA}<br>Cantón: {q.CANTON}<br>Instituciones MEP: {int(q.INSTITUCIONES_MEP)}',max_width=330)).add_to(mapa)
    if estado in ['Todos','Con actividad'] and not centros.empty:
        pins=centros.copy();bases=[coord(normalizar(q.DISTRITO),normalizar(q.CANTON),normalizar(q.PROVINCIA)) for _,q in pins.iterrows()];pins['LAT_BASE']=[x[0] for x in bases];pins['LON_BASE']=[x[1] for x in bases];pins['CLAVE_COORD']=pins.apply(lambda q:f'{q.LAT_BASE:.6f}|{q.LON_BASE:.6f}',axis=1);numero=1
        for _,grupo in pins.groupby('CLAVE_COORD',sort=False):
            grupo=grupo.reset_index(drop=True);cantidad=len(grupo);lat0=float(grupo.at[0,'LAT_BASE']);lon0=float(grupo.at[0,'LON_BASE'])
            for pos,q in grupo.iterrows():
                if cantidad==1:lat,lon=lat0,lon0
                else:
                    anillo=pos//8;pa=pos%8;elementos=min(8,cantidad-anillo*8);ang=2*math.pi*pa/max(elementos,1);radio=0.009+anillo*0.007;lat=lat0+radio*math.cos(ang);lon=lon0+radio*math.sin(ang)
                fs=set(str(q.FUENTES).split(' + '));color='#7e22ce' if len(fs)>1 else ('#16a34a' if 'MPAS' in fs else ('#f97316' if 'Policía Municipal' in fs else '#2563eb'))
                html=f'<div style="width:32px;height:32px;border-radius:50%;background:{color};border:2px solid white;color:white;font-weight:800;text-align:center;line-height:28px;box-shadow:0 2px 5px rgba(0,0,0,.35);">{numero}</div>'
                popup=f'<b>{numero}. {q.CENTRO_MEP}</b><br>Fuente: {q.FUENTES}<br>Código MEP: {q.CODIGO_N}<br>Región: {q.REGION_MEP}<br>Provincia: {q.PROVINCIA}<br>Cantón: {q.CANTON}<br>Distrito: {q.DISTRITO}<br>Primaria: {int(q.PRIMARIA)}<br>Intermedia: {int(q.INTERMEDIA)}<br>Total niños: {int(q.NINOS)}'
                folium.Marker([lat,lon],icon=folium.DivIcon(html=html,icon_size=(32,32),icon_anchor=(16,16)),tooltip=f'{numero}. {q.CENTRO_MEP} · {q.FUENTES}',popup=folium.Popup(popup,max_width=360),z_index_offset=1000+numero).add_to(mapa);numero+=1
        st.caption(f'Pines visibles: {numero-1:,}. La numeración se adapta a los filtros y archivos cargados.')
    st_folium(mapa,use_container_width=True,height=600,returned_objects=[])

if vista=='Base MEP':
    st.subheader('Instituciones MEP');lista=mep.copy()
    if reg!='Todas':lista=lista[lista.REGION_MEP.eq(reg)]
    if pro!='Todas':lista=lista[lista.PROVINCIA.eq(pro)]
    if can!='Todos':lista=lista[lista.CANTON.eq(can)]
    if dis!='Todos':lista=lista[lista.DISTRITO.eq(dis)]
    st.dataframe(lista[['REGION_MEP','PROVINCIA','CANTON','DISTRITO','CENTRO_MEP','CODIGO_N']].rename(columns={'REGION_MEP':'Región MEP','PROVINCIA':'Provincia','CANTON':'Cantón','DISTRITO':'Distrito','CENTRO_MEP':'Institución','CODIGO_N':'Código presupuestario'}),use_container_width=True,hide_index=True)
else:
    st.subheader('Lista de centros abordados')
    if estado=='Sin actividad':st.info('No hay centros abordados para listar en la vista Sin actividad.')
    elif centros.empty:st.info('No existen centros abordados para los filtros seleccionados.')
    else:
        lista=centros[['FUENTES','REGION_MEP','PROVINCIA','CANTON','DISTRITO','CENTRO_MEP','CODIGO_N','PRIMARIA','INTERMEDIA','NINOS']].rename(columns={'FUENTES':'Fuente','REGION_MEP':'Región','PROVINCIA':'Provincia','CANTON':'Cantón','DISTRITO':'Distrito','CENTRO_MEP':'Centro educativo','CODIGO_N':'Código MEP','PRIMARIA':'Primaria','INTERMEDIA':'Intermedia','NINOS':'Total niños'})
        st.dataframe(lista,use_container_width=True,hide_index=True,height=min(650,100+len(lista)*32));st.download_button('Descargar lista CSV',csv_bytes(lista),'centros_filtrados.csv','text/csv')

if mep is not None and not mep.empty and fuentes:
    pendientes=[]
    for dset in fuentes:
        if not dset.empty:
            p=dset[dset.COINCIDENCIA.eq('No localizado')]
            if not p.empty:pendientes.append(p)
    if pendientes:
        pend=pd.concat(pendientes,ignore_index=True)
        with st.expander(f'Registros pendientes de validar ({len(pend)})'):
            st.dataframe(pend[['FUENTE','CENTRO_ORIGEN','CODIGO_N','NINOS','COINCIDENCIA']],use_container_width=True,hide_index=True)
