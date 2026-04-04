# 🐟 Identificador de Peces — Tumbes
**Apoyo a Fiscalización Pesquera | Catálogo IMARPE 2022**

---

## ¿Qué hace esta app?
Sube una foto de un pez → la app la compara con las imágenes del Catálogo Ilustrado de la Ictiofauna de la Región Tumbes (IMARPE, 2022) y devuelve las **5 especies más similares** con su página de referencia en el catálogo.

Funciona 100% offline de APIs externas. Sin costos por consulta.

---

## Archivos necesarios
```
peces_app/
├── app.py
├── requirements.txt
└── README.md
```

---

## Despliegue en Streamlit Community Cloud (GRATIS)

### Paso 1 — Subir a GitHub
1. Crea una cuenta en [github.com](https://github.com) si no tienes
2. Crea un repositorio nuevo (ej: `identificador-peces-tumbes`)
3. Sube los 3 archivos: `app.py`, `requirements.txt`, `README.md`

### Paso 2 — Desplegar en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Clic en **"New app"**
4. Selecciona tu repositorio y el archivo `app.py`
5. Clic en **"Deploy"**

### Paso 3 — Primera carga
- La primera vez que abras la app, descargará automáticamente los catálogos desde Google Drive (~2 min)
- Luego construirá la base de datos de características (~1 min)
- Este proceso solo ocurre **una vez** — las siguientes sesiones cargan en segundos

---

## Requisitos técnicos
- Python 3.9+
- Las dependencias se instalan automáticamente en Streamlit Cloud
- Los catálogos se descargan desde la carpeta pública de Google Drive

---

## Cómo usar en campo (móvil)
1. Abre la URL de tu app en Chrome o Safari
2. Toca el área de carga → selecciona foto de la cámara o galería
3. La app analiza y muestra las 5 especies más similares
4. Verifica en el catálogo físico usando la página indicada

---

## Limitaciones
- La identificación es por similitud de **color** de la imagen del catálogo
- Para mejores resultados: foto bien iluminada, fondo claro, pez completo
- Siempre confirmar con el catálogo físico antes de tomar decisiones de fiscalización

---

## Fuente de datos
Siccha-Ramirez R. et al. (2022). *Catálogo ilustrado de la ictiofauna de la región Tumbes.*
Instituto del Mar del Perú (IMARPE). 490 p.
