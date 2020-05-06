import time
from botDuitModule import bot, dispatcher, app, db
from botDuitModule.secret import bot_token, server_url
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (CommandHandler, ConversationHandler, CallbackQueryHandler,
                          MessageHandler, Filters)
from flask import request
from botDuitModule.dbase import User, Hutang

list_keyboardbutton = []

SAPA, BUAT_APA, BERAPA, APA_BERAPA, BUAT_BARU = range(5)


def message_handler_start():
    return 'Nak buka buku \n hutang ngan sapa'


def handler_start(update, context):
    query = update.callback_query
    if query:
        update = query

    update.message.reply_text(message_handler_start(),
                              reply_markup=handler_siapa(update, context))
    print('context.args: ', context.args)
    return SAPA


def handler_siapa(update, context):

    aaa = array_senarai(update, context)

    keyboardbutton = [InlineKeyboardButton(
        'TAMBAH ORANG', callback_data='WOMBOGETA')]

    aaa.append(keyboardbutton)

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
    query.edit_message_text('Berapa nilai hutang(RMXX.XX)?')
    return BERAPA


def handler_hutang_description(update, context):
    print('berajya hutang desc')
    update.message.reply_text('Pasal apa?')
    print('berjaya psaal')
    nilai = update.message.text
    context.user_data['nilai'] = nilai
    return APA_BERAPA


def dbase_simpan_nama(update, context):
    print('dbase_simpan_nama')
    sapa = str(update.message.text)
    origin = update.message.chat_id

    ass = User(nama_pemberi_id=origin, nama_diberi=sapa)

    db.session.add(ass)
    db.session.commit()
    id_sapa = ass.id
    context.user_data['nama'] = sapa
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
            'Kau hutang dia', callback_data='QORTEXKAU')],
        [InlineKeyboardButton(
            'Dia hutang kau', callback_data='QORTEXDIA')],
        [InlineKeyboardButton(
            'Tolak Hutang', callback_data='QORTEXTOLAK')],
        [InlineKeyboardButton(
            'Main Menu', callback_data='CANCEL')]
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


def menu_tolak_hutang(update, context):
    print('menu_tolak hutang')
    query = update.callback_query
    query.answer()

    print('----------------------')
    tuliss = context.user_data['balance_hutang']
    tulis = f'YAKIN CLEAR HUTANG - RM{tuliss}'

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            tulis, callback_data='QORTEXDELETE')],
        [InlineKeyboardButton(
            'Xlah Gurau Je', callback_data='QORTEXNAMA')]
    ])
    query.edit_message_text(text='WARNING', reply_markup=keyboard)

    return BUAT_APA


def method_delete_hutang(update, context):
    print('method_delete hutang')
    print()
    Hutang.query.filter(
        Hutang.sape_id == context.user_data['id_sapa']).delete()

    db.session.commit()
    print('boleh commit')
    query = update.callback_query
    query.answer()
    handler_menu_orang_tu(update, context)
    return BUAT_APA


def array_senarai(update, context):
    print('senarai')
    list_keyboardbutton = []
    keyboardbutton = []
    total_senarai = User.query.filter(
        User.nama_pemberi_id == update.message.chat_id).all()

    for total in total_senarai:

        n = str(total.id)
        nama_diberi = str(total.nama_diberi)
        context.user_data[n] = nama_diberi
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
    tulisan = tulisan + context.user_data['nama'] + ': \n'
    if total_hutang:

        tulisan = tulisan + 'Dia hutang: \n'
        nilai_kira_aku = 0
        for total in total_hutang:

            if total.dia_hutang:

                nama = str(total.hutang_nama)
                nilai = float(total.nilai_hutang)
                nilai_kira_aku = nilai_kira_aku + total.nilai_hutang
                nilai = str(nilai/100)
                tulisan = tulisan + nama + ' - ' + 'RM' + nilai + '\n'

        print('first')
        print(nilai_kira_aku)
        tulisan = tulisan + '\nKau hutang: \n'

        nilai_kira_dia = 0
        for total in total_hutang:
            if not (total.dia_hutang):

                nama = str(total.hutang_nama)
                nilai = float(total.nilai_hutang)
                nilai_kira_dia = nilai_kira_dia + total.nilai_hutang
                nilai = str(nilai/100)
                tulisan = tulisan + nama + ' - ' + 'RM' + nilai + '\n'
        nilai_kira_balance = nilai_kira_aku - nilai_kira_dia
        nilai_kira_balance = float(nilai_kira_balance)/100
        print(nilai_kira_balance)
        tulisan = tulisan + '\nHutang bersih: \n'
        if (nilai_kira_balance < 0):
            tulisan = tulisan + 'KAU hutang RM' + str(abs(nilai_kira_balance))
        else:
            tulisan = tulisan + 'DIA hutang RM' + str(abs(nilai_kira_balance))

        context.user_data['balance_hutang'] = str(abs(nilai_kira_balance))
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
        print(query['data'])
        if not ((query['data'] =='QORTEXDELETE') or (query['data']=='QORTEXNAMA')):
            print('query data')
            context.user_data['id_sapa'] = int(query['data'])
            context.user_data['nama'] = context.user_data[query['data']]
        print('daata qqq')
        print(context.user_data['nama'])
        print('ottttttt')
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
            CallbackQueryHandler(set_hutang_kau, pattern=r'^QORTEXKAU',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            CallbackQueryHandler(set_hutang_dia, pattern=r'^QORTEXDIA',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            CallbackQueryHandler(menu_tolak_hutang, pattern=r'QORTEXTOLAK',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            CallbackQueryHandler(handler_menu_orang_tu, pattern=r'^QORTEXNAMA',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            CallbackQueryHandler(method_delete_hutang, pattern=r'^QORTEXDELETE',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            MessageHandler(Filters.regex(
                r'^(?!(start|CANCEL)\s).*$'), handler_hutang_description),
            CallbackQueryHandler(handler_start, pattern=r'^CANCEL',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True)

        ],

        BERAPA: [
            MessageHandler(Filters.text, handler_hutang_description)

        ],
        APA_BERAPA: [
            MessageHandler(Filters.text, dbase_simpan_hutang)

        ],

    },
    fallbacks=[CallbackQueryHandler(done, pattern=r'^CANCEL')],
    per_chat=True
)


dispatcher.add_handler(conv_start)


@app.route('/{}'.format(bot_token), methods=['POST'])
def respond():

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
