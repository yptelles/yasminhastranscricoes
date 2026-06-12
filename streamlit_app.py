import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(
    page_title="🎙️ Transcritor",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Transcritor de Áudio")
st.markdown("**Transcrição Automática • Sem Instalação • Grátis**")

# ==================== SESSION STATE ====================
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configuração")
    
    api_key = st.text_input(
        "API Key AssemblyAI:",
        type="password",
        help="Grátis em: https://www.assemblyai.com"
    )
    
    if api_key:
        st.success("✅ API Key configurada!")
    else:
        st.info("""
**Como obter grátis:**
1. Acesse [assemblyai.com](https://www.assemblyai.com)
2. Clique em **Sign Up**
3. Confirme o email
4. Vá em **Dashboard → API Keys**
5. Copie e cole aqui ☝️
        """)

# ==================== FUNÇÕES ====================

def upload_audio(file_bytes, api_key):
    """Faz upload do áudio para AssemblyAI"""
    response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers={
            "authorization": api_key,
            "content-type": "application/octet-stream"
        },
        data=file_bytes
    )
    if response.status_code == 200:
        return response.json()["upload_url"]
    raise Exception(f"Erro no upload (status {response.status_code}): {response.text}")


def start_transcription(audio_url, api_key):
    """Inicia a transcrição"""
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers={
            "authorization": api_key,
            "content-type": "application/json"
        },
        json={
            "audio_url": audio_url,
            "language_code": "pt"
        }
    )
    if response.status_code == 200:
        return response.json()["id"]
    raise Exception(f"Erro ao iniciar transcrição (status {response.status_code}): {response.text}")


def get_transcript(transcript_id, api_key):
    """Verifica status da transcrição"""
    response = requests.get(
        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
        headers={"authorization": api_key}
    )
    return response.json()

# ==================== INTERFACE ====================

if not api_key:
    st.warning("⚠️ Configure sua API Key no sidebar para começar!")
    st.stop()

tab1, tab2 = st.tabs(["📁 Transcrever Áudio", "📋 Histórico"])

# ==================== ABA 1: TRANSCREVER ====================
with tab1:
    st.subheader("📤 Upload de Áudio")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo:",
        type=["mp3", "wav", "mp4", "m4a", "ogg", "flac", "webm", "aac"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ **{uploaded_file.name}** — {uploaded_file.size / (1024*1024):.1f} MB")
        with col2:
            transcribe = st.button("🚀 Transcrever", use_container_width=True)
        
        if transcribe:
            try:
                progress = st.progress(0)
                status_msg = st.empty()
                
                # 1. Upload
                status_msg.info("📤 Enviando arquivo...")
                audio_url = upload_audio(uploaded_file.getvalue(), api_key)
                progress.progress(30)
                
                # 2. Iniciar transcrição
                status_msg.info("🔄 Iniciando transcrição...")
                transcript_id = start_transcription(audio_url, api_key)
                progress.progress(50)
                
                # 3. Aguardar resultado
                while True:
                    result = get_transcript(transcript_id, api_key)
                    t_status = result["status"]
                    
                    if t_status == "completed":
                        progress.progress(100)
                        status_msg.success("✅ Transcrição concluída!")
                        
                        texto = result["text"]
                        
                        # Salvar no histórico
                        st.session_state.transcriptions.insert(0, {
                            "filename": uploaded_file.name,
                            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "text": texto
                        })
                        
                        # Mostrar resultado
                        st.divider()
                        st.subheader("📝 Resultado")
                        st.text_area(
                            "",
                            value=texto,
                            height=300,
                            disabled=True
                        )
                        
                        st.download_button(
                            "📥 Baixar TXT",
                            texto,
                            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_transcricao.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        break
                    
                    elif t_status == "error" or t_status == "failed":
                        progress.empty()
                        st.error(f"❌ Falhou: {result.get('error', 'Erro desconhecido')}")
                        break
                    
                    else:
                        if t_status == "queued":
                            progress.progress(55)
                            status_msg.info("⏳ Na fila de processamento...")
                        elif t_status == "processing":
                            progress.progress(75)
                            status_msg.info("⚙️ Processando áudio...")
                    
                    time.sleep(3)
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")

# ==================== ABA 2: HISTÓRICO ====================
with tab2:
    st.subheader("📋 Transcrições Salvas")
    
    if st.session_state.transcriptions:
        for idx, trans in enumerate(st.session_state.transcriptions):
            with st.expander(
                f"📄 {trans['filename']} • {trans['timestamp']}",
                expanded=(idx == 0)
            ):
                st.markdown(trans["text"])
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Baixar TXT",
                        trans["text"],
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
        st.info("📝 Nenhuma transcrição salva ainda.")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#666;font-size:12px;'>"
    "🎙️ <strong>Transcritor de Áudio</strong> • AssemblyAI • 100% Grátis"
    "</div>",
    unsafe_allow_html=True
)
