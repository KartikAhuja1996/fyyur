
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(250),nullable=True)
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(),nullable=True)
    shows = db.relationship("Show",backref='venue',cascade = "all,delete")
    seeking_talent = db.Column(db.Boolean(),nullable=True)
    seeking_description = db.Column(db.String(500),nullable = True)

    def __repr__(self):
        return f'<Venue {self.seeking_talent} {self.seeking_description} >'


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120),nullable=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship("Show",backref='artist',cascade="all,delete")



class Show(db.Model):
  __tablename__ = "shows"
  id = db.Column(db.Integer,primary_key = True)
  start_time = db.Column(db.DateTime)
  venue_id = db.Column(db.Integer,db.ForeignKey('venues.id'))
  artist_id = db.Column(db.Integer,db.ForeignKey('artists.id'))

# class Album(db.Model):
#     id = db.Column(db.Integer,primary_key=True)
#     name = db.Column(db.String(100))
#     created_at = db.Column(db.DateTime)
#     artist_id = db.Column(db.Integer,db.ForeignKey('artists.id'))
#     songs = db.relationship("Song",backref='album')


# class Song(db.Model):
#     id = db.Column(db.Integer,primary_key = True)
#     name = db.Column(db.String(200))
