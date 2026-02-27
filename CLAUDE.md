# Pepper Root AI Agency — Proje Dokümantasyonu

> **Son Güncelleme:** 27 Şubat 2026
> **Repo:** [github.com/aemregul/PepperRootAiAgency](https://github.com/aemregul/PepperRootAiAgency)

Bu dosya projenin tüm özelliklerini, mimarisini ve nasıl çalıştığını açıklar. Yeni bir AI oturumu veya ekip üyesi bu dosyayı okuyarak projeyi tamamen anlayabilir.

---

## 🧠 Proje Nedir?

Pepper Root AI Agency, **agent-first** (ajantik) bir AI yaratıcı stüdyodur. Kullanıcı doğal dilde istek yapar; AI asistan planlar, üretir, düzenler ve adapte olur. Basit bir chatbot değil — otonom düşünen bir yaratıcı yönetmendir.

**Temel Yetkinlikler:**
- 🖼️ Görsel üretim ve düzenleme (47 AI modeli)
- 🎬 Video üretim ve post-production (FFmpeg + AI)
- 🎵 Müzik/ses üretimi ve senkronizasyon
- 🚀 Tek cümleden tam kampanya oluşturma (otonom)
- 👤 Karakter/marka/mekan hafızası (@tag sistemi)
- 🔍 Web araştırma ve analiz

---

## 🏗️ Mimari

### Tech Stack
| Katman | Teknoloji |
|---|---|
| **Backend** | Python 3.14, FastAPI, SQLAlchemy, Alembic |
| **Frontend** | Next.js 16.1.6, TypeScript, React |
| **Veritabanı** | PostgreSQL (Docker container: `pepperroot-db`) |
| **Cache** | Redis (opsiyonel — yoksa DB fallback) |
| **Primary LLM** | OpenAI GPT-4o |
| **Vision** | GPT-4o Vision, Claude Sonnet 4 |
| **Görsel AI** | fal.ai (Nano Banana, Flux.2, DALL-E vb.) |
| **Video AI** | fal.ai (Kling 3.0, Sora 2), Google Veo 3.1 |
| **Ses AI** | OpenAI Whisper/TTS, ElevenLabs, Mirelo SFX |
| **Arama** | Pinecone (vektör), SerpAPI (web) |
| **Auth** | Google OAuth 2.0, JWT |

### Klasör Yapısı
```
PepperRootAiAgency/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST API endpoints
│   │   ├── core/                # config, database, cache
│   │   ├── models/              # SQLAlchemy modelleri
│   │   ├── services/
│   │   │   ├── agent/           # orchestrator.py, tools.py (36 araç)
│   │   │   ├── plugins/         # fal_plugin_v2.py, fal_models.py
│   │   │   ├── campaign_planner_service.py   # Phase 22
│   │   │   ├── video_editor_service.py       # Phase 23
│   │   │   ├── audio_sync_service.py         # Phase 24
│   │   │   ├── long_video_service.py
│   │   │   ├── google_video_service.py
│   │   │   ├── gemini_image_service.py
│   │   │   ├── voice_audio_service.py
│   │   │   ├── entity_service.py
│   │   │   ├── asset_service.py
│   │   │   ├── quality_control_service.py
│   │   │   └── ...
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages (/, /app, /login)
│       ├── components/          # ChatPanel, AssetsPanel, Sidebar vb.
│       ├── contexts/            # AuthContext
│       └── lib/                 # api.ts
└── CLAUDE.md                    # Bu dosya
```

---

## 🤖 Agent Sistemi (36 Araç)

Agent, GPT-4o tabanlıdır. Kullanıcının mesajını alır, hangi araçları kullanacağına karar verir ve çalıştırır. Tüm araç tanımları `tools.py`, handler'lar `orchestrator.py` dosyasındadır.

### Görsel Üretim & Düzenleme
| Araç | Ne Yapar | Nasıl Çalışır |
|---|---|---|
| `generate_image` | Yeni görsel üretir | Prompt → GPT-4o model seçer → fal.ai'ye gönderir. 9 model destekler (nano_banana, flux2, gpt_image, reve, seedream, recraft, flux2_max, flux_kontext, flux_schnell) |
| `edit_image` | Mevcut görseli düzenler | Gemini 2.5 Flash ile maskesiz inpainting. "Gözlüğü sil", "arka planı değiştir" gibi komutlar. Yüz kimliğini koruma özellikli |
| `outpaint_image` | Görsel boyutunu/formatını değiştirir | fal.ai ile canvas genişletme (1:1→16:9 gibi) |
| `upscale_image` | Kaliteyi artırır | Topaz/Crystal upscaler ile 2x-4x büyütme |
| `remove_background` | Arka planı kaldırır | BiRefNet V2 ile transparent PNG çıktı |
| `generate_grid` | 3x3 grid oluşturur | 9 farklı açı/stil varyasyonu tek seferde |
| `apply_style` | Stil uygular | Sinematik, Pop Art, Anime vb. preset stiller |

### Video Üretim
| Araç | Ne Yapar | Nasıl Çalışır |
|---|---|---|
| `generate_video` | Kısa video üretir (≤10s) | Text-to-video veya image-to-video. 5 model: Kling 3.0, Sora 2, Seedance 1.5, Hailuo 02, Kling 2.5 Turbo |
| `generate_long_video` | Uzun video üretir (15-180s) | Sahne planı oluşturur → her sahneyi paralel üretir → FFmpeg ile crossfade birleştirir. Kullanıcıdan onay ister |
| `edit_video` | Videoyu görsel olarak düzenler | AI ile nesne silme, stil değiştirme |
| `advanced_edit_video` | **[Phase 23]** FFmpeg video post-production | 10 operasyon: trim (kırp), speed (0.25x–4x), fade-in/out, text overlay (7 pozisyon), reverse (boomerang), resize (aspect ratio), concat (birleştir), loop (tekrarla), filter (9 filtre: grayscale, sepia, vintage, blur vb.), extract_frame (kare çıkar) |

### Ses & Müzik
| Araç | Ne Yapar | Nasıl Çalışır |
|---|---|---|
| `generate_music` | AI müzik üretir | MiniMax ile prompttan müzik |
| `add_audio_to_video` | Videoya ses/müzik ekler | Lokal FFmpeg ile birleştirme. Video + audio URL alır, çıktıyı fal.ai'ye yükler |
| `transcribe_voice` | Ses→metin çeviri | OpenAI Whisper v3 (Türkçe/İngilizce) |
| `audio_visual_sync` | **[Phase 24]** Ses-görüntü senkronizasyonu | 6 operasyon: analyze_audio (FFprobe analiz), detect_beats (enerji-tabanlı beat tespit), beat_cut_list (müzik beat'lerine göre sahne geçiş zamanlamaları), generate_sfx (Mirelo SFX ile videodan ses efekti), smart_mix (akıllı müzik mix — volume ducking + fade), tts_narration (TTS seslendirme overlay) |

### Otonom Kampanya
| Araç | Ne Yapar | Nasıl Çalışır |
|---|---|---|
| `plan_and_execute` | **[Phase 22]** Tek cümleden tam kampanya | Kullanıcı "Nike yaz kampanyası — 5 post, 2 video" der → GPT-4o detaylı üretim planı oluşturur (her task için prompt, format, model, bağımlılık) → bağımsız görevler paralel, bağımlı olanlar sıralı çalışır → tüm çıktılar toplanıp sunulur |
| `generate_campaign` | Basit batch varyasyon üretimi | Tek prompttan farklı format/stilde çoklu görsel |

### Entity (Karakter/Marka/Mekan) Yönetimi
| Araç | Ne Yapar | Nasıl Çalışır |
|---|---|---|
| `create_character` | Karakter oluşturur | Ad, açıklama, referans fotoğraf → DB + vektör index. Sonraki üretimlerde yüz tutarlılığı sağlar |
| `create_location` | Mekan oluşturur | "Karanlık lab" gibi → sonraki üretimlerde arka plan olarak kullanılır |
| `create_brand` | Marka oluşturur | İsim, renkler (primary/secondary/accent), slogan, sektör → tüm üretimlere marka kimliği enjekte edilir |
| `get_entity` / `list_entities` | Entity sorgula | Tag veya ID ile çek, tüm entity'leri listele |
| `delete_entity` | Entity sil | Paralel çoklu silme destekler |
| `semantic_search` | Doğal dil ile entity ara | Pinecone vektör DB ile "mavi elbiseli kadın" gibi aramalar |

### Araştırma & Analiz
| Araç | Ne Yapar | Nasıl Çalışır |
|---|---|---|
| `search_web` | Google araması | SerpAPI ile web araması yapıp sonuçları özetler |
| `search_images` | Görsel araması | Google Images'dan referans görseller bulur |
| `browse_url` | Web sayfası okuma | URL'yi çeker ve içeriğini analiz eder |
| `research_brand` | Marka araştırması | Web'den marka bilgilerini toplar (renkler, ton, sektör) |
| `analyze_image` | Görsel analizi | GPT-4o Vision ile görseli detaylı inceler (dövme, yüz, kompozisyon vb.) |
| `analyze_video` | Video analizi | FFmpeg ile key frame çıkarır → GPT-4o Vision ile analiz eder |
| `get_library_docs` | Kütüphane doku çeker | Context7 MCP ile 40+ kütüphanenin güncel API bilgisi |

### Diğer
| Araç | Ne Yapar |
|---|---|
| `manage_core_memory` | Kullanıcı tercihlerini öğrenip hafızaya kaydeder (implicit) |
| `manage_plugin` | Plugin oluştur/düzenle/sil (yaratıcı şablonlar) |
| `save_style` | Stil şablonu kaydet |
| `save_web_asset` | Web'den bulunan görseli Media Panel'e kaydet |

---

## 🎬 47 AI Modeli (9 Kategori)

Tüm modeller `fal_models.py`'de tanımlı, `fal_plugin_v2.py` ile çağrılır. GPT-4o prompt içeriğini analiz edip en uygun modeli seçer ("auto" mode).

| Kategori | Model Sayısı | Model İsimleri |
|---|---|---|
| Görsel Üretim | 9 | Nano Banana Pro, Flux.2, Flux 2 Max, GPT Image 1, Reve, Seedream 4.5, Flux Kontext, Recraft V3, Flux Schnell |
| Görsel Edit | 6 | Nano Banana Edit, Flux Kontext, Qwen Image Edit/Max, Seedream 4.5 Edit, Fibo Edit |
| Video | 15 | Kling 3.0 (i2v/t2v), Sora 2 (i2v/t2v), Veo 3.1 (i2v/t2v), Seedance 1.5 (i2v/t2v), Hailuo 02 (i2v/t2v), Kling 2.5 Turbo (i2v/t2v), Kling O1, LTX-2, PixVerse V5 |
| Ses Efekti | 1 | Mirelo SFX v1.5 |
| Konuşma | 4 | ElevenLabs TTS Turbo, MiniMax Speech-02, Kokoro TTS, Whisper v3 |
| Yüz İşleme | 3 | Face Swap, InstantID, IP-Adapter |
| Upscale | 3 | Topaz, Crystal Upscaler, RealESRGAN |
| Utility | 3 | BiRefNet (bg remove), NSFW Filter, FFmpeg API |

**Model Seçim Örnekleri:**
- "Ghibli tarzı kız" → GPT Image 1 (anime/illustrasyon)
- "Fotorealistik portre" → Nano Banana Pro
- "Tipografi içeren poster" → Flux.2
- "Sinematik sahne" → Reve
- "Logo tasarla" → Recraft V3
- "20 saniyelik hikaye" → Sora 2
- "Kısa sosyal medya clip" → Hailuo 02

---

## 🖥️ Frontend Özellikleri

### Chat Paneli (Merkez)
- **SSE Streaming**: Harf harf animasyonlu yanıtlar (25-30ms/karakter)
- **Çoklu görsel yükleme**: Tek seferde 10'a kadar (thumbnail önizleme)
- **ChatGPT tarzı medya düzeni**: Medya text bubble dışında ayrı blok
- **Video player**: Hover preview + lightbox modal (tam ekran)
- **Video siyah ekran fix**: `#t=0.1` fragment + `onLoadedData`

### Assets Panel (Sağ)
- **6 kategori filtresi**: Tümü, Görsel, Video, Ses, Favoriler, Yüklemeler
- **Yeniden eskiye sıralama**: En yeni medya en üstte
- **Video hover oynatma**: Fareyle üzerine gelince otomatik preview
- **Çöp kutusu**: Silinen asset'ler geri yüklenebilir (thumbnail'lı)

### Sidebar (Sol)
- **Proje yönetimi**: Oluştur, sil, geçiş yap
- **Entity listesi**: Karakterler, Markalar, Mekanlar
- **Plugin/stil dropdown**: 10 hazır stil + kullanıcı plugin'leri
- **Daraltılabilir**: 48px rail ↔ 200px genişleme

### Auth
- **Google OAuth 2.0 only** — tek tıkla giriş
- **Hesabımı hatırla** toggle (localStorage vs sessionStorage)
- **Multi-user izolasyonu**: Her kullanıcı sadece kendi verilerini görür

---

## 🔧 Çalıştırma Komutları

```bash
# PostgreSQL container başlat
docker start pepperroot-db

# Backend çalıştır
cd /Users/emre/PepperRootAiAgency/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend çalıştır
cd /Users/emre/PepperRootAiAgency/frontend
npm run dev
```

### URL'ler
| Servis | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

### Veritabanı
- Container: `pepperroot-db`
- User/Password: `postgres/postgres`
- Database: `pepperroot`, Port: `5432`

---

## 📋 Faz Geçmişi (Tamamlanan Fazlar)

| Faz | Tarih | Açıklama |
|---|---|---|
| 1-4 | Ocak 2026 | Altyapı, Agent çekirdek, Entity sistemi, Video üretimi |
| 5-6 | 30 Ocak | Plugin sistemi, Claude Vision, Roadmap/Task yönetimi |
| 7-8 | 1-3 Şubat | Frontend, Auth (Google OAuth), OpenAI GPT-4o migration |
| 9-10 | 3-6 Şubat | Redis cache, Global Wardrobe, Pinecone semantic search, Context7 |
| 11-13 | 7-17 Şubat | Gemini image edit, Çoklu görsel yükleme, Core Memory, Web Vision |
| 14-16 | 17-18 Şubat | UI redesign, Türkçe lokalizasyon, Autonomous Video Director |
| 17-19.5 | 18-21 Şubat | Multi-model video engine (Veo 3.1), Face intelligence, Robustness |
| 20-21 | 26 Şubat | 47 model entegrasyonu, Agent-driven model selection |
| **22** | **27 Şubat** | **Full Autonomous Studio Orchestration** — `campaign_planner_service.py` |
| **23** | **27 Şubat** | **Real-time Interactive Video Editing** — `video_editor_service.py` |
| **24** | **27 Şubat** | **Audio-Visual Synchronization** — `audio_sync_service.py` |

---

## 📊 Proje İstatistikleri

| Metrik | Değer |
|---|---|
| Agent Araç Sayısı | 36 |
| AI Model Sayısı | 47 |
| Toplam Faz | 24 (tümü tamamlandı) |
| Backend Satır | ~15.000+ |
| Frontend Satır | ~5.000+ |
| Python | 3.14 |
| Next.js | 16.1.6 |

---

## 📌 Eksikler / Yapılacaklar

- [ ] **Deploy**: Railway (Backend) + Vercel (Frontend)
- [ ] Canlı ortam testleri
- [ ] Redis production kurulumu
- [ ] Rate limiting production ayarları
