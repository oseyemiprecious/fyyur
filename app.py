#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from forms import *
from models import db, Venue, Artist, Show   
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  #recent_artists = Artist.query.order_by(Artist.date_created).limit(10).all()
  #recent_venues = Venue.query.order_by(Venue.date_created).limit(10).all()
  return render_template('pages/home.html')
  
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()
  locations = set()
  for venue in venues:
    locations.add((venue.city, venue.state))
  for location in locations:
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
    })

  for venue in venues:
    for i in data:
      if i['city'] == venue.city and i['state'] == venue.state:
        upcoming_shows = show.query.join(venue).filter(venue.id == venue.id).filter(
          show.show_time > datetime.utcnow()
        )
        i['venues'].append(
          { 'id': venue.id, 'name': venue.name, 'num_upcoming_shows': upcoming_shows_count()}
        )
        break
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searched_term = request.form.get('search_term')
  response = (Venue.query.filter((Venue.city.ilike('%' + searched_term + '%') | Venue.name.ilike('%' + searched_term + '%') | Venue.state.ilike('%' + searched_term + '%'))))

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  upcoming_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time > datetime.utcnow())
  past_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time <= datetime.utcnow())

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():
    add = request.form.get
    try:
      print(request.form.getlist('genres'))
      new_venue = Venue(name=add('name'), city=add('city'), state=add('state'), address=add('address'), phone=add('phone'), genres=request.form.getlist('genres'), website_link=add('website_link'), facebook_link=add('facebook_link'), seeking_talent=form.seeking_talent.data, seeking_description=add('seeking_description'))

      db.session.add(new_venue)
      db.session.commit()
      flash('Venue' + request.form['name'] + 'was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occured. Venue ' + add('name') + 'could not be listed.')
    return redirect(url_for('index'))
  else:
    print(form.errors.items())
    flash('An error occurred with the form')
    return redirect(url_for('index'))
  # TODO: insert form data as a new Venue record in the db, instead
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue {venue.name} has been deleted')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash(f'Venue {venue.name} could not be deleted')
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  searched_term = request.form.get('search_term')
  response = (Artist.query.filter((Artist.city.ilike('%' + searched_term + '%') | Artist.name.ilike('%' + searched_term + '%') | Artist.state.ilike('%' + searched_term + '%'))))

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  upcoming_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time > datetime.utcnow())
  past_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time <= datetime.utcnow())

  return render_template('pages/show_artist.html', artist=artist, upcoming_shows=upcoming_shows, past_shows=past_shows)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.state.data = artist.state
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  if form.validate():
    artist.name = form.name.data
    artist.phone = form.phone.data
    artist.state = form.state.data
    artist.city = form.city.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash(f'An error occurred, please check form and try again')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  if form.validate():
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.image_link = form.image_link.data
    
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

  else:
    flash(f'Check submission and try again')
    return redirect(url_for('show_venue', venue_id=venue_id))
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  add = request.form.get
  form = ArtistForm(request.form)
  if form.validate():
    try:
      new_artist = Artist(name=add('name'), city=add('city'), state=add('state'), phone=add('phone'), website_link=add('website_link'), genres=request.form.getlist('genres'), facebook_link=add('facebook_link'), image_link=add('image_link'), seeking_venue=add('seeking_venue'), seeking_description=add('seeking_description'))
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist' + request.form['name'] + 'was succesfully listed')
      return redirect(url_for('index'))
    except:
      flash('Artist' + request.form['name'] + 'could not be listed')
      return redirect(url_for('index'))
  else:
    flash(f'An error occured, please check form and try again')
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  if form.validate():
    try:
      artist_id = request.form.get('artist_id')
      venue_id = request.form.get('venue_id')
      artist = artist.query.get(venue_id)
      venue_name = venue.query.get(venue_id).name
      show = show(artist_id=artist.id, venue_id=venue_id, show_time=request.form.get('start_time'))
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
      return redirect(url_for('index'))
    except:
      db.session.rollback()
      flash('Show could not be listed, Check submission and try again!')
      return redirect(url_for('index'))
  else:
    flash('An error occurred, check the form and try again')
    return redirect(url_for('index'))

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
