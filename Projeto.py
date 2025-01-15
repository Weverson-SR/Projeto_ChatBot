import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st


class GeminiChat:
    LIMITE_TOKENS_DIARIO = 1_000_000  # Limite diário de tokens

    def __init__(self):
        """Inicializa a configuração do Gemini."""
        self.api_key = self._carregar_chave_api()
        self.model = self._configurar_api(self.api_key)
        self.conversa = []
        self.tokens_usados = 0  # Contador de tokens usados

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

    def atualizar_contador_tokens(self, mensagem, resposta_texto):
        """Atualiza o contador de tokens usados com base na mensagem e na resposta."""
        try:
            metadata = getattr(resposta_texto, "usage_metadata", None)
            if metadata:
                input_tokens = metadata.get("input_tokens", 0)
                output_tokens = metadata.get("output_tokens", 0)
                total_tokens = metadata.get("total_tokens", 0)
            else:
                # Estimativa manual caso os metadados não estejam disponíveis
                input_tokens = len(mensagem.split())
                output_tokens = len(resposta_texto.split())
                total_tokens = input_tokens + output_tokens
        except AttributeError:
            # Estimativa manual em caso de erro
            input_tokens = len(mensagem.split())
            output_tokens = len(resposta_texto.split())
            total_tokens = input_tokens + output_tokens

        # Incrementa o contador de tokens usados
        self.tokens_usados += total_tokens

        # Exibe os detalhes da contagem de tokens
        print("\nTokens usados nesta interação:")
        print(f"- Entrada: {input_tokens} tokens")
        print(f"- Saída: {output_tokens} tokens")
        print(f"- Total: {total_tokens} tokens")
        print(f"Tokens usados no total: {self.tokens_usados}/{self.LIMITE_TOKENS_DIARIO}")

    def gerar_resposta(self, mensagem):
        """Gera uma resposta usando o modelo."""
        mensagem = f"Responda em português: {mensagem}"
        response = self.model.generate_content(mensagem)

        # Atualiza o contador de tokens
        self.atualizar_contador_tokens(mensagem, response.text)

        # Retorna a resposta gerada
        return response.text.strip()

    def verificar_limite_tokens(self):
        """Verifica se o limite de tokens está próximo ou foi alcançado."""
        if self.tokens_usados >= self.LIMITE_TOKENS_DIARIO:
            print("\nEncerramos por hoje. Você atingiu o limite de tokens diário.")
            return True
        elif self.tokens_usados >= 0.9 * self.LIMITE_TOKENS_DIARIO:
            print("\nAtenção: Você está próximo do limite diário de tokens.")
        return False

    def iniciar_conversa(self):
        """Controla o loop da conversa com o Gemini."""
        print("Iniciando conversa com Gemini. Digite 'sair' para encerrar.\n")
        try:
            while True:
                user_input = input("Usuário: ")
                if user_input.lower() == "sair":
                    print("Encerrando a conversa. Até mais!")
                    break

                self.conversa.append(f"Usuário: {user_input}")
                resposta_gemini = self.gerar_resposta(user_input)
                print(f"Gemini: {resposta_gemini}")
                self.conversa.append(f"Gemini: {resposta_gemini}")

                # Verifica limite de tokens após cada interação
                if self.verificar_limite_tokens():
                    break
        finally:
            # Limpeza ao encerrar o programa
            print("Encerrando a conexão com o Gemini...")
            del self.model  # Libera o modelo


class StreamlitInterface:
    def __init__(self, gemini_instance):
        self.gemini = gemini_instance

    def handle_input(self):
        # Verifica se o usuário digitou algo
        user_input = st.session_state.get("user_input", "")
        if user_input:
            # Adiciona a mensagem ao histórico
            st.session_state.chat_history.append({"user": user_input})

            # Gera a resposta do Gemini
            resposta = self.gemini.gerar_resposta(user_input)

            # Adiciona a resposta do Gemini ao histórico
            st.session_state.chat_history.append({"gemini": resposta})

            # Limpa a entrada do usuário
            st.session_state.user_input = ""

    def iniciar(self):
        st.sidebar.title("Chat com Gemini")
        st.sidebar.write("Tire suas dúvidas e seja direto!"
                         "Estamos trabalhando para que ele se lembre de suas mensagens.")
        st.sidebar.write("Talvez um contador de tokens aqui?")
        st.title("No que posso ajudar?")

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

        # Força o scroll para a mensagem mais recente
        scroll_script = """
        <script>
            var chatBox = window.parent.document.body;
            chatBox.scrollTop = chatBox.scrollHeight;
        </script>
        """
        st.markdown(scroll_script, unsafe_allow_html=True)

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

        # Ajustando e modelando a caixa de mensagem # Era para ser isso ne pqp, não funciona
        st.markdown("""
            <style>
                .stTextArea{
                    display:flex;
                    justify-content:content;
                    flex-direction: column;
                    width: 100%
                }
                 .stTextArea textarea {
                    white-space: pre-line; /* Permite a quebra automática */
                    word-wrap: break-word; /* Quebra as palavras longas */
                    height: 50px;
                    max-height: 150px;
                    resize: none;
                    overflow-y: auto;
                    padding: 10px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
            </style>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Inicializa o GeminiChat
    gemini_chat = GeminiChat()

    # Inicializa a interface do Streamlit com a instância do GeminiChat
    interface = StreamlitInterface(gemini_chat)
    interface.iniciar()
