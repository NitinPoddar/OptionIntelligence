from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect

from __init__ import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
class Broker_List(db.Model):
    __tablename__ = 'Broker_List'

    id = db.Column(db.Integer, primary_key=True)
    BrokerName = db.Column(db.String(100),unique=True,nullable=False)
    RootAPI = db.Column(db.Text, nullable=False)
    ServerIP= db.Column(db.Text, nullable=True)
    AuthenticatorReq= db.Column(db.Integer, nullable=True)
    PasswordReq= db.Column(db.Integer, nullable=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #user = db.relationship('User', backref=db.backref('posts', lazy=True))
    __table_args__ = (db.UniqueConstraint('BrokerName'),)
    def __repr__(self):
        return f'<Broker_List {self.title}>'

class AlgoList(db.Model):
    __tablename__ = 'AlgoList'

    id = db.Column(db.Integer, primary_key=True)
    AlgoName = db.Column(db.String(100),unique=True,nullable=False)
    Minimum_Fund_Reqd = db.Column(db.Integer, nullable=False)
    Algo_description = db.Column(db.Text, nullable=False)
    Algo_logic = db.Column(db.Text, nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #user = db.relationship('User', backref=db.backref('posts', lazy=True))
    __table_args__ = (db.UniqueConstraint('AlgoName'),)
    def __repr__(self):
        return f'<AlgoList {self.title}>'

class AlgoRegister(db.Model):
    __tablename__ = 'AlgoRegister'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    algo_name = db.Column(db.Text, db.ForeignKey('AlgoList.AlgoName'), nullable=False)
    broker_name= db.Column(db.Text, db.ForeignKey('Broker_List.BrokerName'), nullable=False)
    BrokerUsername=db.Column(db.Text,nullable=False)
    APIKey=db.Column(db.String(1000))
    SecretKey=db.Column(db.String(1000))
    #User = db.relationship('User', backref=db.backref('AlgoRegister', lazy=True))
    #Algo_List = db.relationship('Post', backref=db.backref('AlgoRegister', lazy=True))
    #Broker_List = db.relationship('Post', backref=db.backref('AlgoRegister', lazy=True))

    def __repr__(self):
        return f'<AlgoRegister {self.text[:20]}...>'

class AlgoStatus(db.Model):
    __tablename__ = 'AlgoStatus'

    id = db.Column(db.Integer, primary_key=True)
    algo_id = db.Column(db.Integer, db.ForeignKey('AlgoRegister.id'), nullable=False)
    algo = db.relationship('AlgoRegister', backref=db.backref('AlgoStatus', uselist=False))
    LotSize=db.Column(db.Integer)
    status = db.Column(db.String(50), nullable=False)
    Profit_Percentage=db.Column(db.Numeric)
    NumberofSubscribers=db.Column(db.Integer)

    def __repr__(self):
        return '<AlgoStatus %r>' % self.status

class InstrumentList(db.Model):
    __tablename__ = 'InstrumentList'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.String(50))
    strike = db.Column(db.Float)
    lotsize = db.Column(db.Integer)
    instrumenttype = db.Column(db.String(50))
    exch_seg = db.Column(db.String(50))
    tick_size = db.Column(db.Float)

    def __repr__(self):
        return f'<InstrumentList {self.symbol}>'

class StatusColorMap(db.Model):
    __tablename__ = 'StatusColorMap'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=False)
    color = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return '<StatusColorMap %r>' % self.status
    
# Define the Condition model
class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    condition_text = db.Column(db.String(200), nullable=False)
    condition_type = db.Column(db.String(10), nullable=False)  # 'entry' or 'exit'
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)

# Define the Option model
class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    algorithm = db.Column(db.String(100), nullable=False)
    num_stocks = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)  # Expiry date of the option
    option_type = db.Column(db.String(10), nullable=False)  # 'Call' or 'Put'
    underlying_index = db.Column(db.String(100), nullable=False)  # Underlying index
    conditions = db.relationship('Condition', backref='option', lazy=True)

    def __repr__(self):
        return f"<Option {self.algorithm}: {self.num_stocks}, Expiry: {self.expiry_date}, Type: {self.option_type}, Index: {self.underlying_index}>"

class AlgorithmLogic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    algorithm = db.Column(db.String(100), nullable=False)
    num_stocks = db.Column(db.Integer, nullable=False)
    instrument_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)
    strike_price = db.Column(db.String(20), nullable=False)
    option_type = db.Column(db.String(10), nullable=False)
    order_type = db.Column(db.String(10), nullable=False)
    entry_condition = db.Column(db.Text, nullable=False)
    exit_condition = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Algorithm {self.instrument_name}>'

class AlgorithmExecution(db.Model):
    __tablename__ = 'algorithm_execution'

    id = db.Column(db.Integer, primary_key=True)
    algo_name = db.Column(db.String, nullable=False)
    num_stocks = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Boolean, nullable=False)  
    trade_type = db.Column(db.String, nullable=False)  # Use 'Buy'/'Sell'
    exectime = db.Column(db.DateTime, nullable=False)
    execprice = db.Column(db.Float, nullable=False)
    LTP=db.Column(db.Float, nullable=False)
    trade_no = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    symbol = db.Column(db.String, nullable=False)

