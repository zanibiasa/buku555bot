from flask import Flask
from telegram import Bot
from telegram.ext import Dispatcher
from botDuitModule.secret import bot_token, server_url
from flask_sqlalchemy import SQLAlchemy

bot = Bot(token=bot_token)
dispatcher = Dispatcher(bot, None, use_context=True)

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from botDuitModule import linkurl