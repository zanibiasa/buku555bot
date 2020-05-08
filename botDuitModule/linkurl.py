import re
import uuid
from botDuitModule import bot, dispatcher, app, db
from botDuitModule.secret import bot_token, server_url
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (CommandHandler, ConversationHandler, CallbackQueryHandler,
                          MessageHandler, Filters)
from flask import request
from botDuitModule.dbase import User, Hutang

list_keyboardbutton = []

SAPA, SAPA_TAMBAH, BUAT_APA, BERAPA, APA_BERAPA, BUAT_BARU = range(6)


def message_handler_start():
    return 'Nak buka buku \n hutang ngan sapa'


def handler_start(update, context):
    print('handler start')
    query = update.callback_query

    if query:
        print('handler start - ada quety')
        update = query

        update.edit_message_text(message_handler_start(),
                                 reply_markup=handler_siapa(update, context))
    else:
        print('handler start - no query start')
        update.message.reply_text(message_handler_start(),
                                  reply_markup=handler_siapa(update, context))
    # print('context.args: ', context.args)
    return SAPA


def handler_siapa(update, context):

    aaa = array_senarai(update, context)

    keyboardbutton = [InlineKeyboardButton(
        'TAMBAH ORANG', callback_data='QORTEXNEWNAMA')]

    aaa.append(keyboardbutton)

    return InlineKeyboardMarkup(aaa)


def handler_siapa_tambah(update, context):
    print('handler sisapa tambah')
    query = update.callback_query
    query.answer()

    query.edit_message_text('Nak tambah sapa')
    return SAPA_TAMBAH


def handler_hutang_nilai(update, context):
    print('handler hutang nilai')
    query = update.callback_query
    if query:
        update = query
        query.answer()

    update.edit_message_text('Berapa nilai hutang(0-999.99)?')
    return BERAPA


def handler_hutang_description(update, context):
    print('handler hutang desc')
    testValidHutang = update.message.text
    cubaregex = re.search(
        "^([0-9]{0,3}(([.]{1}[0-9]{0,2})|([.]{0})))$", testValidHutang)
    if not cubaregex:
        update.message.reply_text(
            'Nilai tidak sah. Letak nilai lain (0-999.99')
        return BERAPA

    update.message.reply_text('Pasal apa?')

    nilai = update.message.text
    context.user_data['nilai'] = nilai
    return APA_BERAPA


def dbase_simpan_nama(update, context):
    print('dbase_simpan_nama')
    sapa = str(update.message.text)
    cubaregex = re.search(
        '^([0-9a-zA-Z ]{1,19})$', sapa
    )

    if not cubaregex:
        update.message.reply_text(
            'Nama tidak sah. Sila guna huruf dan nombor sahaja. Letak nama lain:'
        )
        return SAPA_TAMBAH

    origin = update.message.chat_id

    ass = User(nama_pemberi_id=origin, nama_diberi=sapa)

    db.session.add(ass)
    db.session.commit()
    id_sapa = ass.id
    print('id_sapa')
    context.user_data['nama'] = sapa
    context.user_data['id_sapa'] = id_sapa
    context.user_data['wujud'] =None

    keyboard = handler_pilih_hutang(update,context)
    update.message.reply_text(
        text=f'{sapa} - Nak buat apa', reply_markup=keyboard)
    return BUAT_APA


def dbase_simpan_hutang(update, context):
    print('dbase simpan hutang')
    hutang_nama = update.message.text

    cubaregex = re.search(
        '^([0-9a-zA-Z ]{1,19})$', hutang_nama
    )

    if not cubaregex:
        update.message.reply_text(
            'Perihal tidak sah. Sila guna huruf dan nombor sahaja. Letak nama lain:'
        )
        return APA_BERAPA

    id_sapa = context.user_data['id_sapa']

    dia_hutang = context.user_data['hutang']
    nilai_hutang = context.user_data['nilai']

    int_nilai_hutang = float(nilai_hutang)
    int_nilai_hutang = int_nilai_hutang*100
    int_nilai_hutang = int(int_nilai_hutang)

    ss = Hutang(hutang_nama=hutang_nama, nilai_hutang=int_nilai_hutang,
                dia_hutang=dia_hutang, sape_id=id_sapa)

    db.session.add(ss)
    db.session.commit()

    update.message.reply_text(f'RM{nilai_hutang} - {hutang_nama}')
    update.message.reply_text(array_hutang(update, context))
    handler_menu_orang_tu(update, context)

    return BUAT_APA


def handler_pilih_hutang(update, context):
    print('handler_pilih huang')
    print(context.user_data['wujud'])
    if context.user_data['wujud'] is not None:
        print('lolll')
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    'Kau hutang dia', callback_data='QORTEXKAU'),
                InlineKeyboardButton(
                    'Tolak Hutang', callback_data='QORTEXTOLAK')
            ],
            [
                InlineKeyboardButton(
                    'Dia hutang kau', callback_data='QORTEXDIA'),
                InlineKeyboardButton('Main Menu', callback_data='CANCEL')
            ]

        ])
    else:
        print('memang tak wujud')
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    'Kau hutang dia', callback_data='QORTEXKAU'),
                InlineKeyboardButton(
                    'Tolak Hutang', callback_data='QORTEXTOLAK')
            ],
            [
                InlineKeyboardButton(
                    'Dia hutang kau', callback_data='QORTEXDIA'),
                InlineKeyboardButton('Sync Hutang', callback_data='QORTEXSYNC')
            ],
            [
                InlineKeyboardButton('Main Menu', callback_data='CANCEL')
            ]

        ])

    return keyboard


def handler_sync_nama(update, context):
    print('syncccss')
    hash_id = uuid.uuid4().hex[:6]
    print(type(hash_id))
    print(hash_id)
    context.bot_data[hash_id] = context.user_data['id_sapa']
    link_nama = f'Klik link ini untuk sync hutang kamu berdua\nt.me/Buku555Bot?start={hash_id}'
    print(link_nama)
    query = update.callback_query
    print('ddkkd')
    query.edit_message_text(text=link_nama)
    reply = InlineKeyboardMarkup(
        [[InlineKeyboardButton('Back', callback_data='QORTEXNAMA')]])
    print('muuuuu')
    query.message.reply_text(
        text=f'Share link di atas kepada {context.user_data["nama"]}', reply_markup=reply)
    print('generate link nama')
    return BUAT_APA


def set_hutang_kau(update, context):
    print('sethutang kjau')
    context.user_data['hutang'] = False
    handler_hutang_nilai(update, context)
    return BERAPA


def set_hutang_dia(update, context):

    print('sethutang kjau')
    context.user_data['hutang'] = True

    handler_hutang_nilai(update, context)
    return BERAPA


def menu_tolak_hutang(update, context):
    print('menu_tolak hutang')
    query = update.callback_query
    query.answer()

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
    context.user_data['balance_hutang'] = 0
    print('method delete hutang - boleh commit')
    query = update.callback_query
    query.answer()
    handler_menu_orang_tu(update, context)
    return BUAT_APA


def array_senarai(update, context):
    print('array senarai')
    list_keyboardbutton = []
    kbb = []

    total_senarai = User.query.filter(
        User.nama_pemberi_id == update.message.chat_id).all()
    i = 0

    for total in total_senarai:

        kbb = []
        wujud = total.nama_diberi_id
        print(type(wujud))
        n = str(total.id)
        nama_diberi = str(total.nama_diberi)
        context.user_data[n] = {'nama': nama_diberi, 'wujud': wujud}
        print(context.user_data[n])
        keyboardbutton1 = InlineKeyboardButton(nama_diberi, callback_data=n)

        if (i % 2 == 0):

            kbb.append(keyboardbutton1)

            list_keyboardbutton.append(kbb)

        else:

            list_keyboardbutton[int((i-1)/2)].append(keyboardbutton1)

        i += 1

    return list_keyboardbutton


def array_hutang(update, context):
    print('array hutang')

    list_array_hutang = []
    keyboardbutton = []
    total_hutang = Hutang.query.filter(
        Hutang.sape_id == context.user_data['id_sapa']).all()

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

        tulisan = tulisan + '\nHutang bersih: \n'
        if (nilai_kira_balance < 0):
            tulisan = tulisan + 'KAU hutang RM' + str(abs(nilai_kira_balance))
        else:
            tulisan = tulisan + 'DIA hutang RM' + str(abs(nilai_kira_balance))

        context.user_data['balance_hutang'] = str(abs(nilai_kira_balance))
    else:
        tulisan = context.user_data['nama'] + ':- \n Tak de hutang'

    return tulisan


def handler_menu_orang_tu(update, context):
    print('handler menu orang tu')
    query = update.callback_query

    if query:

        print(query.answer())

        if not ((query['data'] == 'QORTEXDELETE') or (query['data'] == 'QORTEXNAMA')):

            context.user_data['id_sapa'] = int(query['data'])
            context.user_data['nama'] = context.user_data[query['data']]['nama']
            print(context.user_data['nama'])
            print(context.user_data[query['data']])
            aaas = context.user_data[query['data']]['wujud']
            print(aaas)
            context.user_data['wujud'] = aaas
            print(context.user_data['wujud'])

    tulis = array_hutang(update, context)
    keyboard = handler_pilih_hutang(update, context)

    if query:

        query.edit_message_text(
            text=tulis, reply_markup=keyboard
        )
    else:

        update.message.reply_text(
            text=tulis, reply_markup=keyboard)

    if query:

        return BUAT_APA


def done(update, context):
    print('done')
    print(update.callback_query)

    query = update.callback_query

    if query:
        update = query
        update.answer()

    update.message.reply_text('TERIMA KASIH \nSila Tekan /start untuk mulakan')

    user_data.clear()
    return ConversationHandler.END

def lain(update,context):
    print('aaaa')


def donea(update, context):
    query = update.callback_query

    if query:
        update = query
        update.answer()

    update.message.reply_text('tak valid')


conv_start = ConversationHandler(
    entry_points=[
        CommandHandler('start', lain, filters= Filters.regex(r'^/start [0-9a-fA-F]{6}')),
        CommandHandler('start', handler_start)
        
    ],

    states={

        SAPA:  [
            CallbackQueryHandler(handler_siapa_tambah,
                                 pattern=r'^(QORTEXNEWNAMA)'),
            CallbackQueryHandler(handler_menu_orang_tu,
                                 pattern=r'^\d.*$'),
            MessageHandler(Filters.text & ~Filters.command, handler_start)

        ],

        SAPA_TAMBAH: [
            MessageHandler(Filters.text & ~Filters.command, dbase_simpan_nama)
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
            CallbackQueryHandler(handler_start, pattern=r'^CANCEL',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            CallbackQueryHandler(handler_sync_nama, pattern=r'^QORTEXSYNC',
                                 pass_update_queue=True, pass_chat_data=True, pass_user_data=True),
            MessageHandler(Filters.text & ~ Filters.command,
                           handler_menu_orang_tu)

        ],

        BERAPA: [
            MessageHandler(Filters.text & ~Filters.command,
                           handler_hutang_description)

        ],
        APA_BERAPA: [
            MessageHandler(Filters.text & ~Filters.command,
                           dbase_simpan_hutang)

        ],

    },
    fallbacks=[
        CommandHandler('done', done),
        MessageHandler(Filters.all, done)
    ],
    allow_reentry=True,
    per_chat=True


)

dispatcher.add_handler(conv_start)


@app.route('/{}'.format(bot_token), methods=['POST'])
def respond():

    update = Update.de_json(request.get_json(force=True), bot)
    print(update)

    dispatcher.process_update(update)
    print('ok')
    return 'ok'


@app.route('/buatdatabase', methods=['GET'])
def buatDb():
    db.create_all()
    return 'dah buat db'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook(f'{server_url}{bot_token}')
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
