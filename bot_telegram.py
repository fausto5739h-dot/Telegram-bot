"""
Bot de Telegram - Verificacion de membresía obligatoria
"""

import logging
from telegram import Update, ChatMember
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

BOT_TOKEN = "8697949870:AAFfPPERMgXX_iThG1xkrADpiQQAPldOn8s"
GRUPO_PRINCIPAL_ID = -1003047416099
GRUPO_REQUERIDO_ID = -1002390073044
ENLACE_GRUPO_REQUERIDO = "https://t.me/fibrabarata"
NOMBRE_GRUPO_REQUERIDO = "FIBRA Y MOVIL Barata Espana"
ELIMINAR_MENSAJE = True

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def es_miembro(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        miembro = await context.bot.get_chat_member(GRUPO_REQUERIDO_ID, user_id)
        return miembro.status in {ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER}
    except Exception as e:
        logger.warning(f"Error verificando usuario {user_id}: {e}")
        return True

async def verificar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GRUPO_PRINCIPAL_ID:
        return
    user = update.effective_user
    message = update.effective_message
    if user.is_bot:
        return
    try:
        miembro = await context.bot.get_chat_member(GRUPO_PRINCIPAL_ID, user.id)
        if miembro.status in {ChatMember.ADMINISTRATOR, ChatMember.OWNER}:
            return
    except:
        pass
    if not await es_miembro(context, user.id):
        if ELIMINAR_MENSAJE:
            try:
                await message.delete()
            except:
                pass
        texto = f"Hola {user.mention_html()}, debes ser miembro de {NOMBRE_GRUPO_REQUERIDO}. Unete aqui: {ENLACE_GRUPO_REQUERIDO}"
        aviso = await context.bot.send_message(chat_id=GRUPO_PRINCIPAL_ID, text=texto, parse_mode="HTML")
        context.job_queue.run_once(eliminar_aviso, when=30, data={"chat_id": GRUPO_PRINCIPAL_ID, "message_id": aviso.message_id})

async def eliminar_aviso(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    try:
        await context.bot.delete_message(chat_id=data["chat_id"], message_id=data["message_id"])
    except:
        pass

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Para escribir debes ser miembro de {NOMBRE_GRUPO_REQUERIDO}: {ENLACE_GRUPO_REQUERIDO}", parse_mode="HTML")

async def comando_verificar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if await es_miembro(context, user.id):
        await update.message.reply_text(f"Eres miembro de {NOMBRE_GRUPO_REQUERIDO}. Puedes escribir.")
    else:
        await update.message.reply_text(f"No eres miembro aun. Unete aqui: {ENLACE_GRUPO_REQUERIDO}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", comando_start))
    app.add_handler(CommandHandler("verificar", comando_verificar))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, verificar_mensaje))
    logger.info("Bot iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
