import streamlit as st
from pydub import AudioSegment
import os
from datetime import datetime
import tempfile

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

# ==================== FUNÇÕES ====================

def get_audio_info(audio_path):
    """Pega informações do áudio"""
    try:
        audio = AudioSegment.from_file(audio_path)
        duration_seconds = len(audio) / 1000
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        
        return {
            'duration': f"{minutes}:{seconds:02d}",
            'frame_rate': audio.frame_rate,
            'channels': audio.channels,
            'size_mb': os.path.getsize(audio_path) / (1024*1024)
        }
    except Exception as e:
        return None

def convert_to_wav(input_path):
    """Converte áudio para WAV"""
    try:
        audio = AudioSegment.from_file(input_path)
        wav_path = input_path.replace(os.path.splitext(input_path)[1], '_converted.wav')
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        st.error(f"❌ Erro ao converter: {e}")
        return None

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
    st.info("✅ Sem login\n✅ Sem API Key\n✅ 100% Grátis")

st.divider()

# ==================== PROCESSAR ====================

if uploaded_file:
    # Salvar arquivo
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    # Mostrar informações
    st.success(f"✅ Arquivo: **{uploaded_file.name}**")
    
    info = get_audio_info(temp_path)
    if info:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Duração", info['duration'])
        with col2:
            st.metric("Taxa", f"{info['frame_rate']} Hz")
        with col3:
            st.metric("Canais", info['channels'])
        with col4:
            st.metric("Tamanho", f"{info['size_mb']:.1f} MB")
    
    st.divider()
    
    # Opções
    st.subheader("📋 Transcrição")
    
    # Campo para digitar/colar transcrição
    transcription = st.text_area(
        "Digite ou cole a transcrição aqui:",
        height=150,
        placeholder="Coloque aqui o texto transcrito manualmente ou de outra fonte...",
        label_visibility="collapsed"
    )
    
    if transcription:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Salvar Transcrição", use_container_width=True):
                st.session_state.transcriptions.insert(0, {
                    'filename': uploaded_file.name,
                    'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'text': transcription
                })
                
                try:
                    os.remove(temp_path)
                except:
                    pass
                
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
        st.info("✏️ Digite ou cole a transcrição acima!")

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
                    use_container_width=True
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
