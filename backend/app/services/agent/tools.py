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
                    "description": "Görselin en-boy oranı."
                },
                "resolution": {
                    "type": "string",
                    "enum": ["1K", "2K", "4K"],
                    "description": "Görselin çözünürlüğü."
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
        "description": "Video üretir. Kling 3.0 Pro kullanılır.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Video açıklaması"},
                "image_url": {"type": "string", "description": "Başlangıç görseli URL (opsiyonel)"},
                "duration": {"type": "string", "enum": ["3", "5", "10"], "description": "Video süresi"},
                "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1"], "description": "Video oranı"}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "edit_image",
        "description": "Mevcut bir görseli düzenler.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "Düzenlenecek görselin URL'si"},
                "prompt": {"type": "string", "description": "Düzenleme talimatı"}
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
        "description": "Bir karakteri veya mekanı sil.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_tag": {"type": "string", "description": "Silinecek entity'nin tag'i"}
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
    }
]

# OpenAI tools formatı
AGENT_TOOLS = convert_to_openai_tools(AGENT_TOOLS_ANTHROPIC)
