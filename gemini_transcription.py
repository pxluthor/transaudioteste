import os
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import toml
from pathlib import Path
import pyaudio
from st_audiorec import st_audiorec
import streamlit.components.v1 as components



config = toml.load("config.toml")


# Carregar a chave de API diretamente do arquivo de configuração
api_key = st.secrets['api_keys']['google'] 
genai.configure(api_key=api_key)

# Configuração da API do Google (Gemini)
generation_config = {
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(model_name = 'models/gemini-1.5-flash-latest',
                              generation_config=generation_config,)

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

rec = sr.Recognizer()
#wav_audio_data = st_audiorec()
with st.sidebar:
  st.title("Gravação de Áudio")
  wav_audio_data = st_audiorec()
  
  st.divider()





#microfones = sr.Microphone().list_microphone_names()
#st.write(microfones)
#selected_microfones = st.multiselect("Selecione o(s) microfone(s)", microfones)

# Função principal
def main():
    components.iframe("https://typebot_view.pxluthor.com.br/api/v1/typebots/meu-typebot-e9lpn27", height=600)
    # Título
    st.title("💬 Chat - Transcription audio 🎙🔉")

   

    # Sidebar
    st.sidebar.button("Limpar Chat", on_click=limpar_chat)
    

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
        # Entrada de texto
        if st.button('Fale comigo'):
            #for microfone in selected_microfones:
            
            
            with sr.Microphone() as mic:
                rec.adjust_for_ambient_noise(mic)
                st.markdown("Pode falar que eu vou gravar")
                voz = rec.listen(mic)
                try:
                    texto = rec.recognize_google(voz, language="pt-BR")
                    prompt = texto
                    resp = model.generate_content(prompt)
                    st.chat_message("user").markdown(prompt)
                    with st.chat_message("assistente"): #mostra o ícone do assistente na tela
                        st.markdown(resp.text) # conteúdo da resposta
            
                        
                except sr.UnknownValueError:
                    st.markdown("Não entendi o que você disse.")
                except sr.RequestError as e:
                    st.markdown(f"Erro ao solicitar o reconhecimento de voz: {e}")

        
        if prompt := st.chat_input("Como posso ajudar?",): # recebe um comando via chat_input e armazena no prompt.
            st.chat_message("user").markdown(prompt) # mostra a mensagem na tela (chat_message) - user formatando o prompt em markdown
            response = st.session_state.chat.send_message(prompt) # envia a mensagem ao assistente (chat.send_message) e armazena a resposta na variável response
            with st.chat_message("assistente"): #mostra o ícone do assistente na tela
                st.markdown(response.text) # conteúdo da resposta
            
    else:
        # Entrada de áudio
        arquivo_carregado = st.file_uploader("Carregar arquivo de áudio (MP3 ou WAV)")
        st.chat_input("Como posso ajudar?")
        if arquivo_carregado:
            with open("audio_temp.mp3", "wb") as f:
                f.write(arquivo_carregado.read())
        # Enviar o arquivo local para a API
            your_file = genai.upload_file("audio_temp.mp3")
            st.info("Audio carregado !")
            
            prompt =''' você é um analista de relacionamento em um callcenter da empresa Leste Telecom,
                        faça a transcrição fiel ao áudio, separando na apresesntando do resultado  as falas do cliente e atendente segundo o modelo de exemplo:
                        tempo - Atendente ou Cliente: Contexto da trancrição de acordo com que está falando
                        
                        Faça um resumo do atendimento.
                        
                        informe os Pontos chave:
                        informe Possíveis problemas:
                        informe Sugestões:
                        informe a Conclusão: '''
  





            
            resp = model.generate_content([prompt, your_file])
            

            if st.button("Fazer transcrição"):
                
                response = st.session_state.chat.send_message(resp.text)
                with st.chat_message("Assistente"):
                    st.success('Transcrição realizada')
                    st.markdown(resp.text)
                    #st.markdown(response.text)
           

# Função para limpar o chat
def limpar_chat():
    st.session_state.chat.history.clear()
    #os.remove("audio_temp.mp3")




if __name__ == "__main__":
    main()
