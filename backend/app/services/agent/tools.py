"""
Agent tarafından kullanılabilen araçların tanımları.
"""

# Agent'a sunulacak araçların listesi (JSON Schema formatında)
AGENT_TOOLS = [
    {
        "name": "generate_image",
        "description": "Kullanıcının isteğine göre AI görseli üretir (Nano Banana Pro). Karakter, mekan veya herhangi bir sahne çizmek için kullanılır. Eğer @tag ile referans verilen bir entity varsa, onun özelliklerini prompt'a ekle.",
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
                    "default": "1:1",
                    "description": "Görselin en-boy oranı."
                },
                "resolution": {
                    "type": "string",
                    "enum": ["1K", "2K", "4K"],
                    "default": "1K",
                    "description": "Görselin çözünürlüğü."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "create_character",
        "description": "Yeni bir karakter oluşturur ve hafızaya kaydeder. ÖNEMLI: Kullanıcı bir görsel ile karakter oluşturmak istediğinde, MUTLAKA önce görseli bir URL'ye yükle (veya current_reference_image parametresini kullan) ve reference_image_url'e kaydet. Bu görseli sonraki isteklerde kullanabilirsin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Karakterin adı (örn: Emre, Ayşe, Robot-X)"
                },
                "description": {
                    "type": "string",
                    "description": "Karakterin detaylı görsel açıklaması (İngilizce). Tüm fiziksel özellikleri dahil et."
                },
                "reference_image_url": {
                    "type": "string",
                    "description": "Karakterin yüz/vücut referans görsel URL'si. KRITIK: Kullanıcı foto gönderip 'bunu kaydet' derse, bu URL'yi mutlaka doldur. Bu görsel daha sonra yüz tanıma için kullanılır."
                },
                "use_current_reference": {
                    "type": "boolean",
                    "default": False,
                    "description": "True ise, kullanıcının gönderdiği referans görseli otomatik olarak bu karaktere bağla."
                },
                "attributes": {
                    "type": "object",
                    "description": "Fiziksel ve kişilik özellikleri. Kullanıcının söylediği tüm detayları buraya kaydet.",
                    "properties": {
                        "eye_color": {
                            "type": "string",
                            "description": "Göz rengi (örn: blue, green, brown, hazel)"
                        },
                        "eyebrow_color": {
                            "type": "string",
                            "description": "Kaş rengi (örn: black, brown, blonde)"
                        },
                        "eyebrow_shape": {
                            "type": "string",
                            "description": "Kaş şekli (örn: thick, thin, arched, straight)"
                        },
                        "hair_color": {
                            "type": "string",
                            "description": "Saç rengi (örn: black, brown, blonde, red)"
                        },
                        "hair_style": {
                            "type": "string",
                            "description": "Saç stili (örn: long wavy, short curly, bald, ponytail)"
                        },
                        "skin_tone": {
                            "type": "string",
                            "description": "Ten rengi (örn: fair, olive, tan, dark)"
                        },
                        "facial_features": {
                            "type": "string",
                            "description": "Yüz özellikleri (örn: sharp jawline, high cheekbones, full lips)"
                        },
                        "age": {
                            "type": "string",
                            "description": "Yaş veya yaş aralığı (örn: 25, mid-30s, elderly)"
                        },
                        "gender": {
                            "type": "string",
                            "description": "Cinsiyet (örn: male, female, non-binary)"
                        },
                        "body_type": {
                            "type": "string",
                            "description": "Vücut tipi (örn: slim, athletic, muscular, curvy)"
                        },
                        "height": {
                            "type": "string",
                            "description": "Boy (örn: tall, short, average height)"
                        },
                        "clothing_style": {
                            "type": "string",
                            "description": "Giyim stili (örn: casual, formal, bohemian)"
                        },
                        "occupation": {
                            "type": "string",
                            "description": "Meslek"
                        },
                        "personality": {
                            "type": "string",
                            "description": "Kişilik özellikleri"
                        }
                    }
                }
            },
            "required": ["name", "description"]
        }
    },
    {
        "name": "create_location",
        "description": "Yeni bir mekan oluşturur ve hafızaya kaydeder. Mekan daha sonra @tag ile referans verilebilir. Örnek: 'Orman' mekanı oluşturulursa @location_orman tag'i ile çağrılabilir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Mekanın adı (örn: Orman, Mutfak, Uzay İstasyonu)"
                },
                "description": {
                    "type": "string",
                    "description": "Mekanın detaylı görsel açıklaması (İngilizce). Örn: 'A dark mystical forest with tall pine trees, foggy atmosphere, moonlight'"
                },
                "attributes": {
                    "type": "object",
                    "description": "Ek özellikler (zaman, hava durumu, vb.)",
                    "properties": {
                        "time_of_day": {"type": "string"},
                        "weather": {"type": "string"},
                        "mood": {"type": "string"}
                    }
                }
            },
            "required": ["name", "description"]
        }
    },
    {
        "name": "get_entity",
        "description": "Kayıtlı bir entity (karakter veya mekan) hakkında bilgi getirir. @tag formatıyla sorgulama yapılır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tag": {
                    "type": "string",
                    "description": "Entity'nin tag'i (örn: @emre, @mutfak, @orman)"
                }
            },
            "required": ["tag"]
        }
    },
    {
        "name": "list_entities",
        "description": "Bu oturumdaki tüm kayıtlı karakterleri ve mekanları listeler.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "enum": ["character", "location", "all"],
                    "default": "all",
                    "description": "Listelenecek entity tipi"
                }
            }
        }
    },
    
    # ===============================
    # YENİ ARAÇLAR - Video, Edit, Upscale
    # ===============================
    
    {
        "name": "generate_video",
        "description": "Video üretir. Görsel veya metinden video oluşturur. Kling 2.5 Turbo Pro kullanılır. Örnek: '@emre ormanda yürüyor videosu yap'",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Video açıklaması (İngilizce önerilir). Hareket ve aksiyon detayları ekle."
                },
                "image_url": {
                    "type": "string",
                    "description": "Başlangıç görseli URL (opsiyonel). Varsa image-to-video üretilir."
                },
                "duration": {
                    "type": "string",
                    "enum": ["3", "5", "10"],
                    "default": "5",
                    "description": "Video süresi (saniye)"
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["16:9", "9:16", "1:1"],
                    "default": "16:9",
                    "description": "Video oranı"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "edit_image",
        "description": "Mevcut bir görseli düzenler. Arka plan değiştirme, stil dönüşümü, nesne ekleme/çıkarma. Nano Banana Edit kullanılır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "Düzenlenecek görselin URL'si"
                },
                "prompt": {
                    "type": "string",
                    "description": "Düzenleme talimatı. Örn: 'Change the background to a beach sunset'"
                }
            },
            "required": ["image_url", "prompt"]
        }
    },
    {
        "name": "upscale_image",
        "description": "Görsel kalitesini ve çözünürlüğünü artırır. Topaz kullanılır. Düşük kaliteli görselleri iyileştirir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "Upscale edilecek görselin URL'si"
                },
                "scale": {
                    "type": "integer",
                    "enum": [2, 4],
                    "default": 2,
                    "description": "Büyütme faktörü (2x veya 4x)"
                }
            },
            "required": ["image_url"]
        }
    },
    {
        "name": "remove_background",
        "description": "Görselin arka planını kaldırır ve şeffaf PNG oluşturur. Ürün fotoğrafları veya karakter görselleri için kullanışlı.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "Arka planı kaldırılacak görselin URL'si"
                }
            },
            "required": ["image_url"]
        }
    },
    {
        "name": "generate_grid",
        "description": "3x3 grid görsel oluşturur. 9 farklı kamera açısı (angles) veya 9 hikaye paneli (storyboard) üretir. Verilen görselden veya @karakterden grid oluşturur. Panel extraction ve upscale özelliği var.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "Kaynak görselin URL'si. @karakter tag'i kullanıldığında otomatik doldurulur."
                },
                "mode": {
                    "type": "string",
                    "enum": ["angles", "storyboard"],
                    "default": "angles",
                    "description": "Grid tipi: 'angles' = 9 farklı kamera açısı, 'storyboard' = 9 hikaye paneli"
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["16:9", "9:16", "1:1"],
                    "default": "16:9",
                    "description": "Grid oranı"
                },
                "extract_panel": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                    "description": "Opsiyonel: Grid oluşturulduktan sonra belirtilen paneli (1-9) upscale edip döndür"
                },
                "scale": {
                    "type": "integer",
                    "enum": [1, 2, 4],
                    "default": 2,
                    "description": "Panel extraction için upscale faktörü"
                },
                "custom_prompt": {
                    "type": "string",
                    "description": "Opsiyonel: Özel prompt. Varsayılan prompt yerine kullanılır."
                }
            },
            "required": ["image_url"]
        }
    },
    
    # ===============================
    # WEB ARAMA ARAÇLARI
    # ===============================
    
    {
        "name": "search_images",
        "description": "İnternetten GÖRSEL arar. Marka/ürün fotoğrafları, referans görseller bulmak için kullan. Örnek: 'Samsung TV product photo', 'Nike shoes', 'luxury car interior'",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Aranacak terim (İngilizce önerilir)"
                },
                "num_results": {
                    "type": "integer",
                    "enum": [3, 5, 10],
                    "default": 5,
                    "description": "Döndürülecek sonuç sayısı"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_web",
        "description": "İnternette genel METİN araması yapar (DuckDuckGo). Bilgi, haber, makale bulmak için kullan. Güncel olaylar, ürün bilgileri, teknik detaylar için.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Aranacak terim veya soru"
                },
                "num_results": {
                    "type": "integer",
                    "enum": [3, 5, 10],
                    "default": 5,
                    "description": "Döndürülecek sonuç sayısı"
                },
                "region": {
                    "type": "string",
                    "enum": ["tr-tr", "us-en", "uk-en", "de-de"],
                    "default": "tr-tr",
                    "description": "Arama bölgesi"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_videos",
        "description": "İnternetten VİDEO arar. YouTube, Vimeo vb. kaynaklardan video bulmak için kullan. Referans video, örnek sahne bulmak için.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Aranacak terim"
                },
                "num_results": {
                    "type": "integer",
                    "enum": [3, 5, 10],
                    "default": 5,
                    "description": "Döndürülecek sonuç sayısı"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "browse_url",
        "description": "Belirtilen URL'ye gider ve sayfa içeriğini okur. Makale, haber, ürün sayfası vb. okumak için kullan. HTML'i temiz metne çevirir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Okunacak web sayfasının URL'si"
                },
                "extract_images": {
                    "type": "boolean",
                    "default": False,
                    "description": "True ise sayfadaki görselleri de listele"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "fetch_web_image",
        "description": "Web'den görsel indirir ve sisteme kaydeder. search_images sonucundaki URL'yi al, indir. Ardından edit_image veya generate_video ile kullanabilirsin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "İndirilecek görselin URL'si"
                },
                "save_as_entity": {
                    "type": "boolean",
                    "default": False,
                    "description": "True ise görseli bir entity'ye referans olarak kaydet"
                },
                "entity_name": {
                    "type": "string",
                    "description": "save_as_entity=True ise entity adı"
                }
            },
            "required": ["image_url"]
        }
    },
    
    # ===============================
    # AKILLI AGENT ARAÇLARI
    # ===============================
    
    {
        "name": "get_past_assets",
        "description": "Bu oturumdaki geçmiş üretimleri (görseller/videolar) getirir. Kullanıcı 'dünkü görseli göster', 'önceki üretimleri listele' gibi isteklerde bulunduğunda kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_tag": {
                    "type": "string",
                    "description": "Belirli bir entity'ye ait olanları getir (örn: @emre, @mutfak). Opsiyonel."
                },
                "asset_type": {
                    "type": "string",
                    "enum": ["image", "video"],
                    "description": "Sadece görsel veya sadece video getir. Opsiyonel."
                },
                "favorites_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Sadece favori işaretli olanları getir."
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maksimum kaç adet getirileceği."
                }
            }
        }
    },
    {
        "name": "mark_favorite",
        "description": "Bir görseli/videoyu favori olarak işaretle. Kullanıcı 'bu çok güzel', 'bunu beğendim', 'favorilere ekle' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "asset_url": {
                    "type": "string",
                    "description": "Favori yapılacak asset'in URL'si. Son üretilen asset için boş bırakılabilir."
                }
            }
        }
    },
    {
        "name": "undo_last",
        "description": "Son yapılan işlemi geri al ve önceki versiyona dön. Kullanıcı 'geri al', 'önceki daha iyiydi', 'bir öncekine dön' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    # ===============================
    # GÖRSEL MUHAKEME ARAÇLARI
    # ===============================
    {
        "name": "analyze_image",
        "description": "Bir görseli analiz et ve kalite kontrolü yap. Görseldeki yüz, kompozisyon, bozukluk gibi sorunları tespit eder. Agent üretim sonrası otomatik kalite kontrolü için veya kullanıcı 'bu görsel nasıl?' diye sorduğunda kullanır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "Analiz edilecek görselin URL'si."
                },
                "check_quality": {
                    "type": "boolean",
                    "default": True,
                    "description": "Kalite kontrolü modu - yüz, kompozisyon ve sorunları analiz eder."
                }
            },
            "required": ["image_url"]
        }
    },
    {
        "name": "compare_images",
        "description": "İki görseli karşılaştır ve hangisinin daha iyi olduğunu belirle. Kullanıcı 'hangisi daha iyi?', 'bunları karşılaştır' dediğinde veya önceki/şimdiki versiyonları kıyaslamak için kullanılır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url_1": {
                    "type": "string",
                    "description": "Birinci görselin URL'si."
                },
                "image_url_2": {
                    "type": "string",
                    "description": "İkinci görselin URL'si."
                }
            },
            "required": ["image_url_1", "image_url_2"]
        }
    },
    # ===============================
    # ROADMAP / GÖREV PLANLAMA
    # ===============================
    {
        "name": "create_roadmap",
        "description": "Karmaşık istekler için çoklu adım görev planı (roadmap) oluştur. Örnek: '3 dakikalık video yap' isteği için: 1) Senaryo oluştur 2) Sahneleri üret 3) Videoları birleştir. Agent büyük işleri parçalara ayırıp sırayla yürütmek için kullanır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "Ana hedef - kullanıcının ne istediğinin özeti."
                },
                "steps": {
                    "type": "array",
                    "description": "Adım adım görev listesi.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["generate_image", "generate_video", "edit_image", "upscale", "analyze", "web_scrape", "custom"],
                                "description": "Görev tipi."
                            },
                            "description": {
                                "type": "string",
                                "description": "Görevin açıklaması."
                            },
                            "params": {
                                "type": "object",
                                "description": "Göreve özel parametreler (opsiyonel)."
                            }
                        },
                        "required": ["type", "description"]
                    }
                }
            },
            "required": ["goal", "steps"]
        }
    },
    {
        "name": "get_roadmap_progress",
        "description": "Mevcut roadmap'in ilerleme durumunu getir. Kullanıcı 'ne durumda?', 'ilerleme nasıl?' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "roadmap_id": {
                    "type": "string",
                    "description": "Roadmap ID'si. Belirtilmezse son aktif roadmap kullanılır."
                }
            }
        }
    },
    
    # ===============================
    # SİSTEM YÖNETİM ARAÇLARI
    # ===============================
    
    {
        "name": "manage_project",
        "description": "Proje oluştur, sil, değiştir veya listele. Kullanıcı 'yeni proje aç', 'projeleri göster', 'Samsung projesine geç', 'bu projeyi sil' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "delete", "switch", "rename", "list"],
                    "description": "Yapılacak işlem"
                },
                "project_name": {
                    "type": "string",
                    "description": "Proje adı (create/rename için)"
                },
                "project_id": {
                    "type": "string",
                    "description": "Proje ID (delete/switch/rename için)"
                },
                "new_name": {
                    "type": "string",
                    "description": "Yeni proje adı (rename için)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "delete_entity",
        "description": "Bir karakteri veya mekanı sil (çöp kutusuna gider). Kullanıcı 'Emre'yi sil', 'bu mekanı kaldır' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_tag": {
                    "type": "string",
                    "description": "Silinecek entity'nin tag'i (örn: @emre, @mutfak)"
                }
            },
            "required": ["entity_tag"]
        }
    },
    {
        "name": "manage_trash",
        "description": "Çöp kutusu işlemleri. Silinen öğeleri göster, geri getir veya kalıcı olarak sil. Kullanıcı 'çöpü göster', 'Emre'yi geri getir', 'çöpü boşalt' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "restore", "delete_permanently", "empty"],
                    "description": "Yapılacak işlem"
                },
                "item_id": {
                    "type": "string",
                    "description": "Öğe ID (restore/delete_permanently için)"
                },
                "item_type": {
                    "type": "string",
                    "enum": ["character", "location", "asset", "plugin"],
                    "description": "Öğe tipi (filtreleme için, opsiyonel)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "manage_plugin",
        "description": "Creative Plugin oluştur, sil veya listele. Kullanıcı 'bunu plugin yap', 'plugin oluştur', 'pluginleri göster' dediğinde kullan. Plugin oluştururken chat context'inden stil, kamera açısı, zaman dilimi çıkar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "delete", "list", "update"],
                    "description": "Yapılacak işlem"
                },
                "plugin_id": {
                    "type": "string",
                    "description": "Plugin ID (delete/update için)"
                },
                "name": {
                    "type": "string",
                    "description": "Plugin adı (create için)"
                },
                "description": {
                    "type": "string",
                    "description": "Plugin açıklaması"
                },
                "config": {
                    "type": "object",
                    "description": "Plugin ayarları",
                    "properties": {
                        "style": {
                            "type": "string",
                            "description": "Görsel stili (örn: cinematic, anime, realistic)"
                        },
                        "camera_angles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Kamera açıları listesi (örn: ['wide shot', 'close-up'])"
                        },
                        "time_of_day": {
                            "type": "string",
                            "description": "Zaman dilimi (örn: golden hour, night, dawn)"
                        },
                        "mood": {
                            "type": "string",
                            "description": "Genel atmosfer (örn: dramatic, peaceful, energetic)"
                        },
                        "color_palette": {
                            "type": "string",
                            "description": "Renk paleti (örn: warm tones, cool blues, high contrast)"
                        },
                        "characters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "İlişkili karakter tag'leri"
                        },
                        "locations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "İlişkili mekan tag'leri"
                        }
                    }
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "get_system_state",
        "description": "Sistemin mevcut durumunu öğren: aktif proje, mevcut karakterler, mekanlar, son üretimler, toplam istatistikler. Kullanıcı 'ne var?', 'durumu göster', 'elimde ne var?' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "include_assets": {
                    "type": "boolean",
                    "default": True,
                    "description": "Son üretimleri dahil et"
                },
                "include_entities": {
                    "type": "boolean",
                    "default": True,
                    "description": "Karakter ve mekanları dahil et"
                },
                "include_plugins": {
                    "type": "boolean",
                    "default": True,
                    "description": "Pluginleri dahil et"
                }
            }
        }
    },
    {
        "name": "manage_wardrobe",
        "description": "Wardrobe (kıyafet) yönetimi. Kıyafet ekle, sil veya listele. Kullanıcı 'bu kıyafeti kaydet', 'kıyafetleri göster' dediğinde kullan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "remove", "list"],
                    "description": "Yapılacak işlem"
                },
                "wardrobe_id": {
                    "type": "string",
                    "description": "Kıyafet ID (remove için)"
                },
                "name": {
                    "type": "string",
                    "description": "Kıyafet adı (add için)"
                },
                "description": {
                    "type": "string",
                    "description": "Kıyafet açıklaması (İngilizce)"
                },
                "attributes": {
                    "type": "object",
                    "description": "Kıyafet özellikleri",
                    "properties": {
                        "type": {"type": "string", "description": "Tip (shirt, dress, suit, etc.)"},
                        "color": {"type": "string"},
                        "style": {"type": "string"},
                        "material": {"type": "string"},
                        "season": {"type": "string"}
                    }
                }
            },
            "required": ["action"]
        }
    }
]


