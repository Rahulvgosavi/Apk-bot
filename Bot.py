import os
import telebot

TOKEN = '8880759832:AAFn7b5JRul4_Z8JGusBFRpbFPAMTtZxkKk'
bot = telebot.TeleBot(TOKEN)

BASE_URL = "BASE_URL = "https://apk-bot-dmue.onrender.com" 

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "बोट तैयार है! अपनी .apk फाइल यहाँ भेजें, मैं आपको डायरेक्ट डाउनलोड लिंक दूंगा।")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    file_info = message.document
    file_name = file_info.file_name

    if not file_name.endswith('.apk'):
        bot.reply_to(message, "कृपया केवल .apk फाइल ही भेजें!")
        return

    bot.reply_to(message, "फाइल प्रोसेस हो रही है, कृपया प्रतीक्षा करें...")

    try:
        file_path_info = bot.get_file(file_info.file_id)
        downloaded_file = bot.download_file(file_path_info.file_path)

        local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        with open(local_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        direct_link = f"{BASE_URL}/downloads/{file_name}"
        
        bot.reply_to(message, f"✅ **लिंक तैयार है!**\n\nइस लिंक को कॉपी करके अपने Admin Panel में डालें:\n`{direct_link}`", parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"एरर आया: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
