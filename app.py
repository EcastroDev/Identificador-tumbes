import streamlit as st
import gdown
import zipfile
import json
import os
import numpy as np
from PIL import Image
import io
import re
import pickle
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
FOLDER_ID    = "1p-_YzXDyZHhIEXCFAz8DeOhBYhDpsjMr"
DATA_DIR     = Path("data")
CACHE_FILE   = DATA_DIR / "features_cache.pkl"

CATALOGS = {
    "CATÁLOGO DE PECES TUMBES-1-18.pdf":    {"start": 1,   "end": 18},
    "CATÁLOGO DE PECES TUMBES-19-45.pdf":   {"start": 19,  "end": 45},
    "CATÁLOGO DE PECES TUMBES-46-96.pdf":   {"start": 46,  "end": 96},
    "CATÁLOGO DE PECES TUMBES-97-167.pdf":  {"start": 97,  "end": 167},
    "CATÁLOGO DE PECES TUMBES-168-219.pdf": {"start": 168, "end": 219},
    "CATÁLOGO DE PECES TUMBES-220-246.pdf": {"start": 220, "end": 246},
}

SPECIES_PATTERN = re.compile(
    r'([A-Z][a-záéíóúñü]+\s+[a-záéíóúñü]+(?:\s+(?:[A-Z][a-záéíóúñü]+,?\s*\d{4}|\([^)]+\)))?)'
    r'[\r\n]+\u201c([^\u201d]+)\u201d',
    re.MULTILINE
)

# ─────────────────────────────────────────────
# EXTRACCIÓN DE IMÁGENES Y CARACTERÍSTICAS
# ─────────────────────────────────────────────

def color_histogram(img: Image.Image, bins=16) -> np.ndarray:
    """Histograma HSV normalizado como vector de características."""
    img_rgb = img.convert("RGB").resize((128, 128))
    arr = np.array(img_rgb, dtype=np.float32) / 255.0
    # Convertir a HSV manualmente (simple)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin + 1e-8
    # Hue
    h = np.zeros_like(r)
    mask_r = (cmax == r)
    mask_g = (cmax == g)
    mask_b = (cmax == b)
    h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6
    h[mask_g] = (b[mask_g] - r[mask_g]) / delta[mask_g] + 2
    h[mask_b] = (r[mask_b] - g[mask_b]) / delta[mask_b] + 4
    h = h / 6.0
    # Saturation
    s = np.where(cmax > 0, delta / (cmax + 1e-8), 0)
    # Value
    v = cmax
    # Histogramas separados
    h_hist, _ = np.histogram(h.flatten(), bins=bins, range=(0,1))
    s_hist, _ = np.histogram(s.flatten(), bins=bins//2, range=(0,1))
    v_hist, _ = np.histogram(v.flatten(), bins=bins//2, range=(0,1))
    feat = np.concatenate([h_hist, s_hist, v_hist]).astype(np.float32)
    norm = np.linalg.norm(feat)
    return feat / (norm + 1e-8)


def extract_all_species(catalog_dir: Path):
    """Extrae especies, imágenes y características de todos los ZIPs."""
    species_db = []

    for filename, info in CATALOGS.items():
        zip_path = catalog_dir / filename
        if not zip_path.exists():
            st.warning(f"No encontrado: {filename}")
            continue

        with zipfile.ZipFile(zip_path, 'r') as zf:
            manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
            pages = {p["page_number"]: p for p in manifest_data["pages"]}
            num_pages = manifest_data["num_pages"]

            for i in range(1, num_pages + 1):
                try:
                    txt = zf.read(f"{i}.txt").decode("utf-8", errors="ignore")
                except KeyError:
                    continue

                ph = re.search(r'^\s*(\d+)\s+(\d+)', txt)
                printed_page = int(ph.group(1)) if ph else 0

                matches = SPECIES_PATTERN.findall(txt)
                for sci, common in matches:
                    sci = sci.strip().replace('\n', ' ')
                    common = common.strip()
                    words = sci.split()
                    if len(words) < 2 or not words[1][0].islower():
                        continue

                    # Cargar imagen de la página
                    img_data = None
                    feat = None
                    page_info = pages.get(i, {})
                    img_path = page_info.get("image", {}).get("path", f"{i}.jpeg")
                    try:
                        raw = zf.read(img_path)
                        img = Image.open(io.BytesIO(raw))
                        img_data = raw
                        feat = color_histogram(img)
                    except Exception:
                        pass

                    species_db.append({
                        "scientific": sci,
                        "common": common,
                        "printed_page": printed_page,
                        "catalog_file": filename,
                        "file_page": i,
                        "has_image": page_info.get("has_visual_content", False),
                        "img_bytes": img_data,
                        "features": feat,
                    })

    return species_db


# ─────────────────────────────────────────────
# CARGA Y CACHÉ
# ─────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_database():
    DATA_DIR.mkdir(exist_ok=True)

    # Si ya existe el caché, cargarlo
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)

    # Descargar archivos desde Google Drive
    with st.spinner("📥 Descargando catálogos desde Google Drive (primera vez, puede tardar ~2 min)..."):
        try:
            gdown.download_folder(
                id=FOLDER_ID,
                output=str(DATA_DIR),
                quiet=True,
                use_cookies=False,
            )
        except Exception as e:
            st.error(f"Error al descargar: {e}")
            return []

    # Extraer especies y características
    with st.spinner("🔬 Procesando catálogo (primera vez, ~1 min)..."):
        db = extract_all_species(DATA_DIR)

    # Guardar caché
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(db, f)

    return db


def find_similar(query_img: Image.Image, db: list, top_k=5):
    """Encuentra las k especies más similares por histograma de color."""
    q_feat = color_histogram(query_img)
    scores = []
    for i, sp in enumerate(db):
        if sp["features"] is not None:
            sim = float(np.dot(q_feat, sp["features"]))
            scores.append((sim, i))
    scores.sort(reverse=True)
    return [(db[i], s) for s, i in scores[:top_k]]


# ─────────────────────────────────────────────
# INTERFAZ
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Identificador de Peces – Tumbes",
    page_icon="🐟",
    layout="wide",
)

# CSS personalizado
st.markdown("""
<style>
    .main { background: #f0f7ff; }
    .stApp { background: linear-gradient(160deg,#0c4a6e,#075985 40%,#0369a1); }
    .block-container { padding-top: 1rem; }
    h1 { color: white !important; font-size: 1.6rem !important; }
    p, li { color: rgba(255,255,255,0.9) !important; }
    .result-card {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .species-title { font-size: 1.1rem; font-weight: bold; color: white; }
    .species-sci { font-style: italic; color: #bae6fd; font-size: 0.9rem; }
    .page-ref {
        background: rgba(37,99,235,0.4);
        border-radius: 6px; padding: 3px 10px;
        font-size: 0.8rem; color: #bfdbfe; display: inline-block;
    }
    .sim-bar-wrap { background: rgba(255,255,255,0.15); border-radius:4px; height:6px; margin-top:4px; }
    .sim-bar { background: #38bdf8; border-radius:4px; height:6px; }
</style>
""", unsafe_allow_html=True)

# Encabezado
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("## 🐟")
with col_title:
    st.markdown("# IDENTIFICADOR DE PECES — TUMBES")
    st.markdown("<p style='font-size:0.75rem;letter-spacing:2px;color:rgba(186,230,253,0.8)'>CATÁLOGO IMARPE 2022 · APOYO A FISCALIZACIÓN PESQUERA</p>", unsafe_allow_html=True)

st.divider()

# Cargar base de datos
db = load_database()

if not db:
    st.error("No se pudo cargar la base de datos. Verifica la conexión y los archivos en Drive.")
    st.stop()

total_species = len(set(sp["scientific"] for sp in db))
st.success(f"✅ Base de datos cargada: **{total_species} especies** del Catálogo IMARPE 2022")

st.markdown("---")

# Subida de imagen
st.markdown("### 📷 Sube la foto del pez")
uploaded = st.file_uploader(
    "Arrastra una imagen o toca para seleccionar (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
)

if uploaded:
    col_img, col_res = st.columns([1, 1])

    with col_img:
        st.markdown("**Imagen analizada:**")
        query_img = Image.open(uploaded).convert("RGB")
        st.image(query_img, use_container_width=True)

    with col_res:
        st.markdown("**🔍 Especies más similares:**")

        with st.spinner("Analizando imagen..."):
            results = find_similar(query_img, db, top_k=5)

        for rank, (sp, sim) in enumerate(results, 1):
            pct = int(sim * 100)
            with st.container():
                st.markdown(f"""
                <div class='result-card'>
                    <div class='species-title'>#{rank} {sp['common']}</div>
                    <div class='species-sci'>{sp['scientific']}</div>
                    <span class='page-ref'>📖 p.{sp['printed_page']}</span>
                    <div class='sim-bar-wrap'><div class='sim-bar' style='width:{pct}%'></div></div>
                    <small style='color:rgba(186,230,253,0.7)'>Similitud: {pct}%</small>
                </div>
                """, unsafe_allow_html=True)

                # Mostrar imagen de referencia del catálogo
                if sp.get("img_bytes"):
                    with st.expander(f"Ver página del catálogo — {sp['common']}"):
                        ref_img = Image.open(io.BytesIO(sp["img_bytes"]))
                        st.image(ref_img, caption=f"{sp['scientific']} · p.{sp['printed_page']} · {sp['catalog_file']}", use_container_width=True)

    # Advertencia técnica
    st.info(
        "💡 **Cómo funciona:** La identificación usa similitud de color entre tu foto y las páginas del catálogo. "
        "Para mejores resultados: foto con buena iluminación, fondo neutro, cuerpo completo visible. "
        "Siempre verifica la especie consultando la página indicada en el catálogo físico."
    )

else:
    st.markdown(
        "<div style='text-align:center;padding:40px;color:rgba(186,230,253,0.6);font-size:1.1rem'>"
        "👆 Sube una foto para identificar la especie"
        "</div>",
        unsafe_allow_html=True,
    )

# Pie de página
st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.7rem;color:rgba(186,230,253,0.4);letter-spacing:1px'>"
    "CATÁLOGO ILUSTRADO DE LA ICTIOFAUNA DE LA REGIÓN TUMBES · IMARPE 2022 · FISCALIZACIÓN PESQUERA"
    "</p>",
    unsafe_allow_html=True,
)
