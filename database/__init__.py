from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

database = SQLAlchemy()


# Create database Model
class Postt(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(200), nullable=False)
    date_created = database.Column(database.DateTime, default=datetime.utcnow)

    def repr(self):
        return '<Name %r>' % self.id