from app import application
from flask import render_template, flash, redirect, url_for, request
# from app.forms import LoginForm, RegistrationForm 
# from flask_login import current_user, login_user, logout_user, login_required
# from app.models import User 
# from werkzeug.urls import url_parse
# from app import db
# from flask import request 
from app.serverlibrary import *


@application.route('/', methods = ['POST', 'GET'])
@application.route('/home', methods = ['POST', 'GET'])
def home():
    if request.method == "POST":
        height = request.form['board-h']
        width = request.form['board-w']
        mineP = request.form['mine-percentage']
        return redirect(url_for('game', height = height, width = width, mineP = mineP))
    return render_template('home.html')

@application.route('/game')
def game():
    height = (request.args['height'])
    width = (request.args['width'])
    return render_template('index.html', height= height, width = width)



