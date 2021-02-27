import telebot
from faunahelper import FaunaHelper
from faunadb.client import FaunaClient
from datetime import datetime
from datetime import date
from telebot import types
import os


bot_token = os.environ['BOT_TOKEN']
faunadb_key = os.environ['FAUNA_KEY']


bot = telebot.TeleBot(bot_token)
faunahelper = FaunaHelper(FaunaClient(faunadb_key))
keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row('💡', '📜')


@bot.message_handler(commands=['start', 'help'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, f'Hello, {message.chat.first_name}! Welcome to Ideas.')
        all_id = faunahelper.get_info_about_all_id()
        if message.chat.id not in all_id:
            faunahelper.add_new_user_by_telegram_id(message.chat.id)
            bot.send_message(438228497,
                             f'New user: {message.chat.id}  -  {message.chat.first_name}  Users:  {len(all_id) + 1}')

    bot.send_message(message.chat.id, '''
    Hello! My name is Idea. I'm telegram bot that was written by @David_Als
    You can safely hold your ideas here.
    There is following commands:
    /help - give you all information like this.
    /idea NAME DATE  or 💡 NAME DATE - create your idea to the future. Example: 💡 MyDream YYYY-MM-DD
    /show_my_ideas  or 📜- showing list of your ideas.
    /delete_idea NAME - deleting idea with name NAME.
    /delete_idea all - deleting list of your ideas.
    /today - your Ideas for today.
      hope you enjoy    :)
    ''')


@bot.message_handler(commands=['idea'])
def idea(message):
    new_idea = message.text.split()
    if len(new_idea) != 3:
        bot.send_message(message.chat.id, '❌Invalid name or date for idea.(/idea name date)')
    else:
        if new_idea[1] == 'all':
            bot.send_message(message.chat.id, '❌Please, choose another name for your Idea. Name all is built in.')
        else:
            if check_valid_date(new_idea[2], message):
                faunahelper.update_idea_by_telegram_id(new_idea[1], new_idea[2], message.chat.id)
                bot.send_message(message.chat.id, '✅ Success')
            else:
                bot.send_message(message.chat.id, f'❌Invalid date. Date should be {date.today()} < your date')


def check_valid_date(dateday, message):
    try:
        d1 = datetime.strptime(str(date.today()), "%Y-%m-%d")
        d2 = datetime.strptime(dateday, "%Y-%m-%d")
        if (d2 - d1).days <= 0:
            return False
        return True
    except ValueError:
        bot.send_message(message.chat.id, f'❌Invalid date. Example: {date.today()}')


@bot.message_handler(commands=['show_my_ideas'])
def show_my_ideas(message):
    ideas = faunahelper.get_ideas_by_telegram_id(message.chat.id)
    if len(ideas.keys()) > 0:
        ideasinfo = ['💡IDEAS💡']
        for count, usersidea in enumerate(ideas.items(), start=1):
            ideasinfo.append(f'{count}.   {usersidea[0]}  —  {usersidea[1]}')
        bot.send_message(message.chat.id, '\n'.join(ideasinfo))
    else:
        bot.send_message(message.chat.id, 'Your list of Ideas is empty.')


@bot.message_handler(commands=['today'])
def today(message):
    llist = check_date(message.chat.id)
    if len(llist) != 0:
        for i in llist:
            bot.send_message(message.chat.id, i)
    else:
        bot.send_message(message.chat.id, "You haven't ideas for realizing today.")


@bot.message_handler(commands=['delete_idea'])
def delete_idea_or_ideas(message):
    info = message.text.split()
    chat_id = message.chat.id
    if len(info) == 2:
        informationfromfaundb = {'Test': -1}
        if info[1] == 'all':
            faunahelper.delete_idea_list_by_telegram_id(chat_id)
            bot.send_message(chat_id, '✅ Ideas was deleted')
        else:
            informationfromfaundb = faunahelper.get_ideas_by_telegram_id(chat_id)
            if info[1] in informationfromfaundb:
                faunahelper.delete_idea_by_name_by_telegram_id(info[1], chat_id)
                bot.send_message(chat_id, f'✅ Idea {info[1]} was deleted')

            else:
                informationfromfaundb['Test2'] = -1
                bot.send_message(chat_id, f'You have no ideas in your list like {info[1]}')
        if len(informationfromfaundb) == 1 or info[1] == 'all':
            bot.send_message(chat_id, 'Now your list of ideas is empty. Do you have new ideas?')
    else:
        bot.send_message(chat_id, '❌Invalid response. /delete_idea (name/all)')


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Write it faster!')

    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'I think you are joking :)')


@bot.message_handler(content_types=['text'])
def idea_emj(message):
    if len(message.text.split()) == 1:
        if message.text == '💡':

            markup_inline = types.InlineKeyboardMarkup()
            item_yes = types.InlineKeyboardButton(text='YES', callback_data='yes')
            item_no = types.InlineKeyboardButton(text='NO', callback_data='no')

            markup_inline.add(item_yes, item_no)
            bot.send_message(message.chat.id, 'IDEA???', reply_markup=markup_inline)

        elif message.text == '📜':
            show_my_ideas(message)
        elif message.text == 'How are you?':
            bot.send_message(message.chat.id, 'Fine, thanks')
        else:
            bot.send_message(message.chat.id, 'Press button or call command :)', reply_markup=keyboard())
    elif message.text[0] == '💡':
        idea(message)


def check_date(idd):
    info = faunahelper.get_info_by_telegram_id(idd)
    ideaslist = list()
    for uidea in info['ideas']:
        if info['ideas'][uidea] == str(date.today()):
            ideaslist.append(f"Today: {info['ideas'][uidea]}. Realize your Idea: {uidea}")
            faunahelper.delete_idea_by_name_by_telegram_id(uidea, idd)
    return ideaslist


def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_idea = types.KeyboardButton('💡')
    item_list = types.KeyboardButton('📜')
    markup.add(item_idea, item_list)
    return markup


if __name__ == '__main__':
    bot.polling(none_stop=True)
