import os
import logging
import requests
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

# =========================
# ENV + LOGGING
# =========================
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

LOGIN_URL = f"{BACKEND_BASE_URL}/api/v1/auth/telegram-login/"
ME_URL = f"{BACKEND_BASE_URL}/api/v1/users/me/"
UPGRADE_URL = f"{BACKEND_BASE_URL}/api/v1/users/me/upgrade-to-seller/"
LOGOUT_URL = f"{BACKEND_BASE_URL}/api/v1/auth/logout/"

REQUEST_TIMEOUT = 10

# Conversation states
SHOP_NAME, REGION, DISTRICT, ADDRESS = range(4)


# =========================
# HELPERS
# =========================
def build_login_payload(update: Update) -> dict:
    tg_user = update.effective_user
    return {
        "telegram_id": tg_user.id,
        "username": tg_user.username or "",
        "first_name": tg_user.first_name or "",
        "last_name": tg_user.last_name or "",
       
    }


def save_tokens(context: ContextTypes.DEFAULT_TYPE, access: str, refresh: str) -> None:
    context.user_data["access"] = access
    context.user_data["refresh"] = refresh


def clear_tokens(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("access", None)
    context.user_data.pop("refresh", None)


def auth_headers(context: ContextTypes.DEFAULT_TYPE) -> dict:
    access = context.user_data.get("access")
    if not access:
        return {}
    return {"Authorization": f"Bearer {access}"}


def is_logged_in(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get("access"))


# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start -> Telegram ma'lumotlarini backendga yuboradi.
    Tokenlarni chatga chiqarmaymiz, bot ichida saqlaymiz.
    """
    payload = build_login_payload(update)

    try:
        r = requests.post(LOGIN_URL, json=payload, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            await update.message.reply_text(
                "Backend xatolik berdi ❌\n"
                f"Status: {r.status_code}\n"
                f"Body: {r.text}"
            )
            return

        data = r.json()
        access = data.get("access")
        refresh = data.get("refresh")
        user = data.get("user", {})

        if not access or not refresh:
            await update.message.reply_text("Backend token qaytarmadi ❌")
            return

        save_tokens(context, access, refresh)

        await update.message.reply_text(
            "✅ Login bo‘ldi!\n"
            f"Role: {user.get('role')}\n\n"
            "Buyruqlar:\n"
            "/me - profilni ko‘rish\n"
            "/upgrade_seller - seller bo‘lish\n"
            "/logout - chiqish\n"
            "/help - yordam"
        )

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Backend’ga ulana olmadim ❌\n{e}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Buyruqlar:\n"
        "/start - login/registratsiya\n"
        "/me - profilni ko‘rish\n"
        "/upgrade_seller - seller bo‘lish (dialog)\n"
        "/logout - chiqish\n"
        "/cancel - dialogni bekor qilish\n"
    )


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /me -> backend’dan user profilini olib beradi (token ishlayotganini tekshiradi)
    """
    if not is_logged_in(context):
        await update.message.reply_text("Avval /start qiling (login bo‘lish kerak).")
        return

    try:
        r = requests.get(ME_URL, headers=auth_headers(context), timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            await update.message.reply_text(
                "Profilni olishda xatolik ❌\n"
                f"Status: {r.status_code}\n"
                f"Body: {r.text}"
            )
            return

        user = r.json()
        await update.message.reply_text(
            "👤 Profil:\n"
            f"id: {user.get('id')}\n"
            f"telegram_id: {user.get('telegram_id')}\n"
            f"username: {user.get('username')}\n"
            f"name: {user.get('first_name')} {user.get('last_name')}\n"
            f"phone: {user.get('phone_number')}\n"
            f"role: {user.get('role')}\n"
        )

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Backend’ga ulana olmadim ❌\n{e}")


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /logout -> refresh tokenni blacklist qiladi
    """
    refresh = context.user_data.get("refresh")
    if not refresh:
        await update.message.reply_text("Siz login bo‘lmagansiz. /start qiling.")
        return

    try:
        r = requests.post(LOGOUT_URL, json={"refresh": refresh}, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            await update.message.reply_text(
                "Logout xatolik ❌\n"
                f"Status: {r.status_code}\n"
                f"Body: {r.text}"
            )
            return

        clear_tokens(context)
        await update.message.reply_text("✅ Chiqildi (logout). Endi /start qiling.")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Backend’ga ulana olmadim ❌\n{e}")


# =========================
# UPGRADE SELLER CONVERSATION
# =========================
async def upgrade_seller_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_logged_in(context):
        await update.message.reply_text("Avval /start qiling (login bo‘lish kerak).")
        return ConversationHandler.END

    await update.message.reply_text("Do‘kon nomini yozing (shop_name):")
    return SHOP_NAME


async def upgrade_seller_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["shop_name"] = update.message.text.strip()
    await update.message.reply_text("Viloyatni yozing (region):")
    return REGION


async def upgrade_seller_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["region"] = update.message.text.strip()
    await update.message.reply_text("Tuman/shaharni yozing (district):")
    return DISTRICT


async def upgrade_seller_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["district"] = update.message.text.strip()
    await update.message.reply_text("Manzil (address) yozing yoki '-' deb yuboring:")
    return ADDRESS


async def upgrade_seller_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    if address == "-":
        address = ""

    payload = {
        "shop_name": context.user_data.get("shop_name", ""),
        "region": context.user_data.get("region", ""),
        "district": context.user_data.get("district", ""),
        "address": address,
        "shop_description": "",
    }

    try:
        r = requests.post(
            UPGRADE_URL,
            json=payload,
            headers=auth_headers(context),
            timeout=REQUEST_TIMEOUT,
        )
        if r.status_code not in (200, 201):
            await update.message.reply_text(
                "Upgrade xatolik ❌\n"
                f"Status: {r.status_code}\n"
                f"Body: {r.text}"
            )
            return ConversationHandler.END

        await update.message.reply_text("✅ Tabriklayman! Endi siz SELLER bo‘ldingiz.")
        await update.message.reply_text("Tekshirish uchun /me yozing.")
        return ConversationHandler.END

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Backend’ga ulana olmadim ❌\n{e}")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END


# =========================
# MAIN
# =========================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN .env ichida yo‘q")

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("logout", logout))

    # Conversation: upgrade seller
    conv = ConversationHandler(
        entry_points=[CommandHandler("upgrade_seller", upgrade_seller_start)],
        states={
            SHOP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, upgrade_seller_shop)],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, upgrade_seller_region)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, upgrade_seller_district)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, upgrade_seller_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)

    app.run_polling()


if __name__ == "__main__":
    main()