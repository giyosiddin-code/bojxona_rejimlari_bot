import logging
import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Logni yoqish
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    filename="bot_logs.log"
)
logger = logging.getLogger(__name__)

# O'zgartirish kerak bo'lgan asosiy sozlamalar - 1-QADAM
##############################################
# BotFather bergan tokenni kiriting
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Kanal ID si yoki username - @ bilan
CHANNEL_ID = "@YOUR_CHANNEL_NAME"

# Admin ID raqamini kiriting (@userinfobot orqali aniqlay olasiz)
ADMIN_USERS = [
    YOUR_ID,  # O'z Telegram ID raqamingizni kiriting
]

# Admin parol
ADMIN_PASSWORD = "admin123"  # Xavfsiz parol kiriting!
##############################################

# Suhbat holatlari
MAIN_MENU, FORMAT_SELECTION, ADMIN_MENU, ADMIN_ADD_CONTENT, ADMIN_SELECT_REGIME, ADMIN_SELECT_FORMAT = range(6)
ADMIN_SEND_MESSAGE = 6  # Yangi holat - Xabar jo'natish paneli
ADMIN_MAILING_LIST = 7  # Yangi holat - Xabar jo'natish ro'yxatini boshqarish
ADMIN_ADD_USER_TO_MAILING = 8  # Yangi holat - Foydalanuvchi qo'shish
ADMIN_REMOVE_USER_FROM_MAILING = 9  # Yangi holat - Foydalanuvchi olib tashlash


# Admin login holatlari
ADMIN_LOGIN = 100

# 16 ta bojxona rejimlari
CUSTOMS_REGIMES = {
    "1": "Eksport",
    "2": "Reeksport",
    "3": "Vaqtincha olib chiqish",
    "4": "Import",
    "5": "Reimport",
    "6": "Vaqtincha olib kirish",
    "7": "Bojxona hududida qayta ishlash",
    "8": "Bojxona hududidan tashqarida qayta ishlash",
    "9": "Vaqtincha saqlash",
    "10": "Erkin bojxona zonasi",
    "11": "Bij olinmaydigan savdo",
    "12": "Erkin ombor",
    "13": "Bojxona ombori",
    "14": "Davlat foydasiga voz kechish",
    "15": "Yo'q qilish",
    "16": "Bojxona tranziti"
}


# 5 xil format turlari
FORMATS = {
    "pptx": "📊 PowerPoint",
    "word": "📝 Word",
    "pdf": "📄 PDF",
    "video": "🎬 Video",
    "link": "🔗 Link"
}

# Ma'lumotlarni to'g'ridan-to'g'ri kodga kiritish - 2-QADAM
##############################################
# Har bir rejim va format uchun kanaldagi xabar ID raqamlarini kiriting
# 0 yoki manfiy qiymatlar - ma'lumot mavjud emas degani
CONTENT_IDS = {
    "1": {  # Import rejimi
        "pptx": 0,  # Mavjud emas (visual namoyish uchun 0 ga o'zgartirildi)
        "word": 0,  # Mavjud emas
        "pdf": 0,    # Mavjud emas
        "video": 212,  # Faqat video mavjud
        "link": 0,   # Mavjud emas
    },
    "2": {  # Export rejimi
        "pptx": 0,   # Mavjud emas
        "word": 0,   # Mavjud emas
        "pdf": 0,    # Mavjud emas
        "video": 0,  # Mavjud emas
        "link": 0,   # Mavjud emas
    },
    "3": {  # Bojxona tranziti
        "pptx": 3001,
        "word": 3002,
        "pdf": 3003,
        "video": 3004,
        "link": 3005,
    },
    "4": {  # Qayta ishlash (ichki)
        "pptx": 4001,
        "word": 4002,
        "pdf": 4003,
        "video": 4004,
        "link": 4005,
    },
    "5": {  # Qayta ishlash (tashqi)
        "pptx": 5001,
        "word": 5002,
        "pdf": 5003,
        "video": 5004,
        "link": 5005,
    },
    "6": {  # Bojxona ombori
        "pptx": 6001,
        "word": 6002,
        "pdf": 6003,
        "video": 6004,
        "link": 6005,
    },
    "7": {  # Erkin ombor
        "pptx": 7001,
        "word": 7002,
        "pdf": 7003,
        "video": 7004,
        "link": 7005,
    },
    "8": {  # Vaqtinchalik olib kirish
        "pptx": 8001,
        "word": 8002,
        "pdf": 8003,
        "video": 8004,
        "link": 8005,
    },
    "9": {  # Vaqtinchalik olib chiqish
        "pptx": 9001,
        "word": 9002,
        "pdf": 9003,
        "video": 9004,
        "link": 9005,
    },
    "10": {  # Erkin muomala uchun chiqarish
        "pptx": 10001,
        "word": 10002,
        "pdf": 10003,
        "video": 10004,
        "link": 10005,
    },
    "11": {  # Bekor qilish
        "pptx": 11001,
        "word": 11002,
        "pdf": 11003,
        "video": 11004,
        "link": 11005,
    },
    "12": {  # Voz kechish
        "pptx": 12001,
        "word": 12002,
        "pdf": 12003,
        "video": 12004,
        "link": 12005,
    },
    "13": {  # Erkin savdo do'koni
        "pptx": 13001,
        "word": 13002,
        "pdf": 13003,
        "video": 13004,
        "link": 13005,
    },
    "14": {  # Erkin bojxona zonasi
        "pptx": 14001,
        "word": 14002,
        "pdf": 14003,
        "video": 14004,
        "link": 14005,
    },
    "15": {  # Maxsus bojxona rejimi
        "pptx": 15001,
        "word": 15002,
        "pdf": 15003,
        "video": 15004,
        "link": 15005,
    },
    "16": {  # Qayta import
        "pptx": 16001,
        "word": 16002,
        "pdf": 16003,
        "video": 16004,
        "link": 16005,
    }
}
##############################################

# Ma'lumotlar fayli
DATA_FILE = "bot_data.json"

# Ma'lumotlarni yuklash
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ma'lumotlarni yuklashda xato: {e}")
    
    # Fayl mavjud bo'lmasa yoki xato bo'lsa, standart ma'lumotlarni qaytarish
    return {
        "content_ids": CONTENT_IDS,
        "user_stats": {}
    }

# Ma'lumotlarni saqlash
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Ma'lumotlarni saqlashda xato: {e}")
        return False

# Ma'lumotlarni yuklash
data = load_data()

# Faylning boshida, asosiy konfiguratsiyadan keyin:
BOT_CREATORS = [
    {"name": "Bot kodini yozuvchi","username": "Uaydullayev G'iyosiddin @UGB121212"},
    {"name": "G'oya muallifi", "username": "Farxodov Farrux"},
    {"name": "Ma'lumot tahrirlovchi", "username": "Ramazonov Murod"}
]

# Boshqa komanda funksiyalari yoniga:
async def bot_creators_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot yaratuvchilari haqida ma'lumot"""
    creators_text = "👨‍💻 <b>BOT YARATUVCHILARI:</b>\n\n"
    
    for creator in BOT_CREATORS:
        creators_text += f"• <b>{creator['name']}</b>: {creator['username']}\n"
    
    creators_text += "\n<i>Botni yaratishda ishtirok etgan barcha insonlarga katta rahmat!</i>"
    
    await update.message.reply_text(creators_text, parse_mode='HTML')
    return MAIN_MENU

# Foydalanuvchi statistikasini yangilash
def update_user_stats(user_id, user_name, action):
    """Foydalanuvchi harakatlarini kuzatish funksiyasi"""
    if "user_stats" not in data:
        data["user_stats"] = {}
    
    user_id_str = str(user_id)
    if user_id_str not in data["user_stats"]:
        data["user_stats"][user_id_str] = {
            "name": user_name,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "actions": []
        }
    
    # Foydalanuvchi ma'lumotlarini yangilash
    data["user_stats"][user_id_str]["last_seen"] = datetime.now().isoformat()
    data["user_stats"][user_id_str]["actions"].append({
        "action": action,
        "timestamp": datetime.now().isoformat()
    })
    
    # So'nggi 100 ta harakatni saqlash
    data["user_stats"][user_id_str]["actions"] = data["user_stats"][user_id_str]["actions"][-100:]
    
    # Ma'lumotlarni saqlash
    save_data(data)

# Bot ishga tushishi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bot ishga tushganda salomlash va rejimlar menyusini ko'rsatish"""
    user = update.effective_user
    
    # Foydalanuvchi statistikasini yangilash
    update_user_stats(user.id, user.first_name, "bot_started")
    
    # Faqat bojxona rejimlari bo'lgan keyboard yaratish
    keyboard = get_regimes_keyboard()
    
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! Bojxona ma'lumotlari botiga xush kelibsiz.\n\n"
        f"Kerakli bojxona rejimini tanlang:\n\n"
        f"Yordam uchun /help buyrug'ini yuboring.",
        reply_markup=keyboard
    )
    
    return MAIN_MENU

# Bojxona rejimlari tugmachalarini ko'rsatish
def get_regimes_keyboard():
    """Bojxona rejimlari uchun keyboard yaratish"""
    keyboard = []
    
    # Rejimlarni 2 ustun bo'yicha joylashtirish
    regimes_list = list(CUSTOMS_REGIMES.items())
    
    # Har 2 ta rejimni bir qatorga joylashtirish
    for i in range(0, len(regimes_list), 2):
        row = []
        # Birinchi tugma
        regime_key1 = regimes_list[i][0]
        regime_name1 = regimes_list[i][1]
        row.append(KeyboardButton(f"{regime_key1}. {regime_name1}"))
        
        # Ikkinchi tugma (agar mavjud bo'lsa)
        if i + 1 < len(regimes_list):
            regime_key2 = regimes_list[i+1][0]
            regime_name2 = regimes_list[i+1][1]
            row.append(KeyboardButton(f"{regime_key2}. {regime_name2}"))
        
        keyboard.append(row)
    
    # Botni yaratuvchilari tugmasi
    #keyboard.append([KeyboardButton("👨‍💻 Bot yaratuvchilari")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Oddiy xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Oddiy xabarlarni qayta ishlash"""
    text = update.message.text
    user = update.effective_user
    
    # Bot yaratuvchilari tugmasi
    if text == "👨‍💻 Bot yaratuvchilari":
        return await bot_creators_command(update, context)
    
    # Rejim tugmasi tanlanganini tekshirish
    for regime_key, regime_name in CUSTOMS_REGIMES.items():
        regime_button_text = f"{regime_key}. {regime_name}"
        if text == regime_button_text:
            logger.info(f"Foydalanuvchi rejimni tanladi: {regime_key}")
            # Rejim tanlanganda format tanlash menyusini ko'rsatish
            # Foydalanuvchi ma'lumotlariga saqlash
            context.user_data["selected_regime"] = regime_key
            
            # Foydalanuvchi statistikasini yangilash
            update_user_stats(user.id, user.first_name, f"selected_regime_{regime_key}")
            
            # Format tanlash klaviaturasini ko'rsatish
            await update.message.reply_text(
                f"Siz {CUSTOMS_REGIMES[regime_key]} rejimini tanladingiz. Ma'lumot formatini tanlang:",
                reply_markup=get_format_keyboard(regime_key)
            )
            return FORMAT_SELECTION
    
    # Agar hech qanday rejim tanlanmagan bo'lsa
    await update.message.reply_text(
        "Iltimos, mavjud rejimlardan birini tanlang yoki /help buyrug'ini yuboring."
    )
    return MAIN_MENU

# Format tanlash klaviaturasini ko'rsatish
def get_format_keyboard(regime_key):
    """Tanlangan rejim uchun format opsiyasini ko'rsatadigan klaviatura"""
    keyboard = []
    
    # Formatlarni 3 qatorga (2+2+1) joylashtirish
    formats_list = list(FORMATS.items())
    
    # Ma'lumotlar mavjudligini tekshirish funksiyasi
    def is_valid_content(regime, format_key):
        content_id = data.get("content_ids", {}).get(regime, {}).get(format_key)
        # ID mavjud va 0 dan katta bo'lishi kerak (haqiqiy ID raqam)
        return content_id is not None and content_id > 0
    
    # Birinchi qator: 2 ta format
    row1 = []
    for i in range(2):
        format_key = formats_list[i][0]
        format_name = formats_list[i][1]
        # Tekshirish: bu format uchun ma'lumot mavjudmi?
        has_content = is_valid_content(regime_key, format_key)
        # Format nomi yoniga indikator qo'shish
        display_name = f"{format_name} ✅" if has_content else f"{format_name} ❌"
        row1.append(InlineKeyboardButton(display_name, callback_data=f"format_{regime_key}_{format_key}"))
    keyboard.append(row1)
    
    # Ikkinchi qator: keyingi 2 ta format
    row2 = []
    for i in range(2, 4):
        format_key = formats_list[i][0]
        format_name = formats_list[i][1]
        has_content = is_valid_content(regime_key, format_key)
        display_name = f"{format_name} ✅" if has_content else f"{format_name} ❌"
        row2.append(InlineKeyboardButton(display_name, callback_data=f"format_{regime_key}_{format_key}"))
    keyboard.append(row2)
    
    # Uchinchi qator: qolgan 1 ta format
    format_key = formats_list[4][0]
    format_name = formats_list[4][1]
    has_content = is_valid_content(regime_key, format_key)
    display_name = f"{format_name} ✅" if has_content else f"{format_name} ❌"
    keyboard.append([InlineKeyboardButton(display_name, callback_data=f"format_{regime_key}_{format_key}")])
    
    # Orqaga qaytish va yangilash tugmalari
    keyboard.append([
        InlineKeyboardButton("🔙 Rejimlar", callback_data="back_to_regimes"),
        InlineKeyboardButton("🔄 Yangilash", callback_data="refresh_format")
    ])
    
    return InlineKeyboardMarkup(keyboard)

# Format tanlash
async def format_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Format tanlanganda ishlaydi"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "refresh_format":
        # Yangilash tugmasi bosilganda
        regime_key = context.user_data.get("selected_regime")
        if regime_key:
            await query.edit_message_text(
                f"Siz {CUSTOMS_REGIMES[regime_key]} rejimini tanladingiz. Ma'lumot formatini tanlang:",
                reply_markup=get_format_keyboard(regime_key)
            )
        else:
            await query.edit_message_text(
                "Kechirasiz, rejim ma'lumotlari yo'qolgan. Iltimos, qayta tanlang:",
                reply_markup=get_regimes_keyboard()
            )
            return MAIN_MENU
        return FORMAT_SELECTION
    
    if query.data == "back_to_regimes":
        await query.edit_message_text(
            "Kerakli bojxona rejimini tanlang:",
        )
        return MAIN_MENU
        
    # Format va rejimni olish
    parts = query.data.split("_")
    regime_key = parts[1]
    format_key = parts[2]
    
    # Foydalanuvchi statistikasini yangilash
    user = update.effective_user
    update_user_stats(user.id, user.first_name, f"selected_format_{regime_key}_{format_key}")
    
    try:
        # Ma'lumot ID sini olish
        message_id = data.get("content_ids", {}).get(regime_key, {}).get(format_key)
        
        # Debug uchun log
        logger.info(f"Tanlangan ma'lumot: Rejim={regime_key}, Format={format_key}, ID={message_id}")
        
        # Ma'lumot mavjudligini tekshirish
        if message_id is None or message_id <= 0:
            logger.warning(f"Ma'lumot ID topilmadi yoki noto'g'ri: Rejim={regime_key}, Format={format_key}, ID={message_id}")
            await query.edit_message_text(
                f"Kechirasiz, {CUSTOMS_REGIMES[regime_key]} rejimi uchun {FORMATS[format_key]} formatidagi ma'lumot hozircha mavjud emas.\n\n"
                "Boshqa format yoki rejimni tanlang:",
                reply_markup=get_format_keyboard(regime_key)
            )
            return FORMAT_SELECTION
        
        # Foydalanuvchiga ma'lumot yuklanayotgani haqida xabar
        await query.edit_message_text(
            f"Kanaldan {FORMATS[format_key]} formatidagi ma'lumot yuklanmoqda...\n"
            f"Kanal: {CHANNEL_ID}"
        )
        
        # Kanaldan ma'lumotni olish va yuborish
        success = await send_content_from_channel(update, context, message_id)
        
        if success:
            # Format tanlash menyusiga qaytish
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Ma'lumot muvaffaqiyatli yuklandi. Yana {CUSTOMS_REGIMES[regime_key]} rejimi uchun boshqa formatni tanlashingiz mumkin:",
                reply_markup=get_format_keyboard(regime_key)
            )
        else:
            # Xatolik bo'lganda, ma'lumotni mavjud emas deb belgilash
            logger.warning(f"Ma'lumot yuklashda xatolik, belgi yangilanmoqda: Rejim={regime_key}, Format={format_key}")
            # Ma'lumot ID sini 0 ga o'zgartirish (mavjud emas degan ma'noda)
            if "content_ids" in data and regime_key in data["content_ids"] and format_key in data["content_ids"][regime_key]:
                data["content_ids"][regime_key][format_key] = 0
                save_data(data)
            
            # Format tanlash menyusiga qaytish
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Ma'lumotni yuklashda xatolik yuz berdi. Bu format endi mavjud emas deb hisoblandi. Iltimos, boshqa formatni tanlang:",
                reply_markup=get_format_keyboard(regime_key)
            )
        
        return FORMAT_SELECTION
        
    except Exception as e:
        logger.error(f"Ma'lumotni yuklashda xato: {e}")
        await query.edit_message_text(
            f"Kechirasiz, tizimda xatolik yuz berdi: {str(e)}\nIltimos, qaytadan urinib ko'ring:",
            reply_markup=get_format_keyboard(regime_key)
        )
        return FORMAT_SELECTION

# Kanaldan ma'lumotni yuborish
async def send_content_from_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, message_id: int) -> bool:
    """
    Kanaldan ma'lumotni ID orqali yuborish.
    
    Qaytaradi:
        bool: Muvaffaqiyatli bo'lsa True, aks holda False
    """
#    Agar ID 0 yoki manfiy bo'lsa, ma'lumot mavjud emas
    if message_id <= 0:
        logger.warning(f"Noto'g'ri message_id: {message_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Xatolik: Ma'lumot mavjud emas (ID: {message_id}).\n"
                  f"Bot administratori bilan bog'laning."
        )
        return False
    
    try:
        # Xatoliklarni tushunarliroq qilish uchun, avval kanalni tekshiramiz
        try:
            # Kanal mavjudligini tekshirish
            chat = await context.bot.get_chat(CHANNEL_ID)
            logger.info(f"Kanal topildi: {chat.title}")
        except Exception as chat_error:
            logger.error(f"Kanal tekshirishda xato: {chat_error}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Xatolik: Kanal topilmadi yoki bot kanalga a'zo emas. Kanal: {CHANNEL_ID}\n"
                     f"Bot administratori bilan bog'laning."
            )
            return False
        
        # Kanaldan xabarni yo'naltirish
        logger.info(f"Xabarni yo'naltirish: {message_id} dan {update.effective_chat.id} ga")
        
        try:
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id
            )
        except Exception as forward_error:
            # Xabarni yo'naltirishda xato bo'lsa, batafsil xatolik xabarini ko'rsatish
            error_message = str(forward_error)
            if "Message to forward not found" in error_message:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Xatolik: Kanalda ushbu formatli ma'lumot kiritilmagan ko'rinadi" #ID: {message_id}\n"
                        # f"Admin bilan bog'laning va ID raqamini tekshiring."
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Xatolik: Xabarni yo'naltirishda muammo yuzaga keldi: {error_message}"
                )
            return False
        
        logger.info(f"Xabar muvaffaqiyatli yo'naltirildi: {message_id}")
        return True
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Xabar yo'naltirishda xato: {error_message}")
        
        # Xatolik turini aniqlash va tegishli xabar ko'rsatish
        if "Message to forward not found" in error_message:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Xatolik: Kanalda ushbu ID raqamli xabar topilmadi. ID: {message_id}\n"
                     f"Admin bilan bog'laning va ID raqamini tekshiring."
            )
        elif "Chat not found" in error_message:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Xatolik: Kanal topilmadi. Kanal ID: {CHANNEL_ID}\n"
                     f"Bot administratoridan kanalni tekshirishini so'rang."
            )
        elif "Bot is not a member" in error_message:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Xatolik: Bot kanalga a'zo emas. Kanal: {CHANNEL_ID}\n"
                     f"Bot administratoridan botni kanalga qo'shishini so'rang."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Xatolik yuz berdi: {error_message}"
            )
        return False

# Asosiy menyuga qaytish
async def back_to_regimes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Rejimlar ro\'yxatiga qaytish"""
    query = update.callback_query
    await query.answer()
    
    # Eski xabarni o'chirib, yangi tugmalarni ko'rsatish
    await query.delete_message()
    
    # Asosiy klaviaturani ko'rsatish bilan xabar yuborish
    keyboard = get_regimes_keyboard()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Kerakli bojxona rejimini tanlang:",
        reply_markup=keyboard
    )
    
    return MAIN_MENU

# Bot bosh menyusiga qaytish
async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bosh menyuga qaytish"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Bosh menyuga qaytish uchun /start buyrug'ini yuboring."
    )
    return ConversationHandler.END

# Yordam buyrug'i
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yordam buyrug'i uchun ma'lumot"""
    help_text = (
        "🤖 Bojxona ma'lumotlar boti yordam:\n\n"
        "1. Kerakli bojxona rejimini tanlang\n"
        "2. Ma'lumot formatini tanlang (PowerPoint, Word, PDF, Video, Link)\n"
        "3. Bot sizga tanlangan ma'lumotni kanaldan yuboradi\n\n"
        "📋 Buyruqlar ro'yxati:\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Ushbu yordam xabarini ko'rsatish\n"
        "/bot_creators - Bot yaratuvchilari haqida ma'lumot\n\n"
        "Agar muammo yuzaga kelsa, bot administratori bilan bog'laning."
    )
    await update.message.reply_text(help_text)
    return MAIN_MENU

# Barcha suhbat holatlaridan bekor qilish
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Har qanday holatdan bekor qilish"""
    await update.message.reply_text(
        "Amallar bekor qilindi. Bosh menyuga qaytish uchun /start buyrug'ini yuboring."
    )
    return ConversationHandler.END

# Admin kirish
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin buyrug'i, autentifikatsiya boshlash"""
    user = update.effective_user
    
    # Admin ID tekshirish - birinchi qadam
    if user.id in ADMIN_USERS:
        await update.message.reply_text(
            "Admin huquqlaringizni tasdiqlash uchun parolni kiriting:\n"
            "(Bekor qilish uchun /cancel buyrug'ini yuboring)"
        )
        return ADMIN_LOGIN
    else:
        await update.message.reply_text("Kechirasiz, siz admin emas ekansiz. Kirishga ruxsat yo'q.")
        return MAIN_MENU

# Admin login
async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin parolini tekshirish"""
    text = update.message.text
    
    # Bekor qilish
    if text == "/cancel":
        await update.message.reply_text("Admin kirish bekor qilindi.")
        keyboard = get_regimes_keyboard()
        await update.message.reply_text(
            "Kerakli bojxona rejimini tanlang:",
            reply_markup=keyboard
        )
        return MAIN_MENU
    
    # Parol tekshirish
    if text == ADMIN_PASSWORD:
        await update.message.reply_text(
            "✅ Admin huquqlaringiz tasdiqlandi!\n\n"
            "Admin panelga xush kelibsiz! Tanlang:",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_MENU
    else:
        await update.message.reply_text(
            "❌ Parol noto'g'ri. Qayta urinib ko'ring yoki bekor qilish uchun /cancel buyrug'ini yuboring"
        )
        return ADMIN_LOGIN

#  Admin klaviaturasini yangilash:

def get_admin_keyboard():
    """Admin panel uchun klaviatura"""
    keyboard = [
        [InlineKeyboardButton("📝 Ma'lumot qo'shish/o'zgartirish", callback_data="admin_add_content")],
        [InlineKeyboardButton("👥 Foydalanuvchilar statistikasi", callback_data="admin_stats")],
        [InlineKeyboardButton("✉️ Xabar jo'natish", callback_data="admin_send_message")],
        [InlineKeyboardButton("📋 Xabar jo'natish ro'yxati", callback_data="admin_mailing_list")],
        [InlineKeyboardButton("🏠 Bosh menyuga qaytish", callback_data="back_to_start")]
    ]
    return InlineKeyboardMarkup(keyboard)
 
# Admin menusini yangilash:

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin menyusi"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "admin_add_content":
        await query.edit_message_text(
            "Qaysi rejim uchun ma'lumot qo'shmoqchisiz?",
            reply_markup=get_regime_selection_keyboard()
        )
        return ADMIN_SELECT_REGIME
    
    elif action == "admin_stats":
        # Foydalanuvchilar statistikasini ko'rsatish
        stats_text = "📊 Foydalanuvchilar statistikasi:\n\n"
        
        user_count = len(data.get("user_stats", {}))
        stats_text += f"• Jami foydalanuvchilar: {user_count}\n\n"
        
        # So'nggi 5 ta faol foydalanuvchi
        stats_text += "So'nggi faol foydalanuvchilar:\n"
        
        # Foydalanuvchilarni so'nggi faollik bo'yicha saralash
        sorted_users = sorted(
            data.get("user_stats", {}).items(),
            key=lambda x: x[1]["last_seen"],
            reverse=True
        )[:5]
        
        for i, (user_id, user_data) in enumerate(sorted_users, 1):
            last_seen = datetime.fromisoformat(user_data["last_seen"]).strftime("%Y-%m-%d %H:%M:%S")
            stats_text += f"{i}. {user_data['name']} - {last_seen}\n"
        
        await query.edit_message_text(
            stats_text,
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_MENU
    
    elif action == "admin_send_message":
        # Xabar jo'natish bo'limi
        await query.edit_message_text(
            "✉️ Xabar jo'natish paneli\n\n"
            "Belgilangan foydalanuvchilarga xabar jo'natish uchun xabar matnini kiriting.\n"
            "Bekor qilish uchun /cancel buyrug'ini yuboring.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_admin")]
            ])
        )
        return ADMIN_SEND_MESSAGE
    
    elif action == "admin_mailing_list":
        # Xabar jo'natish ro'yxatini boshqarish
        return await admin_mailing_list(update, context)
    
    elif action == "back_to_admin":
        # Admin panelga qaytish
        await query.edit_message_text(
            "Admin panelga qaytish",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_MENU
    
    elif action == "back_to_start":
        await query.edit_message_text(
            "Admin paneldan chiqildi. Asosiy menyuga qaytish uchun /start buyrug'ini yuboring."
        )
        return MAIN_MENU
    
    return ADMIN_MENU



def get_regime_selection_keyboard():
    """Rejim tanlash uchun klaviatura"""
    keyboard = []
    
    # Rejimlarni 2 ustunda joylashtiramiz
    regimes_list = list(CUSTOMS_REGIMES.items())
    for i in range(0, len(regimes_list), 2):
        row = []
        
        # Birinchi tugma
        regime_key1 = regimes_list[i][0]
        regime_name1 = regimes_list[i][1]
        row.append(InlineKeyboardButton(f"{regime_key1}. {regime_name1}", callback_data=f"admin_regime_{regime_key1}"))
        
        # Ikkinchi tugma (agar mavjud bo'lsa)
        if i + 1 < len(regimes_list):
            regime_key2 = regimes_list[i+1][0]
            regime_name2 = regimes_list[i+1][1]
            row.append(InlineKeyboardButton(f"{regime_key2}. {regime_name2}", callback_data=f"admin_regime_{regime_key2}"))
        
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_admin")])
    
    return InlineKeyboardMarkup(keyboard)

async def admin_select_regime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin rejim tanlash"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_admin":
        await query.edit_message_text(
            "Admin panelga qaytish",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_MENU
    
    # Rejim kalitini olish
    regime_key = query.data.split("_")[2]
    context.user_data["selected_admin_regime"] = regime_key
    
    # Format tanlash
    await query.edit_message_text(
        f"Siz {CUSTOMS_REGIMES[regime_key]} rejimini tanladingiz. Qaysi format uchun ma'lumot ID si kiritmoqchisiz?",
        reply_markup=get_format_selection_keyboard_admin()
    )
    return ADMIN_SELECT_FORMAT

def get_format_selection_keyboard_admin():
    """Admin uchun format tanlash klaviaturasi"""
    keyboard = []
    
    # Formatlarni 3 qatorga (2+2+1) joylashtirish
    formats_list = list(FORMATS.items())
    
    # Birinchi qator: 2 ta format
    row1 = []
    for i in range(2):
        format_key = formats_list[i][0]
        format_name = formats_list[i][1]
        row1.append(InlineKeyboardButton(format_name, callback_data=f"admin_format_{format_key}"))
    keyboard.append(row1)
    
    # Ikkinchi qator: keyingi 2 ta format
    row2 = []
    for i in range(2, 4):
        format_key = formats_list[i][0]
        format_name = formats_list[i][1]
        row2.append(InlineKeyboardButton(format_name, callback_data=f"admin_format_{format_key}"))
    keyboard.append(row2)
    
    # Uchinchi qator: qolgan 1 ta format
    format_key = formats_list[4][0]
    format_name = formats_list[4][1]
    keyboard.append([InlineKeyboardButton(format_name, callback_data=f"admin_format_{format_key}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_regime_selection")])
    
    return InlineKeyboardMarkup(keyboard)

async def admin_select_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin format tanlash"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_regime_selection":
        await query.edit_message_text(
            "Rejim tanlash",
            reply_markup=get_regime_selection_keyboard()
        )
        return ADMIN_SELECT_REGIME
    
    # Format kalitini olish
    format_key = query.data.split("_")[2]
    context.user_data["selected_admin_format"] = format_key
    
    # Joriy qiymatni ko'rsatish
    regime_key = context.user_data["selected_admin_regime"]
    current_value = data.get("content_ids", {}).get(regime_key, {}).get(format_key)
    
    await query.edit_message_text(
        f"Siz {CUSTOMS_REGIMES[regime_key]} rejimi uchun {FORMATS[format_key]} formatini tanladingiz.\n\n"
        f"Joriy ID: {current_value if current_value else 'Kiritilmagan'}\n\n"
        f"Iltimos, yangi ID raqamini yuboring yoki bekor qilish uchun 'cancel' yozing:"
    )
    return ADMIN_ADD_CONTENT

async def admin_add_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin ma'lumot qo'shish"""
    text = update.message.text
    
    if text.lower() == "cancel":
        await update.message.reply_text(
            "Ma'lumot kiritish bekor qilindi.",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_MENU
    
    try:
        # ID ni butun songa aylantirish
        content_id = int(text.strip())
        
        # Ma'lumotlarni saqlash
        regime_key = context.user_data["selected_admin_regime"]
        format_key = context.user_data["selected_admin_format"]
        
        # ID ni saqlash, lug'at strukturasini tekshirish
        if "content_ids" not in data:
            data["content_ids"] = {}
            
        if regime_key not in data["content_ids"]:
            data["content_ids"][regime_key] = {}
            
        data["content_ids"][regime_key][format_key] = content_id
        
        # Ma'lumotlarni faylga saqlash
        success = save_data(data)
        
        if success:
            await update.message.reply_text(
                f"✅ ID muvaffaqiyatli saqlandi!\n\n"
                f"Rejim: {CUSTOMS_REGIMES[regime_key]}\n"
                f"Format: {FORMATS[format_key]}\n"
                f"Yangi ID: {content_id}\n\n"
                f"ID ma'lumotlari faylga saqlandi va bot qayta ishga tushganda ham saqlanib qoladi."
            )
        else:
            await update.message.reply_text(
                f"✅ ID muvaffaqiyatli saqlandi, lekin faylga saqlashda xatolik yuz berdi.\n\n"
                f"Rejim: {CUSTOMS_REGIMES[regime_key]}\n"
                f"Format: {FORMATS[format_key]}\n"
                f"Yangi ID: {content_id}\n\n"
                f"ESLATMA: Bot qayta ishga tushganda bu o'zgarish saqlanmaydi.\n"
                f"ID ni eslab qoling va kodga qo'shing:\n\n"
                f'"{regime_key}": {{\n'
                f'    "{format_key}": {content_id},\n'
                f"}}"
            )
        
        # Admin paneliga qaytish
        await update.message.reply_text(
            "Admin paneliga qaytish uchun /admin buyrug'ini yuboring yoki rejimni tanlash uchun /start"
        )
        return MAIN_MENU
    
    except ValueError:
        await update.message.reply_text(
            "❌ Xato: ID raqam bo'lishi kerak. Iltimos, qaytadan urinib ko'ring yoki bekor qilish uchun 'cancel' yozing:"
        )
        return ADMIN_ADD_CONTENT

# Statistika buyrug'i (faqat adminlar uchun)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Statistika buyrug'i (faqat adminlar uchun)"""
    user = update.effective_user
    
    # Faqat admin foydalanuvchilar uchun
    if user.id not in ADMIN_USERS:
        await update.message.reply_text("Kechirasiz, bu buyruqdan faqat adminlar foydalanishi mumkin.")
        return MAIN_MENU
    
    # Foydalanuvchilar statistikasini ko'rsatish
    stats_text = "📊 Foydalanuvchilar statistikasi:\n\n"
    
    user_count = len(data.get("user_stats", {}))
    stats_text += f"• Jami foydalanuvchilar: {user_count}\n\n"
    
    # So'nggi 5 ta faol foydalanuvchi
    stats_text += "So'nggi faol foydalanuvchilar:\n"
    
    # Foydalanuvchilarni so'nggi faollik bo'yicha saralash
    sorted_users = sorted(
        data.get("user_stats", {}).items(),
        key=lambda x: x[1]["last_seen"],
        reverse=True
    )[:5]
    
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        last_seen = datetime.fromisoformat(user_data["last_seen"]).strftime("%Y-%m-%d %H:%M:%S")
        stats_text += f"{i}. {user_data['name']} - {last_seen}\n"
    
    await update.message.reply_text(stats_text)
    return MAIN_MENU



async def handle_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Noto'g'ri kiritilgan ma'lumotlarni qayta ishlash"""
    await update.message.reply_text(
        "Iltimos, Rejimlar bo'limiga qaytish tugmasini bosing /help buyrug'ini yuboring."
    )
    return MAIN_MENU



# Xabar jo'natish ro'yxatini boshqarish funksiyalari:

async def admin_mailing_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xabar jo'natish ro'yxatini boshqarish"""
    query = update.callback_query
    await query.answer()
    
    # Mailing list olish
    mailing_list = data.get("mailing_list", [])
    
    # Mailing list haqida ma'lumot
    mailing_text = f"📋 Xabar jo'natish ro'yxati ({len(mailing_list)} ta foydalanuvchi):\n\n"
    
    if mailing_list:
        for i, user_id in enumerate(mailing_list, 1):
            # Foydalanuvchi ma'lumotlarini olish
            user_name = data.get("user_stats", {}).get(str(user_id), {}).get("name", "Noma'lum")
            mailing_text += f"{i}. {user_name} (ID: {user_id})\n"
    else:
        mailing_text += "Ro'yxat bo'sh."
    
    # Mailing list boshqarish tugmalari
    keyboard = [
        [InlineKeyboardButton("➕ Foydalanuvchi qo'shish", callback_data="add_user_to_mailing")],
        [InlineKeyboardButton("➖ Foydalanuvchi olib tashlash", callback_data="remove_user_from_mailing")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_admin")]
    ]
    
    await query.edit_message_text(
        mailing_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ADMIN_MAILING_LIST


async def mailing_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mailing list bo'limidagi callback query larni qayta ishlash"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "add_user_to_mailing":
        # Foydalanuvchi qo'shish
        return await admin_add_user_to_mailing_start(update, context)
    
    elif action == "remove_user_from_mailing":
        # Foydalanuvchi olib tashlash
        return await admin_remove_user_from_mailing_start(update, context)
    
    elif action == "back_to_admin":
        # Admin panelga qaytish
        await query.edit_message_text(
            "Admin panelga qaytish",
            reply_markup=get_admin_keyboard()
        )
        return ADMIN_MENU
    
    return ADMIN_MAILING_LIST


async def admin_add_user_to_mailing_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xabar jo'natish ro'yxatiga foydalanuvchi qo'shish boshlash"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➕ Xabar jo'natish ro'yxatiga foydalanuvchi qo'shish\n\n"
        "Qo'shmoqchi bo'lgan foydalanuvchi ID raqamini kiriting:\n"
        "(Bekor qilish uchun /cancel buyrug'ini yuboring)"
    )
    
    return ADMIN_ADD_USER_TO_MAILING


async def admin_add_user_to_mailing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xabar jo'natish ro'yxatiga foydalanuvchi qo'shish"""
    text = update.message.text
    
    # Bekor qilish
    if text == "/cancel":
        await update.message.reply_text("Foydalanuvchi qo'shish bekor qilindi.")
        await update.message.reply_text(
            "Admin panelga qaytish uchun /admin buyrug'ini yuboring."
        )
        return ConversationHandler.END
    
    try:
        # Foydalanuvchi ID ni raqamga aylantirish
        user_id = int(text.strip())
        
        # Mailing list olish
        if "mailing_list" not in data:
            data["mailing_list"] = []
        
        # Foydalanuvchi allaqachon ro'yxatda bo'lishi mumkin
        if user_id in data["mailing_list"]:
            await update.message.reply_text(
                f"⚠️ Foydalanuvchi (ID: {user_id}) allaqachon ro'yxatda mavjud.\n\n"
                f"Admin panelga qaytish uchun /admin buyrug'ini yuboring."
            )
            return ConversationHandler.END
        
        # Ro'yxatga qo'shish
        data["mailing_list"].append(user_id)
        
        # Ma'lumotlarni saqlash
        save_data(data)
        
        await update.message.reply_text(
            f"✅ Foydalanuvchi (ID: {user_id}) xabar jo'natish ro'yxatiga muvaffaqiyatli qo'shildi.\n\n"
            f"Hozirgi ro'yxatda {len(data['mailing_list'])} ta foydalanuvchi bor.\n\n"
            f"Admin panelga qaytish uchun /admin buyrug'ini yuboring."
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Xato: ID raqam bo'lishi kerak. Iltimos, qaytadan urinib ko'ring yoki bekor qilish uchun /cancel buyrug'ini yuboring:"
        )
        return ADMIN_ADD_USER_TO_MAILING


async def admin_remove_user_from_mailing_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xabar jo'natish ro'yxatidan foydalanuvchi olib tashlash boshlash"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➖ Xabar jo'natish ro'yxatidan foydalanuvchi olib tashlash\n\n"
        "Olib tashlamoqchi bo'lgan foydalanuvchi ID raqamini kiriting:\n"
        "(Bekor qilish uchun /cancel buyrug'ini yuboring)"
    )
    
    return ADMIN_REMOVE_USER_FROM_MAILING


async def admin_remove_user_from_mailing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xabar jo'natish ro'yxatidan foydalanuvchi olib tashlash"""
    text = update.message.text
    
    # Bekor qilish
    if text == "/cancel":
        await update.message.reply_text("Foydalanuvchi olib tashlash bekor qilindi.")
        await update.message.reply_text(
            "Admin panelga qaytish uchun /admin buyrug'ini yuboring."
        )
        return ConversationHandler.END
    
    try:
        # Foydalanuvchi ID ni raqamga aylantirish
        user_id = int(text.strip())
        
        # Mailing list olish
        if "mailing_list" not in data:
            data["mailing_list"] = []
        
        # Foydalanuvchi ro'yxatda bo'lishi kerak
        if user_id not in data["mailing_list"]:
            await update.message.reply_text(
                f"⚠️ Foydalanuvchi (ID: {user_id}) ro'yxatda mavjud emas.\n\n"
                f"Admin panelga qaytish uchun /admin buyrug'ini yuboring."
            )
            return ConversationHandler.END
        
        # Ro'yxatdan olib tashlash
        data["mailing_list"].remove(user_id)
        
        # Ma'lumotlarni saqlash
        save_data(data)
        
        await update.message.reply_text(
            f"✅ Foydalanuvchi (ID: {user_id}) xabar jo'natish ro'yxatidan muvaffaqiyatli olib tashlandi.\n\n"
            f"Hozirgi ro'yxatda {len(data['mailing_list'])} ta foydalanuvchi bor.\n\n"
            f"Admin panelga qaytish uchun /admin buyrug'ini yuboring."
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Xato: ID raqam bo'lishi kerak. Iltimos, qaytadan urinib ko'ring yoki bekor qilish uchun /cancel buyrug'ini yuboring:"
        )
        return ADMIN_REMOVE_USER_FROM_MAILING


# 6. Xabar jo'natish funksiyasi:

async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Belgilangan foydalanuvchilarga xabar jo'natish"""
    text = update.message.text
    
    # Bekor qilish
    if text == "/cancel":
        await update.message.reply_text("Xabar jo'natish bekor qilindi.")
        await update.message.reply_text(
            "Admin panelga qaytish uchun /admin buyrug'ini yuboring."
        )
        return ConversationHandler.END
    
    # Xabar matni
    message_text = text
    
    # Mailing list olish
    mailing_list = data.get("mailing_list", [])
    
    if not mailing_list:
        await update.message.reply_text(
            "⚠️ Xabar jo'natish ro'yxati bo'sh. Avval ro'yxatga foydalanuvchilar qo'shing.\n"
            "Admin panelga qaytish uchun /admin buyrug'ini yuboring."
        )
        return ConversationHandler.END
    
    # Jo'natilgan xabarlar hisobi
    sent_count = 0
    failed_count = 0
    
    # Xabar jo'natish boshlanishi haqida ma'lumot
    await update.message.reply_text(f"🔄 Xabar jo'natish boshlandi. {len(mailing_list)} ta foydalanuvchiga xabar jo'natilmoqda...")
    
    # Barcha foydalanuvchilarga xabar jo'natish
    for user_id in mailing_list:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Xabar jo'natishda xato (ID: {user_id}): {e}")
            failed_count += 1
    
    # Natija haqida ma'lumot
    await update.message.reply_text(
        f"✅ Xabar jo'natish yakunlandi!\n\n"
        f"• Jo'natilgan xabarlar: {sent_count}\n"
        f"• Jo'natilmagan xabarlar: {failed_count}\n\n"
        f"Admin panelga qaytish uchun /admin buyrug'ini yuboring."
    )
    
    return ConversationHandler.END




def main() -> None:
    """Botni ishga tushirish"""
    try:
        # Application yaratish va token kiritish
        application = Application.builder().token(BOT_TOKEN).build()

        # Suhbat oqimini sozlash
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                MAIN_MENU: [
                    # Rejim tugmalarini bosishda qayta ishlash
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
                ],
                FORMAT_SELECTION: [
                    CallbackQueryHandler(format_selected, pattern=r"^format_|^refresh_format|^back_to_regimes$"),
                    CallbackQueryHandler(back_to_regimes, pattern=r"^back_to_regimes$"),
                    CallbackQueryHandler(back_to_start, pattern=r"^back_to_start$"),
                ],
                ADMIN_MENU: [
                    CallbackQueryHandler(admin_menu),
                ],
                ADMIN_SELECT_REGIME: [
                    CallbackQueryHandler(admin_select_regime),
                ],
                ADMIN_SELECT_FORMAT: [
                    CallbackQueryHandler(admin_select_format),
                ],
                ADMIN_ADD_CONTENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_content),
                    CommandHandler("cancel", cancel_command),
                ],
                ADMIN_SEND_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_send_message),
                    CommandHandler("cancel", cancel_command),
                    CallbackQueryHandler(admin_menu, pattern=r"^back_to_admin$"),
                ],
                ADMIN_MAILING_LIST: [
                    CallbackQueryHandler(mailing_list_callback),
                ],
                ADMIN_ADD_USER_TO_MAILING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_to_mailing),
                    CommandHandler("cancel", cancel_command),
                ],
                ADMIN_REMOVE_USER_FROM_MAILING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_remove_user_from_mailing),
                    CommandHandler("cancel", cancel_command),
                ],
                # Admin login holati
                ADMIN_LOGIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_login),
                    CommandHandler("cancel", start),
                ],
            },
            fallbacks=[
                CommandHandler("start", start),
                CommandHandler("help", help_command),
                CommandHandler("admin", admin_command),  
                CommandHandler("stats", stats_command),
                CommandHandler("bot_creators", bot_creators_command),
                CommandHandler("cancel", cancel_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_invalid_input),
            ],
        )


        application.add_handler(conv_handler)

        # Botni ishga tushirish
        print(f"Bot ishga tushdi... (CHANNEL_ID: {CHANNEL_ID})")
        print(f"Admin foydalanuvchilar: {ADMIN_USERS}")
        print("Bot to'g'ri ishlashi uchun kanal mavjud bo'lishi va bot kanalga admin qo'shilgan bo'lishi kerak!")
        application.run_polling()
        
    except Exception as e:
        print(f"XATOLIK: Bot ishga tushishda muammo: {e}")
        print("Token va boshqa sozlamalarni tekshiring!")

if __name__ == "__main__":
    main()
