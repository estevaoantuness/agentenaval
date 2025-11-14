# 🎭 Prompt Management - Versionamento e Rollback

Guia para gerenciar, versionar e fazer rollback dos prompts do agente.

## 📁 Estrutura de Prompts

```
prompts/
├── v1.0/                      # Versão ativa
│   ├── system.txt             # Persona e instruções base
│   ├── triagem.txt            # Instruções de triagem (futuro)
│   ├── objecoes.txt           # Técnicas de contorno (futuro)
│   ├── agendamento.txt        # Coleta de dados (futuro)
│   └── metadata.json          # Metadados e histórico
├── v1.1/                      # Versão anterior
│   └── ...
└── current -> v1.0/           # Symlink para versão ativa
```

## 🔄 Como Versionar um Novo Prompt

### 1. Criar Nova Versão

```bash
# Copiar versão anterior
cp -r prompts/v1.0 prompts/v1.1

# Editar arquivos na v1.1
nano prompts/v1.1/system.txt
```

### 2. Atualizar Metadados

```bash
# prompts/v1.1/metadata.json
{
  "version": "v1.1",
  "description": "Melhorias em contorno de objeções",
  "created_at": "2024-01-16",
  "author": "seu-nome",
  "status": "staging",  # "active", "staging", "deprecated"
  "changes": [
    "Melhorado contorno de objeção sobre investimento",
    "Adicionada menção de ROI em 18-24 meses"
  ],
  "metrics": {
    "average_conversation_length": null,
    "conversion_rate": null,
    "average_response_time_ms": null,
    "cost_per_lead": null
  }
}
```

### 3. Testar Localmente

```bash
# Ativar versão de teste
export PROMPT_VERSION=v1.1

# Rodar testes E2E
pytest tests/e2e/ -v

# Se OK, fazer commit
git add prompts/v1.1/
git commit -m "Add prompt v1.1 with improved objection handling"
```

### 4. Ativar em Produção

Duas opções:

**Opção A: Variável de Ambiente (Recomendado)**

```bash
# No Railway:
# Settings → Variables → PROMPT_VERSION=v1.1
# Salvar e reaplicar (redeploy automático)
```

**Opção B: Symlink (Local)**

```bash
cd prompts
rm current
ln -s v1.1 current
git add current
git commit -m "Switch to prompt v1.1"
git push
```

## ⏮️ Como Fazer Rollback

### Rollback Rápido (via Variável)

```bash
# Railway painel:
# Settings → Variables
# Mudar PROMPT_VERSION=v1.0
# Salvar

# Em minutos, aplicação está usando v1.0 novamente
```

### Rollback via Git

```bash
# Se versão ruim foi commitada
git revert <commit-hash>
git push

# Railway faz deploy automático com versão anterior
```

## 🧪 A/B Testing de Prompts

Para testar duas versões em paralelo:

```python
# Em desenvolvimento (fazer depois)
# src/services/openai_agent.py

class OpenAIAgent:
    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,
        lead_id: Optional[str] = None,
        prompt_version: Optional[str] = None,
        ab_test: bool = False,
    ):
        """
        Se ab_test=True, distribuir:
        - 50% para v1.0
        - 50% para v1.1

        Registrar qual versão foi usada em cada conversa.
        """

        if ab_test:
            import random
            version = random.choice(["v1.0", "v1.1"])
        else:
            version = prompt_version or settings.prompt_version

        # ... resto do código
```

## 📊 Monitorar Performance de Prompts

### Métricas Importantes

```python
# metadata.json preenchido após 100 conversas
{
  "metrics": {
    "average_conversation_length": 4.2,  # mensagens por lead
    "conversion_rate": 0.65,              # agendamentos / leads
    "average_response_time_ms": 1200,     # latência OpenAI
    "cost_per_lead": 0.015,               # USD por lead
    "user_satisfaction": 4.2              # rating 1-5 (futuro)
  }
}
```

### Comparar Versões

```python
# Script para comparar performance (adicionar depois)
# scripts/compare_prompt_versions.py

from src.models.conversation import Conversation
from sqlalchemy import func

# Conversas por versão
v1_0_conversations = db.query(Conversation).filter(
    Conversation.prompt_version == "v1.0"
).all()

v1_1_conversations = db.query(Conversation).filter(
    Conversation.prompt_version == "v1.1"
).all()

# Calcular métricas
for version, conversations in [("v1.0", v1_0), ("v1.1", v1_1)]:
    avg_tokens = sum(c.tokens_total for c in conversations) / len(conversations)
    avg_latency = sum(c.tempo_resposta_ms for c in conversations) / len(conversations)
    print(f"{version}: {avg_tokens} tokens, {avg_latency}ms")
```

## 📝 Exemplos de Prompts

### v1.0 - Sistema Prompt

```
Você é um consultor de franquias experiente com 12+ anos de mercado.
Sua comunicação é em português brasileiro coloquial, acessível e sem jargão técnico.

Características:
- Empático, paciente e genuinamente interessado
- Nunca use emojis
- Objective: Agendar reunião com time de vendas
- Valide elegibilidade regional

Regiões elegíveis: RS, SC, PR, SP, RJ, MG, ES, GO, MT, MS, DF
Nordeste: registrar interesse para medir demanda futura
```

### v1.1 (Futuro) - Melhorias em Objeções

Adicionar seção específica:

```
Técnicas de contorno de objeção:

1. Preço alto:
   "Entendo a preocupação com investimento. A gente oferece um modelo que
   retorna em 18-24 meses porque [diferencial]. Quer saber mais?"

2. Falta de experiência:
   "Ótima pergunta! A gente treina completamente. Você não precisa ter
   experiência prévia, temos [programa de treinamento]. Já ajudamos [X]
   pessoas sem experiência a abrir suas franquias."

3. Região não elegível:
   "Sua região ainda está em fase de avaliação, mas vamos anotar seu interesse.
   Quando abrirmos ali, você será uma das primeiras a saber!"
```

## 🚀 Estratégia de Rollout

### Fase 1: Staging
- Versão em `prompts/v1.1/`
- `PROMPT_VERSION` não muda
- Testes E2E rodam com v1.1
- Se OK → Fase 2

### Fase 2: Canary (10% dos leads)
```python
# Implementar depois
def get_prompt_version(lead_id: str):
    if lead_id.endswith("0"):  # 10% dos IDs
        return "v1.1"
    return "v1.0"
```

### Fase 3: Full Rollout
- Mudar `PROMPT_VERSION=v1.1`
- Todos os novos leads usam v1.1
- Manter v1.0 em `prompts/v1.0/` para rollback

### Fase 4: Deprecate
- Arquivar versão antiga
- Mover `prompts/v1.0/` para `prompts/archived/v1.0/`

## 📋 Checklist para Nova Versão

- [ ] Criar diretório `prompts/v<version>/`
- [ ] Copiar arquivos da versão anterior
- [ ] Editar system.txt com melhorias
- [ ] Atualizar metadata.json com changelog
- [ ] Rodar testes E2E: `pytest tests/e2e/ -v`
- [ ] Fazer commit no Git
- [ ] Fazer PR para review
- [ ] Testar em staging (se infra disponível)
- [ ] Mergear para main
- [ ] Fazer deploy no Railway
- [ ] Monitorar logs por 24h
- [ ] Coletar métricas após 100+ conversas
- [ ] Comparar com versão anterior

## 🔍 Monitorar Prompts em Produção

```bash
# Ver qual versão está em uso
curl https://seu-projeto.up.railway.app/api/admin/usage | jq .

# Ver conversas recentes
curl -H "Authorization: Bearer token" \
  https://seu-projeto.up.railway.app/api/admin/leads/id | jq .conversations

# Análise de logs
railway logs -f | grep "prompt_version\|openai_response"
```

## 🎯 Próximas Melhorias (Fase 3)

1. **Tracking de Prompt**: Salvar `prompt_version` em cada conversa
2. **A/B Testing Automático**: Distribuição em paralelo
3. **Análise de Performance**: Dashboard com métricas por versão
4. **Sugestões de Otimização**: ML para identificar melhorias
5. **Cache de Prompts**: Economizar tokens reutilizando respostas similares

---

**Precisa de ajuda?** Ver [SETUP.md](./SETUP.md) ou abrir issue no GitHub
