import re
from datetime import datetime

from TwitterMedia import TwitterMedia

import sqlite3 as sql
from sqlite3.dbapi2 import IntegrityError

from telegram import ParseMode
from telegram.ext import Updater, MessageHandler, CommandHandler


Pattern = r'(https?://)?(mobile\.)?(twitter|x)\.com/.+?/status/\d+'
Downloader = TwitterMedia(use_print = True)


con = sql.connect('banned.db', isolation_level = None, check_same_thread = False)
c = con.cursor()
c.execute('CREATE TABLE IF NOT EXISTS punished (id INTEGER NOT NULL PRIMARY KEY);')


def log(text):
    print(f"| {datetime.now().strftime('%H:%M:%S')} | {text}")


def start(update, context):
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Hi, send a twitter status url that contains a video/gif to use this bot.\nIf you face any issues please message @ulfsjar"
    )


def ban(update, context):
    if int(update.message.chat_id) != 'enter your own user id here.':
        return
    else:
        try:
            prisoner = context.args[0]
            log(f'Banning {prisoner}')
            
            c.execute('INSERT INTO punished VALUES (?)', (prisoner,))
            context.bot.send_message(
                chat_id = update.message.chat_id,
                parse_mode = ParseMode.MARKDOWN,
                text = f'Banned [{prisoner}](tg://user?id={prisoner})'
            )
        except IntegrityError:
            log('The id is probably already in the database, ignoring.')
    

def processor(update, context):
    text = update.message.text    
    chat_id = update.message.chat_id
    name = update.message.chat.first_name
    username = update.message.chat.username
    message_id = update.message.message_id

    c.execute('SELECT id FROM punished WHERE id=?', (chat_id,))
    exists = c.fetchall()
    
    if exists:
        log(f'{chat_id} is banned, skipping..')
        return
        
    if not text:
        log(f"@{username} | {name} | {chat_id}\nRequest doesn't contain text, skipping...")
        return

    log(f'Request: {username} | {name} | {text}')

    result = re.search(Pattern, text)

    if not result:
        context.bot.send_message(
            chat_id = chat_id,
            reply_to_message_id = message_id,
            text = "_I'm sorry, I couldn't find a twitter url in your message._",
            parse_mode = ParseMode.MARKDOWN
        )
        return
    
    try:
        tweet = Downloader.fetch_media(result.group(0))
    except:
        context.bot.send_message(
            chat_id = chat_id,
            reply_to_message_id = message_id,
            text = "_I'm sorry, something went wrong while trying to find the video._",
            parse_mode = ParseMode.MARKDOWN
        )
        return

    if tweet is not None:
        try:
            context.bot.send_video(
                chat_id = chat_id,
                video = tweet.url,
                reply_to_message_id = message_id,
                supports_streaming = True
            )
        except:
            context.bot.send_message(
                chat_id = chat_id,
                reply_to_message_id = message_id,
                text = f"I'm sorry, telegram is being a lil meanie and not accepting the video.\n\nHere's the URL instead;\n\n{tweet.url}"
            )
    else:
        context.bot.send_message(
            chat_id = chat_id,
            reply_to_message_id = message_id,
            text = "_I'm sorry, something went wrong while trying to find the video._",
            parse_mode = ParseMode.MARKDOWN
        )

def main():
    updater = Updater(
        token = '',
        use_context = True,
        request_kwargs = {'read_timeout': 1000, 'connect_timeout': 1000}
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('ban', ban, pass_args = True))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(None, processor))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    log('ONLINE')
    main()
