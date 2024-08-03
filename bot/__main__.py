from pyrogram import Client, filters
from flask import Flask, jsonify
import threading
import logging
from bot import app, data, sudo_users
from bot.helper.utils import add_task

# Initialize Flask app
flask_app = Flask(__name__)

@flask_app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'Bot is running'})

def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=8000)  # Port 8000
    except Exception as e:
        logging.error(f"Flask app encountered an error: {e}")

# Pyrogram bot setup
video_mimetype = [
    "video/x-flv",
    "video/mp4",
    "application/x-mpegURL",
    "video/MP2T",
    "video/3gpp",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-ms-wmv",
    "video/x-matroska",
    "video/webm",
    "video/x-m4v",
    "video/quicktime",
    "video/mpeg"
]

@app.on_message(filters.incoming & filters.command(['start', 'help']))
def help_message(app, message):
    message.reply_text(f"Hi {message.from_user.mention()}\nI can encode Telegram files in x265, just send me a video.", quote=True)

@app.on_message(filters.user(sudo_users) & filters.incoming & (filters.video | filters.document))
def encode_video(app, message):
    if message.document:
        if not message.document.mime_type in video_mimetype:
            message.reply_text("```Invalid Video !\nMake sure its a valid video file.```", quote=True)
            return
    message.reply_text("```Added to queue...```", quote=True)
    data.append(message)
    if len(data) == 1:
        add_task(message)

# Run Flask and Pyrogram concurrently
if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the Pyrogram bot
    try:
        app.run()
    except KeyboardInterrupt:
        logging.info("Shutting down the bot.")
