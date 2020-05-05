import time
from botDuitModule import bot, dispatcher, app, db
from botDuitModule.secret import bot_token, server_url
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, CallbackQueryHandler,
                          MessageHandler, Filters)
from flask import request
from botDuitModule.dbase import User, Hutang

list_keyboardbutton = []

SAPA, BUAT_APA, BERAPA, APA_BERAPA, BUAT_BARU = range(5)
start = 0

def message_handler_start():
    print('message send')
    return 'Nak buka buku \n hutang ngan sapa'


def handler_start(update, context):
    print('handler_start ada')
    print(context.args)
    handler_siapa(update)
    print('handler_start update')
    update.message.reply_text(message_handler_start(),
                              reply_markup=handler_siapa(update))
    time.sleep(13)
    stop = time.time()
    print(stop)
    print(start)
    buuu = (stop-start)

    print(buuu)                        
    return SAPA


def handler_siapa(update):
    print('siapa update')
    aaa = array_senarai(update)
    print('siapa aaaa')
    keyboardbutton = [InlineKeyboardButton(
        'TAMBAH ORANG', callback_data='WOMBOGETA')]
    print('sssss')
    aaa.append(keyboardbutton)
    print('asd')
    return InlineKeyboardMarkup(aaa)


def handler_siapa_tambah(update, context):
    query = update.callback_query
    query.answer()
    print('sssasdasdasdada')
    query.edit_message_text('Nak tambah sapa')
    return SAPA


def handler_hutang_nilai(update, context):
    query = update.callback_query
    query.answer()
    print('sssasdasdasdada')
    query.edit_message_text('Berapa nilai hutang(RM)?')
    return BERAPA


def handler_hutang_description(update, context):
    print('berajya hutang desc')
    update.message.reply_text('Pasal apa?')
    print('berjaya psaal')
    nilai = update.message.text
    context.user_data['nilai'] = nilai
    return APA_BERAPA


def dbase_simpan_nama(update, context):
    sapa = str(update.message.text)
    origin = update.message.chat_id

    ass = User(nama_first_id=origin, nama_diberi=sapa)

    db.session.add(ass)
    db.session.commit()
    id_sapa = ass.id
    context.user_data['sapa'] = sapa
    context.user_data['id_sapa'] = id_sapa
    keyboard = handler_pilih_hutang()
    update.message.reply_text(text='Nak buat apa', reply_markup=keyboard)
    return BUAT_APA


def dbase_simpan_hutang(update, context):

    hutang_nama = update.message.text
    id_sapa = context.user_data['id_sapa']

    dia_hutang = context.user_data['hutang']
    nilai_hutang = context.user_data['nilai']
    print('simpan hutang')
    int_nilai_hutang = float(nilai_hutang)
    int_nilai_hutang = int_nilai_hutang*100
    int_nilai_hutang = int(int_nilai_hutang)
    print('sss')

    ss = Hutang(hutang_nama=hutang_nama, nilai_hutang=int_nilai_hutang,
                dia_hutang=dia_hutang, sape_id=id_sapa)
    print('sdasfafasf')
    db.session.add(ss)
    db.session.commit()

    update.message.reply_text(f'RM{nilai_hutang} - {hutang_nama}')

    handler_menu_orang_tu(update, context)
    print('dasdas')
    return BUAT_APA


def handler_pilih_hutang():
    print('handler_pilih huang')
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            'Kau hutang dia', callback_data='KAU')],
        [InlineKeyboardButton(
            'Dia hutang kau', callback_data='DIA')],
        [InlineKeyboardButton(
            'Tolak Hutang', callback_data='TOLAK')],
        [InlineKeyboardButton(
            'Cancel', callback_data='CANCELLAA')]
    ])

    return keyboard


def set_hutang_kau(update, context):
    print('sethutang kjau')
    context.user_data['hutang'] = False
    print('setshutang falss')
    handler_hutang_nilai(update, context)


def set_hutang_dia(update, context):
    print('sethutang kjau')
    context.user_data['hutang'] = True

    handler_hutang_nilai(update, context)


def array_senarai(update):
    print('senarai')
    list_keyboardbutton = []
    keyboardbutton = []
    total_senarai = User.query.filter(
        User.nama_pemberi_id == update.message.chat_id).all()

    for total in total_senarai:

        n = str(total.id)
        nama_diberi = str(total.nama_diberi)

        keyboardbutton = [InlineKeyboardButton(nama_diberi, callback_data=n)]

        list_keyboardbutton.append(keyboardbutton)

    
    return list_keyboardbutton


def array_hutang(update, context):

    list_array_hutang = []
    keyboardbutton = []
    total_hutang = Hutang.query.filter(
        Hutang.sape_id == context.user_data['id_sapa']).all()
    print(total_hutang)
    tulisan = ''
    if total_hutang:
        tulisan = tulisan + 'Dia hutang: \n'
        for total in total_hutang:
            if total.dia_hutang:

                nama = str(total.hutang_nama)
                nilai = float(total.nilai_hutang)
                nilai = str(nilai/100)
                tulisan = tulisan + nama + ' - ' + 'RM' + nilai + '\n'
        tulisan = tulisan +  '\nKau hutang: \n'
        for total in total_hutang:
            if not (total.dia_hutang):
                nama = str(total.hutang_nama)
                nilai = float(total.nilai_hutang)
                nilai = str(nilai/100)
                tulisan = tulisan + nama + ' - ' + 'RM' + nilai + '\n'

    else:
        tulisan = 'Tak de hutang'
        print(tulisan)
    return tulisan


def handler_menu_orang_tu(update, context):
    print('---------------------------------')
    query = update.callback_query
    print(query)
    print('----------------------')
    if query:

        print(query.answer())
        print(int(query['data']))
        context.user_data['id_sapa'] = int(query['data'])

    print(context.user_data['id_sapa'])
    tulis = array_hutang(update, context)
    print(tulis)

    print('sdasad')
    keyboard = handler_pilih_hutang()
    print('dd')

    if query:
        print('ni query')

        query.edit_message_text(
            text=tulis, reply_markup=keyboard
        )
    else:
        print('ni bukan query')
        update.message.reply_text(
            text=tulis, reply_markup=keyboard)
    print('hanler pulih')
    if query:
        print('hanler pulasfafih')
        return BUAT_APA


def done(update, context):
    query = update.callback_query
    query.answer()
    print('sssasdasdasdada')
    query.edit_message_text('THANK YOU')

    user_data.clear()
    return ConversationHandler.END


conv_start = ConversationHandler(
    entry_points=[CommandHandler('start', handler_start)],

    states={

        SAPA:  [
            CallbackQueryHandler(handler_siapa_tambah,
                                 pattern=r'^(WOMBOGETA)'),
            CallbackQueryHandler(handler_menu_orang_tu,
                                 pattern=r'^(?!(WOMBOGETA)\s).*$'),
            MessageHandler(Filters.text, dbase_simpan_nama)

        ],

        BUAT_APA: [
            CallbackQueryHandler(set_hutang_kau, pattern=r'^KAU',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            CallbackQueryHandler(set_hutang_dia, pattern=r'^DIA',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            MessageHandler(Filters.text, handler_hutang_description)
        ],

        BERAPA: [
            MessageHandler(Filters.text, handler_hutang_description)

        ],
        APA_BERAPA: [
            MessageHandler(Filters.text, dbase_simpan_hutang)

        ],
        BUAT_BARU: [
            CallbackQueryHandler(
                set_hutang_kau, pattern=r'^KAU', pass_user_data=True),
            CallbackQueryHandler(
                set_hutang_dia, pattern=r'^DIA', pass_user_data=True),
            CallbackQueryHandler(
                set_hutang_dia, pattern=r'^TOLAK', pass_user_data=True),
            MessageHandler(Filters.text, set_hutang_dia)
        ]
    },
    fallbacks=[CallbackQueryHandler(done, pattern=r'^CANCELLAA')],
    per_chat=True
)


dispatcher.add_handler(conv_start)


@app.route('/{}'.format(bot_token), methods=['POST'])
def respond():
    start = time.time()

    update = Update.de_json(request.get_json(force=True), bot)
    print(update)

    dispatcher.process_update(update)

    return 'ok'


@app.route('/buatdatabase', methods=['GET'])
def buatDb():
    db.create_all()
    return 'dah buat db'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=server_url, HOOK=bot_token))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
