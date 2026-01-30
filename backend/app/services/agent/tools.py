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
        "description": "Yeni bir karakter oluşturur ve hafızaya kaydeder. Kullanıcının verdiği fiziksel özellikleri (göz rengi, kaş rengi, saç stili vb.) dikkatlice yakala ve attributes'a kaydet. Karakter daha sonra @tag ile referans verilebilir.",
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
                    "description": "Entity'nin tag'i (örn: @character_emre, @location_orman)"
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
        "description": "Video üretir. Görsel veya metinden video oluşturur. Kling 2.5 Turbo Pro kullanılır. Örnek: '@character_emre ormanda yürüyor videosu yap'",
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
                    "description": "Belirli bir entity'ye ait olanları getir (örn: @character_johny). Opsiyonel."
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
    }
]


