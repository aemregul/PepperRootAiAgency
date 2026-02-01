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
  ├── Video → Kling 2.5 Turbo Pro ile
  └── Referans → reference_image_url alanında saklanır
```

---

## 📊 Genel Durum (1 Şubat 2026)

| Faz | Durum | Tamamlanma |
|-----|-------|------------|
| Hafta 1: Altyapı | ✅ Tamamlandı | %100 |
| Hafta 2: Agent + Entity + Referans + Video | ✅ Tamamlandı | %100 |
| Hafta 3: Akıllı Agent + Plugin + Vision | ✅ Tamamlandı | %100 |
| Hafta 4: Frontend + Web Browsing + Grid | 🔄 Devam Ediyor | %80 |

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

### Öncelik 1: Frontend ✅ TAMAMLANDI!
- [x] Next.js kurulumu
- [x] Chat UI (sol panel)
- [x] Asset Panel (sağ panel grid)
- [x] Plugin bölümü sidebar'da
- [x] Settings modal (tema toggle)
- [x] Dark mode varsayılan
- [x] Prompt çevirisi (tüm diller → İngilizce)
- [x] Gelişmiş karakter özellikleri

### Hafta 4: Web Browsing Agent (1 Şubat) ⭐ YENİ
- [x] search_images - DuckDuckGo görsel arama
- [x] search_web - Metin/bilgi arama
- [x] search_videos - Video arama
- [x] browse_url - Web sayfası okuma (BeautifulSoup)
- [x] fetch_web_image - Görsel indirme ve kaydetme
- [x] Akıllı fallback: search → fetch → edit → video

### Hafta 4: Grid Generator (1 Şubat) ⭐ YENİ
- [x] generate_grid tool
- [x] 3x3 grid (9 kamera açısı veya storyboard)
- [x] Panel extraction ve upscale
- [x] @karakter referansı ile grid

### Öncelik 2: UI Entegrasyonu (Devam)
- [ ] Characters/Locations gerçek veritabanına bağla
- [ ] Media Assets paneli gerçek asset'lere bağla
- [ ] Search fonksiyonu
- [ ] Admin Panel sayfası

### Öncelik 3: Faz 2 Özellikler
- [ ] Marka tanıma (web araştırması)
- [ ] 3 dakikalık video birleştirme
- [ ] Workflow export

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
- Claude Sonnet 4 modeli (claude-sonnet-4-20250514) + Vision desteği
- fal-client v0.12.0
- Modeller: Nano Banana Pro, Kling 2.5 Turbo Pro, Topaz, Bria RMBG

---

## 🎯 SON DURUM (1 Şubat 2026 - 21:00)

**Tamamlanan:**
- ✅ Frontend: Next.js + Tailwind CSS
- ✅ Chat UI çalışıyor (AI yanıt veriyor)
- ✅ Plugin bölümü sidebar'da (fal.ai, Minimax)
- ✅ Settings modal (tema toggle)
- ✅ Dark mode varsayılan
- ✅ Prompt çevirisi (tüm diller → İngilizce)
- ✅ Admin Panel (gelişmiş)
- ✅ Grid Generator Modal
- ✅ Web Browsing Agent (DuckDuckGo + BeautifulSoup)
- ✅ Akıllı fallback zinciri (search → fetch → edit → video)

**Sıradaki Adım:**
- Auth sistemi (Google OAuth)
- Deploy (Railway + Vercel)

---

## ✅ SON COMMITLER

```
fe9ca15 - feat: Roadmap/Task sistemi - çoklu adım görev planlama
aba44aa - feat: Görsel muhakeme sistemi (Claude Vision)
4fe1387 - feat: Minecraft tarzı plugin sistemi
af1f8dc - docs: CLAUDE.md ve proje dökümanları güncellendi
f73a64b - feat: akıllı agent davranışları
```

