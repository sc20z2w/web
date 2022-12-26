from sql import db


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    money = db.Column(db.Integer)


class Game(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    game_time = db.Column(db.String(100), nullable=False)
    guest_team = db.Column(db.String(20), nullable=False)
    home_team = db.Column(db.String(20), nullable=False)
    guest_odds = db.Column(db.Float, nullable=False)
    home_odds = db.Column(db.Float, nullable=False)
    game_state = db.Column(db.String(20), nullable=False)
    win_team = db.Column(db.String(20), nullable=True)


class Bet(db.Model):
    bet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    game_id = db.Column(db.String(20), nullable=False)
    bet_team = db.Column(db.String(20), nullable=False)
    bet_money = db.Column(db.Integer, nullable=False)
    win_money = db.Column(db.Integer, nullable=True)
    bet_state = db.Column(db.String(100), nullable=True)