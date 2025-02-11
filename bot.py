from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from PIL import Image
import asyncio

# Comando /start: envia mensagem de boas-vindas
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie uma foto e eu adicionarei a marca d'água para você.")

# Handler para fotos: baixa a foto, aplica a marca d'água com 80% de opacidade e retorna o resultado
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Seleciona a foto com maior resolução
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive("input.jpg")
    
    # Aplica a marca d'água com 80% de opacidade (mantendo a qualidade da imagem PNG)
    add_watermark("input.jpg", "output.png")
    
    # Envia a imagem processada de volta ao usuário sem legenda
    with open("output.png", "rb") as f:
        await update.message.reply_photo(photo=f)

# Função que aplica a marca d'água (logo) com 80% de opacidade no centro da imagem
def add_watermark(input_path, output_path):
    # Abre a imagem principal e converte para RGBA para suportar transparência
    image = Image.open(input_path).convert("RGBA")
    
    # Abre a logo (marca d'água) e converte para RGBA
    watermark = Image.open("logo.png").convert("RGBA")
    
    # Multiplica o canal alfa da logo por 0.8 para que ela fique com 80% de opacidade
    r, g, b, a = watermark.split()
    new_alpha = a.point(lambda p: int(p * 0.8))
    watermark.putalpha(new_alpha)
    
    # Calcula as coordenadas para centralizar a logo na imagem principal
    base_width, base_height = image.size
    wm_width, wm_height = watermark.size
    x = (base_width - wm_width) // 2
    y = (base_height - wm_height) // 2
    
    # Aplica a logo sobre a imagem principal usando alpha_composite
    image.alpha_composite(watermark, (x, y))
    
    # Salva a imagem final como PNG para preservar a qualidade e transparência
    image.save(output_path)

# Handler para ignorar outras mensagens que não sejam fotos
async def ignore_non_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

if __name__ == "__main__":
    TOKEN = "8085343108:AAHT2O1azRDoJXbV9_4UqQA8CYrsLtFWs1c"  # Token do seu bot
    app = Application.builder().token(TOKEN).build()
    
    # Adiciona os handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(~filters.PHOTO, ignore_non_photo))
    
    # Inicia o bot em modo polling
    asyncio.run(app.run_polling())
