"""
Bot de Telegram - Verificación de membresía obligatoria
Requiere: pip install python-telegram-bot
"""

import logging
from telegram import Update, ChatMember
from telegram.ext import (
Application,
MessageHandler,
filters,
ContextTypes,
CommandHandler,
)

BOT_TOKEN = "8697949870:AAFfPPERMgXX_iThG1xkrADpiQQAPldOn8s"

GRUPO_PRINCIPAL_ID = -1003047416099

GRUPO_REQUERIDO_ID = -1002390073044

ENLACE_GRUPO_REQUERIDO = "https://t.me/fibrabarata"

NOMBRE_GRUPO_REQUERIDO = "FIBRA Y MÓVIL Barata España"

ELIMINAR_MENSAJE = True

logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def es_miembro(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        miembro = await context.bot.get_chat_member(GRUPO_REQUERIDO_ID, user_id)
        estados_validos = {
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER,
        }
        return miembro.status in estados_validos
    except Exception as e:
        logger.warning(f"No se pudo verificar membresía del usuario {user_id}: {e}")
        return True

async def verificar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GRUPO_PRINCIPAL_ID:
        return

    user = update.effective_user
    message = update.effective_message

    if user.is_bot:
        return

    try:
        miembro_principal = await context.bot.get_chat_member(
            GRUPO_PRINCIPAL_ID, user.id
        )
        if miembro_principal.status in {ChatMember.ADMINISTRATOR, ChatMember.OWNER}:
            return
    except Exception:
        pass

    if not await es_miembro(context, user.id):
        if ELIMINAR_MENSAJE:
            try:
                await message.delete()
            except Exception as e:
                logger.warning(f"No se pudo eliminar el mensaje: {e}")

        aviso = await context.bot.send_message(
            chat_id=GRUPO_PRINCIPAL_ID,
            text=(
                f"🚫 {user.mention_html()}, para escribir en este grupo necesitas "
                f"ser miembro de <b>{NOMBRE_GRUPO_REQUERIDO}</b>.

"
                f"👉 Únete aquí: {ENLACE_GRUPO_REQUERIDO}

"
                f"<i>Este mensaje se eliminará en 30 segundos.</i>"
            ),
            parse_mode="HTML",
        )

        context.job_queue.run_once(
            eliminar_aviso,
            when=30,
            data={"chat_id": GRUPO_PRINCIPAL_ID, "message_id": aviso.message_id},
        )

        logger.info(f"Usuario {user.id} (@{user.username}) bloqueado por no ser miembro.")

async def eliminar_aviso(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    try:
        await context.bot.delete_message(
            chat_id=data["chat_id"], message_id=data["message_id"]
        )
    except Exception:
        pass

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Para escribir en el grupo principal debes ser miembro de "
        f"<b>{NOMBRE_GRUPO_REQUERIDO}</b>.

"
        f"👉 {ENLACE_GRUPO_REQUERIDO}",
        parse_mode="HTML",
    )

async def comando_verificar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if await es_miembro(context, user.id):
        await update.message.reply_text(
            f"✅ ¡Perfecto! Ya eres miembro de <b>{NOMBRE_GRUPO_REQUERIDO}</b>. "
            f"Puedes escribir en el grupo principal.",
            parse_mode="HTML",
        )
    else:
        await update.message.reply_text(
            f"❌ Aún no eres miembro de <b>{NOMBRE_GRUPO_REQUERIDO}</b>.

"
            f"Únete aquí: {ENLACE_GRUPO_REQUERIDO}",
            parse_mode="HTML",
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", comando_start))
    app.add_handler(CommandHandler("verificar", comando_verificar))
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & ~filters.COMMAND,
            verificar_mensaje,
        )
    )

    logger.info("Bot iniciado. Esperando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()