import streamlit as st
import anthropic
import base64
import json
from PIL import Image
import io

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Identificador de Peces – Tumbes",
    page_icon="🐟",
    layout="centered",
)

# ── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: linear-gradient(160deg, #0c4a6e, #075985, #0369a1, #1e3a8a); }

  .header-box {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 22px;
    display: flex; align-items: center; gap: 14px;
  }
  .header-box h1 { font-size: 20px; font-weight: 700; color: white; margin: 0; }
  .header-box p  { font-size: 11px; color: rgba(186,230,253,0.8);
                   letter-spacing: 1.5px; text-transform: uppercase; margin: 4px 0 0 0; }

  .card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
  }
  .card-head {
    background: rgba(14,165,233,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 14px;
  }
  .species-title { font-size: 22px; font-weight: 700; color: white; }
  .species-sci   { font-size: 14px; font-style: italic; color: rgba(186,230,253,0.85); }
  .grupo-tag {
    background: rgba(255,255,255,0.15); color: rgba(186,230,253,0.9);
    padding: 2px 10px; border-radius: 20px; font-size: 11px;
    display: inline-block; margin-top: 6px;
  }
  .badge-alto  { background:#065f46; color:#6ee7b7; border:1px solid #047857;
                 padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
  .badge-medio { background:#78350f; color:#fcd34d; border:1px solid #b45309;
                 padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
  .badge-bajo  { background:#7f1d1d; color:#fca5a5; border:1px solid #b91c1c;
                 padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
  .page-badge  { background:rgba(37,99,235,0.4); color:#bfdbfe;
                 border:1px solid rgba(37,99,235,0.6);
                 padding:4px 12px; border-radius:8px; font-size:13px; font-weight:700; }
  .section-label {
    color: rgba(186,230,253,0.8); font-size: 10px;
    font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
  }
  .info-block {
    background: rgba(0,0,0,0.2); border-radius: 10px;
    padding: 11px 13px; margin-bottom: 10px;
  }
  .info-block p { color: rgba(255,255,255,0.8); font-size: 13px; line-height: 1.5; margin: 0; }
  .reg-block {
    background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px; padding: 12px 14px; margin-bottom: 10px;
  }
  .reg-block .reg-title { color: #fca5a5; font-size: 11px; font-weight: 700;
                           text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
  .reg-row { display:flex; gap:8px; margin-bottom:4px; }
  .reg-label { color:#fca5a5; font-size:11px; min-width:95px; }
  .reg-val   { color:rgba(255,255,255,0.85); font-size:12px; }
  .ref-box {
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 10px; color: rgba(186,230,253,0.6); font-size: 11px;
  }
  .alert-warn {
    background: rgba(251,191,36,0.15); border: 1px solid rgba(251,191,36,0.4);
    border-radius: 10px; padding: 12px 16px; color: #fde68a; font-size: 13px;
    margin-bottom: 14px;
  }
  .note-box {
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px; padding: 10px 14px;
    color: rgba(186,230,253,0.8); font-size: 12px; margin-bottom: 14px;
  }
  .footer-txt {
    text-align: center; color: rgba(186,230,253,0.35);
    font-size: 10px; letter-spacing: 1px; margin-top: 24px;
  }
  /* Ocultar elementos por defecto de Streamlit */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Catálogo IMARPE 2022 ─────────────────────────────────────────────────────
CATALOG_INDEX = """CATÁLOGO ILUSTRADO DE LA ICTIOFAUNA DE LA REGIÓN TUMBES (IMARPE, 2022)
ÍNDICE DE ESPECIES (Nombre científico | Nombre común | Página):
Callorhinchus callorynchus (Linnaeus, 1758) | Peje gallo | p.38
Rhincodon typus Smith, 1828 | Tiburón ballena | p.40
Carcharhinus leucas (Müller & Henle, 1839) | Tiburón ñato | p.48
Carcharhinus obscurus (Lesueur, 1818) | Tiburón mantequero | p.50
Prionace glauca (Linnaeus, 1758) | Tiburón azul | p.50
Sphyrna lewini (Griffith & Smith, 1834) | Tiburón martillo | p.52
Sphyrna zygaena (Linnaeus, 1758) | Tiburón martillo | p.54
Notorynchus cepedianus (Péron, 1807) | Tiburón gato | p.56
Echinorhinus cookei Pietschmann, 1928 | Tiburón negro espinoso | p.58
Squatina californica Ayres, 1859 | Angelote | p.60
Tetronarce tremens (de Buen, 1959) | Raya eléctrica | p.62
Rostroraja velezi (Chirichigno F., 1973) | Raya bruja | p.66
Gymnura crebripunctata (Peters, 1869) | Raya mariposa | p.74
Aetobatus narinari (Euphrasen, 1790) | Raya pico de pato | p.82
Mobula birostris (Walbaum, 1792) | Mantarraya gigante | p.82
Elops affinis Regan, 1909 | Picha aguada | p.92
Albula esuncula (Garman, 1899) | Zorro | p.94
Gymnothorax phalarus Bussing, 1998 | Morena cola pintada | p.98
Muraena argus (Steindachner, 1870) | Morena | p.98
Echiophis brunneus (Castro-Aguirre & Suárez de los Cobos, 1983) | Anguila moteada | p.100
Ophichthus frontalis Garman, 1899 | Anguila rayada | p.102
Ophichthus remiger (Valenciennes, 1837) | Anguila común | p.102
Cynoponticus coniceps (Jordan & Gilbert, 1882) | Bio bio | p.106
Anchoa ischana (Jordan & Gilbert, 1882) | Anchoa | p.110
Anchovia macrolepidota (Kner, 1863) | Anchoa plateada | p.112
Cetengraulis mysticetus (Günther, 1867) | Ayamarca | p.112
Lile stolifera (Jordan & Gilbert, 1882) | Pelada | p.114
Opisthonema bulleri (Regan, 1904) | Machete de hebra | p.116
Saccodon wagneri Kner, 1863 | Cholito | p.118
Pseudocurimata troschelii (Günther, 1860) | Dica | p.120
Lebiasina bimaculata Valenciennes, 1847 | Charcoca | p.122
Eretmobrycon brevirostris (Günther, 1860) | Sable / Sabalito | p.124
Rhoadsia altipinna Fowler, 1911 | Pampanito | p.126
Eretmobrycon festae (Boulenger, 1898) | Sabalito | p.126
Brycon dentex Günther, 1860 | Sábalo | p.130
Ariopsis seemanni (Günther, 1864) | Bagre cabeza de piedra | p.132
Bagre panamensis (Gill, 1863) | Bagre marino | p.134
Bagre pinnimaculatus (Steindachner, 1876) | Bagre rojo | p.134
Cathorops fuerthii (Steindachner, 1876) | Bagre negro | p.136
Cathorops multiradiatus (Günther, 1864) | Bagre | p.136
Notarius troschelii (Gill, 1863) | Bagre | p.138
Merluccius gayi (Guichenot, 1848) | Merluza | p.144
Brotula clarkae Hubbs, 1944 | Congrio | p.146
Genypterus maculatus (Tschudi, 1846) | Congrio negro | p.148
Lepophidium prorates (Jordan & Bollman, 1890) | Congrio plateado | p.150
Batrachoides pacifici (Günther, 1861) | Trambollo | p.152
Daector dowi (Jordan & Gilbert, 1887) | Brujo | p.154
Porichthys margaritatus (Richardson, 1844) | Pez fraile luminoso | p.154
Dormitator latifrons (Richardson, 1844) | Chalaco | p.156
Eleotris picta Kner, 1863 | Ñalojo | p.158
Gobiomorus maculatus (Günther, 1859) | Guavina | p.158
Awaous transandeanus (Günther, 1861) | Camotillo de río | p.160
Bathygobius andrei (Sauvage, 1880) | Camotillo de río | p.162
Ctenogobius sagittula (Günther, 1862) | Hoja de maíz | p.162
Abudefduf troschelii (Gill, 1862) | Castañeta | p.164
Microspathodon dorsalis (Gill, 1862) | Castañeta gigante | p.166
Mugil cephalus Linnaeus, 1758 | Lisa | p.170
Mugil setosus Gilbert, 1892 | Lisa plateada | p.172
Andinoacara rivulatus (Günther, 1860) | Mojarra | p.174
Oreochromis aureus (Steindachner, 1864) | Tilapia | p.174
Hypsoblennius brevipinnis (Günther, 1861) | Blénido | p.178
Hypsoblennius paytensis (Steindachner, 1876) | Trambollito | p.180
Atherinella serrivomer Chernoff, 1986 | Pejerrey | p.182
Atherinella nepenthe (Myers & Wade, 1942) | Pejerrey chato | p.182
Ablennes hians (Valenciennes, 1846) | Sierrilla | p.186
Strongylura exilis (Girard, 1854) | Agujilla | p.188
Strongylura scapularis (Jordan & Gilbert, 1882) | Pez aguja | p.188
Tylosurus pacificus (Steindachner, 1875) | Picuda | p.190
Nematistius pectoralis Gill, 1862 | Plumero | p.192
Coryphaena hippurus Linnaeus, 1758 | Perico | p.194
Rachycentron canadum (Linnaeus, 1766) | Cobia | p.196
Remora remora (Linnaeus, 1758) | Rémora | p.198
Alectis ciliaris (Bloch, 1787) | Espejo plumudo | p.200
Carangoides otrynter (Jordan & Gilbert, 1883) | Pámpano de hebra | p.200
Caranx caballus Günther, 1868 | Chumbo | p.202
Caranx caninus Günther, 1867 | Cocinero | p.202
Decapterus macrosoma Bleeker, 1851 | Jurel fino | p.204
Elagatis bipinnulata (Quoy & Gaimard, 1825) | Choclo | p.206
Hemicaranx leucurus (Günther, 1864) | Cachaco | p.206
Hemicaranx zelotes Gilbert, 1898 | Chiri | p.208
Naucrates ductor (Linnaeus, 1758) | Pez piloto | p.208
Oligoplites saurus (Bloch & Schneider, 1801) | Sierrilla | p.212
Selar crumenophthalmus (Bloch, 1793) | Jurel ojón | p.212
Selene brevoortii (Gill, 1863) | Jorobado | p.214
Selene orstedii Lütken, 1880 | Espejo | p.214
Selene peruviana (Guichenot, 1866) | Espejo | p.216
Trachinotus kennedyi Steindachner, 1876 | Pámpano toro | p.216
Trachinotus paitensis Cuvier, 1832 | Pámpano | p.218
Trachinotus rhodopus Gill, 1863 | Pámpano fino | p.218
Xiphias gladius Linnaeus, 1758 | Pez espada | p.224
Istiophorus platypterus (Shaw, 1792) | Pez vela | p.226
Istiompax indica (Cuvier, 1832) | Merlín negro | p.226
Kajikia audax (Philippi, 1887) | Merlín rayado | p.228
Makaira mazara (Jordan & Snyder, 1901) | Merlín azul | p.228
Bothus constellatus (Jordan, 1889) | Lenguado hoja | p.230
Ancylopsetta dendritica Gilbert, 1890 | Lenguado tres ojos | p.234
Cyclopsetta querna (Jordan & Bollman, 1890) | Lenguado con caninos | p.236
Etropus ectenes Jordan, 1889 | Lenguado boquichico | p.238
Hippoglossina macrops Steindachner, 1876 | Lenguado ojón | p.240
Hippoglossina tetrophthalma (Gilbert, 1890) | Lenguado cuatro ocelos | p.240
Paralichthys adspersus (Steindachner, 1867) | Lenguado común | p.242
Syacium ovale (Günther, 1864) | Lenguado | p.244
Achirus klunzingeri (Steindachner, 1880) | Lenguado redondo | p.246
Achirus mazatlanus (Steindachner, 1869) | Lenguado redondo | p.246
Trinectes fluviatilis (Meek & Hildebrand, 1928) | Lenguado de agua dulce | p.248
Trinectes fonsecensis (Günther, 1862) | Lenguado listado | p.250
Symphurus fasciolaris Gilbert, 1892 | Lengüeta | p.252
Symphurus melanurus Clark, 1936 | Lenguado lengüeta | p.254
Hippocampus ingens Girard, 1858 | Caballito de mar | p.256
Trichiurus lepturus Linnaeus, 1758 | Pez cinta | p.260
Acanthocybium solandri (Cuvier, 1832) | Barracuda | p.262
Auxis rochei (Risso, 1810) | Botellita | p.262
Auxis thazard (Lacepède, 1800) | Botellita | p.264
Euthynnus lineatus Kishinouye, 1920 | Pata seca | p.264
Scomber japonicus Houttuyn, 1782 | Caballa | p.266
Thunnus albacares (Bonnaterre, 1788) | Atún de aleta amarilla | p.268
Seriolella violacea Guichenot, 1848 | Palmera | p.270
Peprilus medius (Peters, 1869) | Chiri | p.272
Decodon melasma Gomon, 1974 | Doncella | p.278
Halichoeres dispilus (Günther, 1864) | Doncella | p.278
Halichoeres notospilus (Günther, 1864) | Señorita | p.280
Thalassoma lucasanum (Gill, 1862) | Viejita de cabeza azul | p.280
Nicholsina denticulata (Evermann & Radcliffe, 1917) | Pococho | p.282
Centropomus nigrescens Günther, 1864 | Robalo | p.286
Centropomus medius Günther, 1864 | Robalo | p.286
Chaetodipterus zonatus (Girard, 1858) | Camiseta | p.290
Parapsettus panamensis (Steindachner, 1876) | Camiseta | p.292
Deckertichthys aureolus (Jordan & Gilbert, 1882) | Periche | p.294
Diapterus peruvianus (Cuvier, 1830) | Periche | p.294
Eucinostomus currani Zahuranec, 1980 | Mojarra | p.296
Pseudupeneus grandisquamis (Gill, 1863) | San pedro | p.298
Oplegnathus insignis (Kner, 1867) | Pez loro | p.300
Kyphosus elegans (Peters, 1869) | Bocadulce | p.302
Alphestes immaculatus Breder, 1936 | Mero rojo | p.304
Alphestes multiguttatus (Günther, 1867) | Cherne pintado | p.306
Cratinus agassizii Steindachner, 1878 | Pluma | p.306
Cephalopholis panamensis (Steindachner, 1876) | Mero cabrilla | p.308
Diplectrum conceptione (Valenciennes, 1828) | Carajito | p.308
Diplectrum euryplectrum (Jordan & Bollman, 1890) | Pollo | p.310
Diplectrum maximum Hildebrand, 1946 | Carajito | p.312
Diplectrum rostrum Bortone, 1974 | Camotillo | p.312
Epinephelus analogus Gill, 1863 | Mero manchado | p.314
Epinephelus labriformis (Jenyns, 1840) | Mero murique | p.314
Epinephelus quinquefasciatus (Bocourt, 1868) | Mero ojo chico | p.316
Hemanthias peruanus (Steindachner, 1875) | Doncella | p.316
Hemanthias signifer (Garman, 1899) | Gallo | p.318
Hemilutjanus macrophthalmos (Tschudi, 1846) | Ojo de uva | p.318
Hyporthodus acanthistius (Gilbert, 1892) | Mero colorado | p.320
Hyporthodus niphobles (Gilbert & Starks, 1897) | Mero manchado | p.320
Mycteroperca xenarcha Jordan, 1888 | Mero negro | p.322
Paralabrax humeralis (Valenciennes, 1828) | Cágalo | p.324
Paranthias colonus (Valenciennes, 1846) | Cabinza serránida | p.324
Pronotogrammus multifasciatus Gill, 1863 | Galleta | p.326
Rypticus nigripinnis Gill, 1861 | Jaboncillo | p.326
Serranus huascarii Steindachner, 1900 | Maraño de peña | p.328
Serranus psittacinus Valenciennes, 1846 | Carajito rosado | p.328
Taractes rubescens (Jordan & Evermann, 1887) | Pez hacha | p.330
Cookeolus japonicus (Cuvier, 1829) | Semáforo | p.332
Pristigenys serrula (Gilbert, 1891) | Semáforo | p.334
Johnrandallia nigrirostris (Gill, 1862) | Mariposa | p.336
Pomacanthus zonipectus (Gill, 1862) | Pez ángel | p.338
Caulolatilus affinis Gill, 1865 | Peje blanco | p.340
Caulolatilus princeps (Jenyns, 1840) | Peje fino | p.342
Anisotremus interruptus (Gill, 1862) | Roncador | p.344
Anisotremus taeniatus Gill, 1861 | Sargo rayado | p.344
Genyatremus dovii (Günther, 1864) | Sargo | p.346
Genyatremus pacifici (Günther, 1864) | Chita | p.348
Haemulon steindachneri (Jordan & Gilbert, 1882) | Chivilico | p.348
Haemulopsis axillaris (Steindachner, 1869) | Callana | p.350
Haemulopsis elongatus (Steindachner, 1879) | Callana | p.350
Haemulopsis leuciscus (Günther, 1864) | Cabeza dura | p.352
Haemulopsis nitidus (Steindachner, 1869) | Gallinazo | p.352
Orthopristis chalcea (Günther, 1864) | Callana | p.354
Pomadasys branickii (Steindachner, 1879) | Gallinazo | p.354
Rhencus panamensis (Steindachner, 1875) | Chaparro | p.356
Xenichthys xanti Gill, 1863 | Ojón rayado | p.358
Rhonciscus bayanus (Jordan & Evermann, 1898) | Cabeza dura | p.358
Lutjanus argentiventris (Peters, 1869) | Pargo amarillo | p.360
Lutjanus guttatus (Steindachner, 1869) | Pargo | p.362
Lutjanus novemfasciatus Gill, 1862 | Pargo | p.362
Polydactylus approximans (Lay & Bennett, 1839) | Barbudo azul | p.364
Polydactylus opercularis (Gill, 1863) | Barbudo amarillo | p.366
Pontinus clemensi Fitch, 1955 | Vieja bocona | p.368
Pontinus furcirhinus Garman, 1899 | Diablico | p.368
Bellator gymnostethus (Gilbert, 1892) | Trigla | p.374
Prionotus horrens Richardson, 1844 | Volador | p.376
Prionotus stephanophrys Lockington, 1881 | Falso volador | p.378
Bairdiella ensifera (Jordan & Gilbert, 1882) | Corvinilla | p.382
Corvula macrops (Steindachner, 1875) | Corvinilla | p.384
Cynoscion analis (Jenyns, 1842) | Cachema | p.386
Cynoscion albus (Günther, 1864) | Corvina | p.386
Cynoscion stolzmanni (Steindachner, 1879) | Corvina guavina | p.388
Elattarchus archidium (Jordan & Gilbert, 1882) | Cachema ñata | p.390
Isopisthus altipinnis (Steindachner, 1866) | Ayanque | p.390
Larimus effulgens Gilbert, 1898 | Bereche cola amarilla | p.392
Menticirrhus elongatus (Günther, 1864) | Chula | p.394
Menticirrhus nasus (Günther, 1868) | Chula | p.396
Menticirrhus paitensis Hildebrand, 1946 | Chula | p.396
Micropogonias altipinnis (Günther, 1864) | Corvina dorada | p.398
Nebris occidentalis Vaillant, 1897 | China | p.400
Ophioscion scierus (Jordan & Gilbert, 1884) | Gallinazo | p.402
Paralonchurus dumerilii (Bocourt, 1869) | Suco rayado | p.402
Paralonchurus goodei Gilbert, 1898 | Suco rayado | p.404
Paralonchurus peruanus (Steindachner, 1875) | Suco | p.404
Pareques lanfeari (Barton, 1947) | Roncador rayado | p.406
Pareques viola (Gilbert, 1898) | Roncador | p.408
Stellifer chrysoleuca (Günther, 1867) | Mojarrilla | p.408
Stellifer pizarroensis Hildebrand, 1946 | Mojarrilla | p.412
Umbrina xanti Gill, 1862 | Polla rayada | p.412
Lobotes pacificus Gilbert, 1898 | Berrugata | p.414
Calamus brachysomus (Lockington, 1880) | Sargo del norte | p.416
Lophiodes caulinaris (Garman, 1899) | Trambollo | p.418
Fowlerichthys avalonis (Jordan & Starks, 1907) | Zanahoria | p.420
Canthidermis maculata (Bloch, 1786) | Coche | p.424
Aluterus monoceros (Linnaeus, 1758) | Unicornio | p.428
Lagocephalus lagocephalus (Linnaeus, 1758) | Tamborín oceánico | p.430
Sphoeroides annulatus (Jenyns, 1842) | Tamborín | p.430
Sphoeroides lobatus (Steindachner, 1870) | Tamboreta | p.432
Sphoeroides trichocephalus (Cope, 1870) | Tamborín enano | p.434"""

SYSTEM_PROMPT = f"""Eres un especialista en identificación de recursos hidrobiológicos con experiencia en fiscalización pesquera en el norte del Perú, región Tumbes. Tienes acceso al Catálogo Ilustrado de la Ictiofauna de la Región Tumbes (IMARPE, 2022) con 219 especies registradas.

{CATALOG_INDEX}

INSTRUCCIONES: Cuando recibas una imagen, identifica la(s) especie(s) de pez con el mayor nivel de precisión posible.

RESPONDE ÚNICAMENTE con un JSON válido (sin markdown, sin backticks, sin texto adicional) con esta estructura exacta:
{{
  "especies": [
    {{
      "nombre_comun": "nombre común en español",
      "nombre_cientifico": "Género especie (Autor, año)",
      "grupo": "ej: Pez óseo demersal / Elasmobranquio / Pez pelágico costero",
      "confianza": "alto|medio|bajo",
      "caracteristicas_clave": ["característica visible 1", "característica visible 2", "característica visible 3"],
      "especies_similares": "mencionar especies con las que puede confundirse y cómo diferenciarlas",
      "importancia_fiscalizacion": "relevancia para control y vigilancia pesquera",
      "pagina_catalogo": "p.XX (número exacto del catálogo) o 'No registrada en catálogo Tumbes'",
      "regulacion": {{
        "talla_minima": "XX cm LT o 'No establecida'",
        "veda": "descripción si existe o 'Sin veda conocida'",
        "normativa": "ej: DS-xxx-PRODUCE o 'Sin normativa específica'"
      }}
    }}
  ],
  "nota_imagen": "observación sobre calidad o contexto de la imagen",
  "solicitud_mejor_foto": false,
  "razon_mejor_foto": ""
}}

Si la imagen no muestra claramente un pez, pon solicitud_mejor_foto en true.
Si hay múltiples especies visibles, incluye todas en el array.
Señala si hay juveniles o especies protegidas/sensibles.
Para regulaciones, cita normas peruanas vigentes del PRODUCE/IMARPE cuando aplique."""


def identificar_pez(image_bytes: bytes, media_type: str, api_key: str) -> dict:
    """Llama a la API de Anthropic y retorna el JSON parseado."""
    client = anthropic.Anthropic(api_key=api_key)
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": "Identifica la(s) especie(s) de pez en esta imagen. Responde solo con el JSON indicado."}
            ]
        }]
    )

    raw = message.content[0].text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def badge_html(confianza: str) -> str:
    cls = {"alto": "badge-alto", "medio": "badge-medio", "bajo": "badge-bajo"}.get(confianza, "badge-medio")
    label = {"alto": "✅ Confianza Alta", "medio": "⚠️ Confianza Media", "bajo": "❌ Confianza Baja"}.get(confianza, confianza)
    return f'<span class="{cls}">{label}</span>'


def render_especie(sp: dict):
    """Renderiza la ficha de una especie."""
    has_page = sp.get("pagina_catalogo") and sp["pagina_catalogo"] != "No registrada en catálogo Tumbes"
    reg = sp.get("regulacion", {})
    has_reg = any([reg.get("talla_minima"), reg.get("veda"), reg.get("normativa")])

    page_badge = f'<span class="page-badge">📖 {sp["pagina_catalogo"]}</span>' if has_page else ""
    chars_html = "".join(f"<li style='color:rgba(255,255,255,0.85);font-size:13px;margin-bottom:4px'>{c}</li>"
                         for c in sp.get("caracteristicas_clave", []))

    reg_rows = ""
    if has_reg:
        if reg.get("talla_minima"):
            reg_rows += f'<div class="reg-row"><span class="reg-label">Talla mínima:</span><span class="reg-val">{reg["talla_minima"]}</span></div>'
        if reg.get("veda"):
            reg_rows += f'<div class="reg-row"><span class="reg-label">Veda:</span><span class="reg-val">{reg["veda"]}</span></div>'
        if reg.get("normativa"):
            reg_rows += f'<div class="reg-row"><span class="reg-label">Normativa:</span><span class="reg-val">{reg["normativa"]}</span></div>'
        reg_block = f'<div class="reg-block"><div class="reg-title">⚖️ Regulación Pesquera (Perú)</div>{reg_rows}</div>'
    else:
        reg_block = ""

    ref_txt = (f'Catálogo Ilustrado de la Ictiofauna de la Región Tumbes — IMARPE (2022), {sp["pagina_catalogo"]}'
               if has_page else "No registrada en Catálogo de Peces de Tumbes (IMARPE, 2022)")

    html = f"""
    <div class="card">
      <div class="card-head">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
          <div>
            <div class="species-title">🐟 {sp.get('nombre_comun','—')}</div>
            <div class="species-sci">{sp.get('nombre_cientifico','—')}</div>
            <span class="grupo-tag">{sp.get('grupo','—')}</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px">
            {badge_html(sp.get('confianza','medio'))}
            {page_badge}
          </div>
        </div>
      </div>

      <div class="section-label">Características Clave Observadas</div>
      <ul style="padding-left:18px;margin-bottom:12px">{chars_html}</ul>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="info-block">
          <div class="section-label">Especies Similares</div>
          <p>{sp.get('especies_similares','—')}</p>
        </div>
        <div class="info-block">
          <div class="section-label">Importancia Fiscalización</div>
          <p>{sp.get('importancia_fiscalizacion','—')}</p>
        </div>
      </div>

      {reg_block}

      <div class="ref-box">
        📚 <strong>Referencia:</strong> {ref_txt}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ── UI principal ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <div style="font-size:36px">🐟</div>
  <div>
    <h1>IDENTIFICADOR DE PECES — TUMBES</h1>
    <p>Catálogo IMARPE 2022 · Apoyo a Fiscalización Pesquera · 219 especies</p>
  </div>
</div>
""", unsafe_allow_html=True)

# API Key — desde secrets de Streamlit o campo manual
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = st.text_input(
        "🔑 API Key de Anthropic",
        type="password",
        placeholder="sk-ant-...",
        help="Ingresa tu clave API. Se guarda solo en sesión.",
    )

st.markdown("---")

uploaded = st.file_uploader(
    "📷 Sube una foto del pez",
    type=["jpg", "jpeg", "png", "webp"],
    help="Puedes tomar la foto directamente con la cámara del celular.",
)

if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_container_width=True, caption="Imagen cargada")

    if st.button("🔬 IDENTIFICAR ESPECIE", type="primary", use_container_width=True):
        if not api_key:
            st.error("⚠️ Ingresa tu API Key de Anthropic para continuar.")
        else:
            with st.spinner("Consultando el Catálogo de Peces de Tumbes…"):
                try:
                    # Convertir imagen a bytes
                    buf = io.BytesIO()
                    fmt = uploaded.type.split("/")[-1].upper()
                    fmt = "JPEG" if fmt in ["JPG", "JPEG"] else fmt
                    img.save(buf, format=fmt)
                    img_bytes = buf.getvalue()
                    media_type = uploaded.type or "image/jpeg"

                    resultado = identificar_pez(img_bytes, media_type, api_key)

                    # Alerta de foto insuficiente
                    if resultado.get("solicitud_mejor_foto"):
                        st.markdown(
                            f'<div class="alert-warn">📸 <strong>Se necesita mejor imagen:</strong> {resultado.get("razon_mejor_foto","")}</div>',
                            unsafe_allow_html=True,
                        )

                    # Nota general
                    if resultado.get("nota_imagen"):
                        st.markdown(
                            f'<div class="note-box">💬 {resultado["nota_imagen"]}</div>',
                            unsafe_allow_html=True,
                        )

                    # Fichas de cada especie
                    for sp in resultado.get("especies", []):
                        render_especie(sp)

                except json.JSONDecodeError:
                    st.error("❌ Error al parsear la respuesta. Intenta nuevamente.")
                except anthropic.AuthenticationError:
                    st.error("❌ API Key inválida. Verifica tu clave de Anthropic.")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")

st.markdown(
    '<div class="footer-txt">CATÁLOGO ILUSTRADO DE LA ICTIOFAUNA DE LA REGIÓN TUMBES · IMARPE 2022 · FISCALIZACIÓN PESQUERA</div>',
    unsafe_allow_html=True,
)
