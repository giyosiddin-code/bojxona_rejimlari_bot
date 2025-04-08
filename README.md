Bojxona Rejimlari Bot - README.md
markdownCopy# Bojxona Rejimlari Telegram Boti

Ushbu Telegram bot O'zbekiston Respublikasi bojxona rejimlari haqida ma'lumot berish uchun yaratilgan. Bot 16 ta bojxona rejimiga oid ma'lumotlarni 5 xil formatda (PowerPoint, Word, PDF, Video, Link) taqdim etadi.

## 📋 Bot imkoniyatlari

- 16 ta bojxona rejimi haqida ma'lumot
- Har bir rejim uchun 5 xil formatdagi ma'lumotlar
- Admin panel orqali ma'lumotlarni yangilash
- Foydalanuvchilar statistikasini kuzatish
- Bot yaratuvchilari haqida ma'lumot

## 🛠️ O'rnatish

### Kerakli dasturlar

- Python 3.7 yoki undan yuqori versiya
- python-telegram-bot 20.3 kutubxonasi

### Kutubxonalarni o'rnatish

```bash
pip install python-telegram-bot==20.3
⚙️ Sozlash
Bot kodini ishga tushirishdan oldin quyidagi sozlamalarni o'zgartiring:

Bot tokenini kiriting:

pythonCopyBOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

Kanal ID sini kiriting:

pythonCopyCHANNEL_ID = os.environ.get("CHANNEL_ID", "@your_channel_username")

Admin ID sini kiriting:

pythonCopyADMIN_USERS = [
    int(os.environ.get("ADMIN_ID", "123456789")),
]

Bot yaratuvchilari ma'lumotlarini kiriting:

pythonCopyBOT_CREATORS = [
    {"name": "Bot kodini yozuvchi", "username": "@developer_username"},
    {"name": "G'oya muallifi", "username": "@idea_author_username"},
    {"name": "Yordam beruvchi", "username": "@helper_username"}
]
Ma'lumotlarni tayyorlash
Bot ma'lumotlarni Telegram kanaldan oladi. Buning uchun:

Yangi Telegram kanal yarating
Botni kanalga admin sifatida qo'shing
Kanalga ma'lumotlarni yuklang (PowerPoint, Word, PDF, Video, Link)
Xabar ID larini bot kodidagi CONTENT_IDS lug'atiga kiriting

🚀 Ishga tushirish
bashCopypython bojxona_rejimlari_bot.py
🤖 Bot komandalarini

/start - Botni qayta ishga tushirish
/help - Yordam olish
/bot_creators - Bot yaratuvchilari haqida ma'lumot olish
/admin - Admin panelga kirish (faqat adminlar uchun)
/stats - Statistikani ko'rish (faqat adminlar uchun)

🔧 Texnologiyalar

Python 3
python-telegram-bot 20.3
Telegram Bot API

⚠️ Muhim eslatmalar

Bot kanalga admin sifatida qo'shilgan bo'lishi shart
Ma'lumotlar ID raqamlari to'g'ri kiritilgan bo'lishi kerak
Bot uzluksiz ishlashi uchun serverga joylashtirish tavsiya etiladi

👨‍💻 Yaratuvchilar

Bot kodini yozuvchi: @developer_username
G'oya muallifi: @idea_author_username
Yordam beruvchi: @helper_username

📝 Litsenziya
Bu loyiha MIT litsenziyasi ostida tarqatiladi.
