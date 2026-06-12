import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🎙️ Transcritor", page_icon="🎙️", layout="wide")

st.title("🎙️ Transcritor de Áudio com IA")

# Sidebar
with st.sidebar:
    st.header("⚙️ Config")
    api_key = st.text_input("API Key:", type="password")
    if api_key:
        st.success("✅ OK")

if 'trans' not in st.session_state:
    st.session_state.trans = []

tab1, tab2 = st.tabs(["📤 Upload", "📋 Histórico"])

with tab1:
    if not api_key:
        st.warning("Insira API Key!")
    else:
        st.header("Upload de Áudio")
        file = st.file_uploader("Arquivo:", type=['mp3','wav','mp4','m4a','ogg','flac'])
        
        if file:
            st.info(f"✅ {file.name} ({file.size/1024/1024:.1f}MB)")
            
            if st.button("🚀 Transcrever"):
                try:
                    bar = st.progress(0)
                    txt = st.empty()
                    
                    # Upload
                    txt.text("Enviando...")
                    bar.progress(20)
                    
                    resp = requests.post(
                        "https://api.assemblyai.com/v1/upload",
                        headers={"Authorization": api_key},
                        data=file.getbuffer()
                    )
                    
                    url = resp.json()['upload_url']
                    
                    # Transcrever
                    txt.text("Iniciando transcrição...")
                    bar.progress(40)
                    
                    resp2 = requests.post(
                        "https://api.assemblyai.com/v1/transcript",
                        headers={"Authorization": api_key},
                        json={
                            "audio_url": url,
                            "speaker_labels": True
                        }
                    )
                    
                    tid = resp2.json()['id']
                    
                    # Aguardar
                    txt.text("Processando...")
                    bar.progress(50)
                    
                    for i in range(1440):
                        r = requests.get(
                            f"https://api.assemblyai.com/v1/transcript/{tid}",
                            headers={"Authorization": api_key}
                        )
                        
                        res = r.json()
                        
                        bar.progress(min(50 + i//20, 95))
                        
                        if res['status'] == 'completed':
                            bar.progress(100)
                            st.session_state.resultado = res
                            st.session_state.arquivo = file.name
                            st.success("✅ Pronto!")
                            break
                        elif res['status'] == 'error':
                            st.error("❌ Erro")
                            break
                        
                        time.sleep(5)
                
                except Exception as e:
                    st.error(f"Erro: {e}")

# Resultado
if 'resultado' in st.session_state:
    st.markdown("---")
    st.header("📝 Resultado")
    
    res = st.session_state.resultado
    
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.text_input("Pessoa 1:", "Pessoa 1")
    with col2:
        p2 = st.text_input("Pessoa 2:", "Pessoa 2")
    
    if res.get('utterances'):
        txt = ""
        for u in res['utterances']:
            s = u['speaker']
            t = u['text']
            name = p1 if s == 'A' else p2
            st.write(f"**{name}:** {t}")
            txt += f"{name}: {t}\n"
        
        st.download_button("📥 Baixar TXT", txt, file_name=f"trans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

with tab2:
    st.header("📋 Histórico")
    if st.session_state.trans:
        for t in st.session_state.trans:
            st.write(t)
    else:
        st.info("Vazio")
