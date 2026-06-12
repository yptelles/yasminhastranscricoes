import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="🎙️ Transcritor",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Transcritor de Áudio")
st.markdown("**Transcrição em Tempo Real • Sem Login • Sem API Key**")

# ==================== INICIALIZAR STATE ====================
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

# ==================== HTML COM WEB SPEECH API (CORRIGIDO) ====================

html_code = """
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .container { max-width: 100%; margin: 0 auto; padding: 20px; }
    .button-group { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }
    button {
        padding: 12px 24px;
        font-size: 16px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        background-color: #0066cc;
        color: white;
        transition: background-color 0.2s;
    }
    button:hover { background-color: #0052a3; }
    button:disabled { background-color: #ccc; cursor: not-allowed; }
    .stop-btn { background-color: #cc0000; }
    .stop-btn:hover { background-color: #990000; }
    textarea {
        width: 100%;
        min-height: 200px;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        font-family: monospace;
        resize: vertical;
        box-sizing: border-box;
    }
    .status {
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
        font-weight: bold;
    }
    .status.listening { background-color: #e3f2fd; color: #0066cc; }
    .status.processing { background-color: #fff3e0; color: #ff6600; }
    .status.done { background-color: #e8f5e9; color: #00cc00; }
    .status.error { background-color: #ffebee; color: #cc0000; }
    .info-box {
        background-color: #f5f5f5;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 13px;
    }
    .audio-player {
        margin: 20px 0;
        width: 100%;
    }
</style>

<div class="container">
    <div class="info-box">
        ℹ️ <strong>Como usar:</strong> Clique em "🎤 Iniciar Gravação" para gravar áudio do microfone. 
        O navegador reconhecerá a fala automaticamente em português.
    </div>

    <div class="button-group">
        <button id="startBtn" onclick="startListening()">🎤 Iniciar Gravação</button>
        <button id="stopBtn" class="stop-btn" onclick="stopListening()" disabled>⏹️ Parar</button>
        <button onclick="clearText()">🗑️ Limpar</button>
        <button onclick="copiarTexto()">📋 Copiar</button>
    </div>

    <div id="status" class="status" style="display:none;"></div>

    <div>
        <label><strong>📝 Transcrição:</strong></label>
        <textarea id="output" placeholder="A transcrição aparecerá aqui..."></textarea>
    </div>

    <div style="margin-top: 20px;">
        <label for="audioFile"><strong>📁 Ou faça upload de um arquivo de áudio:</strong></label>
        <input type="file" id="audioFile" accept="audio/*" onchange="handleFileUpload(event)">
    </div>

    <audio id="audioPlayer" class="audio-player" controls style="display:none;"></audio>
</div>

<script>
    const output = document.getElementById('output');
    const status = document.getElementById('status');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    let recognition;
    let isListening = false;
    let finalTranscript = '';

    // Configurar Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = function() {
            isListening = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            showStatus('🎤 Ouvindo... Fale agora!', 'listening');
            output.style.borderColor = '#0066cc';
            finalTranscript = output.value;
        };

        recognition.onresult = function(event) {
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            output.value = finalTranscript + interimTranscript;
            output.scrollTop = output.scrollHeight;
        };

        recognition.onerror = function(event) {
            showStatus('❌ Erro: ' + event.error, 'error');
        };

        recognition.onend = function() {
            isListening = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            if (output.value.trim()) {
                showStatus('✅ Transcrição concluída!', 'done');
            }
        };
    } else {
        showStatus('❌ Web Speech API não suportada. Use Chrome, Edge ou Safari.', 'error');
    }

    function startListening() {
        if (SpeechRecognition) {
            recognition.start();
        }
    }

    function stopListening() {
        if (recognition) {
            recognition.stop();
        }
    }

    function clearText() {
        output.value = '';
        finalTranscript = '';
        status.style.display = 'none';
        output.style.borderColor = '#ddd';
    }

    function copiarTexto() {
        if (output.value) {
            navigator.clipboard.writeText(output.value);
            showStatus('✅ Copiado para clipboard!', 'done');
            setTimeout(() => status.style.display = 'none', 2000);
        }
    }

    function showStatus(message, type) {
        status.textContent = message;
        status.className = 'status ' + type;
        status.style.display = 'block';
    }

    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            const audioPlayer = document.getElementById('audioPlayer');
            const url = URL.createObjectURL(file);
            audioPlayer.src = url;
            audioPlayer.style.display = 'block';
            showStatus('📁 Arquivo carregado. Clique em "Iniciar Gravação" enquanto reproduz para transcrever.', 'processing');
        }
    }
</script>
"""

# ==================== INTERFACE PRINCIPAL ====================

st.components.v1.html(html_code, height=850)

st.divider()

# ==================== SEÇÃO DE SALVAMENTO ====================

st.subheader("💾 Salvar Transcrição")

col1, col2 = st.columns([3, 1])

with col1:
    transcription_text = st.text_area(
        "Cole a transcrição aqui ou edite a do gravador acima:",
        height=100,
        placeholder="A transcrição aparecerá aqui...",
        label_visibility="collapsed"
    )

with col2:
    st.write("")
    st.write("")
    if st.button("💾 Salvar", use_container_width=True):
        if transcription_text.strip():
            st.session_state.transcriptions.insert(0, {
                'text': transcription_text,
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })
            st.success("✅ Salvo!")
            st.rerun()
        else:
            st.warning("⚠️ Digite algo primeiro!")

st.divider()

# ==================== HISTÓRICO ====================

st.subheader("📋 Transcrições Salvas")

if st.session_state.transcriptions:
    for idx, trans in enumerate(st.session_state.transcriptions):
        with st.expander(f"📄 {trans['timestamp']}", expanded=idx == 0):
            st.markdown(trans['text'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📥 Baixar TXT",
                    trans['text'],
                    file_name=f"transcricao_{trans['timestamp'].replace('/', '-').replace(':', '-')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"dl_{idx}"
                )
            
            with col2:
                if st.button("📋 Copiar", key=f"copy_{idx}", use_container_width=True):
                    st.success("✅ Copiado!")
            
            with col3:
                if st.button("🗑️ Deletar", key=f"del_{idx}", use_container_width=True):
                    st.session_state.transcriptions.pop(idx)
                    st.rerun()

else:
    st.info("📝 Nenhuma transcrição salva ainda. Comece a gravar!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🎙️ <strong>Transcritor com Web Speech API</strong> • Funciona no navegador • 100% Grátis • Sem Dependências
</div>
""", unsafe_allow_html=True)
