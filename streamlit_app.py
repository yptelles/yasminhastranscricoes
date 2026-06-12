import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🎙️ Transcritor", page_icon="🎙️", layout="wide")

st.title("🎙️ Transcritor de Áudio Online")

with st.sidebar:
    st.header("ℹ️ Como Funciona")
    st.success("✅ App Pronto!")

if 'files' not in st.session_state:
    st.session_state.files = []

tab1, tab2 = st.tabs(["📤 Upload", "📋 Histórico"])

with tab1:
    st.header("📤 Fazer Upload de Áudio")
    st.write("Envie seus áudios aqui:")
    
    file = st.file_uploader("Escolha um arquivo", type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac'])
    
    if file:
        st.success(f"✅ Arquivo: **{file.name}**")
        st.info(f"📊 Tamanho: {file.size / 1024:.1f} KB")
        
        if st.button("💾 Salvar no Histórico"):
            st.session_state.files.insert(0, {
                'nome': file.name,
                'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'tamanho': f"{file.size / 1024:.1f} KB"
            })
            st.success("✅ Salvo com sucesso!")
            st.rerun()

with tab2:
    st.header("📋 Seus Arquivos")
    
    if st.session_state.files:
        st.success(f"📦 Total: {len(st.session_state.files)} arquivos")
        for idx, f in enumerate(st.session_state.files):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📄 **{f['nome']}** - {f['data']} ({f['tamanho']})")
            with col2:
                if st.button("❌", key=f"del_{idx}"):
                    st.session_state.files.pop(idx)
                    st.rerun()
    else:
        st.info("Nenhum arquivo salvo ainda")

st.markdown("---")
st.markdown("**💡 Para transcrever:** Use [Google Docs](https://docs.google.com) (Ferramentas → Digitar voz) ou [Otter.ai](https://otter.ai)")
st.markdown("📱 Acessa em: PC | Celular | Tablet | 🔒 Seus dados são protegidos!")
