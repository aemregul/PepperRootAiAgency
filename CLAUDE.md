# Pepper Root AI Agency — Proje İlerleme Kaydı

> Bu dosya Claude/Opus ile çalışırken ilerlemeyi takip etmek için kullanılır.
> Yeni bir sohbet başladığında bu dosyayı oku ve kaldığın yerden devam et.

---

## 📊 Genel Durum

| Faz | Durum | Tamamlanma |
|-----|-------|------------|
| Gün 1-3: Altyapı | ✅ Tamamlandı | %100 |
| Gün 4-5: API Endpoint'leri | ✅ Tamamlandı | %100 |
| Gün 6-8: fal.ai Entegrasyonu | ✅ Tamamlandı | %100 |
| Gün 9-14: Agent Çekirdeği | 🔄 Sırada | %0 |
| Gün 15-21: Frontend | ⏳ Bekliyor | %0 |
| Gün 22-28: Entegrasyon | ⏳ Bekliyor | %0 |

---

## ✅ Tamamlanan Adımlar

### Gün 1: Proje İskeleti (28 Ocak 2026)
- [x] Klasör yapısı oluşturuldu
- [x] Git repo başlatıldı
- [x] GitHub'a bağlandı: `aemregul/PepperRootAiAgency`
- [x] .gitignore ve README.md oluşturuldu

### Gün 2-3: Veritabanı (28 Ocak 2026)
- [x] Docker Desktop kuruldu
- [x] PostgreSQL container çalışıyor: `pepperroot-db`
- [x] Python sanal ortam kuruldu (venv)
- [x] requirements.txt paketleri yüklendi
- [x] FastAPI temel uygulama çalışıyor
- [x] SQLAlchemy modelleri oluşturuldu:
  - User, Session, Message, Entity, GeneratedAsset, EntityAsset, Task, AgentState, Plugin
- [x] Alembic migration yapıldı
- [x] Tablolar veritabanında oluşturuldu

### Gün 4-5: API Endpoint'leri (28 Ocak 2026)
- [x] Pydantic şemaları: `app/schemas/schemas.py`
- [x] Session API: `app/api/routes/sessions.py`
  - POST /api/v1/sessions/ (oluştur)
  - GET /api/v1/sessions/ (listele)
  - GET /api/v1/sessions/{id} (detay)
  - DELETE /api/v1/sessions/{id} (sil)
- [x] Chat API: `app/api/routes/chat.py`
  - POST /api/v1/chat/ (mesaj gönder)
- [x] Swagger UI test edildi, çalışıyor

---

### Gün 6-8: fal.ai Entegrasyonu (28 Ocak 2026)
- [x] fal.ai hesabı açıldı
- [x] API key alındı
- [x] .env dosyasına FAL_KEY eklendi
- [x] fal_client paketi kuruldu (v0.12.0)
- [x] fal_plugin.py oluşturuldu: `app/services/plugins/fal_plugin.py`
- [x] Görsel üretme endpoint'leri eklendi: `app/api/routes/generate.py`
  - POST /api/v1/generate/image (prompt'tan görsel)
  - POST /api/v1/generate/image-to-image (referans ile)
- [x] Swagger UI ile test edildi, çalışıyor

---

## 🔄 Şu An Yapılacak

### Gün 9-14: Agent Çekirdeği
- [ ] LLM servisi (Anthropic Claude)
- [ ] Agent temel yapısı
- [ ] Entity çıkarımı
- [ ] @tag sistemi
- [ ] Görev orchestration

---

## 📁 Proje Yapısı

```
PepperRootAiAgency/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoint'leri
│   │   ├── core/             # Config, database
│   │   ├── models/           # SQLAlchemy modelleri
│   │   ├── schemas/          # Pydantic şemaları
│   │   ├── services/         # İş mantığı
│   │   └── main.py           # FastAPI uygulaması
│   ├── alembic/              # Migration dosyaları
│   ├── venv/                 # Python sanal ortam
│   └── requirements.txt
├── frontend/                 # Next.js (henüz yapılmadı)
├── docs/
└── README.md
```

---

## 🔑 Önemli Bilgiler

### Komutlar
```bash
# Backend çalıştır
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# PostgreSQL container başlat
docker start pepperroot-db

# Migration yap
alembic revision --autogenerate -m "açıklama"
alembic upgrade head
```

### URL'ler
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Veritabanı
- Container: pepperroot-db
- User: postgres
- Password: postgres
- Database: pepperroot
- Port: 5432

---

## 📝 Notlar

- Python 3.14 kullanılıyor (çok yeni, bazı paketler uyumsuz olabilir)
- `email-validator` paketi ayrıca kuruldu
- `greenlet` paketi ayrıca kuruldu

---

## 🎯 Proje Hedefi

Web tabanlı, ajantik AI yaratıcı platform:
- Kullanıcı doğal dilde komut verir
- Agent planlar ve görevleri yürütür
- fal.ai ile görsel/video üretir
- Entity sistemi ile karakterleri/mekanları hatırlar
- @tag ile referans verebilirsin
