from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import time
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_BZIP2
from datetime import datetime, time
from dotenv import load_dotenv
load_dotenv()

is_progress = False

def backup(update: Update, context: CallbackContext):
    if str(update.message.chat_id) != os.environ['GROUP_ID']:
        return
    
    global is_progress

    if is_progress:
        context.bot.send_message(chat_id=os.environ['GROUP_ID'], text='Резервная копия формируется...')
        return
    
    context.bot.send_message(chat_id=os.environ['GROUP_ID'], text='Ожидайте...')

    is_progress = True

    send_backup(context=context)
    
    is_progress = False

# Функция для отправки сообщения в группу
def send_backup(context: CallbackContext):
    try:
        # Путь к директории, которую нужно архивировать
        directory = Path(os.environ['DIRECTORY_PATH'])

        # Создаем временный файл архива
        current_date = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        temp_zipfile = f"./deploy {current_date}.zip"

        # Создаем архив с использованием сжатия BZIP2
        with ZipFile(temp_zipfile, 'w', compression=ZIP_BZIP2) as zipf:
            # Рекурсивно добавляем все файлы из директории в архив
            for file in directory.glob('**/*'):
                if file.is_file():
                    zipf.write(file, arcname=file.relative_to(directory))

        # Отправляем архив пользователю
        context.bot.send_document(chat_id=os.environ['GROUP_ID'], document=open(temp_zipfile, 'rb'))

        # Удаляем временный файл архива
        os.remove(temp_zipfile)
    except Exception as e:
        context.bot.send_message(chat_id=os.environ['GROUP_ID'], text=f'Произошла ошибка при создании резервной копии: {e}')

def main():
    updater = Updater(os.environ['BOT_TOKEN'])

    ## Get the dispatcher to register handlers
    dp = updater.dispatcher

    ## Register command handlers
    dp.add_handler(CommandHandler("backup", backup))

    ## Регистрируем функцию отправки сообщения в группу через определенный интервал времени
    if os.environ['BACKUP_AUTO_SENDING'] == 'True':
        job_queue = updater.job_queue
        hours = os.environ['SCHEDULED_HOURS'].split(',')
        for hour in hours:
            job_queue.run_daily(send_backup, time(hour=int(hour), minute=0), days=(0, 1, 2, 3, 4, 5, 6))

    ## Start the bot
    updater.start_polling()

    ## Run the bot until Ctrl-C is pressed or the process receives SIGINT,
    ## SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()