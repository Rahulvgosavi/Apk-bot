import os
import base64
import requests
import telebot
from flask import Flask, request

TOKEN = '8880759832:AAFn7b5JRul4_Z8JGusBFRpbFPAMTtZxkKk'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Render के Environment Variables से GitHub की डिटेल्स लेना
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "बोट तैयार है! अपनी .apk फाइल यहाँ भेजें, मैं इसे सीधे आपके GitHub पर अपलोड करके पर्मानेंट लिंक दूंगा।")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    file_info = message.document
    file_name = file_info.file_name

    if not file_name.endswith('.apk'):
        bot.reply_to(message, "कृपया केवल .apk फाइल ही भेजें!")
        return

    bot.reply_to(message, "फाइल GitHub पर अपलोड हो रही है, कृपया प्रतीक्षा करें...")

    try:
        # टेलीग्राम से फाइल डाउनलोड करना
        file_path_info = bot.get_file(file_info.file_id)
        downloaded_file = bot.download_file(file_path_info.file_path)

        # फाइल को Base64 में बदलना
        encoded_content = base64.b64encode(downloaded_file).decode('utf-8')

        # GitHub API URL
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{file_name}"
        
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        
        data = {
            "message": f"Upload {file_name} via Telegram Bot",
            "content": encoded_content,
            "branch": "main"  # अगर आपकी रिपॉजिटरी की डिफ़ॉल्ट ब्रांच master है, तो यहाँ 'master' कर दें
        }

        # GitHub पर फाइल भेजना
        response = requests.put(url, json=data, headers=headers)

        if response.status_code in [201, 200]:
            # पर्मानेंट Raw डाउनलोड लिंक बनाना
            download_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/{file_name}"
            bot.reply_to(
                message, 
                f"✅ **फाइल सफलतापूर्वक अपलोड हो गई है!**\n\nइस लिंक को कॉपी करके अपने Admin Panel में डालें:\n`{download_url}`", 
                parse_mode="Markdown"
            )
        else:
            error_msg = response.json().get('message', 'Unknown error')
            bot.reply_to(message, f"❌ अपलोड करने में विफल: {error_msg}")

    except Exception as e:
        bot.reply_to(message, f"❌ एक त्रुटि हुई: {str(e)}")

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
