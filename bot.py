import logging
import os
import json
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Load Google Drive Credentials
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = "credentials.json"  # Upload this file to your bot server

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = "7699062884:AAGWDxfvJ9FQ4UjSG0njcUucYwdedB0HGxc"

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Send me any file, and I will upload it to Google Drive.")

async def upload_to_drive(file_path, file_name):
    """Uploads a file to Google Drive"""
    file_metadata = {"name": file_name}
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{file.get('id')}/view"

async def handle_document(update: Update, context: CallbackContext) -> None:
    """Handles document uploads from Telegram"""
    file = await update.message.document.get_file()
    file_path = f"./{update.message.document.file_name}"
    
    await file.download_to_drive(file_path)
    drive_link = await upload_to_drive(file_path, update.message.document.file_name)
    
    await update.message.reply_text(f"✅ File Uploaded to Google Drive: {drive_link}")

    os.remove(file_path)  # Clean up after upload

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    app.run_polling()

if __name__ == "__main__":
    main()
