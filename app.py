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
def leer_libro(data,nombre):
    eng='xlrd' if Path(nombre).suffix.lower()=='.xls' else 'openpyxl'; xl=pd.ExcelFile(io.BytesIO(data),engine=eng); out=[]
    for h in xl.sheet_names:
        b=pd.read_excel(io.BytesIO(data),sheet_name=h,header=None,engine=eng)
        if b.dropna(how='all').empty:continue
        d=pd.read_excel(io.BytesIO(data),sheet_name=h,header=detectar_header(b),engine=eng).dropna(how='all')
        d.columns=[str(c).strip() for c in d.columns];d['HOJA_ORIGEN']=h;out.append(d)
    return pd.concat(out,ignore_index=True,sort=False) if out else pd.DataFrame()
@st.cache_data(show_spinner=False)
def leer_totales(data,nombre):
    eng='xlrd' if Path(nombre).suffix.lower()=='.xls' else 'openpyxl';xl=pd.ExcelFile(io.BytesIO(data),engine=eng)
    labels={'TOTAL ESCUELAS':'centros','TOTAL CENTROS':'centros','TOTAL PRIMARIA':'primaria','TOTAL INTERMEDIA':'intermedia','TOTAL NINOS':'ninos'}
    c={k:[] for k in ['centros','primaria','intermedia','ninos']}
    for h in xl.sheet_names:
        b=pd.read_excel(io.BytesIO(data),sheet_name=h,header=None,engine=eng)
        for i in range(len(b)):
            for j in range(len(b.columns)):
                e=normalizar(b.iat[i,j])
                if e not in labels:continue
                for q in range(j+1,min(j+9,len(b.columns))):
                    v=pd.to_numeric(b.iat[i,q],errors='coerce')
                    if pd.notna(v):c[labels[e]].append(int(round(float(v))));break
    return {k:(max(v) if v else 0) for k,v in c.items()}
def preparar_mep(d):
    ci=buscar_columna(d.columns,['Institución','Institucion','Nombre del centro educativo','Escuela']);cp=buscar_columna(d.columns,['Provincia']);cc=buscar_columna(d.columns,['Cantón','Canton']);cd=buscar_columna(d.columns,['Distrito']);ck=buscar_columna(d.columns,['Código presupuestario','Codigo presupuestario','Código MEP','Codigo MEP'])
    if not all([ci,cp,cc,cd]):raise ValueError('La base MEP no contiene Institución, Provincia, Cantón y Distrito.')
    x=pd.DataFrame({'REGION_MEP':d.HOJA_ORIGEN,'CENTRO_MEP':d[ci],'PROVINCIA':d[cp],'CANTON':d[cc],'DISTRITO':d[cd],'CODIGO_MEP':d[ck] if ck else ''}).dropna(subset=['CENTRO_MEP','PROVINCIA','CANTON','DISTRITO'])
    x['CENTRO_MEP']=x.CENTRO_MEP.astype(str).str.strip();x=x[x.CENTRO_MEP.ne('') & ~x.CENTRO_MEP.map(normalizar).str.startswith('TOTAL')]
    for c in ['REGION_MEP','PROVINCIA','CANTON','DISTRITO']:x[c]=x[c].astype(str).str.strip();x[c+'_N']=x[c].map(normalizar)
    x['CENTRO_MEP_N']=x.CENTRO_MEP.map(normalizar);x['CODIGO_N']=x.CODIGO_MEP.map(normalizar_codigo);x=x.reset_index(drop=True);x['ID_FILA_MEP']=x.index.astype(str);x['ID_NOMBRE']=x.PROVINCIA_N+'|'+x.CANTON_N+'|'+x.DISTRITO_N+'|'+x.CENTRO_MEP_N
    return x
def preparar_programa(d,p):
    q=d[d.HOJA_ORIGEN.map(normalizar).eq(normalizar(p))].copy()
    if q.empty:raise ValueError(f'No se encontró la hoja principal {p}.')
    cn=buscar_columna(q.columns,['Nombre del centro educativo','Institución','Escuela']);ck=buscar_columna(q.columns,['Código MEP','Codigo MEP']);cp=buscar_columna(q.columns,['Provincia']);cc=buscar_columna(q.columns,['Cantón','Canton']);cd=buscar_columna(q.columns,['Distrito']);cr=buscar_columna(q.columns,['Región','Region']);c1=buscar_columna(q.columns,['Primaria']);c2=buscar_columna(q.columns,['Intermedia']);ct=buscar_columna(q.columns,['Total niños capacitados','Total ninos capacitados','Cantidad de niños','Cantidad ninos','Niños','Ninos'])
    if not all([cn,ck,ct]):raise ValueError(f'La hoja {p} no contiene nombre, Código MEP y total de niños.')
    x=pd.DataFrame({'PROGRAMA':p,'CENTRO_ORIGEN':q[cn],'CODIGO_ORIGINAL':q[ck],'PROVINCIA_ORIGEN':q[cp] if cp else '','CANTON_ORIGEN':q[cc] if cc else '','DISTRITO_ORIGEN':q[cd] if cd else '','REGION_ORIGEN':q[cr] if cr else '','PRIMARIA':q[c1] if c1 else 0,'INTERMEDIA':q[c2] if c2 else 0,'NINOS':q[ct]})
    x=x.dropna(subset=['CENTRO_ORIGEN']);x['CENTRO_ORIGEN']=x.CENTRO_ORIGEN.astype(str).str.strip();x=x[x.CENTRO_ORIGEN.ne('') & ~x.CENTRO_ORIGEN.map(normalizar).str.contains('TOTAL NINOS|TOTAL ESCUELAS|TOTAL CENTROS',regex=True)]
    x['CODIGO_N']=x.CODIGO_ORIGINAL.map(normalizar_codigo);x['CENTRO_ORIGEN_N']=x.CENTRO_ORIGEN.map(normalizar)
    for c in ['PRIMARIA','INTERMEDIA','NINOS']:x[c]=pd.to_numeric(x[c],errors='coerce').fillna(0)
    return x.reset_index(drop=True)
def relacionar(m,d):
    cat=m[m.CODIGO_N.ne('')].drop_duplicates('CODIGO_N');cols=['CODIGO_N','ID_FILA_MEP','ID_NOMBRE','CENTRO_MEP','REGION_MEP','PROVINCIA','CANTON','DISTRITO','PROVINCIA_N','CANTON_N','DISTRITO_N'];r=d.merge(cat[cols],on='CODIGO_N',how='left');r['COINCIDENCIA']=np.where(r.ID_FILA_MEP.notna(),'Código MEP / presupuestario','No localizado')
    ops=m.CENTRO_MEP_N.tolist()
    for i,f in r[r.ID_FILA_MEP.isna()].iterrows():
        z=process.extractOne(f.CENTRO_ORIGEN_N,ops,scorer=fuzz.token_sort_ratio)
        if z and z[1]>=92:
            c=m[m.CENTRO_MEP_N.eq(z[0])].iloc[0]
            for k in ['ID_FILA_MEP','ID_NOMBRE','CENTRO_MEP','REGION_MEP','PROVINCIA','CANTON','DISTRITO','PROVINCIA_N','CANTON_N','DISTRITO_N']:r.at[i,k]=c[k]
            r.at[i,'COINCIDENCIA']=f'Revisión por nombre ({z[1]:.0f}%)'
    return r
def coord(d,c,p):
    for k in [d,c]:
        if k in COORDENADAS_REFERENCIA:return COORDENADAS_REFERENCIA[k]
    return PROVINCE_COORDS.get(p,[9.7489,-83.7534])
def resumen(m,a):
    b=m.groupby(['REGION_MEP','PROVINCIA','CANTON','DISTRITO','PROVINCIA_N','CANTON_N','DISTRITO_N'],as_index=False).agg(INSTITUCIONES_MEP=('ID_FILA_MEP','count'));ok=a[a.ID_FILA_MEP.notna()]
    if ok.empty:act=pd.DataFrame(columns=['REGION_MEP','PROVINCIA','CANTON','DISTRITO','CENTROS_ACTIVOS','NINOS'])
    else:act=ok.groupby(['REGION_MEP','PROVINCIA','CANTON','DISTRITO'],as_index=False).agg(CENTROS_ACTIVOS=('ID_NOMBRE','nunique'),NINOS=('NINOS','sum'))
    z=b.merge(act,on=['REGION_MEP','PROVINCIA','CANTON','DISTRITO'],how='left').fillna({'CENTROS_ACTIVOS':0,'NINOS':0});z.CENTROS_ACTIVOS=z.CENTROS_ACTIVOS.astype(int);cs=z.apply(lambda r:coord(r.DISTRITO_N,r.CANTON_N,r.PROVINCIA_N),axis=1);z['LAT']=[v[0] for v in cs];z['LON']=[v[1] for v in cs];return z
def csv_bytes(d):return d.to_csv(index=False).encode('utf-8-sig')
st.markdown('<style>.block-container{padding-top:1.2rem}div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;padding:12px;border-radius:13px}.resumen{background:#fff7ed;border-left:5px solid #f59e0b;padding:14px;border-radius:9px;margin:14px 0}</style>',unsafe_allow_html=True)
st.title('🏫 Seguimiento MPAS y GREAT 2026');st.caption('Lectura individual y unificada de centros educativos abordados.')
with st.sidebar:
    st.header('Carga de archivos');fm=st.file_uploader('Base MEP',type=['xlsx','xls']);fp=st.file_uploader('Base MPAS 2026',type=['xlsx','xls']);fg=st.file_uploader('Base GREAT 2026',type=['xlsx','xls'])
if not all([fm,fp,fg]):st.info('Cargue las tres bases para iniciar.');st.stop()
try:
    mep=preparar_mep(leer_libro(fm.getvalue(),fm.name));mpas=relacionar(mep,preparar_programa(leer_libro(fp.getvalue(),fp.name),'MPAS'));great=relacionar(mep,preparar_programa(leer_libro(fg.getvalue(),fg.name),'GREAT'));tm=leer_totales(fp.getvalue(),fp.name);tg=leer_totales(fg.getvalue(),fg.name)
except Exception as e:st.error(f'No fue posible procesar las bases: {e}');st.stop()
vista=st.radio('Vista del programa',['MPAS','GREAT','Ambos'],horizontal=True);act=mpas.copy() if vista=='MPAS' else great.copy() if vista=='GREAT' else pd.concat([mpas,great],ignore_index=True)
r=resumen(mep,act);st.subheader('Filtros territoriales');a,b,c,d=st.columns(4);reg=a.selectbox('Región MEP',['Todas']+sorted(r.REGION_MEP.unique().tolist()));f=r.copy();f=f if reg=='Todas' else f[f.REGION_MEP.eq(reg)];pro=b.selectbox('Provincia',['Todas']+sorted(f.PROVINCIA.unique().tolist()));f=f if pro=='Todas' else f[f.PROVINCIA.eq(pro)];can=c.selectbox('Cantón',['Todos']+sorted(f.CANTON.unique().tolist()));f=f if can=='Todos' else f[f.CANTON.eq(can)];dis=d.selectbox('Distrito',['Todos']+sorted(f.DISTRITO.unique().tolist()));f=f if dis=='Todos' else f[f.DISTRITO.eq(dis)];estado=st.radio('Estado de actividad',['Todos','Con actividad','Sin actividad'],horizontal=True);fmmap=f.copy();fmmap=fmmap[fmmap.CENTROS_ACTIVOS>0] if estado=='Con actividad' else fmmap[fmmap.CENTROS_ACTIVOS==0] if estado=='Sin actividad' else fmmap
fa=act[act.ID_FILA_MEP.notna()].copy();fa=fa if reg=='Todas' else fa[fa.REGION_MEP.eq(reg)];fa=fa if pro=='Todas' else fa[fa.PROVINCIA.eq(pro)];fa=fa if can=='Todos' else fa[fa.CANTON.eq(can)];fa=fa if dis=='Todos' else fa[fa.DISTRITO.eq(dis)]
nm=int(f.INSTITUCIONES_MEP.sum());cent=int(fa.ID_NOMBRE.nunique());pri=int(fa.PRIMARIA.sum());inter=int(fa.INTERMEDIA.sum());nin=int(fa.NINOS.sum());nac=all(x in ['Todas','Todos'] for x in [reg,pro,can,dis])
if nac and vista=='MPAS' and tm['centros']:cent,pri,inter,nin=tm['centros'],tm['primaria'],tm['intermedia'],tm['ninos']
if nac and vista=='GREAT':pri=tg['primaria'] or pri;inter=tg['intermedia'] or inter;nin=tg['ninos'] or nin
if vista=='Ambos':cent=int(fa.ID_NOMBRE.nunique())
cov=cent/nm*100 if nm else 0;m1,m2,m3,m4,m5,m6=st.columns(6);m1.metric('Instituciones MEP',f'{nm:,}');m2.metric('Centros abordados',f'{cent:,}');m3.metric('Primaria',f'{pri:,}');m4.metric('Intermedia',f'{inter:,}');m5.metric('Total niños',f'{nin:,}');m6.metric('Cobertura',f'{cov:.1f}%');st.markdown(f'<div class="resumen"><b>{vista}</b>: {cent:,} centros de {nm:,}; {nin:,} niños y {cov:.1f}% de cobertura.</div>',unsafe_allow_html=True)
st.subheader('Mapa de seguimiento');st.caption('🟢 MPAS · 🔵 GREAT · 🟣 ambos programas · 🔴 sin actividad')
if not fmmap.empty:
    mapa=folium.Map([float(fmmap.LAT.mean()),float(fmmap.LON.mean())],zoom_start=8,tiles='CartoDB positron')
    if estado in ['Todos','Sin actividad']:
        for _,q in fmmap[fmmap.CENTROS_ACTIVOS==0].iterrows():folium.Marker([q.LAT,q.LON],icon=folium.Icon(color='red',icon='remove'),tooltip=f'{q.DISTRITO} · Sin actividad').add_to(mapa)
    if estado in ['Todos','Con actividad']:
        pins=fa.drop_duplicates(['PROGRAMA','ID_NOMBRE']).copy();both=act[act.ID_FILA_MEP.notna()].groupby('ID_NOMBRE').PROGRAMA.nunique();pins['AMBOS']=pins.ID_NOMBRE.map(both).fillna(1).gt(1);bc=[coord(normalizar(q.DISTRITO),normalizar(q.CANTON),normalizar(q.PROVINCIA)) for _,q in pins.iterrows()];pins['LB']=[x[0] for x in bc];pins['OB']=[x[1] for x in bc];pins['KEY']=pins.apply(lambda q:f'{q.LB:.6f}|{q.OB:.6f}',axis=1);num=1
        for _,g in pins.groupby('KEY',sort=False):
            g=g.reset_index(drop=True);n=len(g);la=float(g.at[0,'LB']);lo=float(g.at[0,'OB'])
            for pos,q in g.iterrows():
                lat,lon=(la,lo) if n==1 else (la+.009*math.cos(2*math.pi*pos/n),lo+.009*math.sin(2*math.pi*pos/n));color='#7e22ce' if q.AMBOS else '#16a34a' if q.PROGRAMA=='MPAS' else '#2563eb';html=f'<div style="width:31px;height:31px;border-radius:50%;background:{color};border:2px solid white;color:white;font-weight:800;text-align:center;line-height:27px">{num}</div>';pop=f'<b>{num}. {q.CENTRO_MEP}</b><br>Programa: {q.PROGRAMA}<br>Código MEP: {q.CODIGO_N}<br>{q.PROVINCIA} · {q.CANTON} · {q.DISTRITO}<br>Niños: {int(q.NINOS)}';folium.Marker([lat,lon],icon=folium.DivIcon(html=html,icon_size=(31,31),icon_anchor=(15,15)),tooltip=f'{num}. {q.CENTRO_MEP} · {q.PROGRAMA}',popup=folium.Popup(pop,max_width=340)).add_to(mapa);num+=1
        st.caption(f'Pines visibles: {num-1:,}')
    st_folium(mapa,use_container_width=True,height=600,returned_objects=[])
st.subheader('Lista de centros abordados');lista=fa[['PROGRAMA','REGION_MEP','PROVINCIA','CANTON','DISTRITO','CENTRO_MEP','CODIGO_N','PRIMARIA','INTERMEDIA','NINOS']].rename(columns={'PROGRAMA':'Programa','REGION_MEP':'Región MEP','PROVINCIA':'Provincia','CANTON':'Cantón','DISTRITO':'Distrito','CENTRO_MEP':'Centro educativo','CODIGO_N':'Código MEP','PRIMARIA':'Primaria','INTERMEDIA':'Intermedia','NINOS':'Total niños'});st.dataframe(lista,use_container_width=True,hide_index=True,height=min(650,100+len(lista)*32));st.download_button('Descargar lista CSV',csv_bytes(lista),'centros_mpas_great.csv','text/csv')
pend=pd.concat([mpas[mpas.ID_FILA_MEP.isna()],great[great.ID_FILA_MEP.isna()]],ignore_index=True)
if not pend.empty:
    with st.expander(f'Registros pendientes de validar ({len(pend)})'):st.dataframe(pend[['PROGRAMA','CENTRO_ORIGEN','CODIGO_N','NINOS','COINCIDENCIA']],use_container_width=True,hide_index=True)
