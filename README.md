# 🐟 Identificador de Peces — Tumbes
### Apoyo a Fiscalización Pesquera · Catálogo IMARPE 2022

App web desarrollada con Streamlit + Claude AI para identificación de especies
hidrobiológicas en la región Tumbes, Perú. Basada en el **Catálogo Ilustrado de
la Ictiofauna de la Región Tumbes (IMARPE, 2022)** con 219 especies registradas.

---

## 🚀 Despliegue en Streamlit Community Cloud (gratis)

### Paso 1 — Sube el código a GitHub

1. Crea una cuenta en [github.com](https://github.com) si no tienes
2. Crea un repositorio nuevo (ej: `identificador-peces-tumbes`)
3. Sube estos archivos:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/secrets.toml.example` (renombrar, ver paso 3)

### Paso 2 — Despliega en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Clic en **"New app"**
4. Selecciona tu repositorio y el archivo `app.py`
5. Clic en **"Deploy"**

### Paso 3 — Configura tu API Key

En el panel de tu app en Streamlit Cloud:
1. Ve a **Settings → Secrets**
2. Pega lo siguiente:

```toml
ANTHROPIC_API_KEY = "sk-ant-TUCLAVEAQUI"
```

3. Guarda. La app se reinicia con la clave configurada.

> 💡 Con la clave en Secrets, los usuarios NO necesitan ingresar ninguna clave.
> La app funciona directamente.

### Paso 4 — Comparte el enlace

Tu app quedará disponible en una URL como:
`https://tuusuario-identificador-peces-tumbes-app-XXXX.streamlit.app`

Compártela con tu equipo de fiscalización. Funciona en celular y escritorio.

---

## 🔑 Obtener API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesión
3. Ve a **API Keys** → **Create Key**
4. Copia la clave (empieza con `sk-ant-`)

> El uso tiene costo por consulta (~$0.003 por imagen identificada con claude-opus-4-5).
> Streamlit Cloud es **gratuito** para apps públicas.

---

## 📋 Uso local (opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de secrets
mkdir .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edita secrets.toml y pon tu API Key real

# Ejecutar
streamlit run app.py
```

---

## 📚 Referencia

Siccha-Ramirez R., Luque C., Vera M., Britzke R., Guevara M., Castillo D. y Miranda J. (2022).
*Catálogo ilustrado de la ictiofauna de la región Tumbes.*
Instituto del Mar del Perú (IMARPE). 490 p.
Depósito legal N° 2023-01264.
