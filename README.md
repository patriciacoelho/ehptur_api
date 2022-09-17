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

#### Obs.: Para um pleno funcionamento certifique-se de configurar as variáveis de ambiente do arquivo `.env` (existe um arquivo de exemplo `.env.example`)
