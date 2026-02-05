"""
Agent Orchestrator - Agent'ın beyni.
Kullanıcı mesajını alır, LLM'e gönderir, araç çağrılarını yönetir.
"""
import json
import uuid
from typing import Optional
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.agent.tools import AGENT_TOOLS
from app.services.plugins.fal_plugin import FalPlugin
from app.services.entity_service import entity_service
from app.services.asset_service import asset_service
from app.services.stats_service import StatsService
from app.services.prompt_translator import translate_to_english, enhance_character_prompt
from app.models.models import Session as SessionModel


async def get_user_id_from_session(db: AsyncSession, session_id: uuid.UUID) -> uuid.UUID:
    """Session'dan user_id'yi al."""
    result = await db.execute(
        select(SessionModel.user_id).where(SessionModel.id == session_id)
    )
    user_id = result.scalar_one_or_none()
    if not user_id:
        raise ValueError(f"Session bulunamadı: {session_id}")
    return user_id


class AgentOrchestrator:
    """Agent'ı yöneten ana sınıf."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.fal_plugin = FalPlugin()
        self.model = "gpt-4o"
        
        self.system_prompt = """Sen Pepper Root AI Agency'nin AKILLI asistanısın.

## 🧠 SEN KİMSİN - AGENTİK ZEKA

Sen pasif bir chatbot DEĞİLSİN. Sen otonom düşünebilen, problem çözebilen, başarısız olduğunda alternatif yollar deneyebilen bir AGENT'sın.

### TEMEL PRENSİPLER:

1. **DÜŞÜN → PLANLA → UYGULA → DOĞRULA**
   - Her istek için önce düşün: "Kullanıcı aslında ne istiyor?"
   - Plan yap: "Hangi adımları atmalıyım?"
   - Uygula: Araçları kullan
   - Doğrula: "Sonuç kullanıcının ihtiyacını karşılıyor mu?"

2. **BAŞARISIZLIK = YENİ FIRSAT**
   - Bir araç başarısız olursa DURMA, alternatif dene
   - Örnek: search_web sonuç vermedi → search_images dene → browse_url dene
   - Her zaman Plan B, C, D olsun

3. **BİLMİYORSAN ARAŞTIR**
   - Tahmin etme, öğren
   - Marka rengi soruldu ama bilmiyorsun → logoyu bul → analiz et → öğren
   - Her türlü bilgi için web araçlarını kullan

4. **PROAKTİF DAVRANIŞ**
   - Kullanıcı "sahibinden renkleri?" dedi ama kayıtlı değil
   - Sadece "bilmiyorum" deme!
   - Otomatik olarak: research_brand çağır → logo bul → renkler çıkar → kaydet

5. **🚨 KRİTİK: HER ZAMAN TOOL ÇAĞIR 🚨**
   - Görsel/video üretimi istendiyse → generate_image veya generate_video MUTLAKA çağır
   - Geçmişteki hataları ASLA varsayma - her istek yeni bir şans
   - "Kredi yetersiz", "hata oluştu" gibi cevapları tool çağırmadan VERME
   - Önceki konuşmada hata olduysa bile ŞİMDİ tekrar dene
   - Kullanıcı bir şey istiyorsa, tool çağırmadan "yapamıyorum" DEME

## 🔧 ARAÇLARIN

**GÖRSEL/VİDEO:**
- generate_image: AI görsel üret
- generate_video: Video üret
- edit_image: Görsel düzenle
- upscale_image: Kalite artır
- remove_background: Arka plan kaldır
- generate_grid: 3x3 grid (9 açı/storyboard)

**ENTITY YÖNETİMİ:**
- create_character: Karakter kaydet
- create_location: Mekan kaydet
- create_brand: Marka kaydet
- get_entity: Entity bilgisi al
- list_entities: Tüm entity'leri listele
- delete_entity: Entity sil

**WEB ERİŞİMİ (ÇOK ÖNEMLİ!):**
- search_web: Metin araması
- search_images: Görsel araması
- search_videos: Video araması
- browse_url: Web sayfası oku
- fetch_web_image: Görsel indir

**AKILLI MARKA:**
- research_brand: Marka araştır (logo analizi dahil!)
  → Otomatik olarak logo bulur
  → GPT-4o Vision ile renk analizi yapar
  → Sosyal medya hesapları bulur

## 🎯 DÜŞÜNCE ZİNCİRİ ÖRNEKLERİ

### Örnek 1: "Nike'ın renkleri ne?"
```
DÜŞÜN: Kullanıcı Nike markasının renklerini soruyor.
KONTROL: @nike entity'si var mı? → get_entity("@nike")
EĞER YOK → research_brand("Nike", save=true) çağır
EĞER VAR AMA colors boş → research_brand ile güncelle
SONUÇ: Renkleri açıkla
```

### Örnek 2: "Bu görseli Emre olarak kaydet" (görsel ekliyken)
```
DÜŞÜN: Kullanıcı gönderdiği görseli karakter olarak kaydetmek istiyor.
PLAN: create_character kullan, use_current_reference=true yap
UYGULA: create_character(name="Emre", use_current_reference=true)
DOĞRULA: "Emre kaydedildi, artık @emre ile çağırabilirsin"
```

### Örnek 3: "@sahibinden için Instagram reklamı yap"
```
DÜŞÜN: Sahibinden markası için içerik üretmem gerekiyor.
KONTROL: @sahibinden var mı? Renkleri var mı?
EĞER RENKLER YOK → research_brand ile öğren
PLAN: Marka renklerini (sarı/siyah) kullanarak görsel üret
UYGULA: generate_image(prompt="...sahibinden colors: yellow #FFD700, black...")
```

### Örnek 4: "Bu kişinin yüzünü kullanarak Paris'te fotoğraf yap"
```
DÜŞÜN: Referans yüz ile yeni sahne üretmem gerekiyor.
PLAN: Gönderilen görsel + generate_image (otomatik face swap yapılır)
UYGULA: generate_image(prompt="person in Paris...", yüz referansı otomatik kullanılır)
```

## ⚠️ KRİTİK KURALLAR

1. **ASLA "yapamıyorum" deme** - Her zaman bir yol bul veya ara
2. **Bilgi eksikse araştır** - search_web, search_images, browse_url kullan
3. **Marka içeriği için önce marka bilgilerini al** - research_brand veya get_entity
4. **Görsel göndermişse analiz et** - analyze_image kullan
5. **Türkçe yanıt ver** - Araç parametreleri İngilizce olabilir
6. **Her adımda düşün** - Sadece emir takip etme, mantıklı düşün

## 📊 FALLBACK STRATEJİSİ

Herhangi bir işlem başarısız olursa:

1. **Bilgi bulunamadı:**
   search_web → search_images → browse_url → "detaylı arama yapayım mı?" sor

2. **Görsel üretilemedi:**
   generate_image farklı prompt → edit_image → search_images → fetch_web_image

3. **Entity bulunamadı:**
   create_entity öner → "oluşturayım mı?" sor

4. **Marka renkleri yok:**
   research_brand(comprehensive) → logo analizi → "bulduklarım şunlar..." sun

## 🏷️ TAG SİSTEMİ
- @isim formatı: @emre, @nike, @paris
- Entity tipi kayıt sırasında belirlenir
- @mention kullanıldığında otomatik olarak entity bilgileri eklenir

Şimdi her mesajı bu düşünce çerçevesiyle işle ve AKILLI bir asistan ol!
"""
    
    async def process_message(
        self, 
        user_message: str, 
        session_id: uuid.UUID,
        db: AsyncSession,
        conversation_history: list = None,
        reference_image: str = None
    ) -> dict:
        """
        Kullanıcı mesajını işle ve yanıt döndür.
        
        Args:
            user_message: Kullanıcının mesajı
            session_id: Oturum ID
            db: Database session
            conversation_history: Önceki mesajlar (opsiyonel)
            reference_image: Base64 encoded referans görsel (opsiyonel)
        
        Returns:
            dict: {"response": str, "images": list, "entities_created": list}
        """
        if conversation_history is None:
            conversation_history = []
        
        # @tag'leri çözümle ve context oluştur
        entity_context = await self._build_entity_context(db, session_id, user_message)
        
        # System prompt'a entity context ekle
        full_system_prompt = self.system_prompt
        if entity_context:
            full_system_prompt += f"\n\n--- Mevcut Entity Bilgileri ---\n{entity_context}"
        
        # Mesaj içeriğini hazırla (referans görsel varsa vision API kullan)
        uploaded_image_url = None
        if reference_image:
            # Görseli fal.ai'ye yükle (edit_image için URL gerekli)
            try:
                upload_result = await self.fal_plugin.upload_base64_image(reference_image)
                if upload_result.get("success"):
                    uploaded_image_url = upload_result.get("url")
                    print(f"📤 Görsel fal.ai'ye yüklendi: {uploaded_image_url[:60]}...")
            except Exception as upload_error:
                print(f"⚠️ Görsel yükleme hatası: {upload_error}")
            
            # Detect media type from base64 data
            media_type = "image/png"
            if reference_image.startswith("iVBORw"):
                media_type = "image/png"
            elif reference_image.startswith("/9j/"):
                media_type = "image/jpeg"
            elif reference_image.startswith("R0lGOD"):
                media_type = "image/gif"
            elif reference_image.startswith("UklGR"):
                media_type = "image/webp"
            
            # OpenAI Vision API format (GPT-4o)
            # data URL formatında: data:image/png;base64,...
            data_url = f"data:{media_type};base64,{reference_image}"
            
            # AI'a yüklenen URL'yi ver
            image_url_info = ""
            if uploaded_image_url:
                image_url_info = f"\n\n🔗 BU GÖRSELİN URL'Sİ: {uploaded_image_url}\n\nEdit isteklerinde edit_image aracını bu URL ile çağır!"
            
            user_content = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url,
                        "detail": "auto"
                    }
                },
                {
                    "type": "text",
                    "text": user_message + f"\n\n[⚡ REFERANS GÖRSEL GÖNDERİLDİ!{image_url_info}\n\nKullanıcı 'düzenle', 'kaldır', 'değiştir' gibi bir şey isterse → edit_image aracını image_url={uploaded_image_url} ile çağır. Kullanıcı 'kaydet' derse → create_character aracını use_current_reference=true ile çağır.]"
                }
            ]
            messages = conversation_history + [
                {"role": "user", "content": user_content}
            ]
        else:
            messages = conversation_history + [
                {"role": "user", "content": user_message}
            ]
        
        # GPT-4o'ya gönder
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "system", "content": full_system_prompt}] + messages,
            tools=AGENT_TOOLS,
            tool_choice="auto"
        )
        
        # Sonucu işle
        result = {
            "response": "",
            "images": [],
            "entities_created": [],
            "_resolved_entities": [],  # İç kullanım için, @tag ile çözümlenen entity'ler
            "_current_reference_image": reference_image  # Mevcut referans görsel (base64)
        }
        
        # @tag'leri çözümle ve result'a ekle
        user_id = await get_user_id_from_session(db, session_id)
        resolved = await entity_service.resolve_tags(db, user_id, user_message)
        result["_resolved_entities"] = resolved
        result["_user_id"] = user_id  # Entity işlemleri için
        
        # Response'u işle - tool call loop
        await self._process_response(response, messages, result, session_id, db)
        
        # İç kullanım alanlarını kaldır
        del result["_resolved_entities"]
        if "_current_reference_image" in result:
            del result["_current_reference_image"]
        
        return result
    
    async def _build_entity_context(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        message: str
    ) -> str:
        """Mesajdaki @tag'leri çözümle ve context string oluştur."""
        user_id = await get_user_id_from_session(db, session_id)
        entities = await entity_service.resolve_tags(db, user_id, message)
        
        if not entities:
            return ""
        
        context_parts = []
        for entity in entities:
            ref_image_info = ""
            if entity.reference_image_url:
                ref_image_info = f"\n  ⚠️ REFERANS GÖRSEL VAR: {entity.reference_image_url}"
                print(f"🔍 Entity {entity.tag} referans görsel bulundu: {entity.reference_image_url[:80]}...")
            else:
                print(f"⚠️ Entity {entity.tag} için referans görsel YOK")
                
            context_parts.append(
                f"- {entity.tag}: {entity.name} ({entity.entity_type})\n"
                f"  Açıklama: {entity.description}\n"
                f"  Özellikler: {json.dumps(entity.attributes, ensure_ascii=False)}"
                f"{ref_image_info}"
            )
        
        return "\n".join(context_parts)
    
    async def _process_response(
        self, 
        response, 
        messages: list, 
        result: dict,
        session_id: uuid.UUID,
        db: AsyncSession
    ):
        """OpenAI GPT-4o response'unu işle, tool call varsa yürüt."""
        
        message = response.choices[0].message
        
        # 🔍 DEBUG: Agent ne döndü?
        print(f"🤖 AGENT RESPONSE:")
        print(f"   - Content: {message.content[:200] if message.content else 'None'}...")
        print(f"   - Tool calls: {len(message.tool_calls) if message.tool_calls else 0}")
        if message.tool_calls:
            for tc in message.tool_calls:
                print(f"   - Tool: {tc.function.name}")
        
        # Normal metin yanıtı
        if message.content:
            result["response"] += message.content
        
        # Tool calls varsa işle
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # 🔍 DEBUG: Tool çağrısı başlıyor
                print(f"🔧 TOOL EXECUTION START: {tool_name}")
                print(f"   Args: {json.dumps(tool_args, ensure_ascii=False)[:200]}...")
                
                # Araç çağrısını yürüt
                tool_result = await self._handle_tool_call(
                    tool_name, 
                    tool_args, 
                    session_id, 
                    db,
                    resolved_entities=result.get("_resolved_entities", []),
                    current_reference_image=result.get("_current_reference_image")
                )
                
                # 🔍 DEBUG: Tool çağrısı bitti
                print(f"🔧 TOOL EXECUTION END: {tool_name}")
                print(f"   Result: success={tool_result.get('success')}, error={tool_result.get('error', 'None')}")
                
                # Görsel üretildiyse ekle
                if tool_result.get("success") and tool_result.get("image_url"):
                    result["images"].append({
                        "url": tool_result["image_url"],
                        "prompt": tool_args.get("prompt", "")
                    })
                
                # Entity oluşturulduysa ekle
                if tool_result.get("success") and tool_result.get("entity"):
                    result["entities_created"].append(tool_result["entity"])
                
                # Tool sonucunu GPT-4o'ya gönder
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False, default=str)
                })
            
            # Devam yanıtı al
            continue_response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "system", "content": self.system_prompt}] + messages,
                tools=AGENT_TOOLS,
                tool_choice="auto"
            )
            
            # Recursive olarak devam et (nested tool calls için)
            await self._process_response(
                continue_response, 
                messages, 
                result, 
                session_id, 
                db
            )
    
    async def _handle_tool_call(
        self, 
        tool_name: str, 
        tool_input: dict,
        session_id: uuid.UUID,
        db: AsyncSession,
        resolved_entities: list = None,
        current_reference_image: str = None
    ) -> dict:
        """Araç çağrısını işle."""
        
        if tool_name == "generate_image":
            return await self._generate_image(
                db, session_id, tool_input, resolved_entities or []
            )
        
        elif tool_name == "create_character":
            return await self._create_entity(
                db, session_id, "character", tool_input,
                current_reference_image=current_reference_image
            )
        
        elif tool_name == "create_location":
            return await self._create_entity(
                db, session_id, "location", tool_input
            )
        
        elif tool_name == "get_entity":
            return await self._get_entity(db, session_id, tool_input)
        
        elif tool_name == "list_entities":
            return await self._list_entities(db, session_id, tool_input)
        
        # YENİ ARAÇLAR
        elif tool_name == "generate_video":
            return await self._generate_video(db, session_id, tool_input, resolved_entities or [])
        
        elif tool_name == "edit_image":
            return await self._edit_image(tool_input)
        
        elif tool_name == "upscale_image":
            return await self._upscale_image(tool_input)
        
        elif tool_name == "remove_background":
            return await self._remove_background(tool_input)
        
        elif tool_name == "generate_grid":
            return await self._generate_grid(db, session_id, tool_input, resolved_entities or [])
        
        elif tool_name == "use_grid_panel":
            return await self._use_grid_panel(db, session_id, tool_input)
        
        # WEB ARAMA ARAÇLARI
        elif tool_name == "search_images":
            return await self._search_images(tool_input)
        
        elif tool_name == "search_web":
            return await self._search_web(tool_input)
        
        elif tool_name == "search_videos":
            return await self._search_videos(tool_input)
        
        elif tool_name == "browse_url":
            return await self._browse_url(tool_input)
        
        elif tool_name == "fetch_web_image":
            return await self._fetch_web_image(db, session_id, tool_input)
        
        # AKILLI AGENT ARAÇLARI
        elif tool_name == "get_past_assets":
            return await self._get_past_assets(db, session_id, tool_input)
        
        elif tool_name == "mark_favorite":
            return await self._mark_favorite(db, session_id, tool_input)
        
        elif tool_name == "undo_last":
            return await self._undo_last(db, session_id)
        
        # GÖRSEL MUHAKEME ARAÇLARI
        elif tool_name == "analyze_image":
            return await self._analyze_image(tool_input)
        
        elif tool_name == "compare_images":
            return await self._compare_images(tool_input)
        
        # ROADMAP / GÖREV PLANLAMA
        elif tool_name == "create_roadmap":
            return await self._create_roadmap(db, session_id, tool_input)
        
        elif tool_name == "get_roadmap_progress":
            return await self._get_roadmap_progress(db, session_id, tool_input)
        
        # SİSTEM YÖNETİM ARAÇLARI
        elif tool_name == "manage_project":
            return await self._manage_project(db, session_id, tool_input)
        
        elif tool_name == "delete_entity":
            return await self._delete_entity(db, session_id, tool_input)
        
        elif tool_name == "manage_trash":
            return await self._manage_trash(db, session_id, tool_input)
        
        elif tool_name == "manage_plugin":
            return await self._manage_plugin(db, session_id, tool_input)
        
        elif tool_name == "get_system_state":
            return await self._get_system_state(db, session_id, tool_input)
        
        elif tool_name == "manage_wardrobe":
            return await self._manage_wardrobe(db, session_id, tool_input)
        
        elif tool_name == "create_brand":
            return await self._create_brand(db, session_id, tool_input)
        
        elif tool_name == "research_brand":
            return await self._research_brand(db, session_id, tool_input)
        
        return {"success": False, "error": f"Bilinmeyen araç: {tool_name}"}
    
    async def _generate_image(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict, 
        resolved_entities: list = None
    ) -> dict:
        """
        Akıllı görsel üretim sistemi.
        
        İş Akışı:
        1. Entity'de referans görsel var mı kontrol et
        2. VARSA → Akıllı sistem: Nano Banana + Face Swap fallback
        3. YOKSA → Sadece Nano Banana Pro
        4. Her üretimde asset'i veritabanına kaydet
        
        Agent kendi başına karar verir ve en iyi sonucu sunar.
        """
        try:
            original_prompt = params.get("prompt", "")
            aspect_ratio = params.get("aspect_ratio", "1:1")
            resolution = params.get("resolution", "1K")
            
            # 🔄 PROMPTU İNGİLİZCE'YE ÇEVİR (Hangi dilde olursa olsun - daha iyi görsel sonuçları için)
            prompt, was_translated = await translate_to_english(original_prompt)
            if was_translated:
                print(f"📝 Prompt çevrildi: '{original_prompt[:50]}...' → '{prompt[:50]}...'")
            
            # Referans görseli olan karakter var mı kontrol et
            face_reference_url = None
            entity_description = ""
            physical_attributes = {}
            
            # Debug: resolved_entities kontrolü
            print(f"🔍 _generate_image: resolved_entities = {len(resolved_entities) if resolved_entities else 0} adet")
            
            if resolved_entities:
                for entity in resolved_entities:
                    print(f"   → Entity: {getattr(entity, 'tag', 'unknown')}, type: {type(entity)}")
                    
                    # Referans görsel kontrolü
                    if hasattr(entity, 'reference_image_url') and entity.reference_image_url:
                        face_reference_url = entity.reference_image_url
                        print(f"   ✅ Referans görsel BULUNDU: {face_reference_url[:80]}...")
                    else:
                        print(f"   ⚠️ Referans görsel YOK - hasattr: {hasattr(entity, 'reference_image_url')}, value: {getattr(entity, 'reference_image_url', 'N/A')}")
                    
                    # Entity açıklamasını topla
                    if hasattr(entity, 'description') and entity.description:
                        entity_description += f"{entity.description}. "
                    # Fiziksel özellikleri topla (attributes içinden)
                    if hasattr(entity, 'attributes') and entity.attributes:
                        attrs = entity.attributes
                        for key in ['eye_color', 'hair_color', 'skin_tone', 'eyebrow_color', 
                                   'eyebrow_shape', 'hair_style', 'facial_features']:
                            if attrs.get(key):
                                physical_attributes[key] = attrs[key]
            
            # Entity açıklamasını ve fiziksel özellikleri prompt'a ekle
            if entity_description or physical_attributes:
                prompt = await enhance_character_prompt(
                    base_prompt=f"{entity_description} {prompt}",
                    physical_attributes=physical_attributes
                )
                print(f"🎨 Karakter prompt zenginleştirildi: '{prompt[:80]}...'")
            
            # AKILLI SİSTEM: Referans görsel varsa
            print(f"🎯 Referans görsel durumu: {face_reference_url is not None}")
            if face_reference_url:
                # Akıllı üretim: Nano Banana → kontrol → Face Swap fallback
                result = await self.fal_plugin.smart_generate_with_face(
                    prompt=prompt,
                    face_image_url=face_reference_url,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution
                )
                
                if result.get("success"):
                    method = result.get("method_used", "unknown")
                    quality_note = result.get("quality_check", "")
                    image_url = result.get("image_url")
                    
                    # 📦 Asset'i veritabanına kaydet
                    entity_ids = [str(getattr(e, 'id', None)) for e in resolved_entities if getattr(e, 'id', None)] if resolved_entities else None
                    await asset_service.save_asset(
                        db=db,
                        session_id=session_id,
                        url=image_url,
                        asset_type="image",
                        prompt=prompt,
                        model_name=method,
                        model_params={
                            "aspect_ratio": aspect_ratio,
                            "resolution": resolution,
                            "face_reference_used": True
                        },
                        entity_ids=entity_ids
                    )
                    
                    # 📊 İstatistik kaydet
                    user_id = await get_user_id_from_session(db, session_id)
                    await StatsService.track_image_generation(db, user_id, method)
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "base_image_url": result.get("base_image_url"),  # Alternatif (Nano Banana)
                        "model": method,
                        "message": f"Görsel üretildi. {quality_note}",
                        "agent_decision": f"Referans görsel algılandı. Yöntem: {method}"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Görsel üretilemedi")
                    }
            
            else:
                # Referans yok - sadece Nano Banana Pro
                result = await self.fal_plugin.generate_with_nano_banana(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution
                )
                
                if result.get("success"):
                    image_url = result.get("image_url")
                    
                    # 📦 Asset'i veritabanına kaydet
                    entity_ids = [str(getattr(e, 'id', None)) for e in resolved_entities if getattr(e, 'id', None)] if resolved_entities else None
                    await asset_service.save_asset(
                        db=db,
                        session_id=session_id,
                        url=image_url,
                        asset_type="image",
                        prompt=prompt,
                        model_name="nano-banana-pro",
                        model_params={
                            "aspect_ratio": aspect_ratio,
                            "resolution": resolution,
                            "face_reference_used": False
                        },
                        entity_ids=entity_ids
                    )
                    
                    # 📊 İstatistik kaydet
                    user_id = await get_user_id_from_session(db, session_id)
                    await StatsService.track_image_generation(db, user_id, "nano-banana-pro")
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": "nano-banana-pro",
                        "message": "Görsel başarıyla üretildi (Nano Banana Pro).",
                        "agent_decision": "Referans görsel yok, Nano Banana Pro kullanıldı"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Görsel üretilemedi")
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_entity(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        entity_type: str, 
        params: dict,
        current_reference_image: str = None
    ) -> dict:
        """
        Yeni entity oluştur.
        
        Eğer use_current_reference=True ise veya reference_image_url verilmişse,
        görseli fal.ai'ye yükleyip entity'ye kaydet.
        """
        try:
            reference_image_url = params.get("reference_image_url")
            use_current_reference = params.get("use_current_reference", False)
            
            # Kullanıcı mevcut referans görselini kullanmak istiyorsa
            if use_current_reference and current_reference_image and not reference_image_url:
                # Base64 görseli fal.ai'ye yükle
                try:
                    upload_result = await self.fal_plugin.upload_base64_image(current_reference_image)
                    if upload_result.get("success"):
                        reference_image_url = upload_result.get("url")
                        print(f"📸 Referans görsel yüklendi: {reference_image_url[:50]}...")
                except Exception as upload_error:
                    print(f"⚠️ Referans görsel yükleme hatası: {upload_error}")
            
            # Session'dan user_id al
            user_id = await get_user_id_from_session(db, session_id)
            
            entity = await entity_service.create_entity(
                db=db,
                user_id=user_id,
                entity_type=entity_type,
                name=params.get("name"),
                description=params.get("description"),
                attributes=params.get("attributes", {}),
                reference_image_url=reference_image_url,
                session_id=session_id  # Opsiyonel - hangi projede oluşturulduğu
            )
            
            return {
                "success": True,
                "message": f"{entity.name} ({entity_type}) oluşturuldu. Tag: {entity.tag}",
                "entity": {
                    "id": str(entity.id),
                    "tag": entity.tag,
                    "name": entity.name,
                    "entity_type": entity.entity_type,
                    "description": entity.description,
                    "reference_image_url": reference_image_url
                },
                "has_reference_image": bool(reference_image_url)
            }
        
        except ValueError as ve:
            # Duplicate entity hatası - kullanıcıya açık mesaj göster
            return {
                "success": False,
                "error": str(ve),
                "duplicate": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_entity(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Tag ile entity bul."""
        try:
            tag = params.get("tag", "")
            user_id = await get_user_id_from_session(db, session_id)
            entity = await entity_service.get_by_tag(db, user_id, tag)
            
            if entity:
                return {
                    "success": True,
                    "entity": {
                        "id": str(entity.id),
                        "tag": entity.tag,
                        "name": entity.name,
                        "entity_type": entity.entity_type,
                        "description": entity.description,
                        "attributes": entity.attributes,
                        "reference_image_url": entity.reference_image_url
                    },
                    "has_reference_image": bool(entity.reference_image_url)
                }
            else:
                return {
                    "success": False,
                    "error": f"'{tag}' tag'i ile entity bulunamadı."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_entities(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Kullanıcının entity'lerini listele."""
        try:
            entity_type = params.get("entity_type", "all")
            user_id = await get_user_id_from_session(db, session_id)
            
            if entity_type == "all":
                entities = await entity_service.list_entities(db, user_id)
            else:
                entities = await entity_service.list_entities(db, user_id, entity_type)
            
            return {
                "success": True,
                "entities": [
                    {
                        "tag": e.tag,
                        "name": e.name,
                        "entity_type": e.entity_type,
                        "description": e.description[:100] + "..." if e.description and len(e.description) > 100 else e.description,
                        "reference_image_url": e.reference_image_url,
                        "has_image": bool(e.reference_image_url)
                    }
                    for e in entities
                ],
                "count": len(entities)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # YENİ ARAÇ METODLARI
    # ===============================
    
    async def _generate_video(self, db: AsyncSession, session_id: uuid.UUID, params: dict, resolved_entities: list = None) -> dict:
        """
        Video üret (text-to-video veya image-to-video).
        
        Entity referansı varsa, önce görsel üretilip image-to-video yapılır.
        """
        try:
            prompt = params.get("prompt", "")
            image_url = params.get("image_url")
            duration = params.get("duration", "5")
            aspect_ratio = params.get("aspect_ratio", "16:9")
            
            # Entity açıklamalarını prompt'a ekle
            if resolved_entities:
                for entity in resolved_entities:
                    if hasattr(entity, 'description') and entity.description:
                        prompt = f"{entity.description}. {prompt}"
            
            # Image-to-video için görsel lazım
            # Eğer görsel yoksa ama entity varsa, önce görsel üret
            if not image_url and resolved_entities:
                # Önce görsel üret
                image_result = await self._generate_image(
                    db, session_id,
                    {"prompt": prompt, "aspect_ratio": aspect_ratio.replace(":", ":")},
                    resolved_entities
                )
                if image_result.get("success"):
                    image_url = image_result.get("image_url")
            
            # Video üret
            result = await self.fal_plugin.generate_video(
                prompt=prompt,
                image_url=image_url,
                duration=duration,
                aspect_ratio=aspect_ratio
            )
            
            if result.get("success"):
                # 📊 İstatistik kaydet
                user_id = await get_user_id_from_session(db, session_id)
                model_name = result.get("model", "kling-3.0-pro")
                await StatsService.track_video_generation(db, user_id, model_name)
                
                return {
                    "success": True,
                    "video_url": result.get("video_url"),
                    "model": model_name,
                    "message": f"Video başarıyla üretildi ({duration}s).",
                    "agent_decision": "Image-to-video" if image_url else "Text-to-video"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Video üretilemedi")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _edit_image(self, params: dict) -> dict:
        """
        GERÇEK GÖRSEL DÜZENLEME (True Inpainting)
        
        fal.ai object-removal API kullanarak:
        - Orijinal görsel korunur
        - Sadece belirtilen nesne silinir/değiştirilir
        - "Gözlüğü kaldır", "şapkayı sil" gibi talimatlar doğrudan çalışır
        """
        try:
            image_url = params.get("image_url")
            edit_instruction = params.get("prompt", "")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "image_url gerekli"
                }
            
            if not edit_instruction:
                return {
                    "success": False,
                    "error": "Düzenleme talimatı gerekli"
                }
            
            print(f"🎨 GERÇEK DÜZENLEME BAŞLADI (Object Removal)")
            print(f"   Görsel: {image_url[:60]}...")
            print(f"   Talimat: {edit_instruction}")
            
            # Talimatı İngilizce'ye çevir (daha iyi sonuç için)
            from app.services.prompt_translator import translate_to_english
            english_instruction, _ = await translate_to_english(edit_instruction)
            
            # Nesne silme talimatlarını tespit et
            removal_keywords = ["kaldır", "sil", "çıkar", "remove", "delete", "erase", "take off"]
            is_removal = any(kw in edit_instruction.lower() for kw in removal_keywords)
            
            import fal_client
            
            if is_removal:
                # Object Removal API - Nesne silme
                # Talimatı "object to remove" formatına çevir
                object_to_remove = english_instruction
                for word in ["remove", "delete", "erase", "take off", "the", "from", "image", "photo"]:
                    object_to_remove = object_to_remove.lower().replace(word, "").strip()
                
                print(f"   Silinecek nesne: {object_to_remove}")
                
                try:
                    result = await fal_client.subscribe_async(
                        "fal-ai/object-removal",
                        arguments={
                            "image_url": image_url,
                            "prompt": object_to_remove,  # "glasses", "hat" gibi
                        },
                        with_logs=True,
                    )
                    
                    if result and "image" in result:
                        print(f"✅ Object Removal başarılı!")
                        return {
                            "success": True,
                            "image_url": result["image"]["url"],
                            "original_image_url": image_url,
                            "model": "object-removal",
                            "method": "fal-ai/object-removal",
                            "message": f"'{object_to_remove}' görselden başarıyla kaldırıldı."
                        }
                except Exception as removal_error:
                    print(f"⚠️ Object Removal hatası: {removal_error}")
            
            # Flux Fill ile inpainting dene (object removal başarısız olursa veya silme değilse)
            try:
                # GPT-4o ile mask oluşturma talimatı al
                analysis_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=500,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url, "detail": "high"}
                                },
                                {
                                    "type": "text",
                                    "text": f"""Bu görsele şu düzenleme uygulanacak: "{edit_instruction}"

Düzenleme tamamlandıktan sonra görsel nasıl görünmeli? Kısa, İngilizce bir prompt yaz.
Örneğin: "A person with clear face, no glasses, natural skin" gibi."""
                                }
                            ]
                        }
                    ]
                )
                
                fill_prompt = analysis_response.choices[0].message.content
                print(f"   Fill prompt: {fill_prompt[:100]}...")
                
                # Flux Pro Fill ile inpainting
                result = await fal_client.subscribe_async(
                    "fal-ai/flux-pro/v1/fill",
                    arguments={
                        "image_url": image_url,
                        "prompt": fill_prompt,
                        "sync_mode": True
                    },
                    with_logs=True,
                )
                
                if result and "images" in result and len(result["images"]) > 0:
                    print(f"✅ Flux Fill başarılı!")
                    return {
                        "success": True,
                        "image_url": result["images"][0]["url"],
                        "original_image_url": image_url,
                        "model": "flux-pro-fill",
                        "method": "fal-ai/flux-pro/v1/fill",
                        "message": f"Görsel başarıyla düzenlendi: {edit_instruction}"
                    }
                    
            except Exception as fill_error:
                print(f"⚠️ Flux Fill hatası: {fill_error}")
            
            # Son çare: Bildiri
            return {
                "success": False,
                "error": f"Görsel düzenleme başarısız. Lütfen daha basit bir talimat deneyin veya görseli yeniden üretin."
            }
        
        except Exception as e:
            print(f"❌ DÜZENLEME HATASI: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _upscale_image(self, params: dict) -> dict:
        """Görsel kalitesini artır."""
        try:
            image_url = params.get("image_url")
            scale = params.get("scale", 2)
            
            if not image_url:
                return {
                    "success": False,
                    "error": "image_url gerekli"
                }
            
            result = await self.fal_plugin.upscale_image(
                image_url=image_url,
                scale=scale
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result.get("image_url"),
                    "model": result.get("model"),
                    "message": f"Görsel {scale}x büyütüldü ve kalitesi artırıldı."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Upscale yapılamadı")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _remove_background(self, params: dict) -> dict:
        """Görsel arka planını kaldır."""
        try:
            image_url = params.get("image_url")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "image_url gerekli"
                }
            
            result = await self.fal_plugin.remove_background(
                image_url=image_url
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result.get("image_url"),
                    "model": result.get("model"),
                    "message": "Arka plan kaldırıldı, şeffaf PNG oluşturuldu."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Arka plan kaldırılamadı")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # AKILLI AGENT METODLARI
    # ===============================
    
    async def _get_past_assets(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Geçmiş üretimleri getir."""
        try:
            entity_tag = params.get("entity_tag")
            asset_type = params.get("asset_type")
            favorites_only = params.get("favorites_only", False)
            limit = params.get("limit", 5)
            
            assets = await asset_service.get_session_assets(
                db=db,
                session_id=session_id,
                entity_tag=entity_tag,
                asset_type=asset_type,
                favorites_only=favorites_only,
                limit=limit
            )
            
            if not assets:
                return {
                    "success": True,
                    "assets": [],
                    "message": "Bu oturumda henüz üretilmiş içerik yok."
                }
            
            # Asset'leri serializable formata dönüştür
            asset_list = []
            for asset in assets:
                asset_list.append({
                    "id": str(asset.id),
                    "url": asset.url,
                    "type": asset.asset_type,
                    "prompt": asset.prompt[:100] + "..." if asset.prompt and len(asset.prompt) > 100 else asset.prompt,
                    "model": asset.model_name,
                    "is_favorite": asset.is_favorite,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None
                })
            
            return {
                "success": True,
                "assets": asset_list,
                "count": len(asset_list),
                "message": f"{len(asset_list)} adet içerik bulundu."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _mark_favorite(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Asset'i favori olarak işaretle."""
        try:
            asset_url = params.get("asset_url")
            
            # URL verilmediyse son asset'i bul
            if not asset_url:
                last_asset = await asset_service.get_last_asset(db, session_id)
                if not last_asset:
                    return {
                        "success": False,
                        "error": "Favori yapılacak içerik bulunamadı."
                    }
                asset_id = last_asset.id
            else:
                # URL'den asset bul
                from sqlalchemy import select
                from app.models.models import GeneratedAsset
                
                result = await db.execute(
                    select(GeneratedAsset).where(
                        GeneratedAsset.url == asset_url,
                        GeneratedAsset.session_id == session_id
                    )
                )
                asset = result.scalar_one_or_none()
                if not asset:
                    return {
                        "success": False,
                        "error": "Asset bulunamadı."
                    }
                asset_id = asset.id
            
            # Favori olarak işaretle
            updated_asset = await asset_service.mark_favorite(db, asset_id, True)
            
            if updated_asset:
                return {
                    "success": True,
                    "asset_id": str(updated_asset.id),
                    "url": updated_asset.url,
                    "message": "İçerik favorilere eklendi! ⭐"
                }
            else:
                return {
                    "success": False,
                    "error": "Favori işaretlenemedi."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _undo_last(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID
    ) -> dict:
        """Son işlemi geri al, önceki versiyona dön."""
        try:
            # Son asset'i bul
            last_asset = await asset_service.get_last_asset(db, session_id)
            
            if not last_asset:
                return {
                    "success": False,
                    "error": "Geri alınacak içerik bulunamadı."
                }
            
            # Parent'ı var mı kontrol et
            if last_asset.parent_asset_id:
                # Parent'ı getir
                parent_asset = await asset_service.get_asset_by_id(
                    db, last_asset.parent_asset_id
                )
                
                if parent_asset:
                    return {
                        "success": True,
                        "previous_url": parent_asset.url,
                        "previous_type": parent_asset.asset_type,
                        "current_url": last_asset.url,
                        "message": "Önceki versiyona dönüldü. İşte önceki içerik:"
                    }
            
            # Parent yoksa, son 2 asset'i getir
            recent_assets = await asset_service.get_session_assets(
                db, session_id, limit=2
            )
            
            if len(recent_assets) >= 2:
                previous_asset = recent_assets[1]
                return {
                    "success": True,
                    "previous_url": previous_asset.url,
                    "previous_type": previous_asset.asset_type,
                    "current_url": last_asset.url,
                    "message": "Bir önceki üretim gösteriliyor:"
                }
            else:
                return {
                    "success": False,
                    "error": "Geri dönülecek önceki içerik bulunamadı."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # GÖRSEL MUHAKEME METODLARI
    # ===============================
    
    async def _analyze_image(self, params: dict) -> dict:
        """
        Görsel analiz - Claude Vision ile kalite kontrolü.
        
        Agent bu metodu şu durumlarda OTOMATIK kullanır:
        - Görsel üretimi sonrası kalite kontrolü
        - Kullanıcı "bu ne?", "bu nasıl?" dediğinde
        - Yüz tutarlılığı kontrolü gerektiğinde
        """
        try:
            from app.services.llm.claude_service import claude_service
            
            image_url = params.get("image_url", "")
            check_quality = params.get("check_quality", True)
            
            if not image_url:
                return {
                    "success": False,
                    "error": "Görsel URL'si gerekli."
                }
            
            result = await claude_service.analyze_image(
                image_url=image_url,
                check_quality=check_quality
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "analysis": result.get("analysis"),
                    "quality_score": result.get("quality_score", 7),
                    "face_detected": result.get("face_detected", False),
                    "face_quality": result.get("face_quality", "bilinmiyor"),
                    "issues": result.get("issues", []),
                    "recommendation": result.get("recommendation", "kabul edilebilir"),
                    "message": f"Görsel analizi tamamlandı. Kalite skoru: {result.get('quality_score', 7)}/10"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Görsel analiz başarısız")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _compare_images(self, params: dict) -> dict:
        """
        İki görseli karşılaştır.
        
        Agent bu metodu şu durumlarda kullanır:
        - Kullanıcı "hangisi daha iyi?" dediğinde
        - Önceki/şimdiki versiyonları kıyaslarken
        """
        try:
            from app.services.llm.claude_service import claude_service
            
            image_url_1 = params.get("image_url_1", "")
            image_url_2 = params.get("image_url_2", "")
            
            if not image_url_1 or not image_url_2:
                return {
                    "success": False,
                    "error": "Her iki görsel URL'si de gerekli."
                }
            
            result = await claude_service.compare_images(
                image_url_1=image_url_1,
                image_url_2=image_url_2
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "comparison": result.get("comparison"),
                    "message": "Görsel karşılaştırması tamamlandı."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Karşılaştırma başarısız")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # ROADMAP METODLARI
    # ===============================
    
    async def _create_roadmap(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """
        Çoklu adım görev planı (roadmap) oluştur.
        
        Agent karmaşık istekleri parçalara ayırarak yönetir.
        """
        try:
            from app.services.task_service import task_service
            
            goal = params.get("goal", "")
            steps = params.get("steps", [])
            
            if not goal or not steps:
                return {
                    "success": False,
                    "error": "Hedef ve adımlar gerekli."
                }
            
            # Roadmap oluştur
            roadmap = await task_service.create_roadmap(
                db=db,
                session_id=session_id,
                goal=goal,
                steps=steps
            )
            
            # İlk görevi otomatik başlat
            first_task = await task_service.get_next_task(db, roadmap.id)
            if first_task:
                await task_service.start_task(db, first_task.id)
            
            return {
                "success": True,
                "roadmap_id": str(roadmap.id),
                "goal": goal,
                "total_steps": len(steps),
                "steps": [
                    {
                        "step": i + 1,
                        "type": s.get("type"),
                        "description": s.get("description")
                    }
                    for i, s in enumerate(steps)
                ],
                "message": f"Roadmap oluşturuldu: {len(steps)} adımlık plan. İlk adım başlatıldı."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_roadmap_progress(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Roadmap ilerleme durumunu getir."""
        try:
            from app.services.task_service import task_service, TaskType
            
            roadmap_id = params.get("roadmap_id")
            
            if not roadmap_id:
                # Son aktif roadmap'i bul
                roadmaps = await task_service.get_session_roadmaps(db, session_id)
                if not roadmaps:
                    return {
                        "success": False,
                        "error": "Aktif roadmap bulunamadı."
                    }
                roadmap = roadmaps[0]
                roadmap_id = roadmap.id
            else:
                roadmap_id = uuid.UUID(roadmap_id)
                roadmap = await task_service.get_roadmap(db, roadmap_id)
            
            if not roadmap:
                return {
                    "success": False,
                    "error": "Roadmap bulunamadı."
                }
            
            # İlerleme durumunu getir
            progress = await task_service.get_roadmap_progress(db, roadmap_id)
            
            return {
                "success": True,
                "roadmap_id": str(roadmap_id),
                "goal": roadmap.input_data.get("goal", ""),
                "status": roadmap.status,
                "progress": progress,
                "message": f"İlerleme: {progress['completed']}/{progress['total']} adım tamamlandı ({progress['progress_percent']}%)"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # SİSTEM YÖNETİM METODLARI
    # ===============================
    
    async def _manage_project(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Proje yönetim işlemleri."""
        try:
            action = params.get("action")
            project_name = params.get("project_name")
            project_id = params.get("project_id")
            
            if action == "create":
                if not project_name:
                    return {"success": False, "error": "Proje adı gerekli."}
                new_id = str(uuid.uuid4())[:8]
                return {"success": True, "project_id": new_id, "message": f"'{project_name}' projesi oluşturuldu!"}
            
            elif action == "list":
                mock_projects = [{"id": "samsung", "name": "Samsung Campaign"}, {"id": "nike", "name": "Nike Spring"}]
                return {"success": True, "projects": mock_projects, "count": len(mock_projects)}
            
            elif action == "switch":
                return {"success": True, "message": f"'{project_id}' projesine geçildi."}
            
            elif action == "delete":
                return {"success": True, "message": f"'{project_id}' projesi çöp kutusuna taşındı."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _delete_entity(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Entity'yi çöp kutusuna taşı."""
        try:
            entity_tag = params.get("entity_tag", "").lstrip("@")
            if not entity_tag:
                return {"success": False, "error": "Entity tag gerekli."}
            
            entity = await entity_service.get_by_tag(db, session_id, f"@{entity_tag}")
            if not entity:
                return {"success": False, "error": f"'{entity_tag}' bulunamadı."}
            
            entity.is_deleted = True
            await db.commit()
            return {"success": True, "message": f"{entity.name} çöp kutusuna taşındı."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _manage_trash(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Çöp kutusu işlemleri."""
        try:
            action = params.get("action")
            item_id = params.get("item_id")
            
            if action == "list":
                from sqlalchemy import select
                from app.models.models import Entity
                result = await db.execute(select(Entity).where(Entity.session_id == session_id, Entity.is_deleted == True))
                items = result.scalars().all()
                trash = [{"id": str(i.id), "name": i.name, "type": i.entity_type} for i in items]
                return {"success": True, "items": trash, "count": len(trash), "message": f"Çöp kutusunda {len(trash)} öğe var." if trash else "Çöp kutusu boş."}
            
            elif action == "restore":
                from sqlalchemy import select
                from app.models.models import Entity
                result = await db.execute(select(Entity).where(Entity.id == uuid.UUID(item_id)))
                entity = result.scalar_one_or_none()
                if entity:
                    entity.is_deleted = False
                    await db.commit()
                    return {"success": True, "message": f"{entity.name} geri getirildi!"}
                return {"success": False, "error": "Öğe bulunamadı."}
            
            elif action == "empty":
                from sqlalchemy import delete
                from app.models.models import Entity
                await db.execute(delete(Entity).where(Entity.session_id == session_id, Entity.is_deleted == True))
                await db.commit()
                return {"success": True, "message": "Çöp kutusu boşaltıldı."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _manage_plugin(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Creative Plugin yönetimi."""
        try:
            action = params.get("action")
            name = params.get("name")
            config = params.get("config", {})
            
            if action == "create":
                if not name:
                    return {"success": False, "error": "Plugin adı gerekli."}
                new_id = str(uuid.uuid4())[:8]
                return {"success": True, "plugin_id": new_id, "message": f"'{name}' plugin'i oluşturuldu! Stil: {config.get('style', 'belirtilmemiş')}"}
            
            elif action == "list":
                mock = [{"id": "1", "name": "Cinematic Portrait"}, {"id": "2", "name": "Anime Style"}]
                return {"success": True, "plugins": mock, "count": len(mock)}
            
            elif action == "delete":
                return {"success": True, "message": "Plugin silindi."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_system_state(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Sistemin mevcut durumunu getir."""
        try:
            entities = await entity_service.list_entities(db, session_id)
            assets = await asset_service.get_session_assets(db, session_id, limit=5) if params.get("include_assets", True) else []
            
            state = {
                "session_id": str(session_id),
                "entities": {"characters": [e.name for e in entities if e.entity_type == "character"],
                            "locations": [e.name for e in entities if e.entity_type == "location"]},
                "recent_assets": len(assets) if assets else 0
            }
            return {"success": True, "state": state, "message": f"{len(entities)} entity, {len(assets) if assets else 0} asset var."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _manage_wardrobe(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Wardrobe (kıyafet) yönetimi."""
        try:
            action = params.get("action")
            name = params.get("name")
            
            if action == "add":
                if not name:
                    return {"success": False, "error": "Kıyafet adı gerekli."}
                return {"success": True, "message": f"'{name}' kıyafeti eklendi!"}
            
            elif action == "list":
                mock = [{"id": "1", "name": "Business Suit"}, {"id": "2", "name": "Casual Jeans"}]
                return {"success": True, "wardrobe": mock, "count": len(mock)}
            
            elif action == "remove":
                return {"success": True, "message": "Kıyafet silindi."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===============================
    # WEB ARAMA METODLARI
    # ===============================
    
    async def _search_images(self, params: dict) -> dict:
        """
        DuckDuckGo ile görsel arar.
        """
        try:
            from duckduckgo_search import DDGS
            
            query = params.get("query")
            num_results = params.get("num_results", 5)
            
            if not query:
                return {"success": False, "error": "Arama terimi gerekli."}
            
            print(f"=== SEARCH IMAGES ===")
            print(f"Query: {query}")
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.images(query, max_results=num_results):
                    results.append({
                        "title": r.get("title", ""),
                        "thumbnail": r.get("thumbnail", ""),
                        "image": r.get("image", ""),
                        "source": r.get("source", ""),
                        "url": r.get("url", "")
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "message": f"'{query}' için {len(results)} görsel bulundu."
            }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _search_web(self, params: dict) -> dict:
        """
        DuckDuckGo ile metin araması yapar.
        """
        try:
            from duckduckgo_search import DDGS
            
            query = params.get("query")
            num_results = params.get("num_results", 5)
            region = params.get("region", "tr-tr")
            
            if not query:
                return {"success": False, "error": "Arama terimi gerekli."}
            
            print(f"=== SEARCH WEB ===")
            print(f"Query: {query}, Region: {region}")
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, region=region, max_results=num_results):
                    results.append({
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "url": r.get("href", "")
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "message": f"'{query}' için {len(results)} sonuç bulundu."
            }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _search_videos(self, params: dict) -> dict:
        """
        DuckDuckGo ile video arar.
        """
        try:
            from duckduckgo_search import DDGS
            
            query = params.get("query")
            num_results = params.get("num_results", 5)
            
            if not query:
                return {"success": False, "error": "Arama terimi gerekli."}
            
            print(f"=== SEARCH VIDEOS ===")
            print(f"Query: {query}")
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.videos(query, max_results=num_results):
                    results.append({
                        "title": r.get("title", ""),
                        "description": r.get("description", ""),
                        "duration": r.get("duration", ""),
                        "publisher": r.get("publisher", ""),
                        "embed_url": r.get("embed_url", ""),
                        "url": r.get("content", "")
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "message": f"'{query}' için {len(results)} video bulundu."
            }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _browse_url(self, params: dict) -> dict:
        """
        URL'ye gider ve sayfa içeriğini okur.
        """
        import httpx
        from bs4 import BeautifulSoup
        
        try:
            url = params.get("url")
            extract_images = params.get("extract_images", False)
            
            if not url:
                return {"success": False, "error": "URL gerekli."}
            
            print(f"=== BROWSE URL ===")
            print(f"URL: {url}")
            
            # Sayfayı indir
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Sayfa yüklenemedi: {response.status_code}"}
                
                html = response.text
            
            # HTML'i parse et
            soup = BeautifulSoup(html, "lxml")
            
            # Script ve style taglarını kaldır
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Başlık
            title = soup.title.string if soup.title else "Başlık yok"
            
            # Meta açıklama
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")
            
            # Ana içerik - article veya main tag'ini ara
            main_content = soup.find("article") or soup.find("main") or soup.find("body")
            
            # Metni çıkar
            text = main_content.get_text(separator="\n", strip=True) if main_content else ""
            
            # Çok uzunsa kısalt
            if len(text) > 5000:
                text = text[:5000] + "...[kısaltıldı]"
            
            result = {
                "success": True,
                "url": url,
                "title": title,
                "description": meta_desc,
                "content": text,
                "content_length": len(text),
                "message": f"'{title}' sayfası okundu."
            }
            
            # Görselleri çıkar
            if extract_images:
                images = []
                for img in soup.find_all("img", src=True)[:10]:
                    src = img.get("src", "")
                    # Relative URL'leri absolute yap
                    if src.startswith("/"):
                        from urllib.parse import urljoin
                        src = urljoin(url, src)
                    if src.startswith("http"):
                        images.append({
                            "src": src,
                            "alt": img.get("alt", "")
                        })
                result["images"] = images
                result["image_count"] = len(images)
            
            return result
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _fetch_web_image(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """
        Web'den görsel indirir ve sisteme kaydeder.
        """
        import httpx
        import base64
        import os
        from datetime import datetime
        
        try:
            image_url = params.get("image_url")
            save_as_entity = params.get("save_as_entity", False)
            entity_name = params.get("entity_name")
            
            if not image_url:
                return {"success": False, "error": "Görsel URL'si gerekli."}
            
            print(f"=== FETCH WEB IMAGE ===")
            print(f"URL: {image_url[:100]}...")
            
            # Görseli indir
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                response = await client.get(
                    image_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Görsel indirilemedi: {response.status_code}"}
                
                # Content type kontrolü
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    return {"success": False, "error": f"Geçersiz içerik tipi: {content_type}"}
                
                image_data = response.content
            
            # Dosya uzantısını belirle
            ext = "jpg"
            if "png" in content_type:
                ext = "png"
            elif "gif" in content_type:
                ext = "gif"
            elif "webp" in content_type:
                ext = "webp"
            
            # Dosyayı kaydet
            upload_dir = settings.STORAGE_PATH
            os.makedirs(upload_dir, exist_ok=True)
            
            filename = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            # URL oluştur (local için)
            saved_url = f"http://localhost:8000/uploads/{filename}"
            
            result = {
                "success": True,
                "url": saved_url,
                "original_url": image_url,
                "filename": filename,
                "size_bytes": len(image_data),
                "message": f"Görsel başarıyla indirildi: {filename}"
            }
            
            # Entity olarak kaydet
            if save_as_entity and entity_name:
                try:
                    # Entity oluştur veya güncelle
                    user_id = await get_user_id_from_session(db, session_id)
                    entity = await entity_service.create_entity(
                        db=db,
                        user_id=user_id,
                        entity_type="character",
                        name=entity_name,
                        description=f"Web'den indirilen görsel: {image_url[:50]}...",
                        reference_image_url=saved_url,
                        session_id=session_id
                    )
                    result["entity_id"] = str(entity.id)
                    result["entity_tag"] = f"@{entity_name.lower().replace(' ', '_')}"
                    result["message"] += f" Entity olarak kaydedildi: @{entity_name}"
                except ValueError as ve:
                    # Duplicate entity - user'a bildir ama görsel yine de kaydedildi
                    result["entity_warning"] = str(ve)
                    result["message"] += f" (⚠️ Entity kaydedilemedi: zaten mevcut)"
            
            # Asset olarak kaydet
            try:
                from app.models.models import Asset
                new_asset = Asset(
                    session_id=session_id,
                    asset_type="image",
                    url=saved_url,
                    prompt=f"Web'den indirildi: {image_url[:100]}",
                    model_used="web_fetch"
                )
                db.add(new_asset)
                await db.commit()
                result["asset_id"] = str(new_asset.id)
            except Exception as e:
                print(f"Asset kayıt hatası: {e}")
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


    async def _generate_grid(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        params: dict,
        resolved_entities: list = None
    ) -> dict:
        """
        3x3 Grid oluşturma.
        
        Özellikler:
        - 9 kamera açısı (angles) veya 9 hikaye paneli (storyboard)
        - @karakter referansı ile otomatik görsel kullanımı
        - Panel extraction ve upscale
        """
        import httpx
        
        try:
            image_url = params.get("image_url")
            mode = params.get("mode", "angles")
            aspect_ratio = params.get("aspect_ratio", "16:9")
            extract_panel = params.get("extract_panel")
            scale = params.get("scale", 2)
            custom_prompt = params.get("custom_prompt")
            
            # Entity referansından görsel al
            if resolved_entities:
                for entity in resolved_entities:
                    if hasattr(entity, 'reference_image_url') and entity.reference_image_url:
                        if not image_url:
                            image_url = entity.reference_image_url
                        break
            
            if not image_url:
                return {"success": False, "error": "Görsel URL'si gerekli. Bir görsel gönder veya @karakter kullan."}
            
            # Grid prompt oluştur
            if custom_prompt:
                grid_prompt = custom_prompt
            else:
                grid_prompt = self._build_grid_prompt(mode)
            
            print(f"=== GRID GENERATION (Agent) ===")
            print(f"Mode: {mode}, Aspect: {aspect_ratio}")
            print(f"Image URL: {image_url[:100]}...")
            
            # Grid oluştur (Nano Banana Pro)
            grid_image_url = None
            
            request_body = {
                "prompt": grid_prompt,
                "image_urls": [image_url],
                "num_images": 1,
                "aspect_ratio": aspect_ratio,
                "output_format": "png",
                "resolution": "2K",
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    response = await client.post(
                        "https://fal.run/fal-ai/nano-banana-pro/edit",
                        headers={
                            "Authorization": f"Key {self.fal_plugin.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=request_body
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("images") and len(data["images"]) > 0:
                            grid_image_url = data["images"][0]["url"]
                except Exception as e:
                    print(f"Nano Banana Pro failed: {e}")
            
            # Fallback: FLUX dev
            if not grid_image_url:
                if aspect_ratio == "16:9":
                    image_size = {"width": 1920, "height": 1080}
                elif aspect_ratio == "9:16":
                    image_size = {"width": 1080, "height": 1920}
                else:
                    image_size = {"width": 1024, "height": 1024}
                
                flux_body = {
                    "prompt": grid_prompt,
                    "image_url": image_url,
                    "strength": 0.75,
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "image_size": image_size,
                    "num_images": 1,
                    "enable_safety_checker": False,
                    "output_format": "png",
                }
                
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        "https://fal.run/fal-ai/flux/dev/image-to-image",
                        headers={
                            "Authorization": f"Key {self.fal_plugin.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=flux_body
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("images") and len(data["images"]) > 0:
                            grid_image_url = data["images"][0]["url"]
                    else:
                        return {"success": False, "error": f"Grid oluşturulamadı: {response.text}"}
            
            if not grid_image_url:
                return {"success": False, "error": "Grid oluşturulamadı."}
            
            result = {
                "success": True,
                "grid_image_url": grid_image_url,
                "mode": mode,
                "aspect_ratio": aspect_ratio,
                "message": f"3x3 {mode} grid oluşturuldu!"
            }
            
            # Panel extraction istendi mi?
            if extract_panel and 1 <= extract_panel <= 9:
                # Panel extraction için grid görselini indir ve crop et
                # Bu client-side yapılıyor, URL'yi döndür
                result["extract_panel"] = extract_panel
                result["scale"] = scale
                result["message"] += f" Panel #{extract_panel} seçildi ({scale}x upscale için hazır)."
            
            # Asset kaydet
            try:
                from app.models.models import Asset
                new_asset = Asset(
                    session_id=session_id,
                    asset_type="image",
                    url=grid_image_url,
                    prompt=f"3x3 {mode} grid",
                    model_used="nano-banana-pro"
                )
                db.add(new_asset)
                await db.commit()
                result["asset_id"] = str(new_asset.id)
            except Exception as e:
                print(f"Asset kayıt hatası: {e}")
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _build_grid_prompt(self, mode: str) -> str:
        """Grid için prompt oluştur."""
        if mode == "angles":
            return """Create a seamless 3x3 grid of 9 cinematic camera angles showing the same subject.

GRID REQUIREMENTS:
- NO white borders or gaps between panels
- Each panel edge-to-edge, flowing into the next
- The SAME EXACT person in ALL 9 panels

9 CAMERA ANGLES:
1. WIDE SHOT - full body, environment visible
2. MEDIUM WIDE - head to knees
3. MEDIUM SHOT - waist up
4. MEDIUM CLOSE-UP - chest and head
5. CLOSE-UP - face fills frame
6. THREE-QUARTER VIEW - face angled 45°
7. LOW ANGLE - heroic
8. HIGH ANGLE - looking down
9. PROFILE - side view

CRITICAL: Face must be clearly visible in ALL panels. Cinematic, photorealistic."""

        elif mode == "storyboard":
            return """Create a seamless 3x3 grid of 9 sequential storyboard panels.

GRID REQUIREMENTS:
- NO white borders or gaps between panels
- Each panel edge-to-edge, flowing into the next
- The SAME EXACT person in ALL 9 panels

9 STORY BEATS:
1. ESTABLISHING - calm moment, wide shot
2. TENSION - notices something
3. REACTION - close-up, concern
4. ACTION BEGINS - starts moving
5. PEAK ACTION - dynamic movement
6. INTENSITY - extreme close-up
7. CLIMAX - dramatic action
8. RESOLUTION - conflict ending
9. CONCLUSION - final emotion

CRITICAL: Same character throughout. Cinematic storyboard quality."""

        else:
            return "Create a seamless 3x3 grid showing 9 variations. NO borders, NO gaps. Photorealistic, cinematic."
    
    async def _use_grid_panel(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        params: dict
    ) -> dict:
        """
        Grid'den belirli bir paneli seç ve işlem yap.
        
        Panel numarası 1-9 arası (3x3 grid):
        | 1 | 2 | 3 |
        | 4 | 5 | 6 |
        | 7 | 8 | 9 |
        """
        try:
            panel_number = params.get("panel_number", 1)
            action = params.get("action", "video")
            video_prompt = params.get("video_prompt", "")
            edit_prompt = params.get("edit_prompt", "")
            
            if not 1 <= panel_number <= 9:
                return {"success": False, "error": "Panel numarası 1-9 arası olmalı."}
            
            # Son grid asset'ini bul
            from app.models.models import GeneratedAsset
            from sqlalchemy import select
            
            result = await db.execute(
                select(GeneratedAsset)
                .where(
                    GeneratedAsset.session_id == session_id,
                    GeneratedAsset.prompt.ilike("%grid%")
                )
                .order_by(GeneratedAsset.created_at.desc())
                .limit(1)
            )
            grid_asset = result.scalar_one_or_none()
            
            if not grid_asset:
                return {"success": False, "error": "Önce bir grid oluşturmalısın. 'Grid yap' komutunu dene."}
            
            grid_url = grid_asset.url
            
            # Panel koordinatlarını hesapla (3x3 grid)
            row = (panel_number - 1) // 3
            col = (panel_number - 1) % 3
            
            # Grid görselinden panel crop için frontend'e bilgi gönder
            # veya server-side crop yap
            
            if action == "video":
                # Panel'i video'ya çevir
                prompt = video_prompt or f"Cinematic motion, subtle movement, panel {panel_number} comes alive"
                
                result = await self._generate_video(
                    db, session_id,
                    {
                        "prompt": prompt,
                        "image_url": grid_url,  # Grid'in tamamını gönderiyoruz, crop frontend'de yapılacak
                        "duration": "5"
                    }
                )
                
                if result.get("success"):
                    result["message"] = f"Panel #{panel_number}'den video oluşturuldu!"
                    result["source_panel"] = panel_number
                    result["grid_url"] = grid_url
                return result
                
            elif action == "upscale":
                # Panel'i upscale et
                result = await self._upscale_image({
                    "image_url": grid_url,
                    "scale": 2
                })
                if result.get("success"):
                    result["message"] = f"Panel #{panel_number} 2x büyütüldü!"
                    result["source_panel"] = panel_number
                return result
                
            elif action == "edit":
                # Panel'i düzenle
                if not edit_prompt:
                    return {"success": False, "error": "Düzenleme için edit_prompt gerekli."}
                
                result = await self._edit_image(db, session_id, {
                    "image_url": grid_url,
                    "prompt": edit_prompt
                })
                if result.get("success"):
                    result["message"] = f"Panel #{panel_number} düzenlendi!"
                    result["source_panel"] = panel_number
                return result
                
            elif action == "download":
                return {
                    "success": True,
                    "message": f"Panel #{panel_number} indirme için hazır.",
                    "grid_url": grid_url,
                    "panel_number": panel_number,
                    "panel_position": {"row": row, "col": col},
                    "instruction": "Frontend'de bu paneli kırpıp indir."
                }
            
            else:
                return {"success": False, "error": f"Bilinmeyen action: {action}"}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    # ===============================
    # MARKA YÖNETİM METODLARI
    # ===============================
    
    async def _create_brand(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        params: dict
    ) -> dict:
        """
        Marka entity'si oluştur.
        
        Kullanıcı manuel olarak marka bilgilerini verdiğinde veya
        research_brand sonucu kaydedildiğinde kullanılır.
        """
        try:
            name = params.get("name")
            description = params.get("description", "")
            logo_url = params.get("logo_url")
            attributes = params.get("attributes", {})
            
            # Session'dan user_id al
            user_id = await get_user_id_from_session(db, session_id)
            
            # Entity service ile brand entity oluştur
            entity = await entity_service.create_entity(
                db=db,
                user_id=user_id,
                entity_type="brand",
                name=name,
                description=description,
                attributes=attributes,
                reference_image_url=logo_url,
                session_id=session_id
            )
            
            return {
                "success": True,
                "message": f"✅ Marka '{name}' başarıyla kaydedildi! Tag: {entity.tag}",
                "brand": {
                    "id": str(entity.id),
                    "tag": entity.tag,
                    "name": entity.name,
                    "description": entity.description,
                    "logo_url": logo_url,
                    "colors": attributes.get("colors", {}),
                    "tagline": attributes.get("tagline", ""),
                    "industry": attributes.get("industry", ""),
                    "tone": attributes.get("tone", "")
                }
            }
        
        except ValueError as ve:
            # Duplicate marka hatası
            return {
                "success": False,
                "error": str(ve),
                "duplicate": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Marka oluşturulamadı: {str(e)}"
            }
    
    async def _research_brand(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        params: dict
    ) -> dict:
        """
        AKILLI Web'den marka araştırması.
        
        İş Akışı:
        1. DuckDuckGo ile marka bilgilerini ara
        2. Logo görselini ara ve indir
        3. GPT-4o Vision ile logo analizi yap → RENKLER ÇIKAR
        4. Sosyal medya hesaplarını bul
        5. (Opsiyonel) Marka olarak kaydet
        """
        try:
            brand_name = params.get("brand_name")
            research_depth = params.get("research_depth", "detailed")
            should_save = params.get("save", False)
            
            # Sonuç tutacak
            brand_info = {
                "name": brand_name,
                "description": "",
                "website": None,
                "colors": {},
                "tagline": "",
                "industry": "",
                "tone": "",
                "social_media": {},
                "logo_url": None,
                "research_notes": []
            }
            
            from duckduckgo_search import DDGS
            import httpx
            import base64
            
            with DDGS() as ddgs:
                # 1. Temel bilgi araması
                search_results = list(ddgs.text(
                    f"{brand_name} brand company official",
                    max_results=5
                ))
                
                if search_results:
                    brand_info["description"] = search_results[0].get("body", "")
                    brand_info["website"] = search_results[0].get("href", "")
                    brand_info["research_notes"].append(f"Web aramasından {len(search_results)} sonuç bulundu")
                
                # 2. 🎨 LOGO GÖRSEL ARAŞTIRMASI - KRİTİK!
                print(f"🔍 {brand_name} logosu aranıyor...")
                logo_found = False
                
                try:
                    # Logo görsellerini ara
                    image_results = list(ddgs.images(
                        f"{brand_name} logo official transparent",
                        max_results=5
                    ))
                    
                    if image_results:
                        brand_info["research_notes"].append(f"Logo aramasında {len(image_results)} görsel bulundu")
                        
                        # En iyi logo adayını bul
                        for img_result in image_results:
                            image_url = img_result.get("image")
                            if not image_url:
                                continue
                            
                            print(f"   → Logo adayı: {image_url[:80]}...")
                            
                            try:
                                # Logoyu indir
                                async with httpx.AsyncClient(timeout=10.0) as client:
                                    response = await client.get(image_url, follow_redirects=True)
                                    if response.status_code == 200:
                                        image_data = response.content
                                        
                                        # Base64'e çevir
                                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                                        
                                        # Content type belirle
                                        content_type = response.headers.get("content-type", "image/png")
                                        if "jpeg" in content_type or "jpg" in content_type:
                                            media_type = "image/jpeg"
                                        elif "png" in content_type:
                                            media_type = "image/png"
                                        elif "webp" in content_type:
                                            media_type = "image/webp"
                                        else:
                                            media_type = "image/png"
                                        
                                        data_url = f"data:{media_type};base64,{image_base64}"
                                        
                                        # 3. 🧠 GPT-4o VISION İLE RENK ANALİZİ!
                                        print(f"   🎨 Logo analiz ediliyor (GPT-4o Vision)...")
                                        
                                        analysis_response = self.client.chat.completions.create(
                                            model="gpt-4o",
                                            max_tokens=500,
                                            messages=[
                                                {
                                                    "role": "system",
                                                    "content": "Sen bir marka renk analisti sin. Verilen logo görselini analiz et ve marka renklerini çıkart. SADECE JSON formatında yanıt ver, başka hiçbir şey yazma."
                                                },
                                                {
                                                    "role": "user",
                                                    "content": [
                                                        {
                                                            "type": "image_url",
                                                            "image_url": {"url": data_url, "detail": "high"}
                                                        },
                                                        {
                                                            "type": "text",
                                                            "text": f"""Bu {brand_name} markasının logosu. Analiz et ve şu bilgileri JSON olarak döndür:

{{
    "primary_color": "#HEX - ana renk",
    "secondary_color": "#HEX - ikincil renk (varsa)",
    "accent_colors": ["#HEX", "#HEX"] veya [],
    "color_names": {{"primary": "renk adı türkçe", "secondary": "renk adı"}},
    "logo_style": "minimalist/ornate/text-based/icon-based/combination",
    "dominant_mood": "profesyonel/eğlenceli/lüks/enerji/güvenilir/yaratıcı"
}}

SADECE JSON döndür, başka açıklama yazma."""
                                                        }
                                                    ]
                                                }
                                            ]
                                        )
                                        
                                        analysis_text = analysis_response.choices[0].message.content.strip()
                                        
                                        # JSON'u parse et
                                        import json
                                        import re
                                        
                                        # JSON bloğunu bul
                                        json_match = re.search(r'\{[\s\S]*\}', analysis_text)
                                        if json_match:
                                            try:
                                                color_data = json.loads(json_match.group())
                                                brand_info["colors"] = color_data
                                                brand_info["logo_url"] = image_url
                                                logo_found = True
                                                
                                                primary = color_data.get("primary_color", "")
                                                color_name = color_data.get("color_names", {}).get("primary", "")
                                                brand_info["research_notes"].append(f"✅ Logo analizi başarılı! Ana renk: {color_name} ({primary})")
                                                print(f"   ✅ Renkler bulundu: {primary} ({color_name})")
                                                break  # İlk başarılı logoda dur
                                            except json.JSONDecodeError:
                                                print(f"   ⚠️ JSON parse hatası")
                                                continue
                                        
                            except Exception as img_error:
                                print(f"   ⚠️ Logo indirme/analiz hatası: {img_error}")
                                continue
                    else:
                        brand_info["research_notes"].append("Logo görseli bulunamadı")
                        
                except Exception as logo_error:
                    print(f"⚠️ Logo araştırma hatası: {logo_error}")
                    brand_info["research_notes"].append(f"Logo araştırma hatası: {str(logo_error)}")
                
                # 4. Slogan araması
                tagline_results = list(ddgs.text(
                    f"{brand_name} slogan tagline",
                    max_results=3
                ))
                
                for result in tagline_results:
                    body = result.get("body", "")
                    title = result.get("title", "")
                    if any(word in body.lower() for word in ["slogan", "tagline", "motto"]):
                        # Slogan'ı çıkarmaya çalış
                        brand_info["tagline"] = body[:150]
                        brand_info["research_notes"].append(f"Slogan bulundu")
                        break
                
                # 5. Sosyal medya araştırması
                if research_depth in ["detailed", "comprehensive"]:
                    # Instagram
                    insta_results = list(ddgs.text(
                        f"{brand_name} official instagram",
                        max_results=3
                    ))
                    for result in insta_results:
                        href = result.get("href", "")
                        if "instagram.com" in href:
                            brand_info["social_media"]["instagram"] = href
                            break
                    
                    # Twitter/X
                    twitter_results = list(ddgs.text(
                        f"{brand_name} official twitter",
                        max_results=3
                    ))
                    for result in twitter_results:
                        href = result.get("href", "")
                        if "twitter.com" in href or "x.com" in href:
                            brand_info["social_media"]["twitter"] = href
                            break
                    
                    # LinkedIn
                    linkedin_results = list(ddgs.text(
                        f"{brand_name} official linkedin company",
                        max_results=3
                    ))
                    for result in linkedin_results:
                        href = result.get("href", "")
                        if "linkedin.com" in href:
                            brand_info["social_media"]["linkedin"] = href
                            break
                    
                    brand_info["research_notes"].append(f"Sosyal medya: {len(brand_info['social_media'])} hesap bulundu")
            
            # Sonuç özeti
            colors_summary = ""
            if brand_info["colors"]:
                primary = brand_info["colors"].get("primary_color", "")
                color_name = brand_info["colors"].get("color_names", {}).get("primary", "")
                if primary:
                    colors_summary = f"\n🎨 Ana Renk: {color_name} ({primary})"
                    if brand_info["colors"].get("secondary_color"):
                        sec = brand_info["colors"]["secondary_color"]
                        sec_name = brand_info["colors"].get("color_names", {}).get("secondary", "")
                        colors_summary += f"\n🎨 İkincil: {sec_name} ({sec})"
            
            result = {
                "success": True,
                "brand_info": brand_info,
                "research_depth": research_depth,
                "logo_analyzed": logo_found,
                "message": f"🔍 {brand_name} hakkında DETAYLI araştırma tamamlandı.\n"
                          f"Website: {brand_info['website'] or 'Bulunamadı'}"
                          f"{colors_summary}"
                          f"\nSosyal Medya: {len(brand_info['social_media'])} hesap"
                          f"\n📝 {len(brand_info['research_notes'])} araştırma notu"
            }
            
            # Kaydetme istendi mi?
            if should_save:
                save_result = await self._create_brand(
                    db=db,
                    session_id=session_id,
                    params={
                        "name": brand_name,
                        "description": brand_info["description"],
                        "logo_url": brand_info["logo_url"],
                        "attributes": {
                            "colors": brand_info["colors"],
                            "tagline": brand_info["tagline"],
                            "industry": brand_info["industry"],
                            "tone": brand_info["colors"].get("dominant_mood", ""),
                            "social_media": brand_info["social_media"],
                            "website": brand_info["website"]
                        }
                    }
                )
                
                if save_result.get("success"):
                    result["saved"] = True
                    result["brand_tag"] = save_result.get("brand", {}).get("tag")
                    result["message"] += f"\n✅ Marka kaydedildi: {result['brand_tag']}"
            
            return result
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Marka araştırması başarısız: {str(e)}"
            }


# Singleton instance
agent = AgentOrchestrator()

