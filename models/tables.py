from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# define what our database user looks like.
class TripsTable(db.Model):

    __tablename__ = "TripsTable"

    id = db.Column('registration_id', db.Integer, primary_key=True)
    trip = db.Column('goal', db.String(255))
    registered_on = db.Column('registered_on', db.DateTime)

    def __init__(self, trip, registered_on):

        self.trip = trip
        self.registered_on = registered_on