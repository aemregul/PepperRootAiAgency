"""
Agent tarafından kullanılabilen araçların tanımları.
"""

# Agent'a sunulacak araçların listesi (JSON Schema formatında)
AGENT_TOOLS = [
    {
        "name": "generate_image",
        "description": "Kullanıcının isteğine göre AI görseli üretir. Karakter, mekan veya herhangi bir sahne çizmek için kullanılır.",
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
    }
]
