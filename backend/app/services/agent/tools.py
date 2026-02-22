"""
Agent tarafından kullanılabilen araçların tanımları.
OpenAI Functions format (function calling).
"""

def convert_to_openai_tools(anthropic_tools: list) -> list:
    """Anthropic tool formatını OpenAI functions formatına çevir."""
    openai_tools = []
    for tool in anthropic_tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}})
            }
        }
        openai_tools.append(openai_tool)
    return openai_tools


# Agent'a sunulacak araçların listesi (Anthropic JSON Schema formatında - geriye uyumluluk)
AGENT_TOOLS_ANTHROPIC = [
    {
        "name": "generate_image",
        "description": "Kullanıcının isteğine göre AI görseli üretir. Smart Router otomatik olarak en iyi modeli seçer: metin/logo/tipografi içeren promptlar için FLUX 2 Flex, genel görseller için Nano Banana Pro. Bir model başarısız olursa otomatik fallback yapılır. Eğer @tag ile referans verilen bir entity varsa, onun özelliklerini prompt'a ekle.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Görselin detaylı açıklaması (İngilizce olması daha iyi sonuç verir)."
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "21:9", "4:5", "5:4"],
                    "description": "Görselin en-boy oranı."
                },
                "model": {
                    "type": "string",
                    "enum": ["fal-ai/nano-banana-pro", "fal-ai/flux-2-flex"],
                    "description": "Opsiyonel: Belirli bir model seçimi. Belirtilmezse Smart Router otomatik seçer. FLUX 2 Flex metin render'da daha iyi, Nano Banana Pro fotogerçekçi."
                },
                "resolution": {
                    "type": "string",
                    "enum": ["1K", "2K", "4K"],
                    "description": "Görselin çözünürlüğü."
                },
                "additional_reference_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Kullanıcının gönderdiği referans görsele EK OLARAK eklenecek, internetten (search_images aracıyla) bulduğun referans resimlerin URL listesi (Multi-Image mantığı için)."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "create_character",
        "description": "Yeni bir karakter oluşturur ve hafızaya kaydeder. Kullanıcı görsel gönderip 'bunu kaydet' derse reference_image_url'yi mutlaka doldur.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Karakterin adı"},
                "description": {"type": "string", "description": "Karakterin detaylı görsel açıklaması (İngilizce)"},
                "reference_image_url": {"type": "string", "description": "Referans görsel URL'si"},
                "use_current_reference": {"type": "boolean", "description": "Mevcut referans görseli kullan"},
                "attributes": {"type": "object", "description": "Fiziksel ve kişilik özellikleri"}
            },
            "required": ["name", "description"]
        }
    },
    {
        "name": "create_location",
        "description": "Yeni bir mekan oluşturur ve hafızaya kaydeder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Mekanın adı"},
                "description": {"type": "string", "description": "Mekanın detaylı görsel açıklaması (İngilizce)"},
                "attributes": {"type": "object", "description": "Ek özellikler"}
            },
            "required": ["name", "description"]
        }
    },
    {
        "name": "get_entity",
        "description": "Kayıtlı bir entity hakkında bilgi getirir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Entity'nin tag'i (örn: @emre)"}
            },
            "required": ["tag"]
        }
    },
    {
        "name": "list_entities",
        "description": "Bu oturumdaki tüm kayıtlı karakterleri, mekanları ve markaları listeler.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "enum": ["character", "location", "brand", "all"],
                    "description": "Listelenecek entity tipi"
                }
            }
        }
    },
    {
        "name": "generate_video",
        "description": "Video üretir (ARKA PLAN GÖREVİ). Bu araç hemen video dönmez, üretimi arka planda başlatır. Üretim bittiğinde asistan otomatik olarak yeni bir mesajla videoyu paylaşacaktır. Kullanıcıya 'başlatıldı' bilgisi ver, ama 'hazır' deme. Modeller: veo (sinematik), kling (insan/lip-sync), luma (hızlı/rüya), runway (sanatsal), minimax (aksiyon).",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Video açıklaması"},
                "image_url": {"type": "string", "description": "Başlangıç görseli URL (opsiyonel)"},
                "duration": {"type": "string", "enum": ["3", "5", "10"], "description": "Video süresi"},
                "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1"], "description": "Video oranı"},
                "model": {
                    "type": "string", 
                    "enum": ["veo", "kling", "luma", "runway", "minimax"], 
                    "description": "Kullanılacak video modeli. Konsepte göre en uygun olanı seç. Belirtilmezse veo kullanılır."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "edit_video",
        "description": "Mevcut bir videoyu düzenler. Nesne kaldırma/değiştirme (inpainting), stil değiştirme (v2v) veya talimatlı düzenleme yapar. Asistan otomatik olarak en iyi yöntemi seçer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "Düzenlenecek videonun URL'si"},
                "prompt": {"type": "string", "description": "Düzenleme talimatı (örn: 'kadını sil', 'anime yap')"},
                "image_url": {"type": "string", "description": "Videonun referans görseli/thumbnail'i (Varsa mutlaka gönderilmeli, daha iyi sonuç verir)"}
            },
            "required": ["video_url", "prompt"]
        }
    },
    {
        "name": "generate_long_video",
        "description": "Uzun video üretir (30 saniye - 3 dakika, ARKA PLAN GÖREVİ). Çok aşamalı bir işlemdir ve arka planda yürütülür. Bittiğinde asistan videoyu yeni bir mesajla paylaşacaktır. Kullanıcıya 'üretim başladı' de, bittiğini iddia etme.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Video senaryosu / ana açıklama"},
                "total_duration": {"type": "integer", "description": "Hedef süre (saniye). Min: 30, Max: 180. Varsayılan: 60"},
                "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1"], "description": "Video oranı"},
                "scene_descriptions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Sahne açıklaması"},
                            "reference_image_url": {"type": "string", "description": "Sahne için kullanılacak referans görselin URL'si (search_images'dan vb.)"},
                            "model": {
                                "type": "string",
                                "enum": ["veo", "kling", "luma", "runway", "minimax"],
                                "description": "BU SAHNE için en uygun video modeli. Örn: Aksiyon için minimax, geçiş/rüya için luma, diyalog/insan yüzü için kling, sanatsal açılar için runway, en yüksek genel kalite için veo."
                            }
                        },
                        "required": ["prompt"]
                    },
                    "description": "Opsiyonel: Sahnelerin açıklamaları. Eğer bu sahne için internetten bulduğun harika bir görsel varsa, URL'sini ekle ki doğrudan Image-to-Video (i2v) yapılsın!"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "edit_image",
        "description": "Mevcut bir görseli akıllı düzenleme ile düzenler (Gemini True Inpainting birincil, fallback: FLUX Kontext, Object Removal). Kıyafet değiştirme, nesne ekleme/çıkarma, renk değiştirme gibi işlemler için ideal. PROMPT ÖNEMLİ: Kısa talimatları zenginleştir! Örn: 'gözlüğü sil' → 'Remove the sunglasses, keep the exact same face, pose, lighting, background unchanged.'",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Düzenlenecek görselin URL'si"},
                "prompt": {"type": "string", "description": "Detaylı düzenleme talimatı (İngilizce). KISA YAZMA! Neyin değişeceğini VE neyin korunacağını açıkça belirt. Örn: 'Change the shirt color to blue. Keep the exact same face, pose, angle, background, and all other details unchanged.'"}
            },
            "required": ["image_url", "prompt"]
        }
    },
    {
        "name": "upscale_image",
        "description": "Görsel kalitesini ve çözünürlüğünü artırır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Upscale edilecek görselin URL'si"},
                "scale": {"type": "integer", "enum": [2, 4], "description": "Büyütme faktörü"}
            },
            "required": ["image_url"]
        }
    },
    {
        "name": "remove_background",
        "description": "Görselin arka planını kaldırır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Arka planı kaldırılacak görselin URL'si"}
            },
            "required": ["image_url"]
        }
    },
    {
        "name": "delete_entity",
        "description": "Bir karakteri veya mekanı sil. ÖNEMLİ: Eğer kullanıcı 'karakterleri sil' gibi ÇOĞUL bir ifade kullanırsa, oluşturulmuş olan (veya panelde görünen) tüm hedeflenen entity'ler için BU ARACI PARALEL OLARAK BİRDEN FAZLA KEZ ÇAĞIR.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_tag": {"type": "string", "description": "Silinecek entity'nin tag'i (örn: @emre, @kisi_1)"}
            },
            "required": ["entity_tag"]
        }
    },
    {
        "name": "manage_wardrobe",
        "description": "Wardrobe (kıyafet) yönetimi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "remove", "list"], "description": "İşlem"},
                "wardrobe_id": {"type": "string", "description": "Kıyafet ID"},
                "name": {"type": "string", "description": "Kıyafet adı"},
                "description": {"type": "string", "description": "Kıyafet açıklaması"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "create_brand",
        "description": "Yeni bir marka oluşturur ve hafızaya kaydeder. Kullanıcı marka bilgilerini verdiğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Markanın adı (örn: Nike, Apple)"},
                "description": {"type": "string", "description": "Markanın kısa açıklaması ve kimliği"},
                "logo_url": {"type": "string", "description": "Logo görseli URL'si (opsiyonel)"},
                "attributes": {
                    "type": "object",
                    "description": "Marka özellikleri",
                    "properties": {
                        "colors": {
                            "type": "object",
                            "properties": {
                                "primary": {"type": "string", "description": "Ana renk (hex kodu)"},
                                "secondary": {"type": "string", "description": "İkincil renk"},
                                "accent": {"type": "string", "description": "Vurgu rengi"}
                            }
                        },
                        "tagline": {"type": "string", "description": "Slogan (örn: Just Do It)"},
                        "industry": {"type": "string", "description": "Sektör (örn: Spor Giyim, Teknoloji)"},
                        "tone": {"type": "string", "description": "Marka tonu (örn: Dinamik, Lüks, Samimi)"},
                        "target_audience": {"type": "string", "description": "Hedef kitle"},
                        "fonts": {"type": "array", "items": {"type": "string"}, "description": "Kullanılan fontlar"},
                        "social_media": {
                            "type": "object",
                            "properties": {
                                "instagram": {"type": "string"},
                                "twitter": {"type": "string"},
                                "website": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "required": ["name", "description"]
        }
    },
    {
        "name": "research_brand",
        "description": "Web'den bir marka hakkında araştırma yapar ve bilgileri çıkartır. Sosyal medya hesaplarını, renk paletini, içerik stilini analiz eder. Araştırma sonuçlarını kaydetmek için save=true kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand_name": {"type": "string", "description": "Araştırılacak markanın adı"},
                "research_depth": {
                    "type": "string",
                    "enum": ["basic", "detailed", "comprehensive"],
                    "description": "basic: sadece temel bilgiler, detailed: sosyal medya dahil, comprehensive: içerik analizi dahil"
                },
                "save": {"type": "boolean", "description": "Araştırma sonucunu marka olarak kaydet"}
            },
            "required": ["brand_name"]
        }
    },
    {
        "name": "generate_grid",
        "description": "3x3 grid oluşturur. 9 farklı kamera açısı (angles) veya 9 hikaye paneli (storyboard) üretir. @karakter referansı ile otomatik görsel kullanır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Referans görsel URL'si (entity tag varsa otomatik alınır)"},
                "mode": {
                    "type": "string",
                    "enum": ["angles", "storyboard"],
                    "description": "Grid modu: angles (9 kamera açısı) veya storyboard (9 hikaye paneli)"
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["16:9", "9:16", "1:1"],
                    "description": "Grid görselinin en-boy oranı"
                },
                "custom_prompt": {"type": "string", "description": "Özel grid promptu (opsiyonel)"}
            }
        }
    },
    {
        "name": "use_grid_panel",
        "description": "Oluşturulmuş grid'den belirli bir paneli seçip işlem yapar. Panel numarası 1-9 arası (3x3: üst-sol=1, alt-sağ=9).",
        "input_schema": {
            "type": "object",
            "properties": {
                "panel_number": {
                    "type": "integer",
                    "description": "Seçilecek panel numarası (1-9). Grid düzeni: 1|2|3 / 4|5|6 / 7|8|9"
                },
                "action": {
                    "type": "string",
                    "enum": ["video", "upscale", "download", "edit"],
                    "description": "Panele uygulanacak işlem: video üret, upscale et, indir veya düzenle"
                },
                "video_prompt": {"type": "string", "description": "Video için hareket/animasyon açıklaması (action=video ise)"},
                "edit_prompt": {"type": "string", "description": "Düzenleme promptu (action=edit ise)"}
            },
            "required": ["panel_number", "action"]
        }
    },
    {
        "name": "semantic_search",
        "description": "Semantik olarak benzer karakterleri, mekanları veya markaları arar. Doğal dil sorgusu ile ilgili entity'leri bulur. Örnek: 'sarışın erkek karakter', 'plaj mekanı', 'spor markası'",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Doğal dil arama sorgusu (örn: 'uzun boylu, atletik erkek karakterler')"
                },
                "entity_type": {
                    "type": "string",
                    "enum": ["character", "location", "brand", "wardrobe", "all"],
                    "description": "Aranacak entity tipi (varsayılan: all)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maksimum sonuç sayısı (varsayılan: 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_library_docs",
        "description": "Herhangi bir kütüphanenin (library) güncel API dokümantasyonunu çeker. LLM'lerin eski/yanlış bilgi üretmesini engeller. Örn: 'react', 'nextjs', 'fastapi', 'fal.ai', 'langchain' gibi popüler kütüphaneler için kullanılabilir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "library_name": {
                    "type": "string",
                    "description": "Dokümantasyonu çekilecek kütüphane adı (örn: 'react', 'nextjs', 'fastapi', 'fal-ai')"
                },
                "query": {
                    "type": "string",
                    "description": "Spesifik bir sorgu veya konu (opsiyonel). Örn: 'hooks', 'routing', 'authentication'"
                },
                "tokens": {
                    "type": "integer",
                    "description": "Döndürülecek maksimum token sayısı (varsayılan: 5000)"
                }
            },
            "required": ["library_name"]
        }
    },
    {
        "name": "save_style",
        "description": "Bir stil/moodboard kaydet. Kaydedilen stil sonraki tüm üretimlerde otomatik uygulanır. Örn: 'cyberpunk stili', 'minimalist beyaz', 'retro 80s'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Stil adı (örn: 'cyberpunk', 'minimalist')"},
                "description": {"type": "string", "description": "Stilin detaylı açıklaması (İngilizce). Renkler, ton, atmosfer, ışık, doku vb."},
                "color_palette": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Renk paleti (hex kodları, opsiyonel)"
                },
                "reference_image_url": {"type": "string", "description": "Referans görsel URL (opsiyonel)"}
            },
            "required": ["name", "description"]
        }
    },
    {
        "name": "generate_campaign",
        "description": "Toplu kampanya üretimi. Tek prompt ile birden fazla varyasyon üretir (farklı açılar, formatlar). Instagram, TikTok, YouTube için optimized boyutlarda.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Kampanya açıklaması / ana konsept"},
                "count": {"type": "integer", "description": "Kaç varyasyon üretilsin (varsayılan: 4, max: 9)"},
                "formats": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["post", "story", "reel", "cover"]},
                    "description": "Üretilecek formatlar. post=1:1, story=9:16, reel=9:16, cover=16:9"
                },
                "brand_tag": {"type": "string", "description": "Marka entity tag'i (opsiyonel, örn: @nike)"}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "transcribe_voice",
        "description": "Sesli mesajı metne çevirir (Whisper API). Kullanıcı ses kaydı gönderdiğinde otomatik kullanılır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_url": {"type": "string", "description": "Ses dosyasının URL'si"},
                "language": {"type": "string", "description": "Dil kodu (varsayılan: 'tr'). 'tr', 'en', 'auto'"}
            },
            "required": ["audio_url"]
        }
    },
    {
        "name": "add_audio_to_video",
        "description": "Video'ya ses/müzik ekler veya seslendirme yapar (TTS). Mevcut bir videoya arka plan müziği, seslendirme veya ses efekti ekler.",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "Video URL'si"},
                "audio_type": {
                    "type": "string",
                    "enum": ["tts", "music", "effect"],
                    "description": "Ses tipi: tts=seslendirme, music=müzik, effect=ses efekti"
                },
                "text": {"type": "string", "description": "TTS için seslendirme metni (audio_type=tts ise zorunlu)"},
                "music_style": {"type": "string", "description": "Müzik stili (audio_type=music ise, örn: 'cinematic', 'upbeat', 'ambient')"},
                "voice": {"type": "string", "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], "description": "TTS ses tonu (varsayılan: 'nova')"}
            },
            "required": ["video_url", "audio_type"]
        }
    },
    {
        "name": "outpaint_image",
        "description": "Görseli genişletir (outpainting). Görselin kenarlarına yeni içerik ekleyerek boyutunu büyütür. Kırpılmış görselleri genişletme, yatay→dikey dönüşüm, panoramik genişletme için kullan. Yön belirtilmezse her yöne 256px genişletir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Genişletilecek görselin URL'si"},
                "prompt": {"type": "string", "description": "Genişletilen alana ne eklenmeli (opsiyonel)"},
                "left": {"type": "integer", "description": "Sola genişletme miktarı (piksel)"},
                "right": {"type": "integer", "description": "Sağa genişletme miktarı (piksel)"},
                "top": {"type": "integer", "description": "Yukarı genişletme miktarı (piksel)"},
                "bottom": {"type": "integer", "description": "Aşağı genişletme miktarı (piksel)"}
            },
            "required": ["image_url"]
        }
    },
    {
        "name": "apply_style",
        "description": "Görsele sanatsal stil uygular (style transfer). Empresyonizm, kübizm, sürrealizm, anime, çizgi film, yağlı boya, suluboya, pixel art gibi stiller uygulanabilir. Moodboard stili aktarımı için de kullanılabilir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Stil uygulanacak görselin URL'si"},
                "style": {"type": "string", "description": "Uygulanacak stil (örn: 'impressionism', 'anime', 'oil painting', 'watercolor', 'pixel art', 'cyberpunk')"},
                "prompt": {"type": "string", "description": "Ek stil açıklaması (opsiyonel)"}
            },
            "required": ["image_url", "style"]
        }
    },
    {
        "name": "manage_plugin",
        "description": "Creative Plugin yönetimi. Kullanıcı 'plugin oluştur' dediğinde sohbetteki mevcut bilgileri (karakter, lokasyon, stil vb.) toplayıp HEMEN bir plugin oluştur. Tüm alanların dolu olması GEREKMEZ — elindeki ne varsa onu kullan. Eksik alan engellemez, plugin oluşturulur.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "delete"],
                    "description": "İşlem tipi"
                },
                "name": {
                    "type": "string",
                    "description": "Plugin adı (create için zorunlu)"
                },
                "description": {
                    "type": "string",
                    "description": "Plugin açıklaması (opsiyonel)"
                },
                "plugin_id": {
                    "type": "string",
                    "description": "Silinecek plugin ID (delete için)"
                },
                "config": {
                    "type": "object",
                    "description": "Plugin ayarları — hepsinin dolu olması gerekmez, mevcut olanları gönder",
                    "properties": {
                        "style": {"type": "string", "description": "Görsel stil (örn: cinematic, anime, minimalist)"},
                        "character_tag": {"type": "string", "description": "Karakter entity tag'i (örn: @emre)"},
                        "location_tag": {"type": "string", "description": "Lokasyon entity tag'i (örn: @paris)"},
                        "timeOfDay": {"type": "string", "description": "Zaman dilimi (örn: golden hour, gece)"},
                        "cameraAngles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Kamera açıları listesi"
                        },
                        "promptTemplate": {"type": "string", "description": "Prompt şablonu — kullanıcının sohbetteki isteğinden oluştur"},
                        "aspectRatio": {"type": "string", "description": "En-boy oranı"},
                        "model": {"type": "string", "description": "Tercih edilen model"}
                    }
                },
                "is_public": {
                    "type": "boolean",
                    "description": "Marketplace'te herkese açık mı (varsayılan: false)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "manage_core_memory",
        "description": "Kullanıcının kendisi hakkında verdiği bilgileri kalıcı hafızada (Core Memory) yönetir. Kullanıcı bir tercihi belirtirse ekle (add). Fikrini değiştirirse veya silmeni isterse sil (delete). Tüm hafızayı sıfırlamak isterse temizle (clear).",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "delete", "clear"],
                    "description": "İşlem tipi. Yeni bilgi eklemek için 'add', eski bir bilgiyi unutmak için 'delete', her şeyi sıfırlamak için 'clear'."
                },
                "fact_category": {
                    "type": "string",
                    "enum": ["style", "identity", "brand", "general", "workflow"],
                    "description": "Bilginin kategorisi (sadece 'add' işleminde gereklidir)"
                },
                "fact_description": {
                    "type": "string",
                    "description": "Kaydedilecek veya SİLİNECEK bilgi içeriği (örn: 'Kullanıcı Nike markası için çalışıyor'). 'clear' işleminde boş kalabilir."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "search_web",
        "description": "DuckDuckGo üzerinden internette genel metin araması yapar. Bilinmeyen kavramları, konuları, son dakika olaylarını araştırmak için kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Arama terimi"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Kaç sonuç getirileceği (varsayılan: 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_images",
        "description": "DuckDuckGo Görsel Arama üzerinden internetten resimler bulur. Resim linklerini (URL) döner. Bir karakterin/kişinin/objenin referans resimlerini (dövmeleri, vücut yapısı vs.) bulmak için kullanırsan, bu URL'leri `generate_image` çağrısındaki `additional_reference_urls` içerisine verebilirsin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Arama terimi (örn: 'johnny depp tattoos shirtless', 'golden retriever running high quality')"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Kaç resim sonucunun URL'si getirilsin (varsayılan: 3)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "analyze_image",
        "description": "GPT-4o Vision ile bir görseli SON DERECE DETAYLI analiz eder. Görseldeki her şeyi okur: yazılar, logolar, yüz ifadeleri, kıyafetler, mekan detayları, renkler, ışık, objelerin konumları, arka plan, kompozisyon. Bu aracı şu durumlarda kullan: (1) Üretilen görselde hata/eksik aranırken, (2) Kullanıcı 'bunu düzelt/değiştir' dediğinde mevcut görseli analiz etmek için, (3) Referans görsel detaylarını öğrenmek için.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "Analiz edilecek resmin URL adresi"
                },
                "question": {
                    "type": "string",
                    "description": "Modele resimle ilgili soracağın açık, spesifik soru. Detaylı analiz için: 'Bu görseldeki her şeyi detaylıca listele: yazılar, kişiler, objeler, renkler, ışık, arka plan, kompozisyon, varsa hatalar.'"
                }
            },
            "required": ["image_url", "question"]
        }
    },
    {
        "name": "analyze_video",
        "description": "Bir video URL'sinden key frame'ler çıkararak GPT-4o Vision ile videoyu analiz eder. Videodaki sahneleri, hareketleri, yazıları, hataları, eksikleri tespit eder. Bu aracı şu durumlarda kullan: (1) Üretilen videoda sorun aranırken, (2) Kullanıcı 'bu videodaki yazıyı değiştir' dediğinde, (3) Referans video/klip içeriğini anlamak için, (4) Videonun kalitesini ve promptla uyumunu kontrol etmek için.",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "Analiz edilecek videonun URL adresi"
                },
                "question": {
                    "type": "string",
                    "description": "Video hakkında sorulacak soru. Örn: 'Bu videoda neler oluyor, sahneleri listele', 'Videodaki yazıları oku', 'Sahne geçişlerini ve hareketleri anlat'"
                },
                "num_frames": {
                    "type": "integer",
                    "description": "Videodan kaç frame çıkarılsın (varsayılan: 6, max: 12). Kısa videolar için 4, uzun için 8-12 önerilir."
                }
            },
            "required": ["video_url", "question"]
        }
    },
    {
        "name": "save_web_asset",
        "description": "Webt'en bulduğun veya kullanıcının çok beğeneceği bir resim URL'sini doğrudan sistemdeki (DB) Media Asset'lere kalıcı olarak kaydeder. Kullanıcı 'bu resmi bana indir/panelime kaydet' dediğinde bunu kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "asset_url": {
                    "type": "string",
                    "description": "Kaydedilecek dosyanın kalıcı URL linki"
                },
                "asset_type": {
                    "type": "string",
                    "enum": ["image", "video"],
                    "description": "Medyanın türü"
                }
            },
            "required": ["asset_url", "asset_type"]
        }
    },
    {
        "name": "generate_music",
        "description": "AI ile müzik/şarkı üretir (MiniMax Music). Metin promptundan profesyonel kalitede müzik oluşturur. Klip, reklam, içerik senesine uygun müzik üretmek için kullan. Şarkı sözleri de verilebilir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Müzik açıklaması. Örn: 'Upbeat electronic dance music with synth leads, energetic and modern, 120 BPM' veya 'Gentle acoustic guitar melody, warm and intimate, folk style'"
                },
                "lyrics": {
                    "type": "string",
                    "description": "Opsiyonel şarkı sözleri. [Verse], [Chorus], [Bridge] yapı etiketleri kullanılabilir."
                },
                "duration": {
                    "type": "integer",
                    "description": "Müzik süresi (saniye). Varsayılan: 30, max: 120"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "add_audio_to_video",
        "description": "Bir videoya müzik/ses ekler veya mevcut sesi değiştirir. Üretilen müziği veya herhangi bir ses dosyasını videoya birleştirir (ffmpeg ile). Kullanıcı 'videoya müzik ekle' veya 'videoyu bu müzikle birleştir' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "Müzik eklenecek videonun URL'si"
                },
                "audio_url": {
                    "type": "string",
                    "description": "Eklenecek müzik/ses dosyasının URL'si"
                },
                "replace_audio": {
                    "type": "boolean",
                    "description": "true: Mevcut sesi tamamen değiştir. false: Üstüne ekle (mix). Varsayılan: true"
                }
            },
            "required": ["video_url", "audio_url"]
        }
    }
]

# OpenAI tools formatı
AGENT_TOOLS = convert_to_openai_tools(AGENT_TOOLS_ANTHROPIC)

