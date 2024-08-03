from pyrogram import Client, filters
from flask import Flask, jsonify
import threading
import logging
from bot import app as pyrogram_app, data, sudo_users
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

def sanitize_message(text):
    """Remove or replace problematic characters or formatting."""
    return text.replace('<pre>', '').replace('</pre>', '').strip()

@pyrogram_app.on_message(filters.incoming & filters.command(['start', 'help']))
def help_message(app, message):
    try:
        user_mention = message.from_user.mention()
        reply_text = f"Hi {user_mention}, I can encode Telegram files in x265. Just send me a video."
        reply_text = sanitize_message(reply_text)
        logging.info(f"Sending help message: {reply_text}")
        message.reply_text(reply_text, quote=True)
    except Exception as e:
        logging.error(f"Error sending help message: {e}")

@pyrogram_app.on_message(filters.user(sudo_users) & filters.incoming & (filters.video | filters.document))
def encode_video(app, message):
    msg = None
    try:
        if message.document:
            if not message.document.mime_type in video_mimetype:
                logging.error(f"Invalid video MIME type: {message.document.mime_type}")
                reply_text = "Invalid Video! Make sure it's a valid video file."
                reply_text = sanitize_message(reply_text)
                logging.info(f"Sending invalid video reply: {reply_text}")
                message.reply_text(reply_text, quote=True)
                return
        
        msg = message.reply_text("Added to queue...", quote=True)
        data.append(message)
        if len(data) == 1:
            add_task(message)
    except Exception as e:
        if msg:
            logging.error(f"Error handling message: {e}")
            reply_text = f"Error: {e}"
            reply_text = sanitize_message(reply_text)
            logging.info(f"Sending error reply: {reply_text}")
            msg.edit(reply_text)
        else:
            logging.error(f"Error: {e}")
    finally:
        if msg and msg.text == "Added to queue...":
            msg.edit("Added to queue...")

# Run Flask and Pyrogram concurrently
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the Pyrogram bot
    try:
        logging.info("Starting the Pyrogram bot.")
        pyrogram_app.run()
    except KeyboardInterrupt:
        logging.info("Shutting down the bot.")
