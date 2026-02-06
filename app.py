import os
import streamlit as st
import google.generativeai as genai

# -------------------------
# Config & Model
# -------------------------
st.set_page_config(
    page_title="BioSense AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_INSTRUCTION = os.getenv(
    "SYSTEM_INSTRUCTION",
    "Eres un asistente útil y claro."
)

if not API_KEY:
    st.error("Falta GEMINI_API_KEY en Secrets (.streamlit/secrets.toml en Cloud) o en variables de entorno.")
    st.stop()

genai.configure(api_key=API_KEY)

# -------------------------
# Styling (CSS)
# -------------------------
st.markdown(
    """
<style>
/* Layout tweaks */
.block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; }
[data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.08); }

/* Title area */
.hero {
  padding: 1.25rem 1.4rem;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(90, 230, 180, 0.18), rgba(90, 150, 230, 0.14));
  border: 1px solid rgba(255,255,255,0.10);
}
.hero h1 { margin: 0; font-size: 2rem; }
.hero p  { margin: 0.35rem 0 0 0; opacity: 0.85; }

/* Chips */
.chip {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  margin-right: 0.4rem;
  font-size: 0.85rem;
  opacity: 0.92;
}

/* Cards */
.card {
  padding: 1rem 1rem;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.04);
}
.card h3 { margin: 0 0 0.3rem 0; }
.card p { margin: 0; opacity: 0.85; }

/* Subtle divider */
.hr {
  height: 1px;
  background: rgba(255,255,255,0.10);
  margin: 1rem 0;
}
</style>
""",
    unsafe_allow_html=True
)

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown("### ⚙️ BioSense AI")
    st.caption("Interfaz tipo chat con Gemini, pensada para bioseñales / EIS / troponina.")
    st.caption("Diseñada para la tesis doctoral de Fausto Díaz Sánchez") 
    st.caption("Autor: Dr. Jesús Andrés Arzola Flores")
    st.markdown(f"- **Modelo:** `{MODEL_NAME}`")
    st.markdown(f"- **Modo:** `Chat con memoria (sesión)`")

    st.markdown("---")
    tone = st.selectbox("Tono de respuesta", ["Técnico", "Didáctico", "Muy conciso"], index=0)
    detail = st.slider("Nivel de detalle", 1, 5, 3)

    st.markdown("---")
    if st.button("🧹 Nueva conversación", use_container_width=True):
        st.session_state.pop("chat", None)
        st.session_state.pop("history", None)
        st.rerun()

    st.caption("Tip: tu API Key va en **Secrets** (Streamlit Cloud) para no exponerla.")

# -------------------------
# Header / Hero
# -------------------------
st.markdown(
    f"""
<div class="hero">
  <h1>🧬 BioSense AI</h1>
  <p>Chat científico para <b>biosensores</b>, <b>EIS</b> y <b>troponina</b>, usando <b>Gemini</b>.</p>
  <div style="margin-top:0.6rem;">
    <span class="chip">Gemini • {MODEL_NAME}</span>
    <span class="chip">Memoria en sesión</span>
    <span class="chip">UI: Streamlit</span>
  </div>
</div>
""",
    unsafe_allow_html=True
)

# -------------------------
# Build prompt policy (simple)
# -------------------------
def build_user_prompt(user_text: str) -> str:
    style = {
        "Técnico": "Responde con rigor técnico, ecuaciones cuando aplique y supuestos claros.",
        "Didáctico": "Responde de forma didáctica, con analogías y pasos numerados.",
        "Muy conciso": "Responde en pocas líneas, directo al punto, sin relleno."
    }[tone]
    return f"""
INSTRUCCIONES DE FORMATO:
- {style}
- Nivel de detalle: {detail}/5
- Si hay riesgos clínicos: incluye advertencia de que no es diagnóstico.

PREGUNTA DEL USUARIO:
{user_text}
""".strip()

# -------------------------
# Init chat & history
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "chat" not in st.session_state:
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_INSTRUCTION
    )
    st.session_state.chat = model.start_chat(history=[])

# -------------------------
# Landing cards (when empty)
# -------------------------
if len(st.session_state.history) == 0:
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown(
            """
<div class="card">
  <h3>👋 Empieza con una pregunta</h3>
  <p>Esta app está pensada para explicación y análisis conceptual de impedancia (EIS), biosensores y mediciones.</p>
  <div class="hr"></div>
  <p><b>Ejemplos:</b></p>
  <ul>
    <li>¿Cómo cambia Rct cuando se une troponina al anticuerpo?</li>
    <li>¿Cómo interpretar un diagrama de Nyquist?</li>
    <li>Propón un protocolo de medición EIS para suero.</li>
  </ul>
</div>
""",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            """
<div class="card">
  <h3>🧪 Modo laboratorio</h3>
  <p>Describe variables, supuestos y controles. Ideal para docencia.</p>
  <div class="hr"></div>
  <p><b>Sugerencia:</b> pega parámetros del circuito equivalente (Rs, Rct, Cdl) y pide interpretación.</p>
</div>
""",
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            """
<div class="card">
  <h3>🧠 Preparación para ML</h3>
  <p>Puedes pedir features y pipelines: extracción de parámetros, ventanas temporales, etc.</p>
  <div class="hr"></div>
  <p><b>Tip:</b> “Dame features para predecir concentración usando EIS”.</p>
</div>
""",
            unsafe_allow_html=True
        )

    st.markdown("")  # spacer
    quick = st.columns(4)
    quick_prompts = [
        "Explica impedancia electroquímica aplicada a troponina.",
        "¿Qué parámetros del circuito de Randles cambian con la unión antígeno-anticuerpo?",
        "Dame un checklist de medición EIS (frecuencias, amplitud, estabilidad).",
        "Propón un enfoque de ML para estimar concentración desde espectros EIS."
    ]
    for col, qp in zip(quick, quick_prompts):
        if col.button(qp, use_container_width=True):
            st.session_state.history.append({"role": "user", "content": qp})
            with st.spinner("Pensando..."):
                resp = st.session_state.chat.send_message(build_user_prompt(qp))
            st.session_state.history.append({"role": "assistant", "content": resp.text})
            st.rerun()

# -------------------------
# Chat history rendering
# -------------------------
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# Chat input
# -------------------------
user_text = st.chat_input("Escribe tu mensaje… (ej. 'Interpreta Rs=50Ω, Rct=120Ω, Cdl=20µF')")

if user_text:
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Generando respuesta..."):
            resp = st.session_state.chat.send_message(build_user_prompt(user_text))
            st.markdown(resp.text)

    st.session_state.history.append({"role": "assistant", "content": resp.text})

