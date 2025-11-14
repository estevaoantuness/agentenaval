# 🚀 Auto-Deploy Configuration - Railway

Guia para configurar deployments automáticos do GitHub para Railway.

## ✅ Status Atual

- ✅ Arquivo `railway.json` criado e commitado
- ✅ Dockerfile presente
- ✅ GitHub Actions CI/CD configurado
- ⏳ Você precisa ativar no Railway Dashboard

---

## 🔧 Ativar Auto-Deploy no Railway

### Step 1: Acessar Railway Dashboard

1. Ir para: https://railway.app
2. Fazer login
3. Selecionar projeto **agentenaval**

### Step 2: Conectar GitHub (Se Não Estiver)

1. Clicar no serviço web **agentenaval-production**
2. Ir para **Settings** (aba)
3. Procurar por **"GitHub"** ou **"Source"**
4. Se não conectado:
   - Clicar **"Connect GitHub"**
   - Selecionar repositório: `estevaoantuness/agentenaval`
   - Autorizar Railway no GitHub

### Step 3: Ativar Automatic Deployments

**Opção A: Via Railway Dashboard**

1. No serviço web, ir para **Deployments**
2. Procurar por **"Automatic Deployments"** ou **"Auto Deploy"**
3. Mudar para **"Enabled"** ou **"On"**
4. Confirmar que está apontando para branch **`main`**

**Opção B: Ver Configuração Atual**

No serviço web → **Settings** → **Deploy**:
- [ ] Source: GitHub (conectado)
- [ ] Branch: `main`
- [ ] Auto Deploy: **Enabled**

### Step 4: Configurar GitHub Integration (Se Necessário)

1. No serviço web → **Settings**
2. Procurar por **"GitHub Integration"**
3. Confirmar:
   - Repository: `estevaoantuness/agentenaval`
   - Branch: `main`
   - Automatic Deployments: **ON**

---

## 🔄 Como Funciona

Após ativar, cada push no GitHub dispara automaticamente:

```
1. Push no GitHub (main branch)
   ↓
2. GitHub envia webhook para Railway
   ↓
3. Railway detecta novo commit
   ↓
4. Railway builda Dockerfile
   ↓
5. Railway roda migrations (alembic)
   ↓
6. Railway inicia app com Gunicorn
   ↓
7. Health check passa
   ↓
8. Novo deploy online! 🎉
```

---

## 📊 Monitorar Deployments

### Via Railway Dashboard

1. Serviço web → **Deployments**
2. Ver histórico de deployments:
   - ✅ Successful (verde)
   - ❌ Failed (vermelho)

### Ver Logs em Tempo Real

1. Serviço web → **Logs**
2. Acompanhar build:
   ```
   [Build] Starting build...
   [Build] Installing dependencies...
   [Build] Running migrations...
   [Build] Starting application...
   [Build] ✅ Build successful
   ```

---

## 🧪 Testar Auto-Deploy

Faça uma mudança simples e push:

```bash
cd /tmp/agentenaval

# Fazer uma mudança pequena (ex: comentário)
echo "# Test auto-deploy" >> README.md

# Commit e push
git add README.md
git commit -m "Test auto-deploy"
git push origin main
```

**Então:**
1. Ir para Railway Dashboard
2. Ver novo deployment aparecer em **Deployments**
3. Acompanhar logs
4. Esperar status mudar para ✅ **Successful**

---

## ⚠️ Troubleshooting

### Deploy falha após push

**Verificar logs:**
1. Railway → Deployments → Clicar no deploy falhado
2. Ver section **"Build Logs"**
3. Procurar por erro (linha vermelha)

**Causas comuns:**
- Variável de ambiente faltando
- Erro no requirements.txt (pacote não existe)
- Erro na sintaxe Python
- Migrations falhando

### Deploy não dispara automaticamente

**Solução:**
1. Verificar branch é `main` (não `develop` ou outro)
2. Verificar GitHub está conectado em Railway
3. Desconectar e reconectar:
   - Settings → GitHub → Disconnect
   - Aguardar 1 minuto
   - Conectar novamente

### Como fazer manual push se auto-deploy falhar

```bash
# Força re-deploy do último commit
railway redeploy

# Ou via Dashboard:
# Deployments → Clicar no deploy anterior → "Redeploy"
```

---

## 🔐 Segurança

- ✅ Railway não tem acesso à suas credenciais de GitHub
- ✅ Apenas lê commits da branch conectada
- ✅ Variáveis de ambiente protegidas no Railway
- ✅ Cada deploy em container isolado

---

## 📈 Próximas Melhorias (Futuro)

1. **Deploy Staging**: Push em `develop` faz deploy em staging.railway.app
2. **Notifications**: Alertas no Slack/Email quando deploy falha
3. **Rollback Automático**: Se health check falha, volta versão anterior
4. **Preview Deployments**: PRs disparam deploy em URL temporária

---

**Pronto!** Agora cada `git push origin main` dispara um novo deploy automaticamente! 🚀
