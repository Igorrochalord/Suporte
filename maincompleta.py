from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
import urllib.parse

# Token e Grupo
TOKEN = "7802698956:AAFkdzLqj35RwLA2dDcsAxnmRnDr3ZcQkKs"
ID_GRUPO_SUPORTE = -4102182375

# Função para limpar URL
def limpar_url(url):
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

# Menu principal fixo (ReplyKeyboard)
def criar_menu_principal():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🧹 Limpar Cache")],
        [KeyboardButton("🆘 Solicitar Suporte")]
    ], resize_keyboard=True)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔧 *Menu Principal* - Escolha uma opção:",
        reply_markup=criar_menu_principal(),
        parse_mode="Markdown"
    )

# Processar mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🧹 Limpar Cache":
        await update.message.reply_text(
            "📎 Cole o link que deseja limpar o cache:",
            reply_markup=criar_menu_principal()
        )
        context.user_data["esperando_url"] = True
    
    elif text == "🆘 Solicitar Suporte":
        await update.message.reply_text(
            "📝 Descreva seu problema ou solicitação:",
            reply_markup=criar_menu_principal()
        )
        context.user_data["esperando_suporte"] = True
    
    elif context.user_data.get("esperando_url"):
        url_limpa = limpar_url(text)
        
        # Botões inline para os links
        botoes = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Abrir link limpo", url=url_limpa)]
        ])
        
        await update.message.reply_text(
            f"🧹 *Cache limpo com sucesso!*\n\n"
            f"🔗 Nova URL: `{url_limpa}`\n\n"
            "⏳ Aguarde 5-10 minutos para refletir as alterações.\n"
            "🔄 Se não funcionar, repita o processo.",
            reply_markup=botoes,
            parse_mode="Markdown"
        )
        
        # Volta ao menu principal
        await update.message.reply_text(
            "Escolha outra opção:",
            reply_markup=criar_menu_principal()
        )
        context.user_data["esperando_url"] = False
    
    elif context.user_data.get("esperando_suporte"):
        # Salva a mensagem e pede o setor
        context.user_data["msg_suporte"] = text
        
        # Teclado inline para seleção de setor
        teclado_setor = InlineKeyboardMarkup([
            [InlineKeyboardButton("Redação", callback_data="setor_redacao")],
            [InlineKeyboardButton("Tecnologia", callback_data="setor_tech")],
            [InlineKeyboardButton("Administração", callback_data="setor_adm")],
            [InlineKeyboardButton("Anexo", callback_data="setor_anexo")],
            [InlineKeyboardButton("Reportes", callback_data="setor_reportes")],
            [InlineKeyboardButton("Jornalistas", callback_data="setor_jornalistas")],
            [InlineKeyboardButton("Projetos especiais", callback_data="setor_especial")],
            [InlineKeyboardButton("Estudio", callback_data="setor_estudio")],
        ])
        
        await update.message.reply_text(
            "🏢 Selecione o setor relacionado:",
            reply_markup=teclado_setor
        )
        context.user_data["esperando_suporte"] = False

# Processar seleção de setor
async def handle_setor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    setor = query.data.replace("setor_", "")
    mensagem = context.user_data.get("msg_suporte", "Sem descrição")
    usuario = query.from_user
    
    # Formata o username para mencionar o usuário
    username = f"@{usuario.username}" if usuario.username else "(sem username)"
    
    # Envia para o grupo de suporte
    await context.bot.send_message(
        chat_id=ID_GRUPO_SUPORTE,
        text=(
            f"📢 *Nova solicitação de suporte*\n\n"
            f"👤 *Usuário:* {usuario.full_name} ({username})\n"
            f"📛 *Setor:* {setor}\n"
            f"📝 *Mensagem:* {mensagem}\n\n"
        ),
        parse_mode="Markdown"
    )
    
    await query.edit_message_text("✅ Solicitação enviada com sucesso!")
    
    # Volta ao menu principal
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Escolha outra opção:",
        reply_markup=criar_menu_principal()
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_setor))
    
    app.run_polling()

if __name__ == "__main__":
    main()