import streamlit as st
import requests
import time
from datetime import datetime
import os

st.set_page_config(
    page_title="🎙️ Transcritor",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Transcritor de Áudio com IA")
st.markdown("**Transcrição automática + Identificação de quem fala**")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configurações")
    
    api_key = st.text_input(
        "Cole sua API Key (AssemblyAI):",
        type="password",
        placeholder="a30efb4d919db009e232d32c5...",
        help="Crie conta grátis em: https://www.assemblyai.com"
    )
    
    if api_key:
        st.info(f"✏️ API Key: {api_key[:10]}...{api_key[-5:]}")
    else:
        st.warning("⚠️ Insira sua API Key para começar")
        st.markdown("""
        **Como obter grátis:**
        1. Vá para [assemblyai.com](https://www.assemblyai.com)
        2. Clique "Sign Up" 
        3. **Confirme seu email!**
        4. Copie seu **API Token**
        5. Cole aqui ☝️
        """)
    
    st.markdown("---")
    
    language = st.selectbox(
        "Idioma:",
        ["Português (pt-BR)", "Inglês (en-US)", "Espanhol (es-ES)"]
    )
    
    lang_map = {
        "Português (pt-BR)": "pt",
        "Inglês (en-US)": "en",
        "Espanhol (es-ES)": "es"
    }
    lang_code = lang_map[language]

# ==================== INICIALIZAR STATE ====================
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# ==================== FUNÇÕES ====================

def upload_and_transcribe(file_path, api_key, language):
    """Upload e inicia transcrição - COM LOGS DETALHADOS"""
    
    try:
        # PASSO 1: Upload do arquivo
        st.info("📤 Fazendo upload do arquivo...")
        
        with open(file_path, 'rb') as f:
            headers = {"Authorization": api_key}
            
            st.write("Enviando para: `https://api.assemblyai.com/v1/upload`")
            
            upload_response = requests.post(
                'https://api.assemblyai.com/v1/upload',
                headers=headers,
                data=f,
                timeout=60
            )
        
        st.write(f"Status do upload: `{upload_response.status_code}`")
        
        if upload_response.status_code != 200:
            error_msg = f"""
            ❌ **Erro no upload!**
            
            **Status:** {upload_response.status_code}
            
            **Resposta:**
            ```
            {upload_response.text}
            ```
            
            **Possíveis causas:**
            - API Key inválida
            - Conta não está ativa
            - Email não foi confirmado
            - Plano expirou
            """
            st.error(error_msg)
            return {
                'success': False,
                'error': f"Upload falhou - Status {upload_response.status_code}"
            }
        
        audio_url = upload_response.json()['upload_url']
        st.success("✅ Upload concluído!")
        st.write(f"Audio URL: `{audio_url[:50]}...`")
        
        # PASSO 2: Iniciar transcrição
        st.info("🔄 Iniciando transcrição...")
        
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "audio_url": audio_url,
            "language_code": language,
            "speaker_labels": True,
            "speakers_expected": 2
        }
        
        st.write("Enviando para: `https://api.assemblyai.com/v1/transcript`")
        st.write(f"Dados: `{data}`")
        
        transcript_response = requests.post(
            'https://api.assemblyai.com/v1/transcript',
            headers=headers,
            json=data,
            timeout=30
        )
        
        st.write(f"Status da transcrição: `{transcript_response.status_code}`")
        
        if transcript_response.status_code != 200:
            error_msg = f"""
            ❌ **Erro na transcrição!**
            
            **Status:** {transcript_response.status_code}
            
            **Resposta:**
            ```
            {transcript_response.text}
            ```
            """
            st.error(error_msg)
            return {
                'success': False,
                'error': f"Transcrição falhou - Status {transcript_response.status_code}"
            }
        
        transcript_id = transcript_response.json()['id']
        st.success("✅ Transcrição iniciada!")
        st.info(f"ID: `{transcript_id}`")
        
        # PASSO 3: Monitorar progresso
        st.info("⏳ Processando áudio (isso pode levar alguns minutos)...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        polling_count = 0
        while True:
            polling_count += 1
            st.write(f"Verificação #{polling_count}...")
            
            status_response = requests.get(
                f'https://api.assemblyai.com/v1/transcript/{transcript_id}',
                headers=headers,
                timeout=30
            )
            
            if status_response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Erro ao verificar status (Status: {status_response.status_code})"
                }
            
            result = status_response.json()
            status = result['status']
            
            st.write(f"Status: `{status}`")
            
            # Atualizar barra de progresso
            if status == 'queued':
                progress_bar.progress(10)
                status_text.info("Status: Aguardando fila...")
            elif status == 'processing':
                progress_bar.progress(50)
                status_text.info("Status: Processando...")
            elif status == 'completed':
                progress_bar.progress(100)
                status_text.success("✅ Transcrição concluída!")
                
                return {
                    'success': True,
                    'id': transcript_id,
                    'data': result
                }
            elif status == 'failed':
                error = result.get('error', 'Erro desconhecido')
                st.error(f"❌ Transcrição falhou: {error}")
                return {
                    'success': False,
                    'error': f"Transcrição falhou: {error}"
                }
            
            time.sleep(3)
    
    except Exception as e:
        st.error(f"❌ Erro geral: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def format_transcript(transcript_data, speaker_names):
    """Formata a transcrição com nomes dos falantes"""
    if 'utterances' not in transcript_data:
        text = transcript_data.get('text', 'Transcrição não disponível')
        return f"**Transcrição Completa:**\n\n{text}"
    
    formatted = "**Transcrição por Falante:**\n\n"
    for utterance in transcript_data['utterances']:
        speaker = utterance['speaker']
        speaker_name = speaker_names.get(f"speaker_{speaker}", f"Pessoa {speaker + 1}")
        text = utterance['text']
        
        formatted += f"**{speaker_name}:** {text}\n\n"
    
    return formatted

# ==================== INTERFACE ====================

if not api_key:
    st.warning("❌ Configure sua API Key no sidebar para começar!")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📤 Upload", "⏳ Processar", "📋 Histórico"])

# ==================== ABA 1: UPLOAD ====================
with tab1:
    st.header("📤 Fazer Upload de Áudio")
    st.markdown("Selecione um arquivo de áudio para transcrever")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo:",
        type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'webm', 'aac'],
        help="Formatos suportados: MP3, WAV, MP4, M4A, OGG, FLAC, WEBM, AAC"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"✅ Arquivo: **{uploaded_file.name}** ({uploaded_file.size / (1024*1024):.1f} MB)")
        
        with col2:
            if st.button("🚀 Transcrever", key="btn_transcribe", use_container_width=True):
                # Salvar arquivo
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.current_file = {
                    'name': uploaded_file.name,
                    'path': temp_path,
                    'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                
                st.success("✅ Arquivo salvo! Vá para 'Processar'")
                st.rerun()

# ==================== ABA 2: PROCESSAR ====================
with tab2:
    st.header("⏳ Processar Transcrição")
    
    if 'current_file' in st.session_state:
        current = st.session_state.current_file
        
        st.info(f"📄 **Arquivo:** {current['name']}")
        st.info(f"🌐 **Idioma:** {language}")
        
        if st.button("▶️ INICIAR PROCESSAMENTO", key="btn_process", use_container_width=True):
            
            # Processar
            result = upload_and_transcribe(
                current['path'],
                api_key,
                lang_code
            )
            
            if result['success']:
                # Salvar no histórico
                st.session_state.transcriptions.insert(0, {
                    'id': result['id'],
                    'filename': current['name'],
                    'timestamp': current['timestamp'],
                    'data': result['data'],
                    'speaker_names': {}
                })
                
                # Limpar arquivo
                try:
                    os.remove(current['path'])
                except:
                    pass
                
                del st.session_state.current_file
                
                st.balloons()
                st.success("✨ Transcrição salva! Vá para 'Histórico'")
                time.sleep(1)
                st.rerun()
            
            else:
                st.error(f"❌ {result['error']}")
    
    else:
        st.info("📝 Faça upload de um arquivo na aba anterior!")

# ==================== ABA 3: HISTÓRICO ====================
with tab3:
    st.header("📋 Histórico de Transcrições")
    
    if st.session_state.transcriptions:
        
        for idx, trans in enumerate(st.session_state.transcriptions):
            with st.expander(
                f"📄 {trans['filename']} • {trans['timestamp']}",
                expanded=idx == 0
            ):
                
                # Renomear falantes
                transcript_data = trans['data']
                
                if 'utterances' in transcript_data:
                    st.subheader("👥 Renomear Falantes")
                    speakers = sorted(set(u['speaker'] for u in transcript_data['utterances']))
                    
                    cols = st.columns(min(len(speakers), 3))
                    for i, speaker_id in enumerate(speakers):
                        with cols[i % len(cols)]:
                            default = trans['speaker_names'].get(f"speaker_{speaker_id}", f"Pessoa {speaker_id + 1}")
                            new_name = st.text_input(
                                f"Falante {speaker_id + 1}:",
                                value=default,
                                key=f"spk_{idx}_{speaker_id}",
                                label_visibility="collapsed"
                            )
                            if new_name != default:
                                trans['speaker_names'][f"speaker_{speaker_id}"] = new_name
                    
                    st.divider()
                
                # Mostrar transcrição
                st.subheader("📝 Transcrição")
                formatted = format_transcript(transcript_data, trans['speaker_names'])
                st.markdown(formatted)
                
                # Botões
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📥 Baixar TXT",
                        formatted,
                        file_name=f"{trans['filename'].rsplit('.', 1)[0]}_transcricao.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("🗑️ Deletar", key=f"del_{idx}", use_container_width=True):
                        st.session_state.transcriptions.pop(idx)
                        st.rerun()
                
                with col3:
                    if st.button("📋 Copiar", key=f"copy_{idx}", use_container_width=True):
                        st.success("✅ Copiado!")
    
    else:
        st.info("📝 Nenhuma transcrição ainda. Comece na aba 'Upload'!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🎙️ <strong>Transcritor de Áudio com IA</strong> • 
    Powered by <a href="https://assemblyai.com" target="_blank">AssemblyAI</a>
</div>
""", unsafe_allow_html=True)
