import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st


class GeminiChat:

    def __init__(self):
        """Inicializa a configuração do Gemini."""
        self.api_key = self._carregar_chave_api()
        self.model = self._configurar_api(self.api_key)
        self.chat = self.model.start_chat(history=[])

    @staticmethod
    def _carregar_chave_api():
        """Carrega a chave da API do arquivo .env."""
        load_dotenv()
        chave_api = os.getenv("GENAI_API_KEY")
        if not chave_api:
            raise ValueError("A chave da API não foi encontrada. Verifique o arquivo .env.")
        return chave_api

    @staticmethod
    def _configurar_api(chave_api):
        """Configura a API do Gemini."""
        genai.configure(api_key=chave_api)
        return genai.GenerativeModel("gemini-1.5-flash")

    def gerar_resposta(self, mensagem):
        try:
            # Envia a mensagem para o modelo e obtém a resposta
            response = self.chat.send_message(mensagem)

            # Retorna o texto gerado pelo modelo
            return response.text.strip()

        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao gerar a resposta."


class StreamlitInterface:
    def __init__(self, gemini_instance):
        self.gemini = gemini_instance
        self.total_tokens = 0

    def handle_input(self):
        """Gerencia a entrada do usuário no Streamlit."""
        # Obtém a entrada do usuário
        input_usuario = st.session_state.get("user_input", "")

        if input_usuario:  # Verifica se há mensagem do usuário
            # Adiciona a mensagem do usuário ao histórico
            st.session_state.chat_history.append({"user": input_usuario})

            try:
                # Gera a resposta do Gemini
                resposta_gemini = self.gemini.gerar_resposta(input_usuario)

                # Adiciona a resposta do Gemini ao histórico
                st.session_state.chat_history.append({"gemini": resposta_gemini})

            except Exception as e:
                # Em caso de erro, mostra no Streamlit
                st.session_state.chat_history.append({"gemini": f"Erro ao gerar resposta: {e}"})

            # Calcula o número de tokens da mensagem do usuário
            user_tokens = len(input_usuario.split())

            # Gera a resposta do Gemini
            resposta_gemini = self.gemini.gerar_resposta(input_usuario)

            # Calcula o número de tokens da resposta do Gemini
            gemini_tokens = len(resposta_gemini.split())

            # Soma os tokens da mensagem do usuário e da resposta do Gemini
            total_tokens = user_tokens + gemini_tokens

            # Soma o total de tokens da conversa
            self.total_tokens += total_tokens

            # Atualiza o contador
            st.session_state["total_tokens"] += total_tokens

    def iniciar(self):
        st.sidebar.title("Chat com Gemini")
        st.sidebar.write("Tire suas dúvidas e seja direto!"
                         "Estamos trabalhando para que ele se lembre de suas mensagens.")
        st.title("No que posso ajudar?")

        def get_contador():
            if "total_tokens" not in st.session_state:
                st.session_state["total_tokens"] = 0
            return st.session_state["total_tokens"]

        st.sidebar.write(f"Contador de tokens: {get_contador()}")

        if "total_tokens" not in st.session_state:
            st.session_state.total_tokens = 0

        # Inicializa o histórico na sessão
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Markdown para mudar o fundo das mensagens tanto do usuário quanto do gemini
        st.markdown("""
            <style>
                .user-message {
                    background-color: rgba(102, 102, 102, 0.1);  /* Fundo cinza claro */
                    padding: 10px;  /* Espaçamento interno */
                    border-radius: 5px;  /* Borda arredondada */
                    margin-bottom: 5px;  /* Espaçamento entre as mensagens */
                    font-size: 14px;  /* Ajuste do tamanho da fonte */
                }
                
                .gemini-message {
                    padding:10px
                }

            </style>
        """, unsafe_allow_html=True)

        # Exibição das mensagens com o estilo
        with st.container():
            for i, mensagem in enumerate(st.session_state.chat_history):
                if "user" in mensagem:
                    # Aplica a classe user-message para as mensagens do usuário
                    st.markdown(f"<p class='user-message'><b>Você:</b> {mensagem['user']}</p>", unsafe_allow_html=True)
                elif "gemini" in mensagem:
                    # Aplica a classe gemini-message para as mensagens do Gemini
                    st.markdown(f"<p class='gemini-message'><b>Gemini:</b> {mensagem['gemini']}</p>",
                                unsafe_allow_html=True)

        # Caixa de entrada do usuário com callback
        st.text_input(
            "Digite sua mensagem aqui",
            placeholder="Pressione Enter para enviar",
            key="user_input",
            on_change=self.handle_input,  # Chama a função ao enviar a mensagem
        )

        # Ajuste de estilo para manter a caixa no final da página
        st.markdown("""
            <style>
                /* Estilo para manter a caixa de mensagem fixa no rodapé */
                .stTextInput {
                    position: fixed; /* Fixa a posição no rodapé */
                    bottom: 0; /* Garante que esteja no fundo */
                    max-width: 700px; /* Largura máxima */
                    width: 100%; /* Ajusta à largura total do container */
                    margin: 0 auto; /* Centraliza horizontalmente */
                }
            </style>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Inicializa o GeminiChat
    gemini_chat = GeminiChat()

    # Inicializa a interface do Streamlit
    interface = StreamlitInterface(gemini_chat)
    interface.iniciar()
