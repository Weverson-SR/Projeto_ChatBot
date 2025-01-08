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
        """Inicializa a interface do Streamlit com uma instância de GeminiChat."""
        self.gemini = gemini_instance

    def iniciar(self):
        """Configura e executa a interface Streamlit."""
        st.title("ChatBot com Gemini")
        st.write("Bem-vindo! Converse com o Gemini")

        # Criando um histórico da sessão (efeito chatgpt)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Input do usuário
        user_input = st.text_input("Digite sua mensagem:", key="user_input", placeholder="Digite algo...")

        if user_input:  # Quando o usuário envia uma mensagem

            # Adiciona a mensagem do usuário ao histórico
            st.session_state.chat_history.append({"user": user_input})

            # Gera a resposta do Gemini
            resposta = self.gemini.gerar_resposta(user_input)

            # Adiciona a resposta ao histórico
            st.session_state.chat_history.append({"gemini": resposta})

            # Exibe o histórico de conversa
        for mensagem in st.session_state.chat_history:
            if "user" in mensagem:
                st.write(f"**Você:** {mensagem['user']}")
            elif "gemini" in mensagem:
                st.write(f"**Gemini:** {mensagem['gemini']}")


if __name__ == "__main__":
    # Inicializa o GeminiChat
    gemini_chat = GeminiChat()

    # Inicializa a interface do Streamlit com a instância do GeminiChat
    interface = StreamlitInterface(gemini_chat)
    interface.iniciar()
