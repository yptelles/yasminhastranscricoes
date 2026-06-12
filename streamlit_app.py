import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from datetime import datetime
import json

# Configuração da página
st.set_page_config(
    page_title="🎙️ Transcritor de Áudio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
        padding: 10px 30px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("🎙️ Transcritor de Áudio Online")
st.markdown("Transcreva seus áudios e ligações facilmente. Sem instalação, funciona em qualquer lugar! 📱💻")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    language = st.selectbox(
        "Idioma da transcrição:",
        ["Português", "English", "Español", "Français", "Deutsch", "Italiano"],
        help="Selecione o idioma do seu áudio"
    )
    
    st.markdown("---")
    st.info("💡 **Dica:** Quanto melhor a qualidade do áudio, melhor a transcrição!")
    
    st.markdown("---")
    st.success("✅ **Status:** Pronto para usar!")

# Mapa de idiomas
language_map = {
    "Português": "pt-BR",
    "English": "en-US",
    "Español": "es-ES",
    "Français": "fr-FR",
    "Deutsch": "de-DE",
    "Italiano": "it-IT"
}

lang_code = language_map[language]

# Inicializar session state
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# Reconhecedor de fala
recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000

# Tabs principais
tab1, tab2, tab3 = st.tabs(["📤 Upload de Arquivo", "🎤 Gravar Áudio", "📋 Histórico"])

with tab1:
    st.header("📤 Upload de Arquivo")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Envie um arquivo de áudio ou vídeo")
        uploaded_file = st.file_uploader(
            "Escolha um arquivo",
            type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac'],
            help="Formatos suportados: MP3, WAV, MP4, M4A, OGG, FLAC, WEBM, AAC"
        )
    
    if uploaded_file is not None:
        with st.spinner("⏳ Processando áudio..."):
            try:
                # Salvar arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    # Se for MP3 ou outro formato, converter para WAV
                    if uploaded_file.name.endswith('.mp3'):
                        audio = AudioSegment.from_mp3(uploaded_file)
                        audio.export(tmp_file.name, format="wav")
                    elif uploaded_file.name.endswith('.mp4'):
                        audio = AudioSegment.from_file(uploaded_file, format="mp4")
                        audio.export(tmp_file.name, format="wav")
                    elif uploaded_file.name.endswith('.m4a'):
                        audio = AudioSegment.from_file(uploaded_file, format="m4a")
                        audio.export(tmp_file.name, format="wav")
                    else:
                        tmp_file.write(uploaded_file.getbuffer())
                    
                    tmp_path = tmp_file.name
                
                # Transcrever
                with sr.AudioFile(tmp_path) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data, language=lang_code)
                        
                        # Salvar no histórico
                        transcription = {
                            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            'filename': uploaded_file.name,
                            'text': text,
                            'type': 'upload'
                        }
                        st.session_state.transcriptions.insert(0, transcription)
                        
                        # Mostrar resultado
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.success("✅ Transcrição concluída com sucesso!")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.subheader("📝 Resultado:")
                        st.text_area("Transcrição", value=text, height=150, disabled=True)
                        
                        # Botão para copiar
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("📋 Copiar Texto"):
                                st.write("✅ Copie o texto acima!")
                        with col2:
                            st.download_button(
                                label="📥 Baixar como TXT",
                                data=text,
                                file_name=f"transcricao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                    
                    except sr.UnknownValueError:
                        st.error("❌ Não consegui entender o áudio. Tente:")
                        st.warning("• Áudio com melhor qualidade")
                        st.warning("• Fala mais clara")
                        st.warning("• Menos barulho de fundo")
                    except sr.RequestError as e:
                        st.error(f"❌ Erro na transcrição: {e}")
                
                # Limpar arquivo temporário
                os.remove(tmp_path)
            
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {str(e)}")

with tab2:
    st.header("🎤 Gravar Áudio Ao Vivo")
    
    st.info("💡 Clique no botão abaixo para gravar áudio com seu microfone")
    
    if st.button("🎤 Iniciar Gravação", key="record_btn", help="Clique para gravar (máx 30 segundos)"):
        st.write("⏹️ Gravando... Fale agora!")
        
        try:
            # Gravar por 30 segundos
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                st.info("🎙️ Ajustando para ruído ambiente... Aguarde 1 segundo")
                
                audio_data = recognizer.listen(source, timeout=30, phrase_time_limit=30)
                
                st.success("✅ Gravação finalizada!")
                
                # Transcrever
                with st.spinner("⏳ Transcrevendo..."):
                    try:
                        text = recognizer.recognize_google(audio_data, language=lang_code)
                        
                        # Salvar no histórico
                        transcription = {
                            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            'filename': f"Gravação {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                            'text': text,
                            'type': 'recording'
                        }
                        st.session_state.transcriptions.insert(0, transcription)
                        
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.subheader("📝 Resultado da Gravação:")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.text_area("Transcrição", value=text, height=150, disabled=True)
                        
                        # Botões
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 Baixar como TXT",
                                data=text,
                                file_name=f"gravacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        with col2:
                            if st.button("✂️ Copiar para área de transferência"):
                                st.info("Copie o texto acima manualmente!")
                    
                    except sr.UnknownValueError:
                        st.error("❌ Não entendi o áudio. Tente:")
                        st.warning("• Falar mais claro")
                        st.warning("• Em ambiente mais quieto")
                        st.warning("• Mais perto do microfone")
                    except sr.RequestError as e:
                        st.error(f"❌ Erro: {e}")
        
        except sr.RequestError:
            st.error("❌ Erro ao acessar o microfone")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

with tab3:
    st.header("📋 Histórico de Transcrições")
    
    if not st.session_state.transcriptions:
        st.info("Nenhuma transcrição ainda. Faça upload ou grave um áudio!")
    else:
        st.success(f"✅ Total de transcrições: {len(st.session_state.transcriptions)}")
        
        for idx, trans in enumerate(st.session_state.transcriptions):
            with st.expander(f"📄 {trans['filename']} - {trans['timestamp']}", expanded=False):
                st.write(trans['text'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="📥 Baixar",
                        data=trans['text'],
                        file_name=f"transcricao_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        key=f"download_{idx}"
                    )
                with col2:
                    if st.button("🗑️ Deletar", key=f"delete_{idx}"):
                        st.session_state.transcriptions.pop(idx)
                        st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("📱 **Funciona em:** Celular, Tablet, PC")

with col2:
    st.markdown("🔒 **Privacidade:** Seus dados são seu!")

with col3:
    st.markdown("⚡ **Sempre Online:** Sem instalação!")
