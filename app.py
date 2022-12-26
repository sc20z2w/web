import hashlib

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from sqlalchemy import or_
from sql import db
from flask_migrate import Migrate
from model import Register, Game, Bet
from logging.config import dictConfig


dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
            },
            "log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": "./log_file/flask.log",
                "maxBytes": 20*1024*1024,
                "backupCount": 10,
                "encoding": "utf8",
            },

        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "log_file"],
        },
    }
)


app = Flask(__name__)
USERNAME = 'root'
PASSWORD ='123456'
HOST = 'localhost'
PORT='3306'
DATABASE='web'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORD,HOST,PORT,DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
SESSION_TYPE = 'filesystem'
db.init_app(app)
app.secret_key = 'asfda8r9q3y9qy#%GFSD^%WTAfasdfasqwe'
migrate = Migrate(app, db)


@app.route('/')
def start():
    db.create_all()
    wager = Game.query.filter_by(game_state='can').all()
    return render_template("bet.html", wager=wager)


@app.route('/skip_register')
def skip_register():
    return render_template("register.html")


@app.route('/skip_add')
def skip_add():
    return render_template("add_wager.html")

@app.route('/skip_change')
def skip_change():
    return render_template("change_password.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        hash_password = hashlib.sha256((request.form.get("password")).encode("utf-8")).hexdigest()
        search = Register.query.all()
        for i in search:
            if i.username == username:
                flash("the username has been registered!")
                return render_template('register.html')
        try:
            register_info = Register(username=request.form.get("username"), password=hash_password,
                                     email=request.form.get("email"), state="No", money=0)
            db.session.add(register_info)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('ERROR!')
            return render_template('register.html')
        return redirect('/')


@app.route('/change_password', methods=["GET", "POST"])
def change_password():
        username = request.form.get("username")
        email = request.form.get("email")
        hash_password = hashlib.sha256((request.form.get("password")).encode("utf-8")).hexdigest()
        search = Register.query.all()
        for i in search:
            if i.username == username and i.email== email:
                if hash_password != i.password:
                    flash("the old password is not correct")
                    return render_template('change_password.html')
                else:
                    i.password=hashlib.sha256((request.form.get("changepw")).encode("utf-8")).hexdigest()
                    db.session.commit()
                    return redirect('login')
            else:
                flash("please enter the correct username and email")
                return render_template('change_password.html')
        return redirect('login')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        user = Register.query.filter_by(username=username).first()
        if user and hashlib.sha256(password.encode("utf-8")).hexdigest() == user.password:
            user.state = 'Yes'
            db.session.commit()
            app.logger.info(f'{username} logged in successfully')
            if user.username == "manager":
                r = make_response(redirect('/manager_bet'))
                r.set_cookie('username', user.username)
                r.set_cookie('userid', str(user.id))
                return r,{'msg': 'success!', 'access_token': '********token******'}
            else:
                r = make_response(redirect('/login_bet'))
                r.set_cookie('username', user.username)
                r.set_cookie('userid', str(user.id))
                return r, {'msg': 'success!', 'access_token': '********token******'}
        else:
            flash("Wrong username or password")
            app.logger.info('%s failed to log in', user.username)
            return render_template("login.html"), {'msg': 'username or password invalid', 'access_token': ''}


@app.route('/search', methods=["GET", "POST"])
def search():
    search_time = request.form.get("search")
    search_home_team = request.form.get("search")
    search_guest_team = request.form.get("search")
    like_info = Game.query.filter_by(game_state='can').filter(
        or_(Game.game_time.like("%"+search_time+"%"),
            Game.home_team.like("%"+search_home_team+"%"),
            Game.guest_team.like("%" + search_guest_team + "%")
            )).all()
    return render_template('search.html', like_info=like_info)


@app.route('/login_bet', methods=["GET", "POST"])
def login_bet():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    wager_bet = Game.query.filter_by(game_state='can').all()
    return render_template('login_bet.html', username=cookie_username, userid=cookie_userid, wager_bet=wager_bet)


@app.route('/manager_bet', methods=["GET", "POST"])
def manager_bet():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    user_bet = Bet.query.all()
    return render_template('manager_bet.html', username=cookie_username, userid=cookie_userid, user_bet=user_bet)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    cookie_username = request.cookies.get('username')
    user = Register.query.filter_by(username=cookie_username).first()
    user.state = 'No'
    db.session.commit()
    app.logger.info('%s log out', user.username)
    return redirect('/'),{'msg': 'logout!', 'access_token': '********token******'}


@app.route('/pay', methods=["GET", "POST"])
def pay():
    cookie_username = request.cookies.get('username')
    user = Register.query.filter_by(username=cookie_username).first()
    user.money = user.money+500
    db.session.commit()
    return redirect('/login_bet')


@app.route('/search_bet', methods=["GET", "POST"])
def search_bet():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    search_bet_time = request.form.get("search_bet")
    search_bet_home_team = request.form.get("search_bet")
    search_bet_guest_team = request.form.get("search_bet")
    like_bet_info = Game.query.filter_by(game_state='can').filter(
        or_(Game.game_time.like("%"+search_bet_time+"%"),
            Game.home_team.like("%"+search_bet_home_team+"%"),
            Game.guest_team.like("%" + search_bet_guest_team + "%")
            )).all()
    return render_template('search_bet.html', like_bet_info=like_bet_info, username=cookie_username, userid=cookie_userid)


@app.route('/search_wager', methods=["GET", "POST"])
def search_wager():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    search_wager_time = request.form.get("search_wager")
    search_wager_home_team = request.form.get("search_wager")
    search_wager_guest_team = request.form.get("search_wager")
    like_wager_info = Game.query.filter_by(game_state='can').filter(
        or_(Game.game_time.like("%"+search_wager_time+"%"),
            Game.home_team.like("%"+search_wager_home_team+"%"),
            Game.guest_team.like("%" + search_wager_guest_team + "%")
            )).all()
    like_wager_over_info = Game.query.filter_by(game_state='over').filter(
        or_(Game.game_time.like("%" + search_wager_time + "%"),
            Game.home_team.like("%" + search_wager_home_team + "%"),
            Game.guest_team.like("%" + search_wager_guest_team + "%")
            )).all()
    return render_template('search_wager.html', like_wager_info=like_wager_info, like_wager_over_info=like_wager_over_info,
                           username=cookie_username, userid=cookie_userid)



@app.route('/bet_guest', methods=["GET", "POST"])
def bet_guest():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    user = Register.query.filter_by(username=cookie_username).first()
    gi = request.args.get('game_id')
    gt = request.args.get('guest_team')
    if user.money>=100:
        user.money = user.money-100
        if Bet.query.filter_by(user_name=cookie_username, game_id=gi, bet_team=gt).all():
            bet = Bet.query.filter_by(user_name=cookie_username, game_id=gi, bet_team=gt).first()
            bet.bet_money = bet.bet_money+100
            bet.bet_state = "./static/image/wait.svg"
        else:
            bet = Bet(user_id=cookie_userid, user_name=cookie_username, game_id=gi, bet_team=gt, bet_money=100)
            bet.bet_state = "./static/image/wait.svg"
            db.session.add(bet)
        db.session.commit()
        return redirect("/show_bet")
    else:
        flash("Do not have enough money!")
        return redirect("/login_bet")


@app.route('/bet_home', methods=["GET", "POST"])
def bet_home():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    user = Register.query.filter_by(username=cookie_username).first()
    gi = request.args.get('game_id')
    ht = request.args.get('home_team')
    if user.money>=100:
        user.money = user.money-100
        if Bet.query.filter_by(user_name=cookie_username, game_id=gi, bet_team=ht).all():
            bet = Bet.query.filter_by(user_name=cookie_username, game_id=gi, bet_team=ht).first()
            bet.bet_money = bet.bet_money+100
            bet.bet_state = "./static/image/wait.svg"
        else:
            bet = Bet(user_id=cookie_userid, user_name=cookie_username, game_id=gi, bet_team=ht, bet_money=100)
            bet.bet_state = "./static/image/wait.svg"
            db.session.add(bet)
        db.session.commit()
        return redirect("/show_bet")
    else:
        flash("Do not have enough money!")
        return redirect("/login_bet")


@app.route('/show_bet', methods=["GET", "POST"])
def show_bet():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    bet_list = Bet.query.filter(Bet.user_name == cookie_username).all()
    return render_template("show_bet.html", username=cookie_username, userid=cookie_userid, bet_list=bet_list)


@app.route('/show_wager', methods=["GET", "POST"])
def show_wager():
    cookie_username = request.cookies.get('username')
    cookie_userid = request.cookies.get('userid')
    wager_list = Game.query.filter_by(game_state='can').all()
    wager_finished = Game.query.filter_by(game_state='over').all()
    return render_template("show_wager.html", username=cookie_username, userid=cookie_userid,
                           wager_list=wager_list, wager_finished=wager_finished)

@app.route('/show_user_bet', methods=["GET", "POST"])
def show_user_bet():
    return redirect('/manager_bet')


@app.route('/delete', methods=["GET", "POST"])
def delete():#delete info to database
    bi=request.args.get('bet_id')
    um=request.args.get('user_name')
    bmoney=request.args.get('bet_money')
    delete_bet=Bet.query.filter_by(bet_id=bi).first()
    if delete_bet.win_money == None:
        bm = Register.query.filter_by(username=um).first()
        bm.money = bm.money + int(bmoney)
    db.session.delete(delete_bet)
    db.session.commit()
    return redirect('/show_user_bet')


@app.route('/win_guest', methods=["GET", "POST"])
def win_guest():
    gi=request.args.get('game_id')
    gt=request.args.get('guest_team')
    go=request.args.get('guest_odds')
    win_game = Game.query.filter_by(game_id=gi).first()
    win_game.game_state='over'
    win_game.win_team = gt
    win_bet = Bet.query.filter_by(game_id=gi).all()
    for i in win_bet:
        if (i.bet_team == gt):
            i.win_money = i.bet_money*float(go)
            win_user = Register.query.filter_by(username = i.user_name).first()
            win_user.money = win_user.money+i.bet_money*float(go)
            i.bet_state="./static/image/win.svg"
        else:
            i.win_money = 0
            i.bet_state = "./static/image/lose.svg"
    db.session.commit()
    return redirect('/show_wager')


@app.route('/win_home', methods=["GET", "POST"])
def win_home():
    gi=request.args.get('game_id')
    ht=request.args.get('home_team')
    ho=request.args.get('home_odds')
    win_game = Game.query.filter_by(game_id=gi).first()
    win_game.game_state = 'over'
    win_game.win_team = ht
    win_bet = Bet.query.filter_by(game_id=gi).all()
    for i in win_bet:
        if (i.bet_team == ht):
            i.win_money = i.bet_money * float(ho)
            win_user = Register.query.filter_by(username=i.user_name).first()
            win_user.money = win_user.money + i.bet_money * float(ho)
            i.bet_state = "./static/image/win.svg"
        else:
            i.win_money = 0
            i.bet_state = "./static/image/lose.svg"
    db.session.commit()
    return redirect('/show_wager')


@app.route('/add_wager', methods=["GET", "POST"])
def add_wager():
    if request.method == 'POST':
        game_time = request.form.get("game_time")
        guest_team = request.form.get("guest_team")
        home_team = request.form.get("home_team")
        search = Game.query.all()
        for i in search:
            if i.game_time == game_time and i.guest_team == guest_team and i.home_team == home_team:
                flash("the wager has been existed!")
                return render_template('add_wager.html')
        try:
            wager_info = Game(game_time = request.form.get("game_time"),
            guest_team = request.form.get("guest_team"),
            home_team = request.form.get("home_team"),
            guest_odds = request.form.get("guest_odds"),
            home_odds = request.form.get("home_odds"),
            game_state='can')
            db.session.add(wager_info)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('ERROR!')
            return render_template('add_wager.html')
    return redirect('manager_bet')


if __name__ == '__main__':
    app.run()



