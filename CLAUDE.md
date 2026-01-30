# Pepper Root AI Agency — Proje İlerleme Kaydı

> Bu dosya Claude/Opus ile çalışırken ilerlemeyi takip etmek için kullanılır.
> Yeni bir sohbet başladığında bu dosyayı oku ve kaldığın yerden devam et.

---

## 🚨 KRİTİK: Proje Vizyonunu Anla!

**Mimari Doküman:** `/Users/emre/Desktop/Pepper_Root_AI_Agency_Mimari_Dokumani.md`

Bu proje **basit bir chatbot DEĞİL**. Ajantik (agent-first) bir sistemdir:

### Agent Ne Yapmalı:
- Hedef alır → Kendi planlar → Uygular → Adapte olur
- Aksiyon alır (pasif değil, aktif)
- Geçmiş assetleri BULUR ve KULLANIR ✅
- "Dünkü video daha iyiydi" demek yerine → Dünkü videoyu GETİRİR ve sunar ✅
- Hata durumunda alternatif yol dener, internetten veri çeker, editler

### @tag Sistemi (ÇOK ÖNEMLİ):
```
@johny = KARAKTER
  ├── Yüz → Referans FOTOĞRAF'tan (Nano Banana + Face Swap)
  ├── Tutarlılık → Her üretimde AYNI yüz
  ├── Video → Kling 2.5 Turbo Pro ile
  └── Referans → reference_image_url alanında saklanır
```

---

## 📊 Genel Durum (30 Ocak 2026)

| Faz | Durum | Tamamlanma |
|-----|-------|------------|
| Hafta 1: Altyapı | ✅ Tamamlandı | %100 |
| Hafta 2: Agent + Entity + Referans + Video | ✅ Tamamlandı | %100 |
| Hafta 3: Akıllı Agent + Frontend | 🔄 Devam Ediyor | %30 |
| Hafta 4: Entegrasyon + Deploy | ⏳ Bekliyor | %0 |

---

## ✅ Tamamlanan Adımlar

### Hafta 1: Altyapı (28 Ocak)
- [x] Klasör yapısı, Git repo, GitHub bağlantısı
- [x] Docker + PostgreSQL container (pepperroot-db)
- [x] FastAPI + SQLAlchemy + Alembic
- [x] Tüm tablolar: User, Session, Message, Entity, GeneratedAsset, Task, AgentState, Plugin

### Hafta 2: Agent Çekirdeği (28-29 Ocak)
- [x] Claude adapter (claude_service.py)
- [x] Agent Orchestrator (orchestrator.py)
- [x] Tool calling sistemi (tools.py)
- [x] Entity sistemi: create_character, create_location, get_entity, list_entities

### Hafta 2: Referans Görsel Sistemi (29-30 Ocak)
- [x] reference_image_url Entity alanı
- [x] /api/v1/upload endpoint'i
- [x] fal.ai Nano Banana Pro + Face Swap entegrasyonu
- [x] 25+ fal.ai modeli entegre edildi (fal_models.py)
- [x] Akıllı model seçici (model_selector.py)

### Hafta 2: Video Üretimi (30 Ocak)
- [x] Kling 2.5 Turbo Pro entegrasyonu
- [x] Image-to-Video desteği
- [x] generate_video agent aracı

### Hafta 3: Akıllı Agent Davranışları (30 Ocak)
- [x] Asset kaydetme sistemi (asset_service.py)
- [x] get_past_assets → Geçmiş üretimleri getir
- [x] mark_favorite → Beğeni işaretle
- [x] undo_last → Önceki versiyona dön
- [x] is_favorite, parent_asset_id DB alanları

---

## 🎯 ŞİMDİ YAPILACAK

### Öncelik 1: Frontend
- [ ] Next.js kurulumu
- [ ] Chat UI (sol panel)
- [ ] Asset Panel (sağ panel grid)
- [ ] Görsel yükleme UI (drag & drop)

### Öncelik 2: İnternetten Veri Çekme
- [ ] Web scraping plugin
- [ ] Referans arama ("Samsung TV" → İnternetten bul)
- [ ] Edit entegrasyonu

### Öncelik 3: Auth + Login
- [ ] Google OAuth
- [ ] JWT token
- [ ] Session yönetimi

---

## 📁 Proje Yapısı

```
PepperRootAiAgency/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # sessions, chat, entities, generate, upload
│   │   ├── core/             # config, database
│   │   ├── models/           # SQLAlchemy modelleri
│   │   ├── schemas/          # Pydantic şemaları
│   │   ├── services/
│   │   │   ├── agent/        # orchestrator.py, tools.py
│   │   │   ├── llm/          # claude_service.py
│   │   │   ├── plugins/      # fal_plugin.py, fal_models.py, model_selector.py
│   │   │   ├── entity_service.py
│   │   │   └── asset_service.py  ← YENİ
│   │   └── main.py
│   ├── alembic/
│   └── requirements.txt
├── frontend/                 # Next.js (henüz yapılmadı)
└── README.md
```

---

## 🔑 Komutlar

```bash
# Backend çalıştır
cd /Users/emre/PepperRootAiAgency/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# PostgreSQL container başlat
docker start pepperroot-db

# Migration yap
alembic revision --autogenerate -m "açıklama"
alembic upgrade head

# Git push
git add . && git commit -m "mesaj" && git push
```

### URL'ler
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Veritabanı
- Container: pepperroot-db
- User/Password: postgres/postgres
- Database: pepperroot
- Port: 5432

---

## 📝 Teknik Notlar

- Python 3.14 kullanılıyor
- Claude Sonnet 4 modeli (claude-sonnet-4-20250514)
- fal-client v0.12.0
- Modeller: Nano Banana Pro, Kling 2.5 Turbo Pro, Topaz, Bria RMBG

---

## 🎯 SON DURUM (30 Ocak 2026)

**Tamamlanan:**
- Kapsamlı fal.ai entegrasyonu (25+ model)
- Yüz tutarlılığı (Nano Banana + Face Swap)
- Video üretimi (Kling 2.5)
- Akıllı agent davranışları (geçmiş assetler, favoriler, undo)

**Sıradaki Adım:**
Frontend geliştirmesi veya kullanıcının belirleyeceği öncelikler

---

## ✅ SON COMMIT

```
f73a64b - feat: akıllı agent davranışları (30 Ocak 2026)
834234f - feat: kapsamlı fal.ai plugin sistemi (30 Ocak 2026)
0ec054b - feat: Entity sistemi ve @tag referans özelliği (29 Ocak 2026)
```
