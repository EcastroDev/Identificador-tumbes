import streamlit as st
import pandas as pd
import gdown
import zipfile
import os
import glob

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
ZIP_FILE_ID   = "1-buA01ayUVId3zs5sbM-O_FJDPplsumq"
ZIP_LOCAL     = "listas_embarcaciones.zip"
CARPETA_DATOS = "listas_embarcaciones"

RECURSOS = {
    "🐟 BONITO":  {"nombre": "Bonito (Sarda chiliensis chiliensis)", "archivo": "Bonito.xlsx"},
    "🐠 MERLUZA": {"nombre": "Merluza (Merluccius gayi peruanus)",   "archivo": "Merluza.xlsx"},
    "🦑 POTA":    {"nombre": "Pota / Calamar gigante (Dosidicus gigas)", "archivo": "Pota.xlsx"},
}

# Etiquetas amigables para mostrar al fiscalizador
ETIQUETAS = {
    # Matrícula
    "MATRICULA": "Matrícula",
    "MATRÍCULA": "Matrícula",
    "N° MATRICULA": "Matrícula",
    "Nº MATRICULA": "Matrícula",
    "NRO MATRICULA": "Matrícula",
    "MAT": "Matrícula",
    # Nombre
    "NOMBRE": "Nombre EP",
    "NOMBRE DE LA EMBARCACIÓN": "Nombre EP",
    "NOMBRE EMBARCACION": "Nombre EP",
    "NOMBRE DE EMBARCACION": "Nombre EP",
    # Capacidad
    "CAPACIDAD DE BODEGA": "Capacidad de bodega (m³)",
    "CAPACIDAD": "Capacidad de bodega (m³)",
    "CAP. BODEGA": "Capacidad de bodega (m³)",
    "CAP BODEGA": "Capacidad de bodega (m³)",
    "CB": "Capacidad de bodega (m³)",
    # Puerto / DPA
    "PUERTO": "Puerto base",
    "DPA": "DPA / Puerto",
    "PUERTO BASE": "Puerto base",
    "CALETA": "Caleta base",
    "LUGAR DE DESEMBARQUE": "Lugar de desembarque",
    # Propietario / Armador
    "ARMADOR": "Armador",
    "PROPIETARIO": "Propietario",
    "TITULAR": "Titular",
    "RAZÓN SOCIAL": "Razón social",
    "RAZON SOCIAL": "Razón social",
    # Permiso / Resolución
    "PERMISO": "Permiso de pesca",
    "N° PERMISO": "Permiso de pesca",
    "RESOLUCIÓN": "Resolución",
    "RESOLUCION": "Resolución",
    "RD": "Resolución",
    # Tipo arte
    "ARTE DE PESCA": "Arte de pesca",
    "ARTE": "Arte de pesca",
    "SISTEMA DE PESCA": "Sistema de pesca",
    # Eslora / TM
    "ESLORA": "Eslora (m)",
    "TM": "Tonelaje (TM)",
    "TONELAJE": "Tonelaje (TM)",
    # Región / Sede
    "REGIÓN": "Región",
    "REGION": "Región",
    "SEDE": "Sede DIREPRO",
    "DIREPRO": "Sede DIREPRO",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Verificador de Embarcaciones",
    page_icon="🐟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
.stApp{background:linear-gradient(160deg,#0a1628 0%,#0d2240 60%,#0a3d2e 100%);min-height:100vh;}
.header-block{text-align:center;padding:1.8rem 1rem 0.4rem;}
.header-block h1{font-family:'IBM Plex Mono',monospace;font-size:1.4rem;color:#00d4aa;letter-spacing:2px;text-transform:uppercase;margin:0;}
.header-block p{color:#7ab8c8;font-size:0.8rem;margin:.3rem 0 0;letter-spacing:1px;}
.result-ok{background:linear-gradient(135deg,rgba(0,200,100,.12),rgba(0,212,170,.08));border:2px solid #00c864;border-radius:14px;padding:1.2rem 1.4rem;margin:1rem 0;}
.result-ok .badge{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;color:#00c864;letter-spacing:2px;margin-bottom:.6rem;}
.result-ok .vessel{font-size:1.15rem;font-weight:700;color:#e0f8f0;margin-bottom:.8rem;padding-bottom:.5rem;border-bottom:1px solid rgba(0,212,170,.2);}
.ficha-row{display:flex;justify-content:space-between;align-items:flex-start;padding:.35rem 0;border-bottom:1px solid rgba(255,255,255,.05);}
.ficha-label{font-size:.72rem;color:#5aa0b8;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:.5px;flex:1;padding-right:.5rem;}
.ficha-val{font-size:.82rem;color:#e0f8f0;font-weight:600;flex:1.5;text-align:right;}
.ficha-val.noregistra{color:#4a7080;font-style:italic;font-weight:400;}
.result-fail{background:rgba(200,40,40,.1);border:2px solid #dc3232;border-radius:14px;padding:1.2rem 1.4rem;margin:1rem 0;}
.result-fail .badge{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;color:#ff5555;letter-spacing:2px;}
.result-fail .detail{font-size:.85rem;color:#ffaaaa;margin-top:.4rem;line-height:1.6;}
.accion{background:rgba(255,180,0,.07);border-left:3px solid #ffc800;padding:.7rem 1rem;border-radius:0 8px 8px 0;margin:.8rem 0;font-size:.8rem;color:#ffe066;line-height:1.6;}
.footer{text-align:center;font-size:.65rem;color:#2a4860;margin-top:2rem;font-family:'IBM Plex Mono',monospace;}
.stSelectbox>div>div{background:rgba(255,255,255,.06)!important;border:1px solid rgba(0,212,170,.25)!important;color:#e0f0ff!important;border-radius:8px!important;}
.stTextInput>div>div>input{background:rgba(255,255,255,.06)!important;border:1px solid rgba(0,212,170,.25)!important;color:#e0f0ff!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-size:1rem!important;letter-spacing:2px!important;text-transform:uppercase!important;}
.stTextInput>div>div>input::placeholder{color:#2a4860!important;}
div[data-testid="stSelectbox"] label,div[data-testid="stTextInput"] label{color:#7ab8c8!important;font-size:.72rem!important;font-family:'IBM Plex Mono',monospace!important;letter-spacing:1.5px!important;text-transform:uppercase!important;}
.stButton>button{background:linear-gradient(135deg,#00d4aa,#0099cc)!important;color:#0a1628!important;border:none!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-weight:700!important;letter-spacing:2px!important;text-transform:uppercase!important;width:100%!important;padding:.6rem!important;font-size:.88rem!important;transition:opacity .2s!important;}
.stButton>button:active{opacity:.75!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:.8rem!important;max-width:520px!important;}
</style>
""", unsafe_allow_html=True)


# ── DESCARGA ZIP ──────────────────────────────────────────────────────────────

def _req_download(file_id, destino):
    import requests, re
    s = requests.Session()
    for url in [
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0&confirm=t",
        f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
    ]:
        try:
            r = s.get(url, stream=True, timeout=60)
            if r.status_code != 200:
                continue
            if "text/html" in r.headers.get("Content-Type",""):
                m = re.search(r'confirm=([0-9A-Za-z_-]+)', r.text)
                if m:
                    r = s.get(f"https://drive.google.com/uc?export=download&confirm={m.group(1)}&id={file_id}", stream=True, timeout=60)
            with open(destino,"wb") as f:
                for chunk in r.iter_content(32768):
                    if chunk: f.write(chunk)
            if zipfile.is_zipfile(destino):
                return True
            if os.path.exists(destino): os.remove(destino)
        except Exception:
            continue
    return False


@st.cache_resource(show_spinner=False)
def init_datos():
    """Descarga y extrae el ZIP una sola vez."""
    if os.path.exists(CARPETA_DATOS):
        if glob.glob(f"{CARPETA_DATOS}/*.xlsx"):
            return True
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    ok = False
    try:
        gdown.download(f"https://drive.google.com/uc?id={ZIP_FILE_ID}", output=ZIP_LOCAL, quiet=True)
        ok = os.path.exists(ZIP_LOCAL) and zipfile.is_zipfile(ZIP_LOCAL)
    except Exception:
        pass
    if not ok:
        ok = _req_download(ZIP_FILE_ID, ZIP_LOCAL)
    if not ok:
        return False
    with zipfile.ZipFile(ZIP_LOCAL,"r") as zf:
        for m in zf.namelist():
            fn = os.path.basename(m)
            if not fn: continue
            with zf.open(m) as src, open(os.path.join(CARPETA_DATOS,fn),"wb") as dst:
                dst.write(src.read())
    return True


# ── LECTURA INTELIGENTE DEL EXCEL ─────────────────────────────────────────────

def _es_fila_encabezado(fila_valores):
    """
    Retorna True si la fila parece contener encabezados de columna reales.
    Busca palabras clave típicas de encabezados de listas de embarcaciones.
    """
    keywords = [
        "MATRICUL","MATRÍCUL","N°","NRO","NOMBRE","EMBARCAC",
        "CAPACIDAD","PERMISO","ARMADOR","PROPIETARIO","PUERTO",
        "CALETA","ARTE","ESLORA","REGIÓN","REGION","RESOLUC",
        "TITULAR","BODEGA","TONELAJE","SEDE","CB","DPA"
    ]
    texto = " ".join(str(v).upper() for v in fila_valores if pd.notna(v) and str(v).strip())
    hits = sum(1 for k in keywords if k in texto)
    return hits >= 2


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_excel(archivo):
    """
    Lee el Excel detectando automáticamente la fila de encabezados reales,
    ignorando títulos y filas decorativas iniciales.
    """
    ruta = os.path.join(CARPETA_DATOS, archivo)
    if not os.path.exists(ruta):
        for f in glob.glob(f"{CARPETA_DATOS}/*"):
            if os.path.basename(f).lower() == archivo.lower():
                ruta = f; break
        else:
            return None, "Archivo no encontrado en el ZIP"

    # Leer el archivo raw sin encabezados para inspeccionar todas las filas
    try:
        raw = pd.read_excel(ruta, engine="openpyxl", header=None, dtype=str)
    except Exception as e:
        return None, f"Error leyendo Excel: {e}"

    if raw.empty:
        return None, "El archivo Excel está vacío"

    # Buscar la fila que contiene los encabezados reales (máx. primeras 15 filas)
    header_row = None
    for i in range(min(15, len(raw))):
        if _es_fila_encabezado(raw.iloc[i].values):
            header_row = i
            break

    if header_row is None:
        # Fallback: usar fila 0 y confiar en la detección posterior
        header_row = 0

    # Reconstruir DataFrame usando esa fila como encabezado
    df = pd.read_excel(ruta, engine="openpyxl", header=header_row, dtype=str)

    # Limpiar columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("UNNAMED")]
    df = df.loc[:, df.columns != "NAN"]
    df = df.dropna(how="all")

    # Limpiar valores
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # Eliminar filas que parecen sub-encabezados repetidos
    if len(df) > 0:
        primera_col = df.columns[0]
        df = df[df[primera_col] != primera_col]

    return df.reset_index(drop=True), None


# ── DETECCIÓN DE COLUMNAS ─────────────────────────────────────────────────────

def detectar_col(df, variantes):
    """Busca la primera columna que coincida con alguna de las variantes."""
    cols_upper = {c.upper(): c for c in df.columns}
    for v in variantes:
        if v.upper() in cols_upper:
            return cols_upper[v.upper()]
    # Búsqueda parcial
    for v in variantes:
        for col in df.columns:
            if v.upper() in col.upper():
                return col
    return None


def detectar_col_matricula(df):
    return detectar_col(df, [
        "MATRÍCULA","MATRICULA","N° MATRÍCULA","N° MATRICULA",
        "Nº MATRICULA","NRO MATRICULA","NRO. MATRICULA",
        "MATRICULA NAVE","MATRICULA DE LA EMBARCACIÓN","MAT","MATR"
    ])


def detectar_col_nombre(df):
    return detectar_col(df, [
        "NOMBRE DE LA EMBARCACIÓN","NOMBRE DE LA EMBARCACION",
        "NOMBRE EMBARCACIÓN","NOMBRE EMBARCACION",
        "NOMBRE DE EMBARCACIÓN","NOMBRE","NAVE"
    ])


# ── BÚSQUEDA ──────────────────────────────────────────────────────────────────

def limpiar(s):
    return str(s).strip().upper().replace(" ","").replace("-","").replace(".","")


def buscar(df, termino_raw, col_mat, col_nom=None):
    termino = limpiar(termino_raw)
    if not termino or len(termino) < 2:
        return None

    vals_mat = df[col_mat].apply(limpiar)

    # 1. Exacta
    mask = vals_mat == termino
    if mask.any():
        return df[mask].copy()

    # 2. Parcial en matrícula
    mask = vals_mat.str.contains(termino, na=False, regex=False)
    if mask.any():
        return df[mask].copy()

    # 3. En nombre
    if col_nom:
        vals_nom = df[col_nom].apply(limpiar)
        mask = vals_nom.str.contains(termino, na=False, regex=False)
        if mask.any():
            return df[mask].copy()

    return None


# ── FICHA FISCALIZADOR ────────────────────────────────────────────────────────

# Orden preferido de campos en la ficha
ORDEN_FICHA = [
    "NOMBRE","NOMBRE DE LA EMBARCACIÓN","NOMBRE EMBARCACION","NOMBRE DE EMBARCACION",
    "MATRICULA","MATRÍCULA","N° MATRICULA","Nº MATRICULA","NRO MATRICULA",
    "CAPACIDAD DE BODEGA","CAPACIDAD","CAP. BODEGA","CAP BODEGA","CB",
    "PUERTO","PUERTO BASE","DPA","CALETA","LUGAR DE DESEMBARQUE",
    "ARMADOR","PROPIETARIO","TITULAR","RAZÓN SOCIAL","RAZON SOCIAL",
    "ARTE DE PESCA","ARTE","SISTEMA DE PESCA",
    "PERMISO","N° PERMISO","RESOLUCIÓN","RESOLUCION","RD",
    "ESLORA","TM","TONELAJE",
    "REGIÓN","REGION","SEDE","DIREPRO",
]


def etiqueta_amigable(col):
    """Convierte nombre de columna técnico a etiqueta legible."""
    return ETIQUETAS.get(col.upper(), col.title())


def valor_o_nr(val):
    """Retorna el valor o 'No registra' si está vacío."""
    v = str(val).strip()
    if not v or v.lower() in ["nan","none","","0"]:
        return None  # Se marcará como "No registra"
    return v


def render_ficha(fila, col_mat, col_nom, recurso_nombre):
    """Genera HTML de ficha completa orientada al fiscalizador."""
    nombre_emb = valor_o_nr(fila.get(col_nom, "")) or "No registra"
    matricula_emb = valor_o_nr(fila.get(col_mat, "")) or "—"

    # Construir filas de datos en el orden preferido
    cols_mostradas = set()
    filas_html = ""

    def agregar_fila(col):
        nonlocal filas_html
        if col not in fila.index or col in cols_mostradas:
            return
        cols_mostradas.add(col)
        val = valor_o_nr(fila[col])
        label = etiqueta_amigable(col)
        if val:
            filas_html += (
                f'<div class="ficha-row">'
                f'<span class="ficha-label">{label}</span>'
                f'<span class="ficha-val">{val}</span>'
                f'</div>'
            )
        else:
            filas_html += (
                f'<div class="ficha-row">'
                f'<span class="ficha-label">{label}</span>'
                f'<span class="ficha-val noregistra">No registra</span>'
                f'</div>'
            )

    # Primero: campos en orden preferido
    for campo_preferido in ORDEN_FICHA:
        # Buscar columna que coincida con este campo preferido
        for col in fila.index:
            if col.upper() == campo_preferido.upper() and col not in cols_mostradas:
                agregar_fila(col)

    # Luego: columnas restantes que no se mostraron
    for col in fila.index:
        if col not in cols_mostradas:
            agregar_fila(col)

    return f"""
<div class="result-ok">
  <div class="badge">✅ AUTORIZADA</div>
  <div class="vessel">{nombre_emb}</div>
  <div class="ficha-row">
    <span class="ficha-label">Recurso verificado</span>
    <span class="ficha-val" style="color:#00d4aa;">{recurso_nombre}</span>
  </div>
  {filas_html}
</div>"""


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-block">
  <h1>⚓ VERIFICADOR<br>DE EMBARCACIONES</h1>
  <p>DIREPRO TUMBES · PRODUCE</p>
</div>
""", unsafe_allow_html=True)

# Inicializar datos al arrancar
listas_ok = init_datos()

if not listas_ok:
    st.error("No se pudieron cargar las listas. Verifica los permisos del ZIP en Google Drive.")
    st.stop()

recurso_key = st.selectbox("RECURSO A VERIFICAR", options=list(RECURSOS.keys()))
recurso_info = RECURSOS[recurso_key]

st.markdown(
    f'<div style="font-size:.72rem;color:#7ab8c8;font-family:IBM Plex Mono,monospace;'
    f'margin:.1rem 0 .7rem;">▸ {recurso_info["nombre"]}</div>',
    unsafe_allow_html=True
)

termino = st.text_input(
    "MATRÍCULA, NÚMERO O NOMBRE DE EMBARCACIÓN",
    placeholder="Ej: PS-56224-BM  ó  56224  ó  nombre",
    max_chars=60,
    key="busqueda",
)

buscar_btn = st.button("🔍  VERIFICAR EMBARCACIÓN")

# ── LÓGICA DE BÚSQUEDA ────────────────────────────────────────────────────────

if buscar_btn or (termino and len(termino.strip()) >= 3):

    df, error = cargar_excel(recurso_info["archivo"])

    if error or df is None:
        st.error(f"Error cargando {recurso_info['archivo']}: {error}")
    else:
        col_mat = detectar_col_matricula(df)
        col_nom = detectar_col_nombre(df)

        if col_mat is None:
            st.error(
                f"No se detectó columna de matrícula en {recurso_info['archivo']}. "
                f"Columnas disponibles: {list(df.columns)}"
            )
        else:
            resultados = buscar(df, termino.strip(), col_mat, col_nom)

            if resultados is not None and len(resultados) > 0:
                if len(resultados) > 1:
                    st.markdown(
                        f'<div style="font-size:.78rem;color:#00d4aa;font-family:IBM Plex Mono,'
                        f'monospace;margin:.3rem 0 .2rem;">📋 {len(resultados)} coincidencias encontradas</div>',
                        unsafe_allow_html=True
                    )
                for _, fila in resultados.iterrows():
                    st.markdown(
                        render_ficha(fila, col_mat, col_nom, recurso_info["nombre"]),
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f"""
<div class="result-fail">
  <div class="badge">❌ NO AUTORIZADA</div>
  <div class="detail">
    <b>{termino.strip().upper()}</b> no figura en la lista oficial
    para <b>{recurso_info['nombre']}</b>.
  </div>
</div>""", unsafe_allow_html=True)
                st.markdown("""
<div class="accion">
  ⚠️ <b>Acción del fiscalizador:</b> Documentar en acta de fiscalización.
  Verificar permiso de pesca vigente y tipificar conforme
  DS 017-2017-PRODUCE y modificatorias vigentes.
</div>""", unsafe_allow_html=True)

            st.markdown(
                f'<div style="font-size:.65rem;color:#2a4860;text-align:right;'
                f'font-family:IBM Plex Mono,monospace;margin-top:.4rem;">'
                f'{len(df):,} embarcaciones en lista · {recurso_info["archivo"]}</div>',
                unsafe_allow_html=True
            )

# ── EXPANDERS ─────────────────────────────────────────────────────────────────

with st.expander("📋 ¿Cómo usar?"):
    st.markdown("""
    1. Selecciona el **recurso** que está siendo extraído.
    2. Ingresa la **matrícula completa**, solo el **número** o el **nombre** del barco.
    3. Toca **VERIFICAR** — también busca automáticamente al escribir.

    **Ejemplos válidos:** `PS-56224-BM` · `56224` · `SEÑOR DE SIPAN`

    ✅ **AUTORIZADA** → Ficha completa con todos los datos de la embarcación.
    ❌ **NO AUTORIZADA** → Documentar en acta.
    """)

with st.expander("⚖️ Base legal"):
    st.markdown("""
    - DS 017-2017-PRODUCE – Reglamento de Fiscalización y Sanción
    - DS 009-2025-PRODUCE / DS 006-2025-PRODUCE – Modificatorias
    - DS 020-2011-PRODUCE – ROP Tumbes
    - RM N° 00070-2026-PRODUCE – Bonito artesanal 2026
    """)

st.markdown("""
<div class="footer">
  DIREPRO TUMBES · PRODUCE · USO OFICIAL EN CAMPO<br>
  Datos según lista PRODUCE vigente
</div>
""", unsafe_allow_html=True)
