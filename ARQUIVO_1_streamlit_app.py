import streamlit as st
import whisper
import os
from datetime import datetime
import tempfile

st.set_page_config(
    page_title="🎙️ Transcritor",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Transcritor de Áudio")
st.markdown("**Transcrição Rápida • Sem Login • Sem API Key**")

# ==================== CACHE DO MODELO ====================
@st.cache_resource
def load_model(model_name="base"):
    """Carrega modelo Whisper uma única vez"""
    with st.spinner(f"⏳ Carregando modelo {model_name}..."):
        model = whisper.load_model(model_name)
    return model

# ==================== INICIALIZAR STATE ====================
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# ==================== CONFIGURAÇÕES ====================
with st.sidebar:
    st.header("⚙️ Configurações")
    
    model_choice = st.radio(
        "Modelo:",
        ["tiny (Rápido)", "base (Recomendado)", "small (Melhor)"],
        index=1
    )
    
    model_map = {
        "tiny (Rápido)": "tiny",
        "base (Recomendado)": "base",
        "small (Melhor)": "small"
    }
    selected_model = model_map[model_choice]

# ==================== INTERFACE ====================

st.subheader("📤 Fazer Upload de Áudio")

uploaded_file = st.file_uploader(
    "Escolha um arquivo de áudio:",
    type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac'],
    help="Formatos suportados: MP3, WAV, MP4, M4A, OGG, FLAC, WEBM, AAC"
)

st.divider()

# ==================== PROCESSAR UPLOAD ====================

if uploaded_file:
    # Informações do arquivo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Arquivo", uploaded_file.name)
    with col2:
        st.metric("Tamanho", f"{uploaded_file.size / (1024*1024):.1f} MB")
    with col3:
        st.metric("Modelo", selected_model)
    
    st.divider()
    
    # Botão para iniciar transcrição
    if st.button("🚀 INICIAR TRANSCRIÇÃO", use_container_width=True, key="transcribe_btn"):
        
        # Salvar arquivo
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Carregar modelo
            model = load_model(selected_model)
            
            # Transcrever
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.info(f"🔄 Transcrevendo com {selected_model}...")
            progress_bar.progress(30)
            
            result = model.transcribe(
                temp_path,
                language="pt",
                verbose=False
            )
            
            progress_bar.progress(70)
            
            transcription_text = result['text']
            
            # Salvar no histórico
            st.session_state.transcriptions.insert(0, {
                'filename': uploaded_file.name,
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'text': transcription_text,
                'model': selected_model
            })
            
            # Limpar arquivo temporário
            try:
                os.remove(temp_path)
            except:
                pass
            
            progress_bar.progress(100)
            status_text.success("✅ Transcrição concluída!")
            
            st.divider()
            
            # Mostrar resultado
            st.subheader("📝 Resultado da Transcrição")
            st.text_area(
                "Transcrição:",
                value=transcription_text,
                height=200,
                disabled=True,
                label_visibility="collapsed"
            )
            
            # Botões
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📥 Baixar TXT",
                    transcription_text,
                    file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_transcricao.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                if st.button("💾 Salvar no Histórico", use_container_width=True):
                    st.success("✅ Já está salvo!")
        
        except Exception as e:
            st.error(f"❌ Erro na transcrição: {str(e)}")
            try:
                os.remove(temp_path)
            except:
                pass

st.divider()

# ==================== HISTÓRICO ====================

st.subheader("📋 Transcrições Salvas")

if st.session_state.transcriptions:
    
    for idx, trans in enumerate(st.session_state.transcriptions):
        with st.expander(
            f"📄 {trans['filename']} • {trans['timestamp']} ({trans['model']})",
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
    st.info("📝 Nenhuma transcrição salva. Faça upload de um áudio!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🎙️ <strong>Transcritor com Whisper</strong> • Transcrição Automática Rápida • 100% Grátis
</div>
""", unsafe_allow_html=True)
