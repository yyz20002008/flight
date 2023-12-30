from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy.sql import func
db = SQLAlchemy()
class FlightDB(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DRP_DATETIME =  db.Column(db.Text)
    ARR_DATETIME =  db.Column(db.Text)
    DEP_AIRPORT =   db.Column(db.Text)
    ARR_AIRPORT =   db.Column(db.Text)
    AIRLINE =       db.Column(db.Text)
    FLIGHTNUMBER =  db.Column(db.Text)
    PRICE =         db.Column(db.Text)
    LINK =          db.Column(db.Text)
    CREATEDDATE =   db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    #def __init__(self, DRP_DATETIME, ARR_DATETIME,ARR_AIRPORT, DEP_AIRPORT, AIRLINE,FLIGHTNUMBER,PRICE,LINK,CREATEDDATE):
       
    def __repr__(self):
        return f'<Flight {self.AIRLINE+self.FLIGHTNUMBER}>'