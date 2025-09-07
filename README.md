## Muro Destek Discord Botu

Basit bir ticket sistemi:
- `/destek ac`: Bu kanala bir "Destek Aç" butonu yollar.
- "Destek Aç" butonu: Yeni bir ticket kanalı açar, `@everyone` etiketler ve konu/başlıkta rastgele sayı ekler.
- "Close": Kapatma işlemi başlatır, kullanıcıdan en az 5 harfli neden ister; geçerliyse kanalı "closed-..." olarak yeniden adlandırır ve kilitler.

### Kurulum
1. Python 3.10+
2. Bağımlılıklar:
```bash
pip install -r requirements.txt
```
3. Ortam değişkeni ayarla:
```bash
set DISCORD_TOKEN=YOUR_BOT_TOKEN
```
Windows PowerShell için:
```powershell
$env:DISCORD_TOKEN = "YOUR_BOT_TOKEN"
```

### Çalıştırma
```bash
python bot.py
```

### Notlar
- Botun sunucuda uygulama komutlarına (slash) ve kanal yönetimi izinlerine ihtiyacı var.
- İlk kurulumda slash komutlarının görünmesi birkaç dakika sürebilir.


