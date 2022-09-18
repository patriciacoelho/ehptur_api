### API

## Pré-requisitos

- Um servidor mongo configurado localmente ou no Mongo Atlas;
- Python 3.6 ou superior (com pip e venv)

## Executando o projeto

Primeiro crie e ative o ambiente virtual com o `venv`

```bash
python3 -m venv venv
source venv/bin/activate
```

- Para instalar as dependências você pode executar

```bash
make install
```

- Para rodar a aplicação você pode executar

```bash
make run
```

- Para rodar a aplicação em **modo de desenvolvimento** você pode executar o comando a seguir, mas antes certifique-se de executar `pip install pyopenssl`, para instalar esse pacote que permite que se acesse por HTTPS (`https://127.0.0.1:5000`) necessário para a autenticação pelo Google oAuth2

```bash
make dev
```


#### Obs.: Para um pleno funcionamento certifique-se de configurar as variáveis de ambiente do arquivo `.env` (existe um arquivo de exemplo `.env.example`) e de ter no diretório `api` o arquivo `client_secret.json` disponibilizado no Google Console ao registrar a credencial para usar a autenticação pelo Google

