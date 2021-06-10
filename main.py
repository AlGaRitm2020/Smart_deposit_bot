from random import randint
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    ConversationHandler

# from nlp import get_stems, check_stems
# from key_words import KeyWords
# from pycbrf_test import get_currency


from config import TOKEN
from key_words import KeyWords
from nlp import check_stems, get_stems

from soup import get_data


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Добро пожаловать! \n' +
                              'Я телеграм бот-помощник NLP-bank. Я могу показать информацию ' +
                              'о банке, посмотреть баланс, перевести деньги, забокировать ' +
                              'карту, написать в поддержку.')
    update.message.reply_text('Для начала работы введите номер вашей карты')

    return 1


def sort_by_profit(update: Update, context: CallbackContext, reverse=True, period='12 month', start_index=0):
    """
    Print most profit actives per 12 week/month/year/month
    You can set reverse for sorting
    """
    if period == '12 month':
        sort_index = 16
        grow_period = 'годовой'
    elif period == 'year':
        sort_index = 15
        grow_period = 'с начала года'
    elif period == 'month':
        sort_index = 14
        grow_period = 'месячный'
    else:
        sort_index = 13
        grow_period = 'недельный'

    most_profit_data = sorted(data, key=lambda x: x[sort_index], reverse=reverse)
    for i in range(start_index, start_index + 15):
        (update.message.reply_text(
            f'{i + 1} "{most_profit_data[i][3]}" {grow_period} рост: {most_profit_data[i][sort_index]}'))


def stream(update, context):

    """
    main handler for messages
    checking keywords in message
    """

    is_answered = False
    content_count_per_page = 15
    stems = get_stems(update.message.text)
    print(stems)
    global period_gl, start_index_gl, reverse_gl
    reverse_gl = True
    if check_stems(stems, KeyWords.increase):
        reverse_gl = False
    if check_stems(stems, KeyWords.profit):
        start_index_gl = 0
        if check_stems(stems, KeyWords.week):
            period_gl = 'week'
        elif check_stems(stems, KeyWords.month):
            period_gl = 'month'
        elif check_stems(stems, KeyWords.year):
            period_gl = 'year'
        else:
            period_gl = '12 month'

        sort_by_profit(update, context, reverse=reverse_gl, period=period_gl, start_index=start_index_gl)
    elif check_stems(stems, KeyWords.extra_content):
        start_index_gl += content_count_per_page
        sort_by_profit(update, context, reverse=reverse_gl, period=period_gl,
                       start_index=start_index_gl)


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    text_handler = MessageHandler(Filters.text, stream)

    dispatcher.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    data = get_data()
    main()
