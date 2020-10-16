#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from forms import *
from datetime import datetime
from flask_migrate import Migrate
import itertools
from models import db,Artist,Venue,Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

csrf = CSRFProtect(app)


# lazy initializing database
db.init_app(app)

migrate = Migrate(app,db)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if format == 'full':
      format='%A %B, %d, %Y %I-%M %p'
  elif format == 'medium':
      format="%a %b, %d, %Y %I:%m %p"
  return value.strftime(format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()

  return render_template('pages/home.html',data={
    'artists':artists,
    'artists_count':len(artists),
    'venues':venues,
    'venues_count':len(venues)
  })


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #getting venues grouped by state 
  grouped_venues =  db.session.query(Venue.state).group_by(Venue.state).all()

  #initialize data variable
  areas = []

  #populating the data variables
  for venue in grouped_venues:
    venues = Venue.query.filter(Venue.state==venue[0]).order_by(Venue.id).all()

    # filering upcoming shows
    upcoming_shows = []
    for show in venues[0].shows:
      if(show.start_time > datetime.now()):
        upcoming_shows.append(show)
    city = {
      'city':venues[0].city,
      'state':venues[0].state,
      'venues':venues,
      'upcoming_shows':upcoming_shows,
      'upcoming_shows_count':len(upcoming_shows)
    }
    areas.append(city)

  
  data = {
    "count":len(Venue.query.all()),
    "areas":areas
  }  

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  # data = Venue.query.all()
  return render_template('pages/venues.html', data=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # formatting search keyword for the like operation

  search = "%{}%".format(request.form.get('search_term'))

  # getting the filtered venues relevant to the search keyword
  venues = Venue.query.filter(Venue.name.ilike(search)).all()

  response = {
    "count":len(venues), #getting length of the returned venues
    "data":venues 
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  if(venue is None):
    return render_template("errors/404.html")
  

  upcoming_shows_query = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    show = {
      'artist_id':show.artist_id,
      'artist_name':show.artist.name,
      'artist_image_link':show.artist.image_link,
      'start_time':show.start_time
    }
    upcoming_shows.append(show)

  past_shows_query = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []  

  for show in past_shows_query:
    show = {
      'artist_id':show.artist_id,
      'artist_name':show.artist.name,
      'artist_image_link':show.artist.image_link,
      'start_time':show.start_time
    }
    past_shows.append(show)

  data = {
    'id':venue.id,
    'name':venue.name,
    'genres':venue.genres.split(","),
    'address':venue.address,
    'city':venue.city,
    'state':venue.state,
    'phone':venue.phone,
    'website':venue.website_link,
    'facebook_link':venue.facebook_link,
    'image_link':venue.image_link,
    'seeking_talent':venue.seeking_talent,
    'seeking_description':venue.seeking_description,
    'past_shows':past_shows,
    'past_shows_count':len(past_shows),
    'upcoming_shows':upcoming_shows,
    'upcoming_shows_count':len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():

  
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = VenueForm(request.form)
  if(form.validate()):
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      genres = ",".join(map(str,form.genres.data)) 
    )
    print(venue)
    try:
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      error =True
    finally:
      db.session.close()
    if(error):
      flash('Venue ' + request.form['name'] + ' not listed!')
    else:
      flash('Venue ' + request.form['name'] + ' successfully listed!')
    return redirect(url_for('venues'))
  else:
    return render_template("forms/new_venue.html",form=form)
  
  
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()

  artists_count = len(artists)

  data = {
    "count":artists_count,
    "artists":artists
  }

  return render_template('pages/artists.html', data=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".


  # formatting the search term
  search = "%{}%".format(request.form.get('search_term'))

  # filtering artist with case insensitive formatted search term
  data = Artist.query.filter(Artist.name.ilike(search)).all()

  # making a response object with count key
  response = {
    "count":len(data),
    "data":data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  artist = Artist.query.get(artist_id)
  
  if(artist is None):
    return render_template('errors/404.html')
  
  # query upcoming shows
  upcoming_shows_query = Show.query.join(Artist).join(Venue).filter(Artist.id == artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []

  #query past shows
  past_shows_query = Show.query.join(Artist).join(Venue).filter(Artist.id == artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  #populating the upcoming_show show_data
  for show in upcoming_shows_query:
    show_data = {
      'venue_id':show.venue.id,
      'venue_name':show.venue.name,
      'venue_image_link':show.venue.image_link,
      'start_time':show.start_time}
    upcoming_shows.append(show_data)

  for show in past_shows_query:
    show_data = {
      'venue_id':show.venue.id,
      'venue_name':show.venue.name,
      'venue_image_link':show.venue.image_link,
      'start_time':show.start_time}
    past_shows.append(show_data)

  data = {
    'id':artist.id,
    'name':artist.name,
    'city':artist.city,
    'seeking_venue':False,
    'seeking_description':'',
    'state':artist.state,
    'genres':artist.genres.split(","),
    'phone':artist.phone,
    'website':artist.website_link,
    'image_link':artist.image_link,
    'facebook_link':artist.facebook_link,
    'upcoming_shows':upcoming_shows,
    'upcoming_shows_count':len(upcoming_shows),
    'past_shows':past_shows,
    'past_shows_count':len(past_shows )
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)

  if artist is None:
    return render_template("errors/404.html")
  
  form = ArtistForm(name=artist.name,id=artist.id,
                    genres=artist.genres.split(","),
                    state=artist.state,city=artist.city,
                    phone=artist.phone,facebook_link=artist.facebook_link,
                    image_link=artist.image_link,website_link=artist.website_link)
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form,obj=artist)
  if(form.validate_on_submit()):
     
    form.populate_obj(artist)
    artist.genres = ",".join(map(str,form.genres.data)) 
    
  else:
    return render_template('forms/edit_artist.html', form=form, artist=artist)   

  try:  
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
  
  if(error):
    flash("Unable to edit Artist " + str(artist_id))
  else:
    flash("Artist edited successfully " + str(artist_id))

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)

  if(venue is None):
    return render_template('errors/404.html')
  

  form = VenueForm(
    id = venue.id,
    name = venue.name,
    genres = venue.genres.split(","),
    state = venue.state,
    city = venue.city,
    phone = venue.phone,
    address= venue.address,
    website_link = venue.website_link,
    facebook_link  = venue.facebook_link,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description,
    image_link = venue.image_link
    
    )
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  error = False
  venue = Venue.query.get(venue_id)
  if venue is None:
    return render_template("errors/404.html")
  

  form = VenueForm(request.form,obj=venue)
  if(form.validate()):
    form.populate_obj(venue)
    venue.genres = ",".join(map(str,form.genres.data))
  else:
    return render_template("forms/edit_venue.html",venue=venue,form=form)

  try:
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if(error):
      flash("Unable to update the venue")
  else:
      flash("Venue update Successfully ")

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = ArtistForm(request.form)
  if(form.validate()):
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = ",".join(map(str,form.genres.data)),
      website_link = form.website_link.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data 
    )
    try:
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if(error):
      flash('Unable to add artist!')
    else:
      flash('Artist ' + request.form['name'] + ' successfully listed!')
  else:
    return render_template("forms/new_artist.html",form=form)

  return redirect(url_for("index"))
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # getting all shows joining the venue and artist
  shows = Show.query.join(Venue).join(Artist).all()

  #declaring and initializing the data array
  data = []

  #populating the data array with the relevant data to show
  for show in  shows:
    d = {
      'venue_name':show.venue.name,
      'venue_id':show.venue.id,
      'artist_id':show.artist.id,
      'artist_name':show.artist.name,
      'artist_image_link':show.artist.image_link,
      'start_time':show.start_time
    }
    data.append(d)  

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form)
  if(form.validate()):
    print("form validated")
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    try:
      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if(error):
      flash('An Error Occurred ! Unable to add Show')
    else:
      flash('Show was successfully listed!')  
    return redirect(url_for('index'))  

  else:
    return render_template('forms/new_show.html',form=form)
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
