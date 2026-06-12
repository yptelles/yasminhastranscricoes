import streamlit as st
import requests
import time

st.set_page_config(page_title="🎙️ Transcritor", page_icon="🎙️", layout="wide")
st.title("🎙️ Transcritor de Áudio")

with st.sidebar:
    st.header("API Key")
    key = st.text_input("Cole aqui:", type="password")

if not key:
    st.warning("⚠️ Insira API Key na barra lateral")
else:
    st.success("✅ API Key OK")
    
    file = st.file_uploader("Arquivo:", type=['mp3','wav','mp4','m4a','ogg','flac'])
    
    if file:
        st.info(f"✅ {file.name}")
        
        if st.button("Transcrever"):
            try:
                st.write("Enviando...")
                
                h = {"Authorization": key}
                r = requests.post(
                    "https://api.assemblyai.com/v1/upload",
                    headers=h,
                    data=file.getbuffer()
                )
                
                if r.status_code == 200:
                    url = r.json()["upload_url"]
                    st.write("Processando...")
                    
                    r2 = requests.post(
                        "https://api.assemblyai.com/v1/transcript",
                        headers=h,
                        json={"audio_url": url, "speaker_labels": True}
                    )
                    
                    tid = r2.json()["id"]
                    
                    for i in range(120):
                        r3 = requests.get(
                            f"https://api.assemblyai.com/v1/transcript/{tid}",
                            headers=h
                        )
                        
                        res = r3.json()
                        
                        if res.get("status") == "completed":
                            st.success("✅ Pronto!")
                            
                            for u in res.get("utterances", []):
                                s = "Pessoa 1" if u["speaker"] == "A" else "Pessoa 2"
                                st.write(f"**{s}:** {u['text']}")
                            break
                        elif res.get("status") == "error":
                            st.error("Erro")
                            break
                        
                        time.sleep(3)
                else:
                    st.error(f"Erro: {r.status_code}")
            
            except Exception as e:
                st.error(f"Erro: {str(e)}")
