import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="🎙️ Transcritor",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Transcritor de Áudio")
st.markdown("**Simples • Grátis • Sem Login**")

# ==================== INICIALIZAR STATE ====================
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# ==================== INTERFACE ====================

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Fazer Upload")
    uploaded_file = st.file_uploader(
        "Escolha um áudio:",
        type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac'],
        label_visibility="collapsed"
    )

with col2:
    st.subheader("⚙️ Info")
    st.info("✅ Sem login\n✅ Sem API\n✅ Grátis")

st.divider()

# ==================== PROCESSAR ====================

if uploaded_file:
    st.success(f"✅ Arquivo: **{uploaded_file.name}** ({uploaded_file.size / (1024*1024):.1f} MB)")
    
    st.subheader("📋 Transcrição")
    
    # Campo para digitar/colar transcrição
    transcription = st.text_area(
        "Digite ou cole a transcrição aqui:",
        height=150,
        placeholder="Cole aqui o texto transcrito...",
        label_visibility="collapsed"
    )
    
    if transcription:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Salvar", use_container_width=True):
                st.session_state.transcriptions.insert(0, {
                    'filename': uploaded_file.name,
                    'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'text': transcription
                })
                st.success("✅ Salvo!")
                st.rerun()
        
        with col2:
            st.download_button(
                "📥 Baixar TXT",
                transcription,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_transcricao.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    else:
        st.info("✏️ Cole a transcrição acima!")

st.divider()

# ==================== HISTÓRICO ====================

st.subheader("📋 Transcrições Salvas")

if st.session_state.transcriptions:
    
    for idx, trans in enumerate(st.session_state.transcriptions):
        with st.expander(
            f"📄 {trans['filename']} • {trans['timestamp']}",
            expanded=idx == 0
        ):
            st.markdown(trans['text'])
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📥 Baixar TXT",
                    trans['text'],
                    file_name=f"{trans['filename'].rsplit('.', 1)[0]}_transcricao.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"dl_{idx}"
                )
            
            with col2:
                if st.button("🗑️ Deletar", key=f"del_{idx}", use_container_width=True):
                    st.session_state.transcriptions.pop(idx)
                    st.rerun()

else:
    st.info("📝 Nenhuma transcrição ainda.")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🎙️ <strong>Transcritor Simples</strong> • Sem Login • Sem API Key • 100% Grátis
</div>
""", unsafe_allow_html=True)
