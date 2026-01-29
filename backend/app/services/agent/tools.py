"""
Agent tarafından kullanılabilen araçların tanımları.
"""

# Agent'a sunulacak araçların listesi (JSON Schema formatında)
AGENT_TOOLS = [
    {
        "name": "generate_image",
        "description": "Kullanıcının isteğine göre AI görseli üretir. Karakter, mekan veya herhangi bir sahne çizmek için kullanılır. Eğer @tag ile referans verilen bir entity varsa, onun özelliklerini prompt'a ekle.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Görselin detaylı açıklaması (İngilizce olması daha iyi sonuç verir)."
                },
                "image_size": {
                    "type": "string",
                    "enum": ["square_hd", "landscape_4_3", "portrait_4_3", "landscape_16_9", "portrait_16_9"],
                    "default": "square_hd",
                    "description": "Görselin boyutu."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "create_character",
        "description": "Yeni bir karakter oluşturur ve hafızaya kaydeder. Karakter daha sonra @tag ile referans verilebilir. Örnek: 'Emre' karakteri oluşturulursa @character_emre tag'i ile çağrılabilir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Karakterin adı (örn: Emre, Ayşe, Robot-X)"
                },
                "description": {
                    "type": "string",
                    "description": "Karakterin detaylı görsel açıklaması (İngilizce). Örn: 'A tall man with brown hair, wearing a blue jacket, friendly smile'"
                },
                "attributes": {
                    "type": "object",
                    "description": "Ek özellikler (yaş, meslek, vb.)",
                    "properties": {
                        "age": {"type": "string"},
                        "occupation": {"type": "string"},
                        "personality": {"type": "string"}
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
    }
]
