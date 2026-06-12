import streamlit as st
import speech_recognition as sr
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

if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# ==================== FUNÇÕES ====================

def convert_audio_to_wav(input_path):
    """Converte qualquer áudio para WAV"""
    try:
        audio = AudioSegment.from_file(input_path)
        wav_path = input_path.replace(os.path.splitext(input_path)[1], '.wav')
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        st.error(f"❌ Erro ao converter áudio: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcreve áudio usando Google Speech Recognition"""
    try:
        # Converter para WAV se necessário
        if not audio_path.endswith('.wav'):
            audio_path = convert_audio_to_wav(audio_path)
            if not audio_path:
                return None
        
        # Inicializar reconhecedor
        recognizer = sr.Recognizer()
        
        # Carregar áudio
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        
        # Transcrever
        st.info("🔄 Transcrevendo áudio...")
        text = recognizer.recognize_google(audio_data, language='pt-BR')
        
        return text
    
    except sr.UnknownValueError:
        st.error("❌ Não foi possível entender o áudio")
        return None
    except sr.RequestError as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Erro: {e}")
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

# ==================== PROCESSAR UPLOAD ====================

if uploaded_file:
    st.success(f"✅ Arquivo: **{uploaded_file.name}** ({uploaded_file.size / (1024*1024):.1f} MB)")
    
    if st.button("🚀 Transcrever Agora!", use_container_width=True, key="transcribe"):
        # Salvar arquivo
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Transcrever
        with st.spinner("⏳ Processando... Isso pode levar alguns minutos..."):
            result = transcribe_audio(temp_path)
        
        if result:
            # Salvar no histórico
            st.session_state.transcriptions.insert(0, {
                'filename': uploaded_file.name,
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'text': result
            })
            
            # Limpar arquivo
            try:
                os.remove(temp_path)
            except:
                pass
            
            st.balloons()
            st.success("✨ Pronto!")
            st.rerun()

st.divider()

# ==================== HISTÓRICO ====================

st.subheader("📋 Transcrições")

if st.session_state.transcriptions:
    
    for idx, trans in enumerate(st.session_state.transcriptions):
        with st.expander(
            f"📄 {trans['filename']} • {trans['timestamp']}",
            expanded=idx == 0
        ):
            # Mostrar texto
            st.markdown(trans['text'])
            
            st.divider()
            
            # Botões
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
    st.info("📝 Nenhuma transcrição ainda. Faça upload de um áudio!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🎙️ <strong>Transcritor Simples</strong> • Sem Login • Sem API Key • 100% Grátis
</div>
""", unsafe_allow_html=True)
