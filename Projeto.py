import streamlit as st
import google.generativeai as genai
import sqlite3
import json

class GeminiChat:

    def __init__(self):
        """Inicializa a configuração do Gemini."""
        self.sqlite = Sqlite()
        dados_usuario_form = self.sqlite.seleciona_usuario()
        if dados_usuario_form:
            self.nome_usuario_form = dados_usuario_form['nome']
            self.chave_api_form = dados_usuario_form['gemini_token']
        else:
            st.warning("Nenhum dado encontrado no banco de dados. Por favor, insira suas informações.")
            raise ValueError("Dados não encontrados no banco de dados para inicialização.")

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
        st.sidebar.write("Tire suas dúvidas e seja direto!")
        st.title("No que posso ajudar?")

        self.exibir_formulario_necessario()

        if st.session_state.get("formulario_preenchido", False):
            st.write("Agora você pode conversar com o Gemini!")
            self.handle_input()
            self.exibir_historico_chat()

    def exibir_formulario_necessario(self):
        if not self.sqlite.existe_usuario():
            with st.expander("Formulario"):
                with st.form("formulario"):
                    st.subheader("Insira seus dados")
                    self.nome_usuario_formulario = st.text_input("Nome:", placeholder="Digite seu nome")
                    self.chave_api_formulario = st.text_input("Chave API:", placeholder="Digite sua chave API", type="password")
                    botao = st.form_submit_button("Salvar")

                    if botao:
                        if not self.nome_usuario_formulario or not self.chave_api_formulario:
                            st.error("Preencha todos os campos antes de salvar!")
                            return
                        # Salva a chave API e o nome do usuário no banco de dados
                        self.sqlite.insira_usuario(self.nome_usuario_formulario, self.chave_api_formulario)
                        # Salva os dados do usuário no arquivo JSON
                        self.json_usuario.nome_usuario = self.nome_usuario_formulario
                        self.json_usuario.chave_api = self.chave_api_formulario
                        self.json_usuario.salvar_dados()
                        st.success("Dados salvos com sucesso!")
                        st.session_state.formulario_preenchido = True
        else:
            st.session_state.formulario_preenchido = True

    def exibir_historico_chat(self):
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        for mensagem in st.session_state.get("chat_history", []):
            if "user" in mensagem:
                st.markdown(f'<div class="user-message">{mensagem["user"]}</div>', unsafe_allow_html=True)
            elif "gemini" in mensagem:
                st.markdown(f'<div class="gemini-message">{mensagem["gemini"]}</div>', unsafe_allow_html=True)

    import streamlit as st

    def handle_input(self):
        """Gerencia a entrada do usuário no Streamlit."""

        def capturar_mensagem():
            mensagem = st.session_state.input_usuario
            st.session_state.chat_history.append({"user": mensagem})
            if self.gemini is None:
                st.error("Erro: A instância do Gemini ainda não foi iniciada.")
                return
            try:
                resposta_gemini = self.gemini.gerar_resposta(mensagem)
                st.session_state.chat_history.append({"gemini": resposta_gemini})
                self.total_tokens += len(mensagem.split()) + len(resposta_gemini.split())
                st.session_state["total_tokens"] = self.total_tokens
            except Exception as e:
                print(f"Erro ao gerar resposta: {e}")
            st.session_state.input_usuario = ""

        # Aplicar o estilo CSS para manter a caixa de texto fixa no rodapé
        st.markdown("""
            <style>
                /* Estilo para manter a caixa de mensagem fixa no rodapé */
                .stTextInput {
                    position: fixed; /* Fixa a posição no rodapé */
                    bottom: 65px; /* Garante que esteja no fundo */
                    max-width: 700px; /* Largura máxima */
                    width: 100%; /* Ajusta à largura total do container */
                    margin: 0 auto; /* Centraliza horizontalmente */
                } 
            </style>
        """, unsafe_allow_html=True)

        st.text_input("Digite sua mensagem:", placeholder="Digite aqui...", key="input_usuario",
                      on_change=capturar_mensagem)


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
                padding: 10px;
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

    # Seleciona o banco de dados
    def seleciona_usuario(self):
        self.cursor.execute("SELECT * FROM usuario")
        dados_usuario_form = self.cursor.fetchone()
        if dados_usuario_form:
            return {'nome': dados_usuario_form[0], 'gemini_token': dados_usuario_form[1]}
        else:
            return None

    # Verifica se o usuário existe
    def existe_usuario(self):
        self.cursor.execute("SELECT 1 FROM usuario LIMIT 1")
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
    try:
        gemini_instance = GeminiChat()
    except ValueError:
        gemini_instance = None

    interface = StreamlitInterface(gemini_instance)
    interface.iniciar()
