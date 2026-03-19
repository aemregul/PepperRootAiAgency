---
description: Projedeki kritik çalışma kuralları — her değişiklikten önce oku
---

# Kritik Çalışma Kuralları

Bu kurallar her değişiklikten önce kontrol edilmelidir.

## Kural 1 — Branch Tabanlı Geliştirme
- `main` branch'a direkt push **YASAK**
- Her değişiklik için yeni branch oluştur
- Branch isimlendirme: `fix/…`, `feat/…`, `hotfix/…`
- Test başarılıysa merge et, başarısızsa düzelt

## Kural 2 — Bir Şeyi Düzeltirken Başka Şey Bozma
- Değişiklik yapmadan önce etki analizi yap
- Riskli değişiklik varsa **önce kullanıcıyı bilgilendir**
- Onay almadan riskli değişiklik **yapma**

## Kural 3 — Test Etmeden Push Yok
- Her değişiklik önce **lokalde** test edilecek (import, syntax, çalıştırma)
- Sonra **branch preview deploy** üzerinde canlıda test
- Test edilmemiş kod `main`'e merge edilmez

## Kural 4 — Bilgilendirme Zorunluluğu
- Ne yapacağını, hangi dosyaları değiştireceğini, potansiyel riskleri **önceden söyle**
- Sessizce dosya değiştirme, "bonus" özellik ekleme, planlanmamış değişiklik yapma

## Kural 5 — Sadece İstenen Şeye Odaklan
- Kullanıcının istediğini yap, ekstra "iyileştirme" ekleme
- Çalışan sisteme müdahale etme
- Sorun çözülmüyorsa kullanıcıyla konuş

## Kural 6 — Öncelik: Stabilite
- Yeni özellik eklemeden önce mevcut sistemin çalıştığından emin ol
- Kritik akışlar: chat yanıtı, kısa video, uzun video, gerçek zamanlı hata bildirimi
- "Yanıt vermedi" / "asılı kaldı" hissi oluşturan sessiz hatalar → kritik bug

## Değişiklik Öncesi Kontrol Listesi

Her değişiklik öncesi şunları yap:
1. ✅ Hangi dosyalar değişecek?
2. ✅ Bu değişiklik başka özellikleri etkiler mi?
3. ✅ Riskli bir durum var mı? → Kullanıcıyı bilgilendir
4. ✅ Branch oluşturuldu mu? (main'e direkt değişiklik yok)
5. ✅ Lokal test yapılacak mı? → Evet, her zaman
