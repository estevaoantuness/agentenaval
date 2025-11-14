# 📡 API Reference - Agente Naval

Documentação completa dos endpoints da API.

## 🔐 Autenticação

Todos os endpoints requerem autenticação via Bearer Token no header:

```http
Authorization: Bearer seu-webhook-secret
```

Gerar token seguro:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📍 Base URL

```
Desenvolvimento:  http://localhost:5000
Produção:        https://seu-projeto.up.railway.app
```

## 🏥 Health Check

### GET `/health`

Verifica saúde da aplicação e banco de dados.

**Sem autenticação requerida**

```bash
curl http://localhost:5000/health
```

**Response 200 OK:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000",
  "version": "1.0.0",
  "database": "connected"
}
```

**Status possíveis:**
- `healthy`: Tudo funcionando
- `degraded`: Banco de dados offline
- `unhealthy`: Erro crítico

## 📊 Status da Aplicação

### GET `/status`

Status geral da aplicação.

**Autenticação:** Requerida (Bearer Token)

```bash
curl -H "Authorization: Bearer seu-webhook-secret" \
  http://localhost:5000/status
```

**Response 200 OK:**

```json
{
  "status": "operational",
  "environment": "production",
  "timestamp": "2024-01-15T10:30:00.000000",
  "version": "1.0.0"
}
```

## 📨 Webhook da Evolution API

### POST `/api/webhooks/evolution`

Recebe mensagens da Evolution API (WhatsApp).

**Autenticação:** Bearer Token obrigatório

**Request:**

```bash
curl -X POST http://localhost:5000/api/webhooks/evolution \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu-webhook-secret" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "instanceId": "sua-instance-id",
      "messages": [
        {
          "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": false,
            "id": "BAE5123456789"
          },
          "message": {
            "conversation": "Olá, gostaria de abrir uma franquia"
          },
          "messageTimestamp": 1699999999
        }
      ]
    }
  }'
```

**Response 200 OK:**

```json
{
  "status": "ok"
}
```

**Response 401 Unauthorized:**

```json
{
  "error": "unauthorized",
  "code": 401,
  "message": "Token de autenticação inválido",
  "timestamp": "2024-01-15T10:30:00.000000",
  "request_id": "uuid-here"
}
```

**Webhook Payload Schema:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `event` | string | Tipo de evento (`messages.upsert`) |
| `data.instanceId` | string | ID da instância Evolution API |
| `data.messages[].key.remoteJid` | string | JID do WhatsApp (phone@s.whatsapp.net) |
| `data.messages[].key.fromMe` | boolean | True se mensagem enviada por nós |
| `data.messages[].message.conversation` | string | Texto da mensagem |

### GET `/api/webhooks/evolution`

Verifica webhook (usado na configuração).

**Resposta automática 200 OK**

## 📈 Admin - Estatísticas

### GET `/api/admin/usage`

Retorna estatísticas de uso da aplicação.

**Autenticação:** Bearer Token obrigatório

```bash
curl -H "Authorization: Bearer seu-webhook-secret" \
  http://localhost:5000/api/admin/usage
```

**Response 200 OK:**

```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "leads": {
    "total": 45,
    "new_24h": 3,
    "by_status": {
      "novo": 5,
      "em_triagem": 8,
      "agendado": 20,
      "não_elegível": 12
    }
  },
  "conversations": {
    "total": 180,
    "total_tokens": 45000,
    "total_cost_usd": 6.75,
    "average_latency_ms": 1250
  },
  "schedulings": {
    "total": 20,
    "upcoming": 15
  },
  "limits": {
    "cost_limit_monthly": 20,
    "cost_current": 6.75,
    "cost_percentage": 33.7
  }
}
```

## 📋 Admin - Listar Leads

### GET `/api/admin/leads`

Lista todos os leads com filtros opcionais.

**Autenticação:** Bearer Token obrigatório

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `status` | string | - | Filtrar por status (novo, em_triagem, agendado, etc) |
| `limit` | integer | 20 | Número máximo de resultados |
| `offset` | integer | 0 | Offset para paginação |

**Request:**

```bash
curl -H "Authorization: Bearer seu-webhook-secret" \
  "http://localhost:5000/api/admin/leads?status=agendado&limit=10&offset=0"
```

**Response 200 OK:**

```json
{
  "total": 20,
  "limit": 10,
  "offset": 0,
  "leads": [
    {
      "id": "uuid-here",
      "phone": "5511999999999",
      "nome": "João Silva",
      "email": "joao@empresa.com",
      "regiao": "SP",
      "cidade": "São Paulo",
      "interesse": "Abrir franquia em São Paulo",
      "disponibilidade": "Sábado à tarde",
      "status": "agendado",
      "elegivel": true,
      "tentativas_follow_up": 0,
      "data_ultimo_follow_up": null,
      "data_proximo_follow_up": "2024-01-16T10:30:00.000000",
      "data_reuniao_preferencial": "2024-01-20T14:30:00.000000",
      "horario_preferencial": "14:30",
      "data_contato": "2024-01-15T08:00:00.000000",
      "data_ultima_interacao": "2024-01-15T10:30:00.000000",
      "created_at": "2024-01-15T08:00:00.000000",
      "updated_at": "2024-01-15T10:30:00.000000"
    }
  ]
}
```

## 👤 Admin - Detalhe do Lead

### GET `/api/admin/leads/{lead_id}`

Retorna detalhes completos de um lead incluindo conversas e agendamentos.

**Autenticação:** Bearer Token obrigatório

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `lead_id` | uuid | ID do lead |

**Request:**

```bash
curl -H "Authorization: Bearer seu-webhook-secret" \
  http://localhost:5000/api/admin/leads/550e8400-e29b-41d4-a716-446655440000
```

**Response 200 OK:**

```json
{
  "lead": {
    "id": "uuid-here",
    "phone": "5511999999999",
    "nome": "João Silva",
    "status": "agendado",
    "elegivel": true,
    "created_at": "2024-01-15T08:00:00.000000"
  },
  "conversations": [
    {
      "id": "uuid-here",
      "lead_id": "uuid-here",
      "mensagem_entrada": "Olá, gostaria de abrir uma franquia",
      "mensagem_saida": "Olá! É um prazer ouvir que se interessou...",
      "tokens_input": 15,
      "tokens_output": 30,
      "tokens_total": 45,
      "custo_estimado": 9,
      "tempo_resposta_ms": 1250,
      "timestamp": "2024-01-15T08:05:00.000000"
    }
  ],
  "schedulings": [
    {
      "id": "uuid-here",
      "lead_id": "uuid-here",
      "data_reuniao": "2024-01-20T14:30:00.000000",
      "status": "agendado",
      "vendedor_atribuido": "Carlos Silva",
      "vendedor_email": "carlos@empresa.com",
      "notas": "Cliente interessado em região de São Paulo",
      "created_at": "2024-01-15T10:30:00.000000"
    }
  ]
}
```

## 📊 Estatísticas por Status

Estados possíveis de um lead:

```
novo                    → Lead acabou de chegar
↓
em_triagem              → Agente está coletando informações
↓
aguardando_resposta     → Aguardando resposta do lead
↓
agendado                → Reunião agendada com vendedor
└─→ sem_resposta        → Lead não respondeu após 2h
    ↓
    recuperando         → Tentando reengajar
    ↓
    inativo             → Desistido após 7 dias

não_elegível            → Região não elegível (Nordeste)
```

## 🔄 Exemplo de Fluxo Completo

### 1. Lead envia mensagem (webhook)

```
Evolution API envia:
POST /api/webhooks/evolution
{
  "event": "messages.upsert",
  "data": {
    "messages": [{
      "remoteJid": "5511999999999@s.whatsapp.net",
      "message": {"conversation": "Oi, gostaria de abrir franquia"}
    }]
  }
}
```

### 2. Sistema processa

```
- Cria lead com status: novo
- Muda para: em_triagem
- Chama OpenAI
- Salva conversa
- Marca para follow-up em 2h
```

### 3. Admin verifica

```
GET /api/admin/leads?status=em_triagem
GET /api/admin/leads/lead-id (ver detalhes)
GET /api/admin/usage (acompanhar custos)
```

## 🚨 Códigos de Erro

| Código | Erro | Descrição |
|--------|------|-----------|
| 200 | OK | Sucesso |
| 400 | validation_error | Payload inválido |
| 401 | unauthorized | Token inválido ou faltando |
| 404 | not_found | Recurso não encontrado |
| 429 | rate_limit | Muitas requisições (>30/min por phone) |
| 500 | internal_error | Erro do servidor |

## 🔗 Rate Limiting

```
30 requisições por minuto por telefone
100 requisições por minuto globalmente
```

Resposta quando atingido:

```http
HTTP/1.1 429 Too Many Requests

{
  "error": "rate_limit",
  "code": 429,
  "message": "Limite de requisições atingido",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

**Precisa de mais informações?** Ver [SETUP.md](./SETUP.md) ou [TESTING.md](./TESTING.md)
