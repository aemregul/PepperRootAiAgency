---
description: Branch oluştur, test et, deploy et (Railway + Vercel)
---

# Deploy Workflow

> ⚠️ `main` branch'a direkt push YASAK. Her değişiklik branch üzerinden yapılır.

## 1. Yeni Branch Oluştur

Branch isimlendirme: `fix/bug-adi`, `feat/ozellik-adi`, `hotfix/acil-duzeltme`

```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency && git checkout -b feat/yeni-ozellik
```

## 2. Değişiklikleri Yap ve Commit Et

```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency && git add -A && git commit -m "feat: açıklayıcı commit mesajı"
```

## 3. Branch'ı Push Et

```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency && git push -u origin HEAD
```

## 4. Lokal Test Kontrolleri

Backend testi:
// turbo
```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency/backend && source venv/bin/activate && python -c "import app.main; print('✅ Backend import OK')"
```

Frontend build testi:
// turbo
```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency/frontend && npm run build
```

## 5. Vercel Preview Deploy (Frontend)

Vercel, push edilen branch'ı otomatik preview deploy olarak yayınlar.
- Vercel dashboard'unda preview URL'i kontrol et
- Preview ortamında test et

## 6. Railway Deploy (Backend)

Railway, GitHub bağlantısı varsa branch push'ta otomatik deploy eder.
- Railway dashboard'unda deploy durumunu kontrol et
- Backend health check: `curl https://pepperrootaiagency-production.up.railway.app/api/health`

## 7. Test Başarılıysa → Main'e Merge

```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency && git checkout main && git pull origin main && git merge feat/yeni-ozellik && git push origin main
```

## 8. Branch Temizliği

```bash
cd /Users/emre/.codex/worktrees/2795/PepperRootAiAgency && git branch -d feat/yeni-ozellik && git push origin --delete feat/yeni-ozellik
```

## Canlı URL'ler

| Ortam     | Frontend                                  | Backend                                               |
| --------- | ----------------------------------------- | ----------------------------------------------------- |
| Canlı     | https://pepper-root-ai-agency.vercel.app  | https://pepperrootaiagency-production.up.railway.app  |
