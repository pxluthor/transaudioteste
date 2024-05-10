import os
import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
from pathlib import Path
import toml


config = toml.load("secrets.toml")
google_api_key = config["api_keys"]["google"]

# Configuração da API do Google (Gemini)
#genai.configure(api_key=os.getenv("GOOGLE_GEMINI_KEY"))
genai.configure(api_key=google_api_key)
google_api_key = config["api_keys"]["google"]

model = genai.GenerativeModel('gemini-pro')

# Função para transcrever áudio
def transcrever_audio(arquivo_audio):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(arquivo_audio) as fonte:
            audio = r.record(fonte)
        texto = r.recognize_google(audio, language='pt-BR')  # Definindo o idioma para português do Brasil
        return texto
    except sr.UnknownValueError:
        return "Erro: Não foi possível entender o áudio."
    except sr.RequestError as e:
        return f"Erro na transcrição do áudio: {e}"

# Função para converter o papel de parede
def role_to_streamlit(role):
    return "assistente" if role == "model" else role

# Função principal
def main():
    # Título
    st.title("🔉 Aplicativo de Transcrição Automática 🔉")

    # Sidebar
    st.sidebar.button("Limpar Chat", on_click=limpar_chat)
    st.sidebar.button("Exportar Texto Transcrito", on_click=exportar_texto)

    # Inicialização do chat
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    # Exibir histórico do chat
    for message in st.session_state.chat.history:
        with st.chat_message(role_to_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Opções de entrada: texto ou áudio
    opcao_entrada = st.sidebar.radio("Selecione o tipo de entrada:", ("Texto", "Áudio"))

    if opcao_entrada == "Texto":
        # Entrada de texto (como antes)
        if prompt := st.chat_input("Como posso ajudar?"):
            st.chat_message("user").markdown(prompt)
            response = st.session_state.chat.send_message(prompt)
            with st.chat_message("assistente"):
                st.markdown(response.text)
    else:
    # Entrada de áudio
        arquivo_carregado = st.file_uploader("Carregar arquivo de áudio (MP3 ou WAV)")
        if arquivo_carregado:
            texto_transcrito = transcrever_audio(arquivo_carregado)
            st.write("Texto transcrito:", texto_transcrito)
            st.success('Transcrição realizada')

            if st.button("Analisar transcrição"):
                response = st.session_state.chat.send_message(texto_transcrito)
                with st.chat_message("assistente"):
                    st.markdown(response.text)

# Função para limpar o chat
def limpar_chat():
    st.session_state.chat.history.clear()

# Função para exportar o texto transcrito
def exportar_texto():
    texto_transcrito = ""
    if st.session_state.chat.history:
        for message in st.session_state.chat.history:
            if message.role == "assistente":
                texto_transcrito += message.parts[0].text + "\n"
        if texto_transcrito:
            st.download_button(
                label="Baixar Texto Transcrito",
                data=texto_transcrito,
                file_name="texto_transcrito.txt",
                mime="text/plain",
            )
    else:
        st.warning("Não há texto transcrito para exportar.")

if __name__ == "__main__":
    main()
