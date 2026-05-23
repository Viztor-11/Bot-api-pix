# Discord Betting Bot

Bot de apostas para Discord integrado com Mercado Pago PIX.

## Funcionalidades

- Sistema de apostas:
  - 1v1
  - 2v2
  - 3v3
  - 4v4

- Integração com PIX Mercado Pago
- Criação automática de salas privadas
- Sistema de confirmação de moderador
- Confirmação de jogadores
- Timeout automático para pagamentos
- Sistema de logs
- Sistema de definição de vencedor

---

## Tecnologias

- Python
- discord.py
- Mercado Pago SDK
- Railway
- dotenv

---

## Instalação

Clone o projeto:

```bash
git clone https://github.com/Viztor-11/Bot-api-pix.git
```

Entre na pasta:

```bash
cd Bot-api-pix
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env`

```env
TOKEN=SEU_TOKEN_DISCORD
MP_ACCESS_TOKEN=SEU_TOKEN_MERCADO_PAGO
MOD_ROLE_ID=ID_DO_CARGO
LOG_CHANNEL_ID=ID_DO_CANAL
```

---

## Executar localmente

```bash
python main.py
```

---

## Hospedagem

O projeto pode ser hospedado usando:

- Railway
- Render
- VPS Linux

---

## Estrutura do projeto

```text
Bot-api-pix/
│
├── images/
├── services/
├── views/
├── utils/
│
├── main.py
├── config.py
├── data.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Preview

### Tela inicial

<img src="images/preview.png" width="700">

---

### Seleção de modo

<img src="images/modos.png" width="700">

---

### Escolha da plataforma

<img src="images/plataforma.png" width="700">

---

### Inserção do valor

<img src="images/valor.png" width="700">

---

### Nova aposta criada

<img src="images/aposta.png" width="700">

---

### Sala privada criada

<img src="images/sala.png" width="700">

---

### Pagamento PIX

<img src="images/qr.png" width="700">

---

### Resultado da partida

<img src="images/winner.png" width="700">

---

## Licença

Este projeto utiliza a licença MIT.