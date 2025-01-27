import google.generativeai as genai
import streamlit as st
import sqlite3
import json


class GeminiChat:

    def __init__(self):
        """Inicializa a configuração do Gemini."""
        self.sqlite = Sqlite()
        dados_usuario_form = sqlite.seleciona_usuario()
        if dados_usuario_form:
            self.nome_usuario_form = dados_usuario_form['nome']
            self.chave_api_form = dados_usuario_form['gemini_token']
        else:
            raise ValueError("Nenhum dado encontrado no banco de  INIT")

        self.model = self._configurar_api(self.chave_api_form)
        self.chat = self.model.start_chat(history=[])

    @staticmethod
    def _configurar_api(chave_api_form):
        """Configura a API do Gemini."""
        genai.configure(api_key=chave_api_form)
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
    def __init__(self, gemini_instance=None):
        self.gemini = gemini_instance
        self.total_tokens = 0
        self.nome_usuario_formulario = None
        self.chave_api_formulario = None
        self.sqlite = Sqlite()
        self.json_usuario = JsonUsuario()

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

        if "formulario_preenchido" not in st.session_state:
            st.session_state.formulario_preenchido = False


        with st.expander("Formulario"):
            if not self.sqlite.existe_usuario(self.nome_usuario_formulario):
                with st.form("Formulario"):
                    st.subheader("Insira seus dados")
                    self.nome_usuario_formulario = st.text_input("Nome:", placeholder="Digite seu nome")
                    self.chave_api_formulario = st.text_input("Chave API:", placeholder="Digite sua chave API", type="password")
                    botao = st.form_submit_button("Salvar")

                    if botao:
                        # Salva a chave API e o nome do usuário no banco de dados
                        self.sqlite.insira_usuario(self.nome_usuario_formulario, self.chave_api_formulario)
                        # Salva os dados do usuário no arquivo JSON
                        self.json_usuario.nome_usuario = self.nome_usuario_formulario
                        self.json_usuario.chave_api = self.chave_api_formulario
                        self.json_usuario.salvar_dados()
                        st.success("Dados salvos com sucesso!")
                        st.session_state.formulario_preenchido = True

        if st.session_state.formulario_preenchido:
            st.write("Agora você pode conversar com o Gemini!")
            self.handle_input()

            for mensagem in st.session_state.chat_history:
                if "user" in mensagem:
                    st.markdown(f'<div class="user-message">{mensagem["user"]}</div>', unsafe_allow_html=True)
                elif "gemini" in mensagem:
                    st.markdown(f'<div class="gemini-message">{mensagem["gemini"]}</div>', unsafe_allow_html=True)

    def handle_input(self):
        """Gerencia a entrada do usuário no Streamlit."""
        input_usuario = st.text_input("Digite sua mensagem:" , placeholder="Digite aqui...")
        if input_usuario:
            st.session_state.chat_history.append({"user": input_usuario})
            # Verifica se a instância foi iniciada
            if self.gemini is None:
                st.error("Erro: A instãncia do Gemini ainda não foi iniciada.")
                return
            try:
                resposta_gemini = self.gemini.gerar_resposta(input_usuario)
                st.session_state.chat_history.append({"gemini": resposta_gemini})
                self.total_tokens += len(input_usuario.split()) + len(resposta_gemini.split())
                st.session_state["total_tokens"] = self.total_tokens
            except Exception as e:
                print(f"Erro ao gerar resposta: {e}")
            # Ajuste de estilo para manter a caixa no final da página
        st.markdown("""<style>
            /* Estilo para manter a caixa de mensagem fixa no rodapé */
            .stTextInput {
                position: fixed; /* Fixa a posição no rodapé */
                bottom: 0; /* Garante que esteja no fundo */
                max-width: 700px; /* Largura máxima */
                width: 100%; /* Ajusta à largura total do container */
                margin: 0 auto; /* Centraliza horizontalmente */
            }
        </style>""", unsafe_allow_html=True)


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

class Sqlite:
    def __init__(self):
        self.conn = sqlite3.connect("gemini.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela()

    # Cria uma tabela no banco de dados
    def criar_tabela(self):

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS usuario (
            nome TEXT NOT NULL,
            gemini_token TEXT NOT NULL PRIMARY KEY
            )""")
        self.conn.commit()

    # Insere dados na tabela
    def insira_usuario(self, nome_usuario_formulario, chave_api_formulario):
        self.cursor.execute("""INSERT INTO usuario (nome, gemini_token) VALUES (?, ?) """,
                            (nome_usuario_formulario, chave_api_formulario))
        self.conn.commit()
        self.conn.close()

    # Seleciona o banco de dados
    def seleciona_usuario(self):
        self.cursor.execute("SELECT * FROM usuario")
        dados_usuario_form = self.cursor.fetchone()
        if dados_usuario_form:
            return {'nome': dados_usuario_form[0], 'gemini_token': dados_usuario_form[1]}
        else:
            return None

    # Verifica se o usuário existe
    def existe_usuario(self, nome_usuario):
        cursor = self.conn.cursor()
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuario (
                        id INTEGER PRIMARY KEY,
                        nome TEXT NOT NULL,
                        chave_api TEXT NOT NULL
                    )
                """)
        self.conn.commit()
        # Verifica se o usuário já está cadastrado no banco de dados
        self.cursor.execute("SELECT * FROM usuario WHERE nome = ?", (nome_usuario,))
        resultado = self.cursor.fetchone()
        return resultado is not None

    # Atualiza o usuário
    def atualiza_usuario(self, nome_usuario_formulario, chave_api_formulario):
        self.cursor.execute("""UPDATE usuario SET gemini_token = ? WHERE nome = ?""",
                            (chave_api_formulario, nome_usuario_formulario))
        self.conn.commit()


class JsonUsuario:

    def __init__(self):
        self.nome_usuario = None
        self.chave_api = None

    def carregar_dados(self):
        try:
            with open('dados_usuario.json', 'r') as arquivo:
                dados = json.load(arquivo)
                self.nome_usuario = dados['nome']
                self.chave_api = dados['chave_api']
        except FileNotFoundError:
            pass

    def salvar_dados(self):
        dados = {'nome': self.nome_usuario, 'chave_api': self.chave_api}
        with open('dados_usuario.json', 'w') as arquivo:
            json.dump(dados, arquivo)


if __name__ == "__main__":
    # Verifica se a instância do Gemini já foi armazenada
    if "gemini_instance" not in st.session_state:
        sqlite = Sqlite()
        dados_usuario_form = sqlite.seleciona_usuario()

        if dados_usuario_form:
            gemini_chat = GeminiChat()
        else:
            gemini_chat = None
            st.error("Nenhum dado encontrado no banco de dados MAIN.")

        # Armazena a instância no session_state
        st.session_state["gemini_instance"] = gemini_chat

    # Inicializa a interface com a instância persistida
    interface = StreamlitInterface(gemini_instance=st.session_state["gemini_instance"])
    interface.iniciar()