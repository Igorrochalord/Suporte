from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

import urllib.parse

# Função para limpar a URL
def limpar_url(url):
    # Remove parâmetros (ex: ?utm_source, ?s=20 etc)
    parsed = urllib.parse.urlparse(url)
    url_limpa = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return url_limpa

# Função que responde com a URL limpa e botões
async def tratar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text

    # Detecta se há uma URL
    if "http" in mensagem:
        palavras = mensagem.split()
        for palavra in palavras:
            if palavra.startswith("http"):
                url_original = palavra
                url_limpa = limpar_url(url_original)

                # Cria botões
                botoes = [
                    [
                        InlineKeyboardButton("🔗 Abrir link limpo", url=url_limpa),
                        InlineKeyboardButton("📎 Link original", url=url_original),
                    ]
                ]
                markup = InlineKeyboardMarkup(botoes)

                await update.message.reply_text(
                    f"🧹 Aqui está sua URL limpa:\n{url_limpa}",
                    reply_markup=markup
                )
                return

# Inicialização do bot
app = ApplicationBuilder().token("").build()

# Adiciona handler que responde a qualquer mensagem de texto com link
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tratar_mensagem))

print("Bot rodando...")
app.run_polling()
