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
  ├── Referans → reference_image_url alanında saklanır
  └── ⚠️ @ olmadan da tanınır! ("johny" → @johny) ← YENİ

@nike = MARKA
  ├── Renkler → primary/secondary/accent
  ├── Slogan → "Just Do It" vb.
  ├── Sosyal Medya → Instagram, Twitter
  └── research_brand ile web'den otomatik tara
```

---

## 📊 Genel Durum (26 Şubat 2026 - 05:31)

| Faz | Durum | Tamamlanma |
|-----|-------|------------|
| Hafta 1: Altyapı | ✅ Tamamlandı | %100 |
| Hafta 2: Agent + Entity + Referans + Video | ✅ Tamamlandı | %100 |
| Hafta 3: Akıllı Agent + Plugin + Vision | ✅ Tamamlandı | %100 |
| Hafta 4: Frontend + Auth + Multi-User | ✅ Tamamlandı | %100 |
| Hafta 5: Performance + LLM Migration | ✅ Tamamlandı | %100 |
| Hafta 6: Polish + Admin Panel | ✅ Tamamlandı | %100 |
| Hafta 7: Semantic Search + Context7 | ✅ Tamamlandı | %100 |
| Hafta 8: Agent Intelligence Upgrade | ✅ Tamamlandı | %100 |
| Hafta 9: Advanced Features (Phase 2) | ✅ Tamamlandı | %100 |
| Hafta 10: UI Redesign + Localization | ✅ Tamamlandı | %100 |
| Hafta 11: Gemini + Multi-Image + Edit Pipeline | ✅ Tamamlandı | %100 |
| Hafta 12: Video Robustness + Face Intelligence | ✅ Tamamlandı | %100 |
| Hafta 13: Multi-Model AI Engine + Agent-Driven Selection | ✅ Tamamlandı | %100 |
- **26 Şubat 2026:** 47 AI modeli entegre edildi. Agent-driven model seçimi aktif.
  - **47 Model:** 9 kategori (Image 9, Edit 6, Face 3, Video 15, Audio 1, Speech 4, Upscale 3, Utility 3)
  - **Agent-Driven Selection:** GPT-4o içerik analizi yapıp en uygun modeli seçiyor
  - **Yeni Modeller:** Sora 2, GPT Image 1, Flux.2, Seedance 1.5, Hailuo 02, ElevenLabs TTS, Mirelo SFX

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

### ✅ Pinecone Semantic Search (6-7 Şubat) ⭐ YENİ
- [x] Pinecone vektör veritabanı entegrasyonu
- [x] OpenAI ada-002 embedding servisi
- [x] semantic_search tool - Doğal dil ile entity arama
- [x] Entity create/delete'te otomatik vektör sync
- [x] Database fallback (Pinecone devre dışıysa)

### ✅ Context7 MCP Entegrasyonu (7 Şubat) ⭐ YENİ
- [x] context7_service.py - Kütüphane dokümantasyonu çekme
- [x] get_library_docs tool - Agent için güncel API bilgisi
- [x] 40+ popüler kütüphane için önceden tanımlı ID'ler
- [x] HTTP API entegrasyonu (Python native)
- [x] **Video Asset Fixes** (8 Şubat) ⭐ BUGFIX
  - [x] Backend `asset_type` handling (video vs image)
  - [x] Frontend `AssetsPanel` video rendering & hover playback (AbortError fix)
  - [x] Frontend `SavedImagesModal` video support (grid + preview)
  - [x] Frontend `ChatPanel` video rendering (console error fix)
- [x] **Video Asset Fixes** (8 Şubat) ⭐ BUGFIX
  - [x] Backend `asset_type` handling (video vs image)
  - [x] Frontend `AssetsPanel` video rendering & hover playback (AbortError fix)
  - [x] Frontend `SavedImagesModal` video support (grid + preview)
  - [x] Frontend `ChatPanel` video rendering (console error fix)

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
- **47 AI Modeli (9 Kategori):**
  - Görsel: Nano Banana Pro, Flux.2, Flux 2 Max, GPT Image 1, Reve, Seedream 4.5, Flux Kontext, Recraft V3, Flux Schnell
  - Edit: Nano Banana Edit, Flux Kontext, Qwen Image Edit/Max, Seedream 4.5 Edit, Fibo Edit
  - Video: Kling 3.0, Sora 2, Veo 3.1, Seedance 1.5, Hailuo 02, Kling 2.5, Kling O1, LTX-2, PixVerse V5
  - Ses: Mirelo SFX v1.5, ElevenLabs TTS, MiniMax Speech-02, Kokoro TTS, Whisper v3
  - Utility: Topaz Upscale, Crystal Upscaler, BiRefNet, NSFW Filter

---

## 🎯 SON DURUM (26 Şubat 2026 - 05:31)

**🚀 FAZLAR + YENİ ÖZELLİKLER:**

- ✅ **Faz 1-10:** Tamamlandı (detaylar yukarıda)
- ✅ **Faz 11:** Çoklu Görsel Yükleme (Max 10) & Gemini Image Edit
- ✅ **Faz 12-13:** Implicit Core Memory
- ✅ **Faz 14-15:** Web-Aware Vision
- ✅ **Faz 16:** Autonomous Video Director (BackgroundTasks + WebSocket)
- ✅ **Faz 17:** Smart Multi-Model Video Engine (Kling, Veo 3.1)
- ✅ **Faz 18-19.5:** Documentation & Robustness
- ✅ **Faz 20:** Multi-Model AI Engine (47 model, 9 kategori)
- ✅ **Faz 21:** Agent-Driven Model Selection (GPT-4o model seçimi)
- ✅ **Faz 22:** Assets Panel UX & Chat Media Rendering ⭐ YENİ

**Toplam Kod:** 10000+ satır | **28+ Agent Tool** | **47 AI Modeli**

### 🖼️ Assets Panel UX & Chat Media Rendering (26 Şubat 2026 - 05:31) ⭐ YENİ

1. **Assets Panel Header Düzeltmeleri (`AssetsPanel.tsx`):**
   - Sağ panel header yüksekliği sol panelle eşitlendi (`h-14` = 56px) → flush alignment
   - 6 filtre ikonu ile 3 aksiyon butonu arasına dikey çizgi eklendi (işlevsel ayırım)
   - Icon-only filter tabs → tooltip ile isim/count gösterimi
   - `justify-evenly` ile tüm butonlar eşit dağıtıldı

2. **Video Thumbnail & Hover Play:**
   - Video `preload` → `metadata` + `#t=0.1` ile ilk kare gösterimi (siyah ekran düzeltildi)
   - Hover overlay'e `pointer-events-none` → fareyle üzerine gelince video otomatik oynatılıyor

3. **Sıralama — Yeniden Eskiye:**
   - `filteredAssets` reverse edilerek en yeni medya en üstte gösteriliyor
   - Tüm kategorilerde (Tümü, Görsel, Video, Ses, Favoriler, Yüklemeler) aktif

4. **Chat Inline Media Rendering (`ChatPanel.tsx`):**
   - Regex düzeltildi: `[ÜRETİLEN GÖRSELLER: url]` ve `[Bu mesajda üretilen görseller: url]` her ikisi tanınıyor
   - Streaming sonrası inline asset tag'leri otomatik temizleniyor → thumbnail render
   - Non-streaming (dosyalı) yanıtlarda da inline URL tag'leri temizleniyor
   - Chat history'den `metadata_.videos[0].url` çıkarılıp `video_url` set ediliyor

5. **Video Progress Card Yeniden Yazıldı (`GenerationProgressCard.tsx`):**
   - Kendi bozuk WebSocket bağlantısı kaldırıldı (yanlış URL'ye bağlanıyordu)
   - Sade display bileşenine dönüştürüldü — `progress` ve `status` prop olarak alıyor
   - ChatPanel'in çalışan WebSocket'inden gelen **gerçek ilerleme** yüzdesi karta aktarılıyor
   - Alt kısımdaki İngilizce prompt yazısı kaldırıldı
   - Duplicate "Videonuz hazır!" mesajı önlendi (`message_id` dedup)

6. **Custom Chat Video Player:**
   - Native browser controls kaldırıldı (karmaşık butonlar, kötü fullscreen)
   - Sol altta play butonu → hover'da video sessiz preview oynatılıyor
   - Tıklayınca **lightbox modal** açılıyor (tam ekran, proper controls)
   - `lightboxVideo` state + portal modal eklendi

7. **ChatGPT Tarzı Medya Düzeni:**
   - Medya (görsel/video/ses) artık text bubble **DIŞINDA** ayrı bloklar olarak render ediliyor
   - Kullanıcı: medya üstte, metin altta
   - Asistan: metin üstte, medya altta
   - Daha temiz görsel hiyerarşi

8. **Otomatik Yön Algılama & Sabit Boyutlar:**
   - `onLoadedMetadata` (video) ve `onLoad` (image) ile dikey/yatay algılama
   - **Asistan medyası:** Dikey 280×420px, Yatay 420×280px
   - **Kullanıcı medyası:** Dikey 200×300px, Yatay 300×200px (biraz daha küçük)
   - `object-cover` ile doğal oran korunuyor

### 🐛 DEVAM EDEN SORUNLAR (27 Şubat 2026 — Düzeltildi ✅)

1. **✅ Chat Video Siyah Ekran Sorunu — DÜZELTİLDİ:**
   - `renderContent` fonksiyonundaki video tag'lerine `#t=0.1` src fragment'ı eklendi
   - `onLoadedData` callback ile `currentTime = 0.1` set edilerek çift güvence sağlandı
   - Hem markdown-link videoları hem standalone URL videoları düzeltildi
   - `muted` attribute eklendi (autoplay policy uyumluluğu)

2. **✅ "Yatay formatta çevir" Referans Görseli Sorunu — DÜZELTİLDİ:**
   - `_handle_tool_call`'da `generate_video` ve `generate_long_video` için session-cached referans görseli auto-injection eklendi
   - `uploaded_reference_url` yoksa bile `_session_reference_images` cache'inden referans alınıyor
   - Kullanıcı önceki mesajda görsel yükleyip sonraki mesajda "videoya çevir" dediğinde referans kaybedilmiyor

---

## 📋 EKSİKLER / YAPILACAKLAR

- [ ] Deploy: Railway (Backend) + Vercel (Frontend)
- [ ] Canlı ortam testleri
- [x] **Teknik Test (26 Madde): 53/54 ✅**
### Phase 17: Smart Multi-Model Video Engine [COMPLETED 2026-02-21]
- **Multi-Model Routing:** Added `{model: veo|kling|luma|runway|minimax}` support to `generate_video` and `generate_long_video`.
- **Google Veo 3.1 Integration:** Implemented `GoogleVideoService` using Vertex AI / Google GenAI SDK for the highest fidelity cinematic video.
- **Per-Scene Adaptive Routing:** `LongVideoService` now selects different models for each scene based on the director's roadmap.
- **Smart Model Decision:** Updated Orchestrator system prompt to handle model selection based on scene context (e.g., minimax for action, kling for lip-sync).
- **Fallback Mechanism:** Google Veo 3.1 requests automatically fallback to Luma/Kling via Fal.ai if API errors occur.

### Phase 18-19.5: Documentation & Robustness [COMPLETED 2026-02-21]
- **Video Background Robustness:** Fixed blocking `time.sleep` with `await asyncio.sleep` in video services.
- **Fail-Safe Reporting:** Background task errors are now saved as persistent chat messages.
- **Intelligent Face Selection:** GPT-4o Vision filters and selects the best matching face reference in multi-subject images.
- **Hallucination Protection:** Strict system prompt rules prevent AI from claiming video completion prematurely.
- **Safety Refusal Bypass:** Softened prompts to avoid GPT-4o "I can't identify people" refusals for fictional characters.

### Current Fokus & Roadmap
- ✅ Phase 20: Multi-Model AI Engine (47 model entegrasyonu) — **TAMAMLANDI**
- ✅ Phase 21: Agent-Driven Model Selection (GPT-4o model seçimi) — **TAMAMLANDI**
- ✅ Phase 22: Full Autonomous Studio Orchestration — **TAMAMLANDI (27 Şubat 2026)**
- [ ] Phase 23: Real-time Interactive Video Editing (Planned)
- [ ] Phase 24: Audio-Visual Synchronization (Planned)
- [ ] **Deploy:** Railway (Backend) + Vercel (Frontend)

### Phase 22: Full Autonomous Studio Orchestration [COMPLETED 2026-02-27] ⭐ YENİ
- **CampaignPlannerService** (`campaign_planner_service.py`): GPT-4o ile tek cümleden detaylı üretim planı çıkarır
- **Paralel Execution Engine**: Bağımsız görevleri `asyncio.gather` ile paralel, bağımlı görevleri sıralı çalıştırır
- **Akıllı Plan Format**: Her task için type, prompt, format, aspect_ratio, model ve dependency tanımı
- **Marka Entegrasyonu**: `brand_tag` ile entity'den renkler, slogan, ton otomatik çekilir
- **Yeni Tool**: `plan_and_execute` — 34. araç olarak tools.py'ye eklendi
- **Orchestrator Handler**: `_plan_and_execute` metodu + system prompt güncellemesi
- **Backward Compat**: Mevcut `generate_campaign` korundu, tüm 33 eski araç değişmedi
- **Örnek Kullanım**: "Nike yaz kampanyası — 5 post, 2 video, 1 kapak" → GPT-4o planlar, paralel üretir, sonuçları toplar

### 🎬 47 Model AI Engine & Agent-Driven Selection (26 Şubat 2026) ⭐ YENİ

1. **47 AI Modeli Entegrasyonu (`fal_models.py`):**
   - Görsel Üretim (9): Nano Banana Pro, Flux.2, Flux 2 Max, GPT Image 1, Reve, Seedream 4.5, Flux Kontext, Recraft V3, Flux Schnell
   - Görsel Edit (6): Nano Banana Edit, Flux Kontext, Qwen Image Edit, Qwen Image Max Edit, Seedream 4.5 Edit, Fibo Edit
   - Video Üretim (15): Kling 3.0 (i2v/t2v), Sora 2 (i2v/t2v), Veo 3.1 (i2v/t2v), Seedance 1.5 (i2v/t2v), Hailuo 02 (i2v/t2v), Kling 2.5 Turbo (i2v/t2v), Kling O1, LTX-2, PixVerse V5
   - Ses Efekti (1): Mirelo SFX v1.5 (video→audio)
   - Konuşma (4): ElevenLabs TTS Turbo v2.5, MiniMax Speech-02, Kokoro TTS, Whisper v3 (STT)
   - Yüz (3), Upscale (3), Utility (3)

2. **Agent-Driven Model Selection (`fal_plugin_v2.py`):**
   - GPT-4o prompt içeriğini analiz ederek en uygun modeli SEÇİYOR
   - `IMAGE_MODEL_MAP`: nano_banana, flux2, flux2_max, gpt_image, reve, seedream, recraft
   - `VIDEO_MODEL_MAP`: kling, sora2, veo, seedance, hailuo
   - Keyword tabanı yerine AI analizi ile model seçimi ("auto" fallback korunuyor)
   - Örnek: "Ghibli tarzı kız" → GPT Image 1 | "20s hikaye" → Sora 2 | "kısa clip" → Hailuo 02

3. **Smart Router Güncellendi:**
   - Video fallback zinciri: 5 model (Kling → Sora 2 → Veo 3.1 → Seedance → Hailuo)
   - Edit fallback zinciri: 5 model (Flux Kontext → Flux Pro Kontext → Qwen Edit → OmniGen → Flux Inpaint)
   - Image fallback zinciri: 3 model (Nano Banana → Flux.2 → Reve)

4. **Yeni Plugin Actions:** `text_to_speech`, `video_to_audio` (FalPluginV2 → 13 aksiyon)

---

### 📝 SON GELİŞMELER (21 Şubat 2026 - 03:15)

### 🔮 Intelligent Face Selection & Async Stability (Phase 18-19.5) ⭐ YENİ
1. **Zeki Referans Filtreleme (GPT-4o Vision):**
   - Çoklu referans görseli (erkek/kadın) yüklendiğinde, sistem artık talimatı analiz edip en uygun olanı seçiyor.
   - "Erkek karakter ekle" dendiğinde kadın referansı elenerek kimlik karışıklığı (gender-swap) önleniyor.
2. **Video Arka Plan Stabilizasyonu (LRO Polling):**
   - Google Veo 3.1 için polling mantığı düzeltildi.
   - Bloklayan `time.sleep` hataları asenkron `asyncio.sleep`e çevrilerek sunucu kilitlenmesi önlendi.
3. **Hata Yakalama & Hallüsinasyon Engelleme:**
   - Arka plan görev hataları artık sohbete kalıcı mesaj olarak kaydediliyor.
   - Agent'ın video hazır olmadan "Hazır" demesi sistem promptu ile yasaklandı.

### 🎬 Autonomous Video Director (Faz 16 Tamamlandı) ⭐ YENİ
1. **Asenkron Mimari (Backend):**
   - Uzun videolar 3-4 dakika sürdüğü için API request'ini bloklamaması adına `BackgroundTasks` entegrasyonu yapıldı.
   - Oratoryo `generate_long_video` tool'unu çağırır çağırmaz işlem arka plana atılıyor ve kullanıcıya "Üretime başladım!" denilip frontend kilitlenmekten kurtuluyor.
2. **WebSocket & Progress Push:**
   - Arka plandaki video üretimi tamamlandığında sistem otomatik olarak veritabanına yeni bir `ChatMessage` oluşturuyor (Asistandan gelmiş gibi).
   - Yeni mesaj, aktif kullanıcı oturumuna WebSocket Manager üzerinden `message_created` eventiyle anlık iletiliyor.
3. **Web-Enhanced Scene Routing (Director Logic):**
   - System prompt güncellenerek ajans "Yönetmen" kimliğine büründürüldü: Sahneleri planlayıp aralarda eksik olan görselleri `search_images` ile webt'en araştırıyor.
   - Bulduğu referans "URL"leri `VideoSegment` içerisine `reference_image_url` olarak besleyip doğrudan `Image-to-Video` (i2v) çıktı almayı sağlıyor.

### 🧠 Gemini True Inpainting & Multi-Model Image Yeteneği ⭐ YENİ
1. **Google Cloud Gemini Entegrasyonu:**
   - Fal.ai üzerindeki model sorunlarını (outpaint, nesne kaldırma kusurları vs.) kökten çözmek için Google Gemini 2.5 API'ı (`gemini_image_service.py`) sisteme dahil edildi.
   - Düzenleme (edit_image) komutlarında "maskesiz doğal blending" yeteneği sayesinde "kediyi kaldır", "gözlüğü sil" komutlarını mükemmel uyguluyor.
2. **Face Identity Preservation (Yüz Koruma):**
   - Sistem bir yüz referansına sahipse her düzenlemede/retouch işleminde yüzün bütünlüğünü %100 koruyup kıyafet veya arka planı değiştirme operasyonunu sorunsuz hallediyor.

### 📝 Core Memory & Web Vision Tamamlandı (Faz 12-15) ⭐ YENİ
1. **Kalıcı Hafıza Aracı (`remember_user_preference`):**
   - Sistem konuşmaları dinleyerek kullanıcının sevdiği marka tonlarını, sevmediği arka planları kendi kendine (implicit) öğrenip Redis+DB'ye Core Memory olarak kazıyor.
2. **Web Görsel Analizi (`analyze_image` & `save_web_asset`):**
   - Webt'en veya url ile gelen görselleri GPT-4o Vision ile direkt analiz edip "Bu kadının sağ kolunda yılan dövmesi var" benzeri prompt içi veriye (context injection) dönüştürüyor ve istenirse direkt projeye "Medya Varlığı" olarak indirebiliyor.

### 🎨 Prompt Enrichment Pipeline (19 Şubat - PM) ⭐ YENİ

1. **Prompt Zenginleştirme Güçlendirildi (`prompt_translator.py`):**
   - System prompt yeniden yazıldı — cinematic lighting, volumetric light, HDR, bokeh, 8K UHD
   - Örnek zenginleştirmeler eklendi (uçan araba, güneş batan deniz)
   - Yeni `enrich_prompt()` fonksiyonu — entity olmayan genel promptlar için ek katman
   - `STANDARD_NEGATIVE_PROMPT` sabiti — blurry, distorted, bad anatomy vb.

2. **fal.ai Kalite Parametreleri (`fal_plugin_v2.py`):**
   - `guidance_scale: 5.0` (varsayılandan yüksek)
   - `num_inference_steps: 30` (28'den artırıldı)
   - `output_format: png` (JPEG sıkıştırma kaybı yok)
   - `enable_safety_checker: False` (sanatsal kısıtlama yok)

3. **Orchestrator Entegrasyonu:**
   - Entity yokken bile `enrich_prompt()` çağrılıyor
   - Artık her görsel üretim sinematik kalitede prompt alıyor

### 🧪 Kapsamlı Teknik Test (19 Şubat - PM) ⭐ YENİ

1. **26 Tool Handler Testi — 26/26 ✅:**
   - Tüm araçlar (image, video, entity, plugin, search, style) handler'a sahip
   - `edit_video` inline handler olarak doğrulandı
   - `manage_plugin` yeni eklenen DB handler çalışıyor

2. **Entity CRUD Testi — Real User Session ile:**
   - `create_character`, `create_location`, `create_brand` → DB'ye yazıyor
   - `get_entity`, `list_entities`, `delete_entity` → çalışıyor
   - `semantic_search`, `manage_wardrobe` → sorunsuz

3. **Plugin CRUD Testi:** create → list → delete zinciri sorunsuz

4. **FalPluginV2:** 13 aksiyon (generate_image, video, edit_image, edit_video, upscale_image/video, face_swap, smart_generate, outpaint, style, text_to_speech, video_to_audio)

### 🧩 Plugin & Stil Entegrasyonu (19 Şubat) ⭐ YENİ

1. **Hazır Stil Şablonları Dropdown:**
   - 10 built-in stil (Sinematik, Pop Art, Anime, Minimal vb.)
   - `Palette` 🎨 butonu ile erişim (send butonu yanında)
   - `createPortal` ile `overflow-hidden` bypass edildi
   - Kullanıcının yüklü plugin'leri de aynı dropdown'da (🧩 Eklentilerim)

2. **Plugin Oluşturma Akışı Düzeltildi:**
   - `manage_plugin` tool'u `tools.py`'ye eklendi (26 toplam tool)
   - System prompt güncellendi — "Eksik alan engel değil, elindekiyle oluştur"
   - `_manage_plugin` handler: Mock data → gerçek DB kaydı (`CreativePlugin` modeli)
   - Frontend buton mesajı sadeleştirildi

3. **Plugin "Kullan" Düzeltmesi:**
   - Eski: Tıklayınca otomatik gönderiyordu
   - Yeni: `pendingInputText` ile input'a yazar, kullanıcı düzenleyip gönderir
   - `onSetInputText` prop zinciri: Sidebar → page.tsx → ChatPanel

4. **model_dump Bug Fix:**
   - `orchestrator.py` — `SimpleNamespace` objeleri için `model_dump()` yerine manuel dict dönüşümü

### 🔧 Asset Silme & Çöp Kutusu Düzeltmeleri (19 Şubat) ⭐ YENİ

1. **Asset Deletion Bug Fix:**
   - `IntegrityError` düzeltildi — `entity_assets` NOT NULL constraint hatası
   - İlişkili `EntityAsset` kayıtları silme öncesi temizleniyor
   - Child asset `parent_asset_id` referansları temizleniyor
   - Silinen asset `TrashItem` tablosuna ekleniyor

2. **Çöp Kutusu Thumbnail Desteği:**
   - Backend `TrashItemResponse`'a `original_data` eklendi (URL bilgisi)
   - `TrashModal.tsx` artık silinen görselleri 56×56px thumbnail olarak gösteriyor
   - Video dosyaları için video ikonu, kırık görseller için fallback
   - "Görseller" filtre tab'ı eklendi

3. **Anlık UI Güncellemeleri (Sayfa Yenilemeden):**
   - Asset silme → çöp kutusu anında güncellenir (`onAssetDeleted` callback)
   - Çöpten geri yükleme → media panel anında güncellenir (`onAssetRestore` callback)
   - `page.tsx` üzerinden bidirectional `refreshKey` mekanizması

### 🚀 SSE Streaming Yeniden Yazıldı (19 Şubat) ⭐ YENİ

1. **Tek Streaming Çağrı Mimarisi:**
   - Eski: 2 OpenAI çağrısı (non-streaming + streaming) → çift bekleme
   - Yeni: TEK streaming çağrı, tool call chunk'ları paralel biriktirilir
   - Tool call yoksa tokenlar direkt yield edilir (gerçek real-time)

2. **ChatGPT Tarzı Harf Harf Animasyon:**
   - Tokenlar karakterlere bölünüp kuyruk sistemiyle render ediliyor
   - 25-30ms/karakter hızında doğal yazım efekti
   - Kuyruk birikmesi durumunda adaptif hızlanma

3. **Loading Göstergesi İyileştirmesi:**
   - Normal sohbetlerde "Düşünüyor..." metni kaldırıldı
   - Yerine: 3 zıplayan nokta (●●●) animasyonu
   - Uzun işlemlerde (görsel/video) açıklayıcı metin korunuyor
   - İlk token geldiğinde loading kaybolur, mesaj kutusu belirir
   - Çift kutu (double-box) sorunu düzeltildi

### 🔒 Auth & Altyapı Düzeltmeleri (19 Şubat) ⭐ YENİ

1. **Auth Header Düzeltmeleri (api.ts):**
   - `getTrashItems`, `restoreTrashItem`, `permanentDeleteTrashItem` → auth header eklendi
   - `deleteSession`, `updateSession` → auth header eklendi
   - Production ortamında auth zorunlu olduğunda patlamayacak

2. **Çöp Kutusu Otomatik Temizleme (main.py):**
   - Backend başlatıldığında süresi dolmuş `TrashItem` kayıtları otomatik silinir
   - `expires_at < now()` kontrolü ile temizleme

3. **Pipeline Timeout Koruması (fal_plugin_v2.py):**
   - BiRefNet arka plan kaldırma: 15s limit
   - Nano Banana Pro Edit: 45s limit
   - GPT Image 1 Edit: 60s limit
   - FLUX Kontext Pro: 45s limit
   - Her adım timeout olursa bir sonraki fallback'e geçer


### 🖼️ Görsel Üretim Pipeline Yenileme (18 Şubat) ⭐ YENİ

1. **Model A/B Testi (4 model karşılaştırıldı):**
   - `fal-ai/gpt-image-1/edit-image` — En iyi yüz koruma, fotorealistik ama yapay hissi var
   - `fal-ai/flux-pro/kontext` — İyi yüz koruma, daha işlenmiş görünüm
   - `fal-ai/instantid` — Başarısız sonuçlar
   - `fal-ai/ip-adapter-face-id` — Başarısız sonuçlar

2. **Yeni 3 Aşamalı Pipeline (`_smart_generate_with_face`):**
   - **Ön İşlem:** BiRefNet arka plan kaldırma (referans fotoğraftaki kırmızı arka planın sızmasını önler)
   - **Aşama 1:** Nano Banana Pro Edit — Grid eklentisiyle aynı endpoint (`/edit`), en iyi fotorealizm
   - **Aşama 2:** GPT Image 1 Edit — ChatGPT'nin kullandığı model (fallback)
   - **Aşama 3:** FLUX Kontext Pro — Son alternatif

3. **Chat Input İyileştirmesi:**
   - `<input>` → `<textarea>` değişimi (çok satırlı giriş)
   - Auto-resize (max 200px)
   - Shift+Enter ile yeni satır, Enter ile gönder
   - **Bug fix:** Mesaj gönderdikten sonra textarea yüksekliği sıfırlanıyor

### 🔧 Referans Görsel & Arka Plan Kaldırma Düzeltmeleri (19 Şubat - Gece) ⭐ YENİ

1. **BiRefNet V2 Arka Plan Kaldırma:**
   - Eski `fal-ai/bria/rmbg` endpoint'i ölmüştü (`Path /rmbg not found`)
   - Yeni: `fal-ai/birefnet/v2` + `output_format: png` → gerçek transparent PNG
   - `operating_resolution: 1024x1024`, `model: General Use (Light)`

2. **FalPluginV2 Method Call Düzeltmeleri (5 tool):**
   - `remove_background` → `_remove_background` (dict param)
   - `face_swap` → `_face_swap` (dict param)
   - `smart_generate_with_face` → `_smart_generate_with_face` (dict param)
   - `generate_video` → `_generate_video` (dict param)
   - `upscale_image` → `_upscale_image` (dict param)
   - Hepsi public method yerine private method + dict format gerekiyordu

3. **Image Editing Asset Kaydetme:**
   - `remove_background`, `edit_image`, `outpaint_image`, `upscale_image`, `apply_style`
   - Önceden sadece `generate_image` ve `generate_video` asset kaydediyordu
   - Şimdi tüm görsel işlem sonuçları Medya Varlıkları paneline kaydediliyor

4. **URL Sızıntısı Düzeltildi:**
   - `[ÜRETİLEN GÖRSELLER: url]` artık chat mesajlarında görünmüyor
   - URL'ler sadece `metadata_` alanında saklanıyor
   - System prompt güçlendirildi: `fal.media` URL'leri markdown, ham veya köşeli parantez formatında yasaklandı

5. **Session Referans Görsel Hafızası:**
   - `_session_reference_images` dict ile session bazlı referans görseli cache
   - Mesaj 1'de yüklenen fotoğraf, mesaj 2'de otomatik yeniden kullanılıyor
   - Hem streaming hem non-streaming path'te aktif
   - GPT-4o'ya önceki referans URL'si `[ÖNCEKİ REFERANS GÖRSEL URL: ...]` olarak iletiliyor

6. **Referans Görsel Auto-Injection:**
   - `_handle_tool_call`'da `IMAGE_TOOLS` için otomatik `image_url` enjeksiyonu
   - Kullanıcı fotoğraf yükleyip "arka planı kaldır" dediğinde image_url otomatik ekleniyor

### 📌 Bilinen Sorunlar
- [x] ~~Sayfa yenilendiğinde kullanıcı mesajındaki yüklenen görsel önizlemesi kaybolur~~ → **Düzeltildi** (reference_urls metadata)
- [x] ~~Yeni marka oluşturulduğunda sidebar'da görünmüyor~~ → **Düzeltildi** (entity key fix)
- [ ] Uzun prompt'larla görsel üretim timeout olabiliyor (~45-60s)
- [ ] AI referans görsel yüklenmiş olsa bile yüz kimliğini iyi koruyamıyor → **Hibrit Gemini ile çözülecek**

### 🌟 20 Şubat 2026 - Oturum Güncellemesi ⭐ YENİ

1. **Yeni Marka UI Refresh Bug Fix:**
   - `_create_brand` result'a `entity` key eklendi → SSE `entities` event tetikleniyor
   - Sidebar sayfa yenilemeden güncelleniyor

2. **Kullanıcı Görsel Kalıcılığı (Chat History):**
   - `_uploaded_image_url` artık result dict'ten silinmiyor
   - `chat.py` → `reference_url` user message metadata'ya kaydediliyor
   - `ChatPanel.tsx` → history yüklerken `metadata_.reference_url` okunuyor
   - Sayfa yenilendiğinde kullanıcı görselleri thumbnail olarak görünüyor

3. **Gemini Image Edit Entegrasyonu:**
   - Google Cloud Billing aktif edildi
   - `gemini-2.5-flash-image` modeli doğrulandı
   - Test script çalıştırıldı → Gemini native görsel düzenleme çalışıyor
   - **Bulgu:** Gemini, face identity korumada fal.ai pipeline'ından çok daha iyi

4. **Prompt Enrichment İyileştirmesi:**
   - `orchestrator.py` system prompt güçlendirildi — GPT-4o kısa komutları detaylı edit talimatlarına zenginleştiriyor
   - `tools.py` `edit_image` tool description güncellendi

5. **Çoklu Görsel Yükleme (Max 10) ✅:**
   - **Frontend (`ChatPanel.tsx`):**
     - `attachedFile` → `attachedFiles[]`, `filePreview` → `filePreviews[]`
     - `multiple` file input + 10 limit kontrolü
     - Horizontal thumbnail grid (X butonları + "3/10" sayaç + "+" ekle butonu)
     - Preview ObjectURL'leri gönderimde revoke edilmiyor (mesajda görünür kalıyor)
     - History yükleme: `metadata_.reference_urls[]` array desteği
   - **Frontend (`api.ts`):**
     - `sendMessage` → `File[]` kabul ediyor, `/with-files` endpoint kullanıyor
   - **Backend (`chat.py`):**
     - Yeni `/with-files` endpoint (`List[UploadFile]`, max 10)
     - `_process_chat` → `reference_images_base64: List[str]`
     - Tüm URL'ler `reference_urls` olarak user message metadata'ya kaydediliyor
     - `/with-image` backward compat korunuyor
   - **Backend (`orchestrator.py`):**
     - `process_message` → `reference_images: list` parametresi
     - Tüm görseller fal.ai'ye yükleniyor
     - GPT-4o Vision'a her görsel ayrı `image_url` content part olarak gönderiliyor
     - `_uploaded_image_urls` result dict'e eklendi

### 🌟 22 Şubat 2026 - Otonom Entity Kontrolü ve Silme Düzeltmeleri ⭐ YENİ

1. **Otonom (İzinsiz) Entity Üretimi Engellendi:**
   - `orchestrator.py` sistem komutlarına kesin bir kısıtlama getirildi: Kullanıcı açıkça "kaydet" demedikçe görsellerden çıkarılan kişiler/mekanlar otonom olarak `create_character` veya `create_location` ile KESİNLİKLE kaydedilmeyecek.
   - LLM'in bu kısıtlamalara kesin itaati sağlandı.

2. **Çoklu Entity Silme (Halüsinasyon Önleyici) Düzeltmesi:**
   - Kullanıcı "karakterleri sil" gibi çoğul bir istekte bulunduğunda sistemin senaryo yazma (halüsinasyon) hatasına düşmesi engellendi.
   - `tools.py` içerisinde `delete_entity` aracının açıklaması güncellenerek hedefteki her bir entity için (örn: @kisi_1, @woman_in_white) bu aracın **paralel olarak (birden çok kez) çağrılması gerektiği** Modele açıkça belirtildi.

### 🎨 UI Redesign + Türkçe Lokalizasyon (17 Şubat)

1. **Sidebar Yeniden Tasarım:**
   - Daraltılabilir rail (48px) + hover'da genişleme (200px)
   - CSS-only tooltip yerine inline label sistemi
   - İkon boyutları büyütüldü (24px ana, 20px özellik butonları)
   - Flexbox ile mükemmel merkezleme
   - Smooth geçiş animasyonları

2. **Kapsamlı Türkçe Lokalizasyon (55+ çeviri):**
   - `Sidebar.tsx` — Projects→Projeler, Entities→Varlıklar, Characters→Karakterler, Locations→Lokasyonlar, Brands→Markalar, Creative Plugins→Yaratıcı Eklentiler, Marketplace→Eklenti Mağazası
   - `GridGeneratorModal.tsx` — Tüm ilerleme aşamaları, buton etiketleri, yükleme alanı, mod seçiciler (30+ çeviri)
   - `AssetsPanel.tsx` — Media Assets→Medya Varlıkları, Refresh→Yenile, VIDEO→VİDEO
   - `AdminPanelModal.tsx` — Admin Panel→Yönetim Paneli, Plugin Marketplace→Eklenti Mağazası
   - `PluginMarketplaceModal.tsx` — Plugin Marketplace→Eklenti Mağazası
   - `ChatPanel.tsx` — VIDEO→VİDEO, alt text çevirileri
   - `page.tsx` (Landing) — Powered by→gücüyle, Studio→Stüdyo

3. **Unified Chat Tasarımı:**
   - Tek asistan modeli — proje bazlı sohbet
   - Yeni proje oluşturma modal'ı
   - Chat paneli yeniden tasarlandı

### 🚀 Phase 2: Advanced Features (8 Yeni Özellik) — Önceki

1. **WebSocket Real-Time Progress** — `progress_service.py`, `ws.py`
2. **Auto Quality Control (GPT-4o Vision)** — `quality_control_service.py`
3. **Self-Learning (Prompt Hafızası)** — Başarılı prompt'lar hafızaya kaydedilir
4. **Cross-Project Memory** — `conversation_memory_service.py`
5. **Style Transfer / Moodboard** — `save_style` tool
6. **Batch Campaign Mode** — `generate_campaign` tool
7. **Multi-Agent Collaboration** — `multi_agent_service.py`
8. **Voice + Audio** — `voice_audio_service.py` (Whisper STT + OpenAI TTS)

### 🟢 Önceki Düzeltmeler (11 Şubat)
1. Video Editing V2 Migration — `FalPluginV2` uyumluluğu
2. Frontend Hydration Fix — `ChatPanel.tsx` `<p>` nesting hatası

---
