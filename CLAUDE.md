# Pepper Root AI Agency — Proje İlerleme Kaydı

> Bu dosya Claude/Opus ile çalışırken ilerlemeyi takip etmek için kullanılır.
> Yeni bir sohbet başladığında bu dosyayı oku ve kaldığın yerden devam et.

---

## � KRİTİK: Proje Vizyonunu Anla!

**Mimari Doküman:** `/Users/emre/Desktop/Pepper_Root_AI_Agency_Mimari_Dokumani.md`

Bu proje **basit bir chatbot DEĞİL**. Ajantik (agent-first) bir sistemdir:

### Agent Ne Yapmalı:
- Hedef alır → Kendi planlar → Uygular → Adapte olur
- Aksiyon alır (pasif değil, aktif)
- Geçmiş assetleri BULUR ve KULLANIR
- "Dünkü video daha iyiydi" demek yerine → Dünkü videoyu GETİRİR ve sunar
- Hata durumunda alternatif yol dener, internetten veri çeker, editler

### @tag Sistemi (ÇOK ÖNEMLİ):
```
@emre = GERÇEK KİŞİ
  ├── Yüz → Referans FOTOĞRAF'tan (yüklenmiş)
  ├── Vücut şekli → Referans fotoğraftan
  ├── Karakter özellikleri → Kayıtlı bilgiler
  └── Tutarlılık → Her üretimde AYNI kişi
```

**Yanlış:** Sadece metin açıklaması ("uzun boylu, kahverengi saçlı")
**Doğru:** Referans fotoğraf + IP-Adapter/PuLID ile yüz tutarlılığı

---

## �📊 Genel Durum (29 Ocak 2026)

| Faz | Durum | Tamamlanma |
|-----|-------|------------|
| Gün 1-3: Altyapı | ✅ Tamamlandı | %100 |
| Gün 4-5: API Endpoint'leri | ✅ Tamamlandı | %100 |
| Gün 6-8: fal.ai Entegrasyonu | ✅ Tamamlandı | %100 |
| Gün 9-14: Agent Çekirdeği | 🔄 Devam Ediyor | %60 |
| Gün 15-21: Frontend | ⏳ Bekliyor | %0 |
| Gün 22-28: Entegrasyon | ⏳ Bekliyor | %0 |

---

## ✅ Tamamlanan Adımlar

### Gün 1-3: Altyapı (28 Ocak 2026)
- [x] Klasör yapısı, Git repo, GitHub bağlantısı
- [x] Docker + PostgreSQL container (pepperroot-db)
- [x] FastAPI + SQLAlchemy + Alembic
- [x] Tüm tablolar: User, Session, Message, Entity, GeneratedAsset, EntityAsset, Task, AgentState, Plugin

### Gün 4-5: API Endpoint'leri (28 Ocak 2026)
- [x] Session API: /api/v1/sessions/
- [x] Chat API: /api/v1/chat/
- [x] Swagger UI çalışıyor

### Gün 6-8: fal.ai Entegrasyonu (28 Ocak 2026)
- [x] fal_plugin.py oluşturuldu
- [x] /api/v1/generate/image (prompt'tan görsel)
- [x] /api/v1/generate/image-to-image (referans ile)

### Gün 9-12: Entity Sistemi (29 Ocak 2026)
- [x] entity_service.py - CRUD ve tag parsing
- [x] Agent araçları: create_character, create_location, get_entity, list_entities
- [x] Context injection (orchestrator.py)
- [x] Entity API: /api/v1/entities/
- [x] @tag ile görsel üretimi TEST EDİLDİ, ÇALIŞIYOR

---

## � ŞİMDİ YAPILACAK (Eksik Özellikler)

### Öncelik 1: Referans Görsel Sistemi
```
Kullanıcı: [FOTOĞRAF YÜKLER] "Bu Emre"
    ↓
Entity'ye referans görsel bağlanır
    ↓
@emre → Fotoğraftaki YÜZ kullanılarak üretim
```

Gerekli işler:
- [ ] Entity modeline `reference_images` alanı ekle (DB migration)
- [ ] Görsel yükleme endpoint'i
- [ ] fal.ai PuLID/IP-Adapter entegrasyonu (yüz tutarlılığı)
- [ ] Agent'ın referans görseli kullanması

### Öncelik 2: Video Üretimi
- [ ] fal.ai video modelleri entegrasyonu
- [ ] Video API endpoint'i

### Öncelik 3: Akıllı Agent Davranışı
- [ ] Geçmiş assetleri bulma ve getirme
- [ ] Karşılaştırma ve tercih sistemi
- [ ] State/Rollback

### Öncelik 4: Ek Yetenekler
- [ ] İnternetten veri çekme (web scraping)
- [ ] Görsel/video edit
- [ ] Çoklu adım görev planlama

---

## 📁 Proje Yapısı

```
PepperRootAiAgency/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # sessions, chat, entities, generate
│   │   ├── core/             # config, database
│   │   ├── models/           # SQLAlchemy modelleri
│   │   ├── schemas/          # Pydantic şemaları
│   │   ├── services/
│   │   │   ├── agent/        # orchestrator.py, tools.py
│   │   │   ├── llm/          # claude_service.py
│   │   │   ├── plugins/      # fal_plugin.py
│   │   │   └── entity_service.py
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
- Flux Schnell model görsel üretim için

---

## 🎯 SON DURUM (Bu Chat'te)

**Tamamlanan:**
- Entity sistemi ve @tag çalışıyor (metin bazlı)
- Agent tool calling çalışıyor
- Context injection çalışıyor

**Eksik (Kritik):**
- Referans görsel sistemi (fotoğraf yükleme + yüz tutarlılığı)
- Video üretimi
- Akıllı agent davranışı (geçmiş assetleri getirme)

**Sıradaki Adım:**
Entity'ye referans görsel ekleme ve fal.ai PuLID/IP-Adapter entegrasyonu

---

## ⚠️ PUSH BEKLİYOR

Uncommitted değişiklikler var:
- entity_service.py (yeni)
- entities.py (yeni)
- orchestrator.py (güncellendi)
- tools.py (güncellendi)
- chat.py (güncellendi)
- main.py (güncellendi)
- CLAUDE.md (güncellendi)

```bash
git add . && git commit -m "feat: Entity sistemi ve @tag referans özelliği" && git push
```
