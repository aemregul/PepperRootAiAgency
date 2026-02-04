"use client";

import { useState } from "react";
import { X, Store, Search, Star, Download, Plus, Filter, TrendingUp, Clock, Users } from "lucide-react";
import { CreativePlugin } from "./CreativePluginModal";

interface PluginMarketplaceModalProps {
    isOpen: boolean;
    onClose: () => void;
    onInstall: (plugin: CreativePlugin) => void;
    myPlugins: CreativePlugin[];
}

// Community creative plugins - zengin çeşitlilik
const communityPlugins: CreativePlugin[] = [
    // === GÖRSEL PAKETLER ===
    {
        id: "comm1",
        name: "Cinematic Portrait Pack",
        description: "Hollywood tarzı portre çekimleri için hazır ayarlar. Dramatic lighting ve bokeh efektleri.",
        author: "StudioPro",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Değişken", isVariable: true },
            location: { id: "studio", name: "Professional Studio", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Close-up", "Medium Shot", "Over Shoulder"],
            style: "Cinematic",
            promptTemplate: "professional portrait, dramatic lighting, shallow depth of field, {character}"
        },
        createdAt: new Date("2026-01-15"),
        downloads: 1250,
        rating: 4.9
    },
    {
        id: "comm2",
        name: "E-Commerce Product Shots",
        description: "Online mağaza için ürün fotoğrafları. Beyaz arka plan, soft shadows.",
        author: "ShopVisuals",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün", isVariable: true },
            location: { id: "whitebg", name: "White Background", settings: "" },
            timeOfDay: "Studio Light",
            cameraAngles: ["Front View", "45 Degree", "Top Down"],
            style: "Commercial",
            promptTemplate: "product photography, white background, soft shadows, professional lighting"
        },
        createdAt: new Date("2026-01-20"),
        downloads: 890,
        rating: 4.7
    },
    {
        id: "comm3",
        name: "Urban Street Style",
        description: "Sokak modası çekimleri için şehir ortamları ve doğal ışık.",
        author: "StreetVision",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Değişken", isVariable: true },
            location: { id: "urban", name: "Urban Street", settings: "" },
            timeOfDay: "Afternoon",
            cameraAngles: ["Wide Shot", "Medium Shot", "Dutch Angle"],
            style: "Editorial",
            promptTemplate: "street fashion photography, urban environment, natural light, {character}"
        },
        createdAt: new Date("2026-01-25"),
        downloads: 720,
        rating: 4.6
    },
    {
        id: "comm4",
        name: "Food Photography Pro",
        description: "Yemek fotoğrafçılığı için profesyonel ayarlar.",
        author: "FoodieShots",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Yemek", isVariable: true },
            location: { id: "restaurant", name: "Restaurant Table", settings: "" },
            timeOfDay: "Warm Light",
            cameraAngles: ["Top Down", "45 Degree", "Close-up"],
            style: "Warm Tones",
            promptTemplate: "food photography, appetizing, warm tones, shallow depth of field"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 560,
        rating: 4.8
    },
    {
        id: "comm5",
        name: "Minimalist Interior",
        description: "İç mekan tasarımı ve mimari fotoğraflar için minimalist yaklaşım.",
        author: "ArchViz",
        isPublic: true,
        config: {
            character: { id: "none", name: "Yok", isVariable: false },
            location: { id: "interior", name: "Modern Interior", settings: "" },
            timeOfDay: "Natural Light",
            cameraAngles: ["Wide Shot", "Corner View", "Detail Shot"],
            style: "Minimalist",
            promptTemplate: "interior photography, minimalist design, natural light, clean lines"
        },
        createdAt: new Date("2026-01-29"),
        downloads: 340,
        rating: 4.5
    },

    // === VİDEO & ANİMASYON PAKETLER ===
    {
        id: "video1",
        name: "Video Reklam Paketi",
        description: "Sosyal medya video reklamları için hazır şablonlar. Instagram Reels, TikTok, YouTube Shorts.",
        author: "AdCreative",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün/Kişi", isVariable: true },
            location: { id: "studio", name: "Clean Studio", settings: "" },
            timeOfDay: "Bright",
            cameraAngles: ["Product Hero", "Lifestyle", "Call to Action"],
            style: "Commercial Video",
            promptTemplate: "video advertisement, dynamic movement, product showcase, engaging, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 2100,
        rating: 4.9
    },
    {
        id: "video2",
        name: "Anime & Manga Style",
        description: "Anime tarzı karakter ve sahne üretimi. Studio Ghibli, Makoto Shinkai stilleri.",
        author: "AnimeArtist",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Karakter", isVariable: true },
            location: { id: "fantasy", name: "Anime World", settings: "" },
            timeOfDay: "Sunset",
            cameraAngles: ["Portrait", "Action Pose", "Emotional"],
            style: "Anime",
            promptTemplate: "anime style, detailed, vibrant colors, studio ghibli inspired, {character}"
        },
        createdAt: new Date("2026-02-02"),
        downloads: 3450,
        rating: 4.8
    },
    {
        id: "video3",
        name: "Music Video Aesthetics",
        description: "Müzik videoları için sinematik görüntüler. Neon, retro, futuristik tema.",
        author: "MVProductions",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Artist", isVariable: true },
            location: { id: "neon", name: "Neon City", settings: "" },
            timeOfDay: "Night",
            cameraAngles: ["Wide Cinematic", "Close Portrait", "Dutch Angle"],
            style: "Music Video",
            promptTemplate: "music video aesthetic, neon lights, cinematic, dramatic composition, {character}"
        },
        createdAt: new Date("2026-02-03"),
        downloads: 1890,
        rating: 4.7
    },

    // === SOSYAL MEDYA PAKETLER ===
    {
        id: "social1",
        name: "Instagram Influencer Pack",
        description: "Instagram için estetik içerik. Lifestyle, selfie, flat lay kompozisyonlar.",
        author: "InstaCreator",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Influencer", isVariable: true },
            location: { id: "aesthetic", name: "Aesthetic Space", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Selfie Style", "Flat Lay", "Mirror Shot"],
            style: "Instagram",
            promptTemplate: "instagram aesthetic, lifestyle, vibrant, trendy, influencer style, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 4200,
        rating: 4.9
    },
    {
        id: "social2",
        name: "LinkedIn Professional",
        description: "Profesyonel profil ve kurumsal içerik için iş dünyası görselleri.",
        author: "CorpMedia",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Professional", isVariable: true },
            location: { id: "office", name: "Modern Office", settings: "" },
            timeOfDay: "Day",
            cameraAngles: ["Headshot", "Working Shot", "Team Meeting"],
            style: "Corporate",
            promptTemplate: "professional business portrait, corporate, clean, confident, {character}"
        },
        createdAt: new Date("2026-01-30"),
        downloads: 1560,
        rating: 4.6
    },
    {
        id: "social3",
        name: "YouTube Thumbnail Pro",
        description: "Yüksek CTR için dikkat çekici YouTube thumbnail tasarımları.",
        author: "ThumbnailKing",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Creator", isVariable: true },
            location: { id: "colorful", name: "Vibrant Background", settings: "" },
            timeOfDay: "Bright",
            cameraAngles: ["Face Reaction", "Dramatic", "Action"],
            style: "YouTube",
            promptTemplate: "youtube thumbnail, expressive, bold colors, eye-catching, dramatic, {character}"
        },
        createdAt: new Date("2026-02-02"),
        downloads: 2890,
        rating: 4.8
    },

    // === SEKTÖREL PAKETLER ===
    {
        id: "sector1",
        name: "Real Estate Showcase",
        description: "Gayrimenkul ilanları için profesyonel mülk fotoğrafları ve 3D turlar.",
        author: "PropertyViz",
        isPublic: true,
        config: {
            character: { id: "none", name: "Yok", isVariable: false },
            location: { id: "property", name: "Luxury Property", settings: "" },
            timeOfDay: "Twilight",
            cameraAngles: ["Exterior Wide", "Interior Panorama", "Aerial View"],
            style: "Real Estate",
            promptTemplate: "real estate photography, luxury home, professional, inviting, architectural beauty"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 980,
        rating: 4.7
    },
    {
        id: "sector2",
        name: "Automotive Photography",
        description: "Otomobil ve araç fotoğrafçılığı. Showroom kalitesinde çekimler.",
        author: "AutoShots",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Araç", isVariable: true },
            location: { id: "showroom", name: "Car Showroom", settings: "" },
            timeOfDay: "Studio",
            cameraAngles: ["Front 3/4", "Side Profile", "Interior"],
            style: "Automotive",
            promptTemplate: "automotive photography, showroom quality, sleek, professional lighting, {character}"
        },
        createdAt: new Date("2026-01-25"),
        downloads: 670,
        rating: 4.6
    },
    {
        id: "sector3",
        name: "Fashion Lookbook",
        description: "Moda markaları için lookbook ve katalog çekimleri.",
        author: "FashionForward",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Model", isVariable: true },
            location: { id: "studio", name: "Fashion Studio", settings: "" },
            timeOfDay: "Soft Light",
            cameraAngles: ["Full Body", "Three Quarter", "Detail Close-up"],
            style: "Fashion Editorial",
            promptTemplate: "fashion photography, editorial, high fashion, stylish, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 1340,
        rating: 4.8
    },

    // === ÖZEL DURUMLAR ===
    {
        id: "special1",
        name: "Wedding Photography",
        description: "Düğün fotoğrafçılığı için romantik ve duygusal anlar.",
        author: "WeddingMoments",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Çift", isVariable: true },
            location: { id: "wedding", name: "Wedding Venue", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Couple Portrait", "Candid Moment", "Detail Shot"],
            style: "Romantic",
            promptTemplate: "wedding photography, romantic, emotional, beautiful couple, {character}"
        },
        createdAt: new Date("2026-01-22"),
        downloads: 2100,
        rating: 4.9
    },
    {
        id: "special2",
        name: "Sports Action Shots",
        description: "Spor ve aksiyon fotoğrafçılığı. Dinamik hareketler, donmuş anlar.",
        author: "ActionFreeze",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Sporcu", isVariable: true },
            location: { id: "sports", name: "Sports Arena", settings: "" },
            timeOfDay: "Day",
            cameraAngles: ["Action Freeze", "Wide Arena", "Close Intensity"],
            style: "Sports",
            promptTemplate: "sports photography, action, dynamic, powerful, athletic, {character}"
        },
        createdAt: new Date("2026-01-18"),
        downloads: 890,
        rating: 4.7
    },
    {
        id: "special3",
        name: "Podcast Cover Art",
        description: "Podcast kapak görselleri ve sosyal medya tanıtımları.",
        author: "PodcastPro",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Host", isVariable: true },
            location: { id: "studio", name: "Podcast Studio", settings: "" },
            timeOfDay: "Moody",
            cameraAngles: ["Portrait", "Microphone Shot", "Graphic Style"],
            style: "Podcast",
            promptTemplate: "podcast cover art, professional, engaging, personal brand, {character}"
        },
        createdAt: new Date("2026-02-03"),
        downloads: 560,
        rating: 4.5
    },

    // === 3D & TECH ===
    {
        id: "tech1",
        name: "3D Product Render",
        description: "Ürün için fotorealistik 3D renderlar. Stüdyo kalitesinde.",
        author: "3DStudio",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün", isVariable: true },
            location: { id: "3dstudio", name: "3D Studio", settings: "" },
            timeOfDay: "Studio",
            cameraAngles: ["Hero Shot", "Exploded View", "Material Detail"],
            style: "3D Render",
            promptTemplate: "3d product render, photorealistic, studio lighting, professional, {character}"
        },
        createdAt: new Date("2026-02-04"),
        downloads: 1120,
        rating: 4.8
    },
    {
        id: "tech2",
        name: "Tech Startup Visuals",
        description: "Teknoloji startup'ları için modern ve futuristik görseller.",
        author: "TechVision",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Tech Product", isVariable: true },
            location: { id: "futuristic", name: "Futuristic Lab", settings: "" },
            timeOfDay: "Blue Hour",
            cameraAngles: ["Product Feature", "In Use", "Abstract Tech"],
            style: "Tech",
            promptTemplate: "technology, futuristic, innovative, clean design, startup, {character}"
        },
        createdAt: new Date("2026-02-04"),
        downloads: 780,
        rating: 4.6
    },

    // === SANAT & YARATICI ===
    {
        id: "art1",
        name: "Digital Art Fantasy",
        description: "Fantastik dijital sanat. Ejderhalar, büyücüler, efsanevi dünyalar.",
        author: "FantasyArt",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Karakter", isVariable: true },
            location: { id: "fantasy", name: "Fantasy Realm", settings: "" },
            timeOfDay: "Mystical",
            cameraAngles: ["Epic Wide", "Character Portrait", "Battle Scene"],
            style: "Fantasy Art",
            promptTemplate: "digital fantasy art, epic, magical, detailed, dramatic lighting, {character}"
        },
        createdAt: new Date("2026-01-20"),
        downloads: 4500,
        rating: 4.9
    },
    {
        id: "art2",
        name: "Watercolor Illustration",
        description: "Sulu boya tarzı illüstrasyonlar. Yumuşak, organik, sanatsal.",
        author: "WatercolorArt",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Konu", isVariable: true },
            location: { id: "nature", name: "Nature Scene", settings: "" },
            timeOfDay: "Soft",
            cameraAngles: ["Portrait", "Landscape", "Still Life"],
            style: "Watercolor",
            promptTemplate: "watercolor illustration, soft colors, artistic, organic texture, {character}"
        },
        createdAt: new Date("2026-01-15"),
        downloads: 1230,
        rating: 4.7
    },
    {
        id: "art3",
        name: "Retro 80s Synthwave",
        description: "80'ler retro synthwave estetiği. Neon, grid, güneş batımı.",
        author: "RetroWave",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Element", isVariable: true },
            location: { id: "retro", name: "Synthwave City", settings: "" },
            timeOfDay: "Sunset",
            cameraAngles: ["Wide Horizon", "Neon Portrait", "Car Chase"],
            style: "Synthwave",
            promptTemplate: "synthwave aesthetic, 80s retro, neon colors, grid, sunset, {character}"
        },
        createdAt: new Date("2026-02-02"),
        downloads: 2340,
        rating: 4.8
    },

    // === EĞİTİM & KURUMSAL ===
    {
        id: "edu1",
        name: "E-Learning Course Visuals",
        description: "Online kurslar için eğitici görseller ve illüstrasyonlar.",
        author: "EduDesign",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Konu", isVariable: true },
            location: { id: "classroom", name: "Digital Classroom", settings: "" },
            timeOfDay: "Bright",
            cameraAngles: ["Infographic", "Diagram", "Character Explain"],
            style: "Educational",
            promptTemplate: "educational illustration, clean, informative, friendly, modern design, {character}"
        },
        createdAt: new Date("2026-02-03"),
        downloads: 890,
        rating: 4.6
    },
    {
        id: "edu2",
        name: "Children's Book Illustration",
        description: "Çocuk kitapları için sevimli ve eğlenceli illüstrasyonlar.",
        author: "KidsArt",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Karakter", isVariable: true },
            location: { id: "fantasy", name: "Magical World", settings: "" },
            timeOfDay: "Colorful",
            cameraAngles: ["Character Focus", "Scene Wide", "Action Moment"],
            style: "Children's Book",
            promptTemplate: "children's book illustration, cute, colorful, whimsical, friendly, {character}"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 1560,
        rating: 4.9
    },

    // === SAĞLIK & WELLNESS ===
    {
        id: "health1",
        name: "Medical & Healthcare",
        description: "Sağlık sektörü için profesyonel tıbbi görseller.",
        author: "MedVisuals",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Tıbbi Konu", isVariable: true },
            location: { id: "hospital", name: "Medical Facility", settings: "" },
            timeOfDay: "Clean Light",
            cameraAngles: ["Clinical", "Caring", "Professional"],
            style: "Medical",
            promptTemplate: "medical photography, healthcare, professional, clean, trustworthy, {character}"
        },
        createdAt: new Date("2026-01-25"),
        downloads: 670,
        rating: 4.5
    },
    {
        id: "health2",
        name: "Yoga & Meditation",
        description: "Yoga ve meditasyon için huzurlu, zen görseller.",
        author: "ZenStudio",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Pose", isVariable: true },
            location: { id: "zen", name: "Peaceful Space", settings: "" },
            timeOfDay: "Soft Morning",
            cameraAngles: ["Full Body Flow", "Close Focus", "Environment"],
            style: "Zen",
            promptTemplate: "yoga photography, peaceful, serene, natural light, mindfulness, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 1120,
        rating: 4.8
    },

    // === FİNANS & İŞ ===
    {
        id: "finance1",
        name: "Fintech & Banking",
        description: "Fintech ve bankacılık için modern, güvenilir görseller.",
        author: "FinanceViz",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Finansal Konsept", isVariable: true },
            location: { id: "modern", name: "Modern Office", settings: "" },
            timeOfDay: "Professional",
            cameraAngles: ["Data Visualization", "App Interface", "Trust Shot"],
            style: "Fintech",
            promptTemplate: "fintech design, modern, trustworthy, clean, professional, digital banking, {character}"
        },
        createdAt: new Date("2026-01-30"),
        downloads: 780,
        rating: 4.6
    },
    {
        id: "finance2",
        name: "Crypto & Blockchain",
        description: "Kripto para ve blockchain projeleri için futuristik görseller.",
        author: "CryptoArt",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Crypto Element", isVariable: true },
            location: { id: "digital", name: "Digital Space", settings: "" },
            timeOfDay: "Neon",
            cameraAngles: ["Abstract", "Network Visual", "Coin Hero"],
            style: "Crypto",
            promptTemplate: "cryptocurrency design, blockchain, futuristic, neon, digital, {character}"
        },
        createdAt: new Date("2026-02-02"),
        downloads: 1890,
        rating: 4.7
    },

    // === OYUN & ENTERTAİNMENT ===
    {
        id: "game1",
        name: "Game Character Design",
        description: "Video oyun karakterleri için konsept sanatı.",
        author: "GameArtist",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Karakter", isVariable: true },
            location: { id: "game", name: "Game World", settings: "" },
            timeOfDay: "Dramatic",
            cameraAngles: ["Character Sheet", "Action Pose", "Portrait"],
            style: "Game Art",
            promptTemplate: "game character design, detailed, dynamic, concept art, {character}"
        },
        createdAt: new Date("2026-01-22"),
        downloads: 3200,
        rating: 4.9
    },
    {
        id: "game2",
        name: "Mobile Game UI",
        description: "Mobil oyunlar için renkli ve eğlenceli UI elementleri.",
        author: "MobileGameUI",
        isPublic: true,
        config: {
            character: { id: "variable", name: "UI Element", isVariable: true },
            location: { id: "game", name: "Game Interface", settings: "" },
            timeOfDay: "Vibrant",
            cameraAngles: ["Button", "Icon", "Screen Layout"],
            style: "Game UI",
            promptTemplate: "mobile game UI, colorful, playful, engaging, cartoon style, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 1450,
        rating: 4.7
    },

    // === SEYAHAT & TURİZM ===
    {
        id: "travel1",
        name: "Travel Photography",
        description: "Seyahat ve turizm için etkileyici destinasyon fotoğrafları.",
        author: "Wanderlust",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Destinasyon", isVariable: true },
            location: { id: "travel", name: "Exotic Location", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Landscape Wide", "Detail Shot", "Human Element"],
            style: "Travel",
            promptTemplate: "travel photography, wanderlust, beautiful destination, inspiring, {character}"
        },
        createdAt: new Date("2026-01-20"),
        downloads: 2100,
        rating: 4.8
    },
    {
        id: "travel2",
        name: "Hotel & Resort Marketing",
        description: "Otel ve resort tanıtımı için lüks konaklama görselleri.",
        author: "HospitalityPro",
        isPublic: true,
        config: {
            character: { id: "none", name: "Yok", isVariable: false },
            location: { id: "hotel", name: "Luxury Resort", settings: "" },
            timeOfDay: "Warm Afternoon",
            cameraAngles: ["Room Interior", "Pool View", "Dining Experience"],
            style: "Hospitality",
            promptTemplate: "luxury hotel photography, elegant, inviting, high-end resort, relaxing atmosphere"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 760,
        rating: 4.6
    },

    // === BEBEK & AİLE ===
    {
        id: "family1",
        name: "Newborn & Baby Photos",
        description: "Yeni doğan ve bebek fotoğrafçılığı için yumuşak tonlar.",
        author: "BabyMoments",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Bebek", isVariable: true },
            location: { id: "nursery", name: "Cozy Nursery", settings: "" },
            timeOfDay: "Soft Natural",
            cameraAngles: ["Close-up", "With Parent", "Sleeping"],
            style: "Newborn",
            promptTemplate: "newborn photography, soft, gentle, warm tones, precious moments, {character}"
        },
        createdAt: new Date("2026-01-18"),
        downloads: 1340,
        rating: 4.9
    },
    {
        id: "family2",
        name: "Family Portrait Sessions",
        description: "Aile portreleri için doğal ve samimi anlar.",
        author: "FamilyFirst",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Aile", isVariable: true },
            location: { id: "outdoor", name: "Natural Setting", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Group Portrait", "Candid Moment", "Playful"],
            style: "Family",
            promptTemplate: "family photography, warm, loving, natural, candid moments, {character}"
        },
        createdAt: new Date("2026-01-25"),
        downloads: 980,
        rating: 4.7
    },

    // === EVCİL HAYVAN ===
    {
        id: "pet1",
        name: "Pet Photography Pro",
        description: "Evcil hayvan fotoğrafçılığı için eğlenceli ve sevimli kareler.",
        author: "PetLens",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Evcil Hayvan", isVariable: true },
            location: { id: "studio", name: "Pet Studio", settings: "" },
            timeOfDay: "Bright",
            cameraAngles: ["Portrait", "Action", "Funny Moment"],
            style: "Pet",
            promptTemplate: "pet photography, adorable, playful, expressive, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 2200,
        rating: 4.9
    },

    // === KOZMETİK & GÜZELLİK ===
    {
        id: "beauty1",
        name: "Beauty & Cosmetics",
        description: "Kozmetik ürünleri ve güzellik içerikleri için glamour çekimler.",
        author: "GlamourShots",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün/Model", isVariable: true },
            location: { id: "beauty", name: "Beauty Studio", settings: "" },
            timeOfDay: "Soft Light",
            cameraAngles: ["Product Close-up", "Application Shot", "Model Portrait"],
            style: "Beauty",
            promptTemplate: "beauty photography, glamorous, elegant, cosmetics, flawless, {character}"
        },
        createdAt: new Date("2026-01-30"),
        downloads: 1670,
        rating: 4.8
    },
    {
        id: "beauty2",
        name: "Skincare & Wellness",
        description: "Cilt bakımı ve wellness markaları için doğal görseller.",
        author: "SkinGlow",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün", isVariable: true },
            location: { id: "spa", name: "Spa Environment", settings: "" },
            timeOfDay: "Natural",
            cameraAngles: ["Product Hero", "Texture Detail", "Lifestyle"],
            style: "Skincare",
            promptTemplate: "skincare photography, natural, clean, fresh, wellness, organic feel, {character}"
        },
        createdAt: new Date("2026-02-02"),
        downloads: 890,
        rating: 4.6
    },

    // === FİTNESS & SPOR ===
    {
        id: "fitness1",
        name: "Gym & Fitness Marketing",
        description: "Spor salonları ve fitness markaları için enerjik görseller.",
        author: "FitMedia",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Sporcu", isVariable: true },
            location: { id: "gym", name: "Modern Gym", settings: "" },
            timeOfDay: "Dramatic",
            cameraAngles: ["Action Shot", "Equipment Focus", "Motivation"],
            style: "Fitness",
            promptTemplate: "fitness photography, powerful, energetic, motivational, athletic, {character}"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 1450,
        rating: 4.7
    },

    // === MİMARİ ===
    {
        id: "arch1",
        name: "Architectural Visualization",
        description: "Mimari projeler için fotorealistik 3D görselleştirmeler.",
        author: "ArchRender",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Bina", isVariable: true },
            location: { id: "exterior", name: "Urban Context", settings: "" },
            timeOfDay: "Blue Hour",
            cameraAngles: ["Exterior Hero", "Interior Space", "Detail"],
            style: "Architectural",
            promptTemplate: "architectural visualization, photorealistic, modern design, {character}"
        },
        createdAt: new Date("2026-02-03"),
        downloads: 1120,
        rating: 4.8
    },

    // === MÜZİK ===
    {
        id: "music1",
        name: "Album Cover Art",
        description: "Albüm kapakları için yaratıcı ve dikkat çekici tasarımlar.",
        author: "AlbumArtist",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Artist/Tema", isVariable: true },
            location: { id: "abstract", name: "Abstract Space", settings: "" },
            timeOfDay: "Artistic",
            cameraAngles: ["Square Format", "Visual Metaphor", "Typography Ready"],
            style: "Album Art",
            promptTemplate: "album cover art, creative, eye-catching, artistic, memorable, {character}"
        },
        createdAt: new Date("2026-01-22"),
        downloads: 2560,
        rating: 4.8
    },

    // === FİLM & TV ===
    {
        id: "film1",
        name: "Movie Poster Design",
        description: "Film ve dizi posterleri için sinematik kompozisyonlar.",
        author: "PosterPro",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Film/Karakter", isVariable: true },
            location: { id: "cinematic", name: "Dramatic Scene", settings: "" },
            timeOfDay: "Dramatic",
            cameraAngles: ["Hero Poster", "Character Ensemble", "Teaser"],
            style: "Movie Poster",
            promptTemplate: "movie poster design, cinematic, dramatic, compelling, theatrical, {character}"
        },
        createdAt: new Date("2026-02-01"),
        downloads: 1890,
        rating: 4.9
    },
    {
        id: "film2",
        name: "Documentary Style",
        description: "Belgesel ve gerçekçi hikaye anlatımı için görsel stil.",
        author: "DocuVision",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Konu", isVariable: true },
            location: { id: "real", name: "Real Location", settings: "" },
            timeOfDay: "Natural",
            cameraAngles: ["Candid", "Environmental Portrait", "Detail"],
            style: "Documentary",
            promptTemplate: "documentary photography, authentic, real, storytelling, human interest, {character}"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 670,
        rating: 4.5
    },

    // === YEMEK & İÇECEK ===
    {
        id: "food2",
        name: "Beverage & Cocktails",
        description: "İçecek markaları ve barlar için profesyonel içecek fotoğrafları.",
        author: "DrinkShots",
        isPublic: true,
        config: {
            character: { id: "variable", name: "İçecek", isVariable: true },
            location: { id: "bar", name: "Bar Setting", settings: "" },
            timeOfDay: "Moody",
            cameraAngles: ["Hero Shot", "Pour Action", "Ingredient Detail"],
            style: "Beverage",
            promptTemplate: "beverage photography, refreshing, elegant, professional, {character}"
        },
        createdAt: new Date("2026-02-03"),
        downloads: 890,
        rating: 4.7
    },
    {
        id: "food3",
        name: "Bakery & Desserts",
        description: "Pastane ve tatlılar için iştah açıcı görseller.",
        author: "SweetLens",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Tatlı", isVariable: true },
            location: { id: "bakery", name: "Artisan Bakery", settings: "" },
            timeOfDay: "Warm",
            cameraAngles: ["Close-up", "Slice Shot", "Display"],
            style: "Bakery",
            promptTemplate: "bakery photography, delicious, appetizing, artisan, warm tones, {character}"
        },
        createdAt: new Date("2026-01-30"),
        downloads: 1230,
        rating: 4.8
    },

    // === MODA DETAY ===
    {
        id: "fashion2",
        name: "Streetwear & Urban Fashion",
        description: "Streetwear markaları için urban ve edgy görseller.",
        author: "StreetStyle",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Model", isVariable: true },
            location: { id: "urban", name: "Urban Environment", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Full Look", "Brand Focus", "Lifestyle"],
            style: "Streetwear",
            promptTemplate: "streetwear fashion, urban, edgy, authentic, street culture, {character}"
        },
        createdAt: new Date("2026-02-02"),
        downloads: 1780,
        rating: 4.8
    },
    {
        id: "fashion3",
        name: "Jewelry & Accessories",
        description: "Takı ve aksesuar için detaylı makro çekimler.",
        author: "LuxuryDetails",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün", isVariable: true },
            location: { id: "studio", name: "Luxury Studio", settings: "" },
            timeOfDay: "Studio",
            cameraAngles: ["Macro Detail", "On Model", "Artistic"],
            style: "Jewelry",
            promptTemplate: "jewelry photography, luxury, detailed, elegant, precious, {character}"
        },
        createdAt: new Date("2026-01-25"),
        downloads: 920,
        rating: 4.7
    },

    // === SOSYAL SORUMLULUK ===
    {
        id: "cause1",
        name: "Environmental & Nature",
        description: "Çevre ve doğa koruma projeleri için etkileyici görseller.",
        author: "EcoVision",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Doğa", isVariable: true },
            location: { id: "nature", name: "Natural Environment", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Landscape", "Wildlife", "Environmental Impact"],
            style: "Nature",
            promptTemplate: "nature photography, environmental, majestic, conservation, beauty of earth, {character}"
        },
        createdAt: new Date("2026-01-20"),
        downloads: 1450,
        rating: 4.9
    },

    // === NFT & DİJİTAL SANAT ===
    {
        id: "nft1",
        name: "NFT Collection Art",
        description: "NFT koleksiyonları için unique dijital sanat eserleri.",
        author: "NFTCreator",
        isPublic: true,
        config: {
            character: { id: "variable", name: "NFT Karakter", isVariable: true },
            location: { id: "digital", name: "Digital Realm", settings: "" },
            timeOfDay: "Vibrant",
            cameraAngles: ["Character Portrait", "Full Body", "Trait Variations"],
            style: "NFT Art",
            promptTemplate: "NFT art, unique, collectible, digital art, distinctive style, {character}"
        },
        createdAt: new Date("2026-02-04"),
        downloads: 3100,
        rating: 4.7
    },

    // === HORROR & DARK ===
    {
        id: "dark1",
        name: "Horror & Dark Fantasy",
        description: "Korku ve karanlık fantezi temalı atmosferik görseller.",
        author: "DarkArtist",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Creature/Scene", isVariable: true },
            location: { id: "dark", name: "Haunted Space", settings: "" },
            timeOfDay: "Night",
            cameraAngles: ["Atmospheric", "Creature Reveal", "Suspense"],
            style: "Horror",
            promptTemplate: "horror art, dark fantasy, atmospheric, eerie, haunting, {character}"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 1670,
        rating: 4.6
    },

    // === SCI-FI ===
    {
        id: "scifi1",
        name: "Sci-Fi & Space",
        description: "Bilim kurgu ve uzay temalı futuristik görseller.",
        author: "SpaceArt",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Uzay/Konsept", isVariable: true },
            location: { id: "space", name: "Outer Space", settings: "" },
            timeOfDay: "Cosmic",
            cameraAngles: ["Space Vista", "Ship Design", "Planet View"],
            style: "Sci-Fi",
            promptTemplate: "science fiction art, space, futuristic, cosmic, epic scale, {character}"
        },
        createdAt: new Date("2026-02-03"),
        downloads: 2890,
        rating: 4.9
    }
];

export function PluginMarketplaceModal({ isOpen, onClose, onInstall, myPlugins }: PluginMarketplaceModalProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [sortBy, setSortBy] = useState<"downloads" | "rating" | "recent">("downloads");
    const [installedIds, setInstalledIds] = useState<string[]>([]);

    if (!isOpen) return null;

    // Filter by search
    const filteredPlugins = communityPlugins.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.author.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Sort
    const sortedPlugins = [...filteredPlugins].sort((a, b) => {
        if (sortBy === "downloads") return b.downloads - a.downloads;
        if (sortBy === "rating") return b.rating - a.rating;
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });

    // Check if already installed
    const isInstalled = (pluginId: string) => {
        return myPlugins.some(p => p.id === pluginId) || installedIds.includes(pluginId);
    };

    const handleInstall = (plugin: CreativePlugin) => {
        onInstall(plugin);
        setInstalledIds([...installedIds, plugin.id]);
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose} />

            <div
                className="relative w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-5 border-b"
                    style={{ borderColor: "var(--border)", background: "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)" }}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
                            <Store size={24} className="text-purple-500" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Plugin Marketplace</h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Topluluk tarafından oluşturulan Creative Plugin'ler
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 rounded-xl hover:bg-[var(--background)] transition-all">
                        <X size={20} />
                    </button>
                </div>

                {/* Search & Filters */}
                <div className="flex items-center gap-3 p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="flex-1 relative">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--foreground-muted)" }} />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Plugin ara..."
                            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm"
                            style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                        />
                    </div>
                    <div className="flex items-center gap-1 p-1 rounded-xl" style={{ background: "var(--background)" }}>
                        <button
                            onClick={() => setSortBy("downloads")}
                            className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === "downloads" ? "bg-purple-500 text-white" : ""}`}
                        >
                            <Download size={12} /> Popüler
                        </button>
                        <button
                            onClick={() => setSortBy("rating")}
                            className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === "rating" ? "bg-purple-500 text-white" : ""}`}
                        >
                            <Star size={12} /> En İyi
                        </button>
                        <button
                            onClick={() => setSortBy("recent")}
                            className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === "recent" ? "bg-purple-500 text-white" : ""}`}
                        >
                            <Clock size={12} /> Yeni
                        </button>
                    </div>
                </div>

                {/* Plugin Grid */}
                <div className="p-4 overflow-y-auto max-h-[calc(85vh-180px)]">
                    <div className="grid grid-cols-2 gap-4">
                        {sortedPlugins.map((plugin) => (
                            <div
                                key={plugin.id}
                                className="p-4 rounded-xl transition-all hover:shadow-lg"
                                style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                            >
                                {/* Header */}
                                <div className="flex items-start justify-between mb-3">
                                    <div>
                                        <h3 className="font-semibold">{plugin.name}</h3>
                                        <div className="flex items-center gap-2 text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                            <span className="flex items-center gap-1">
                                                <Users size={10} /> {plugin.author}
                                            </span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Star size={10} className="text-yellow-500" /> {plugin.rating}
                                            </span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Download size={10} /> {plugin.downloads.toLocaleString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Description */}
                                <p className="text-xs mb-3 line-clamp-2" style={{ color: "var(--foreground-muted)" }}>
                                    {plugin.description}
                                </p>

                                {/* Tags */}
                                <div className="flex flex-wrap gap-1 mb-3">
                                    {plugin.config.style && (
                                        <span className="px-2 py-0.5 text-xs rounded" style={{ background: "var(--card)" }}>
                                            {plugin.config.style}
                                        </span>
                                    )}
                                    {plugin.config.cameraAngles && plugin.config.cameraAngles.slice(0, 2).map((angle, i) => (
                                        <span key={i} className="px-2 py-0.5 text-xs rounded" style={{ background: "var(--card)" }}>
                                            {angle}
                                        </span>
                                    ))}
                                </div>

                                {/* Action */}
                                <button
                                    onClick={() => handleInstall(plugin)}
                                    disabled={isInstalled(plugin.id)}
                                    className={`w-full py-2 text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-2 ${isInstalled(plugin.id)
                                        ? "bg-green-500/20 text-green-500 cursor-default"
                                        : "hover:opacity-90"
                                        }`}
                                    style={!isInstalled(plugin.id) ? { background: "var(--accent)", color: "var(--background)" } : {}}
                                >
                                    {isInstalled(plugin.id) ? (
                                        <>✓ Yüklendi</>
                                    ) : (
                                        <><Plus size={14} /> Projeme Ekle</>
                                    )}
                                </button>
                            </div>
                        ))}
                    </div>

                    {sortedPlugins.length === 0 && (
                        <div className="text-center py-12">
                            <Store size={48} className="mx-auto mb-4 opacity-20" />
                            <p style={{ color: "var(--foreground-muted)" }}>
                                Arama sonucu bulunamadı
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
