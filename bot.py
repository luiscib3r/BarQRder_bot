from barcode import Code128
from barcode.writer import ImageWriter
import qrcode
import uuid
from telegram.ext import Updater, CallbackContext
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler
from telegram.ext import Filters
from telegram import Update, Chat, ChatAction
import os
from dotenv import load_dotenv
load_dotenv()


start_message = '''
Hola ¿que deseas hacer?
    
Usa /qr para generar códigos QR.
Usa /barcode para generar códigos de barras.
'''


# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(start_message)


# Send files
def send_file(filename: str, chat: Chat):
    chat.send_action(action=ChatAction.UPLOAD_PHOTO, timeout=None)

    chat.send_photo(
        photo=open(filename, 'rb')
    )

    os.unlink(filename)


# QR GENERATOR
QR_INPUT_TEXT = 0


def qr_command_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Envíame el texto para generarte un código QR')

    return QR_INPUT_TEXT


def generate_qr(text: str) -> str:
    filename = str(uuid.uuid1()) + '.jpg'

    img = qrcode.make(text)
    img.save(filename)

    return filename


def qr_input_text(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    filename = generate_qr(text)

    send_file(filename, update.message.chat)

    return ConversationHandler.END


# BARCODE GENERATOR
BARCODE_INPUT_TEXT = 1


def barcode_command_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Envíame el texto para generarte un código de barras.')

    return BARCODE_INPUT_TEXT


def generate_barcode(text: str) -> str:
    filename = str(uuid.uuid1()) + '.jpg'

    with open(filename, 'wb') as f:
        Code128(text, writer=ImageWriter()).write(f)

    return filename


def barcode_input_text(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    filename = generate_barcode(text)

    send_file(filename, update.message.chat)

    return ConversationHandler.END


if __name__ == '__main__':
    TOKEN = os.getenv('BOT_TOKEN')
    NAME = os.getenv('NAME')
    PORT = os.getenv('PORT')

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('qr', qr_command_handler),
            CommandHandler('barcode', barcode_command_handler),
        ],

        states={
            QR_INPUT_TEXT: [
                MessageHandler(Filters.text, qr_input_text)
            ],
            BARCODE_INPUT_TEXT: [
                MessageHandler(Filters.text, barcode_input_text)
            ]
        },

        fallbacks=[]
    ))

    # updater.start_polling()
    # updater.idle()

    updater.start_webhook(listen='0.0.0.0', port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://{}.herokuapp.com/{}'.format(NAME, TOKEN))
    updater.idle()
