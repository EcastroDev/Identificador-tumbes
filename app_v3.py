import streamlit as st
import numpy as np
from PIL import Image
import io
import pickle
from pathlib import Path

# ─────────────────────────────────────────────
# PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Identificador de Peces – Tumbes",
    page_icon="🐟",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: linear-gradient(160deg,#0c4a6e 0%,#075985 40%,#0369a1 100%); }
.block-container { padding-top:.8rem; max-width:1000px; }
h1,h2,h3 { color:white !important; }
p,li,label,.stMarkdown p { color:rgba(255,255,255,.9) !important; }
.rcard {
    background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18);
    border-radius:14px; padding:13px 15px; margin-bottom:9px;
}
.sp-name { font-size:1.05rem; font-weight:700; color:#fff; }
.sp-sci  { font-style:italic; color:#bae6fd; font-size:.83rem; }
.sp-page {
    background:rgba(37,99,235,.45); border-radius:6px;
    padding:2px 10px; font-size:.78rem; color:#bfdbfe; display:inline-block; margin-top:4px;
}
.bar-bg { background:rgba(255,255,255,.15); border-radius:4px; height:5px; margin-top:6px; }
.bar-fg { background:#38bdf8; border-radius:4px; height:5px; }
.loading-msg {
    background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.15);
    border-radius:12px; padding:20px; text-align:center; margin:20px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
c1, c2 = st.columns([1, 9])
with c1:
    st.markdown("<div style='font-size:2.5rem;margin-top:5px'>🐟</div>", unsafe_allow_html=True)
with c2:
    st.markdown("## IDENTIFICADOR DE PECES — TUMBES")
    st.markdown(
        "<p style='font-size:.72rem;letter-spacing:2px;color:rgba(186,230,253,.75);margin-top:-8px'>"
        "CATÁLOGO IMARPE 2022 · APOYO A FISCALIZACIÓN PESQUERA</p>",
        unsafe_allow_html=True,
    )
st.divider()

# ─────────────────────────────────────────────
# CARGA BASE DE DATOS
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_db():
    db_path = Path(__file__).parent / "species_db.pkl"
    with open(db_path, "rb") as f:
        return pickle.load(f)

# ─────────────────────────────────────────────
# CARGA CLIP + EMBEDDINGS (primera vez ~3-4 min)
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_clip_and_embeddings():
    """
    Descarga CLIP ViT-B/32 (~338MB) y computa embeddings de las 219 especies.
    Solo ocurre UNA VEZ después de cada despliegue.
    """
    import torch
    from transformers import CLIPProcessor, CLIPModel

    model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.eval()

    db = load_db()

    embeddings = []
    for sp in db:
        if sp.get("fish_thumb"):
            img = Image.open(io.BytesIO(sp["fish_thumb"])).convert("RGB")
            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                feat = model.get_image_features(**inputs)
                feat = feat / feat.norm(dim=-1, keepdim=True)
            embeddings.append(feat.squeeze().numpy().astype(np.float32))
        else:
            embeddings.append(np.zeros(512, dtype=np.float32))

    return model, processor, db, np.stack(embeddings)


def query_clip(query_img: Image.Image, model, processor, db, embeddings, top_k=5):
    import torch
    inputs = processor(images=query_img.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        q = model.get_image_features(**inputs)
        q = q / q.norm(dim=-1, keepdim=True)
    q = q.squeeze().numpy()
    sims = np.dot(embeddings, q)
    top_idx = np.argsort(sims)[::-1][:top_k]
    return [(db[i], round(float(sims[i]) * 100)) for i in top_idx]


# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────
db = load_db()
total_sp = len(set(s["scientific"] for s in db))

# Intentar cargar CLIP (puede tardar la primera vez)
clip_ready = False
model = processor = embeddings = None

with st.spinner("🤖 Cargando modelo de visión CLIP (primera vez: ~3-4 min, luego instantáneo)..."):
    try:
        model, processor, db, embeddings = load_clip_and_embeddings()
        clip_ready = True
    except Exception as e:
        st.error(f"No se pudo cargar CLIP: {e}")

if clip_ready:
    st.success(f"✅ **{total_sp} especies** listas · Modelo CLIP activo")
else:
    st.warning("⚠️ Modelo CLIP no disponible. Verifica que torch y transformers estén instalados.")
    st.stop()

st.markdown("---")

# ─────────────────────────────────────────────
# SUBIDA DE IMAGEN / CÁMARA
# ─────────────────────────────────────────────
st.markdown("### 📷 Captura o sube la foto del pez")
tab_cam, tab_file = st.tabs(["📸  Tomar foto con cámara", "📂  Subir imagen"])

img_input = None
with tab_cam:
    cam = st.camera_input("Apunta la cámara al pez y toca el botón")
    if cam:
        img_input = Image.open(cam).convert("RGB")

with tab_file:
    upl = st.file_uploader(
        "Arrastra o selecciona una imagen (JPG, PNG, WEBP)",
        type=["jpg","jpeg","png","webp"],
    )
    if upl:
        img_input = Image.open(upl).convert("RGB")

# ─────────────────────────────────────────────
# RESULTADOS
# ─────────────────────────────────────────────
if img_input:
    st.markdown("---")
    ci, cr = st.columns([1, 1])

    with ci:
        st.markdown("**Imagen analizada:**")
        st.image(img_input, use_container_width=True)

    with cr:
        st.markdown("**🔍 Top 5 — especies más similares:**")
        with st.spinner("Analizando con CLIP..."):
            results = query_clip(img_input, model, processor, db, embeddings, top_k=5)

        for rank, (sp, pct) in enumerate(results, 1):
            st.markdown(f"""
            <div class='rcard'>
                <div class='sp-name'>#{rank} &nbsp; {sp['common']}</div>
                <div class='sp-sci'>{sp['scientific']}</div>
                <span class='sp-page'>📖 p.{sp['printed_page']}</span>
                <div class='bar-bg'>
                    <div class='bar-fg' style='width:{min(pct,100)}%'></div>
                </div>
                <small style='color:rgba(186,230,253,.65)'>Similitud CLIP: {pct}%</small>
            </div>""", unsafe_allow_html=True)

            if sp.get("fish_thumb"):
                with st.expander(f"📄 Ver foto del catálogo — {sp['common']}"):
                    st.image(
                        Image.open(io.BytesIO(sp["fish_thumb"])),
                        caption=f"{sp['scientific']} · p.{sp['printed_page']}",
                        use_container_width=True,
                    )

    st.info("💡 CLIP analiza forma, textura y patrones del pez — no solo color. "
            "Para mejores resultados: foto clara, pez completo, buena iluminación.")

else:
    st.markdown(
        "<div style='text-align:center;padding:35px;color:rgba(186,230,253,.45)'>"
        "👆 Usa la cámara o sube una foto para identificar</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<p style='text-align:center;font-size:.65rem;color:rgba(186,230,253,.3);"
    "letter-spacing:1px;margin-top:18px'>"
    "CATÁLOGO ILUSTRADO DE LA ICTIOFAUNA DE LA REGIÓN TUMBES · IMARPE 2022</p>",
    unsafe_allow_html=True,
)
