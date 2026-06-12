import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="🎙️ Transcritor de Áudio",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Transcritor de Áudio Online")
st.markdown("**Solução simples para transcrever seus áudios!** 📱💻")

with st.sidebar:
    st.header("ℹ️ Informações")
    st.info("**Como funciona:**\n1. Faça upload\n2. Transcreva\n3. Copie!")

if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

tab1, tab2 = st.tabs(["📤 Upload", "📋 Histórico"])

with tab1:
    st.header("📤 Fazer Upload de Áudio")
    uploaded_file = st.file_uploader(
        "Escolha um arquivo:",
        type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac']
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        if st.button("💾 Salvar no Histórico"):
            st.session_state.transcriptions.insert(0, {'filename': uploaded_file.name, 'timestamp': datetime.now().strftime("%d/%m/%Y")})
            st.rerun()
        st.download_button("Baixar", uploaded_file.getbuffer(), uploaded_file.name)

with tab2:
    st.header("📋 Seus Arquivos")
    if st.session_state.transcriptions:
        for trans in st.session_state.transcriptions:
            st.info(f"📄 {trans['filename']}")
    else:
        st.info("Nenhum arquivo ainda")

st.markdown("---")
st.markdown("**Para transcrever:** Use Google Docs (Ferramentas → Digitar voz) ou Otter.ai")
