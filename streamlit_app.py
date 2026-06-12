import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🎙️ Transcritor", page_icon="🎙️", layout="wide")

st.title("🎙️ Transcritor de Áudio com IA")
st.markdown("**Transcrição automática + Identificação de quem fala**")

# Sidebar - API Key
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input(
        "Cole sua API Key (AssemblyAI):",
        type="password",
        help="Crie conta grátis em: https://www.assemblyai.com"
    )
    
    if api_key:
        st.success("✅ API Key configurada!")
    else:
        st.warning("⚠️ Insira sua API Key para começar")
    
    st.markdown("---")
    st.info("""
    **Como obter API Key (Grátis):**
    1. Vá para assemblyai.com
    2. Clique "Sign Up" (grátis)
    3. Copie seu API Token
    4. Cole acima
    """)

# Inicializar session state
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# Função para transcrever
def transcrever_audio(file_bytes, api_key):
    """Envia áudio para AssemblyAI e retorna transcrição com speakers"""
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        # Upload do arquivo
        st.info("📤 Enviando arquivo...")
        upload_response = requests.post(
            "https://api.assemblyai.com/v1/upload",
            headers=headers,
            data=file_bytes,
            timeout=60
        )
        
        if upload_response.status_code != 200:
            st.error("❌ Erro ao fazer upload")
            return None
        
        audio_url = upload_response.json()['upload_url']
        st.success("✅ Arquivo enviado!")
        
        # Solicitar transcrição com speaker detection
        st.info("🎙️ Processando transcrição...")
        
        transcript_request = {
            "audio_url": audio_url,
            "speaker_labels": True,
            "speakers_expected": 2
        }
        
        transcript_response = requests.post(
            "https://api.assemblyai.com/v1/transcript",
            headers=headers,
            json=transcript_request,
            timeout=60
        )
        
        if transcript_response.status_code != 200:
            st.error("❌ Erro na solicitação")
            return None
        
        transcript_id = transcript_response.json()['id']
        
        # Verificar status
        st.info("⏳ Aguardando transcrição... (alguns minutos)")
        
        while True:
            status_response = requests.get(
                f"https://api.assemblyai.com/v1/transcript/{transcript_id}",
                headers=headers,
                timeout=60
            )
            
            result = status_response.json()
            status = result.get('status')
            
            if status == 'completed':
                st.success("✅ Transcrição concluída!")
                return result
            elif status == 'error':
                st.error(f"❌ Erro: {result.get('error')}")
                return None
            
            time.sleep(3)
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return None

# Tabs
tab1, tab2 = st.tabs(["📤 Upload e Transcrição", "📋 Histórico"])

with tab1:
    st.header("📤 Fazer Upload de Áudio")
    
    if not api_key:
        st.warning("⚠️ Configure sua API Key na barra lateral!")
    else:
        file = st.file_uploader(
            "Escolha um arquivo:",
            type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac', 'mov']
        )
        
        if file:
            st.success(f"✅ {file.name} ({file.size / 1024 / 1024:.1f} MB)")
            
            if st.button("🚀 Transcrever"):
                result = transcrever_audio(file.getbuffer().read(), api_key)
                
                if result and result.get('status') == 'completed':
                    st.session_state.current_transcript = result
                    st.rerun()

# Mostrar transcrição
if 'current_transcript' in st.session_state:
    st.markdown("---")
    st.header("📝 Transcrição")
    
    result = st.session_state.current_transcript
    
    col1, col2 = st.columns(2)
    with col1:
        speaker_1_name = st.text_input("Renomear Pessoa 1:", "Pessoa 1", key="s1")
    with col2:
        speaker_2_name = st.text_input("Renomear Pessoa 2:", "Pessoa 2", key="s2")
    
    if result.get('utterances'):
        st.subheader("Transcrição:")
        
        full_text = ""
        for utterance in result['utterances']:
            speaker = utterance.get('speaker', 'Desconhecido')
            
            if speaker == 'A':
                name = speaker_1_name
            elif speaker == 'B':
                name = speaker_2_name
            else:
                name = f"Falante {speaker}"
            
            text = utterance.get('text', '')
            st.write(f"**{name}:** {text}")
            full_text += f"{name}: {text}\n\n"
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Baixar TXT",
                full_text,
                file_name=f"transcricao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
        with col2:
            if st.button("💾 Salvar"):
                st.session_state.transcriptions.insert(0, {
                    'nome': file.name,
                    'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'texto': full_text
                })
                st.success("✅ Salvo!")
    else:
        st.info("Nenhuma fala detectada")

with tab2:
    st.header("📋 Histórico")
    
    if st.session_state.transcriptions:
        for idx, trans in enumerate(st.session_state.transcriptions):
            with st.expander(f"📄 {trans['nome']} - {trans['data']}"):
                st.write(trans['texto'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📥 Baixar", trans['texto'], file_name=f"trans_{idx}.txt", key=f"dl_{idx}")
                with col2:
                    if st.button("❌ Deletar", key=f"del_{idx}"):
                        st.session_state.transcriptions.pop(idx)
                        st.rerun()
    else:
        st.info("Nenhuma transcrição")

st.markdown("---")
st.markdown("**✅ Gratuito:** 600 min/mês | **🎯 Automático:** Identifica quem fala | **📥 Baixável:** Em TXT")
