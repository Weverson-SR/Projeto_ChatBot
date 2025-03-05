# Chatbot Pessoal com Gemini API

Este projeto é um chatbot simples que utiliza a Gemini API para fornecer respostas diretas. Ele salva as informações do usuário em um banco de dados SQLite e em um arquivo `.json`, o que permite que o chatbot reconheça o usuário e recupere a chave API entre as sessões.

## Funcionalidades

- Cadastro do usuário com nome e chave API Gemini.
- Armazenamento das informações do usuário no banco de dados SQLite e no arquivo `.json`.
- Recuperação das informações do usuário entre as sessões.
- Integração com a Gemini API para fornecer respostas dinâmicas.

## Bibliotecas utilizadas

- `Streamlit`: Para a criação da interface do usuário.
- `Generative AI (genai)`: Para integração com a API do Gemini.
- `SQLite`: Para gerenciamento do banco de dados local.
- `JSON`: Para armazenamento e recuperação de dados do usuário.

## Descrição do Funcionamento

- Banco de Dados: O SQLite armazena permanentemente os dados do usuário (nome e chave API). O arquivo dados_usuario.json também guarda essas informações, permitindo que o chatbot se lembre do usuário entre sessões.

- Interação: O bot responde às mensagens do usuário por meio da API Gemini. A cada nova mensagem, o histórico de chat é atualizado.

- Interface: A interface é baseada em Streamlit, permitindo uma experiência simples no navegador.

## Como rodar

1. Faça o clone deste repositório em sua máquina:
   ```bash
   git clone https://github.com/Weverson-SR/Projeto_ChatBot

2. Instale as dependências necessárias:
   
         pip install -r requirements.txt

3. Execute o Streamlit com o seguinte comando:
   ```bash
   Inicie o streamlit com o comando: streamlit run app.py
   
   Se o aplicativo não abrir automaticamente, certifique-se de fornecer o caminho completo para o arquivo app.py, por exemplo:
   
   streamlit run /caminho/para/o/projeto/app.py (Lembre-se que o app é o nome de seu arquivo Python)
   
4. Após rodar o comando acima, o aplicativo será aberto em seu navegador. Se não abrir automaticamente, você pode acessá-lo via:
   ```bash
   http://localhost:8501
   
## Não se esqueça! Crie sua chave de API do Gemini

Antes de usar a aplicação, você precisa criar sua chave de API do Gemini. Siga as instruções da [Documentação oficial do Gemini API](https://ai.google.dev/gemini-api/docs/api-key?hl=pt-br)

1. Clique em "Conseguir uma chave da API Gemini no Google AI Studio".
2. Siga as instruções para criar sua chave de API.
3. Após gerar sua chave, copie e cole-a na aplicação quando solicitado.


## Melhorias futuras

- `NLP (Processamento de Linguagem Natural)`: Implementação de um sistema de captura de palavras-chave e contextos para tornar o chatbot mais responsivo e inteligente.


- Criação de uma interface gráfica utilizando `Tkinter`, `PyQt`, ou outras bibliotecas nativas do Python.
  
- Uma nova versão já está sendo feita: [Mentris](https://github.com/Weverson-SR/Mentris)

## Contribuição

Se você deseja contribuir para o projeto, fique à vontade para fazer um fork, enviar pull requests ou abrir issues com sugestões de melhorias.
