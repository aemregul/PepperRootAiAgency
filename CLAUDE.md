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
- Hata durumunda alternatif yol dener, internetten veri çeker, editler ✅
- Ürettiği görseli ANALIZ eder, kalite kontrolü yapar ✅
- Büyük işleri parçalara ayırır (roadmap) ✅
- **YENİ:** İnternette arama yapar, web sayfası okur ✅
- **YENİ:** 3x3 Grid oluşturur (9 açı/storyboard) ✅

### @tag Sistemi (ÇOK ÖNEMLİ):
```
@johny = KARAKTER
  ├── Yüz → Referans FOTOĞRAF'tan (Nano Banana + Face Swap)
  ├── Tutarlılık → Her üretimde AYNI yüz
  ├── Video → Kling 3.0 Pro ile
  └── Referans → reference_image_url alanında saklanır

@nike = MARKA ⭐ YENİ
  ├── Renkler → primary/secondary/accent
  ├── Slogan → "Just Do It" vb.
  ├── Sosyal Medya → Instagram, Twitter
  └── research_brand ile web'den otomatik tara
```

---

## 📊 Genel Durum (4 Şubat 2026 - 22:15)

| Faz | Durum | Tamamlanma |
|-----|-------|------------|
| Hafta 1: Altyapı | ✅ Tamamlandı | %100 |
| Hafta 2: Agent + Entity + Referans + Video | ✅ Tamamlandı | %100 |
| Hafta 3: Akıllı Agent + Plugin + Vision | ✅ Tamamlandı | %100 |
| Hafta 4: Frontend + Auth + Multi-User | ✅ Tamamlandı | %100 |
| Hafta 5: Performance + LLM Migration | ✅ Tamamlandı | %100 |
| Hafta 6: Polish + Admin Panel | ✅ Tamamlandı | %100 |

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

### Hafta 3: Plugin Sistemi (30 Ocak) ⭐ YENİ
- [x] PluginBase abstract class (plugin_base.py)
- [x] Plugin Loader dinamik yükleme (plugin_loader.py)
- [x] FalPluginV2 (fal_plugin_v2.py)
- [x] Admin API endpoints (/api/v1/plugins/)
- [x] Enable/disable, configure, health check

### Hafta 3: Görsel Muhakeme - Claude Vision (30 Ocak) ⭐ YENİ
- [x] analyze_image tool - Kalite kontrolü, yüz tespiti
- [x] compare_images tool - İki görseli karşılaştır
- [x] Agent artık ürettiği görseli analiz edebilir

### Hafta 3: Roadmap/Task Sistemi (30 Ocak) ⭐ YENİ
- [x] task_service.py - Çoklu adım görev yönetimi
- [x] create_roadmap tool - Büyük işleri parçalara ayır
- [x] get_roadmap_progress tool - İlerleme takibi
- [x] Alt görev sistemi, otomatik tamamlama

---

## 🎯 ŞİMDİ YAPILACAK

### ✅ Frontend TAMAMLANDI!
- [x] Next.js kurulumu
- [x] Chat UI (sol panel)
- [x] Asset Panel (sağ panel grid)
- [x] Plugin bölümü sidebar'da
- [x] Settings modal (tema toggle)
- [x] Dark mode varsayılan
- [x] Prompt çevirisi (tüm diller → İngilizce)
- [x] Gelişmiş karakter özellikleri

### ✅ Auth Sistemi TAMAMLANDI! (1 Şubat)
- [x] Google OAuth 2.0 entegrasyonu
- [x] JWT token (Argon2 hash)
- [x] Login/Register sayfası (modern UI)
- [x] Multi-user izolasyonu (her user kendi verisini görür)
- [x] Logout sistemi (sidebar dropdown)
- [x] Auth middleware (protected routes)

### ✅ Veri Güvenliği TAMAMLANDI! (1 Şubat)
- [x] Auto-save draft (localStorage 500ms debounce)
- [x] Offline message queue
- [x] Error recovery (başarısız mesajları kaydet)
- [x] Offline status banner

### ✅ UI Polish TAMAMLANDI! (1 Şubat)
- [x] Image Lightbox Modal (tam ekran görsel inceleme)
- [x] Navigation arrows (prev/next)
- [x] Download button
- [x] Favorite toggle

### ✅ OpenAI GPT-4o Migration (3 Şubat) ⭐ YENİ
- [x] OpenAI API entegrasyonu (config.py, orchestrator.py)
- [x] GPT-4o primary LLM olarak aktif
- [x] Tool calling OpenAI formatına convert edildi
- [x] Claude'dan GPT-4o'ya geçiş tamamlandı (hız optimizasyonu)

### ✅ Redis Cache Entegrasyonu (3 Şubat) ⭐ YENİ
- [x] RedisCache service (app/core/cache.py)
- [x] Session caching (1 saat TTL)
- [x] Entity caching (30 dk TTL) - ~100x hızlanma
- [x] AI Response memoization (24 saat TTL)
- [x] Rate limiting (sliding window)
- [x] Graceful degradation (Redis yoksa DB fallback)

### ✅ Global Wardrobe (3 Şubat) ⭐ YENİ
- [x] Save-to-Wardrobe butonu (Shirt icon)
- [x] Cross-session entity persistence
- [x] Entity CASCADE delete fix (proje silinince entity kalır)

### ✅ Login/Auth İyileştirmeleri (3-4 Şubat)
- [x] Password visibility toggle (Eye/EyeOff)
- [x] Double-click bug fix
- [x] OAuth error handling iyileştirmesi
- [x] System status endpoint (/api/v1/system/status)
- [x] Backend warm-up (lifespan handler)
- [x] Login sayfası sadeleştirildi - Sadece Google OAuth (4 Şubat)
- [x] Header buton birleştirildi (Giriş Yap + Ücretsiz Başla → tek "Giriş Yap")
- [x] OAuth callback Suspense boundary eklendi
- [x] "Ana Sayfaya Dön" linki eklendi

- [x] "Hesabımı hatırla" checkbox (localStorage vs sessionStorage) (4 Şubat)

### Öncelik: Deploy (Sırada)
- [ ] Railway backend deploy
- [ ] Vercel frontend deploy
- [ ] Uçtan uca test

---

## 📁 Proje Yapısı

```
PepperRootAiAgency/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # sessions, chat, entities, generate, upload, plugins
│   │   ├── core/             # config, database
│   │   ├── models/           # SQLAlchemy modelleri
│   │   ├── schemas/          # Pydantic şemaları
│   │   ├── services/
│   │   │   ├── agent/        # orchestrator.py, tools.py
│   │   │   ├── llm/          # claude_service.py (Vision desteği)
│   │   │   ├── plugins/      # plugin_base.py, plugin_loader.py, fal_plugin_v2.py
│   │   │   ├── entity_service.py
│   │   │   ├── asset_service.py
│   │   │   └── task_service.py  ← YENİ (Roadmap)
│   │   └── main.py
│   ├── alembic/
│   └── requirements.txt
├── frontend/                 # Next.js (henüz yapılmadı)
└── README.md
```

---

## 🔧 API Endpoints (Yeni)

```
# Plugin Yönetimi
GET  /api/v1/plugins/           - Tüm pluginleri listele
GET  /api/v1/plugins/{name}     - Plugin detayı
POST /api/v1/plugins/{name}/enable   - Aktif et
POST /api/v1/plugins/{name}/disable  - Devre dışı bırak
POST /api/v1/plugins/{name}/configure - Ayarla
GET  /api/v1/plugins/health     - Sağlık kontrolü
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
- Plugins API: http://localhost:8000/api/v1/plugins/

### Veritabanı
- Container: pepperroot-db
- User/Password: postgres/postgres
- Database: pepperroot
- Port: 5432

---

## 📝 Teknik Notlar

- Python 3.14 kullanılıyor
- **Primary LLM:** OpenAI GPT-4o (gpt-4o) ✅
- **Secondary LLM:** Claude Sonnet 4 (Vision için)
- **Cache:** Redis (alpine container)
- fal-client v0.12.0
- Modeller: Nano Banana Pro, Kling 2.5 Turbo Pro, Topaz, Bria RMBG

---

## 🎯 SON DURUM (4 Şubat 2026 - 22:15)

**Bugün Tamamlanan (4 Şubat Akşam):**
- ✅ **Kling 3.0 Pro** video entegrasyonu (en yeni model)
- ✅ **Kullanım İstatistikleri Takibi** (stats_service.py)
- ✅ **Admin Panel Analitik** - gerçek model dağılımı
- ✅ **Web Search** - DuckDuckGo (API key gerektirmez)
- ✅ **Marka Sistemi** - create_brand, research_brand

**Bugün Tamamlanan (Öğlen):**
- ✅ Admin Panel gerçek veri bağlantısı
- ✅ Landing page dinamik butonlar
- ✅ "Hesabımı hatırla" checkbox

**Sıradaki Adım:**
- Deploy (Railway + Vercel)
- Uçtan uca test

---

## ✅ SON COMMITLER

```
b66e956 - feat: Add brand entity system with web research
6314185 - feat: Enable web search with DuckDuckGo
04d939f - feat: Dynamic model distribution in Admin Panel
2027685 - feat: Add usage statistics tracking
d015e48 - feat: Upgrade to Kling 3.0 Pro video model
c3eac33 - fix: Admin panel now shows real database stats
4b030e2 - fix: Admin panel shows only real integrated AI models
```


