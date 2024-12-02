# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################

#create engine
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup 
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# 1. (/) - Start at homepage - List available routes.

@app.route('/')
def homepage():
    #"""Homepage listing all the available routes"""
    return (
        
        f"Welcome to the Hawaii Climate App! Available routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start> (enter as /api/v1.0/YYYY-MM-DD)<br>"
        f"/api/v1.0/<start>/<end> (enter as /api/v1.0/YYYY-MM-DD/YYYY-MM-DD)"
    )

# 2. /api/v1.0/precipitation
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    """Return precipitation data for the last 12 months"""
    # Get the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query to retrieve the precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(
    Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    session.close()

    # Convert results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

# 3. /api/v1.0/stations - Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    """Return a JSON list of stations"""
    stations_data = session.query(Station.station, Station.name).all()

    session.close()

    # Create a list of dictionaries with station and name
    stations_list = [{"station": station, "name": name} for station, name in stations_data]

    return jsonify(stations_list)

# 4. /api/v1.0/tobs - Query the dates and temperature observations of the most-active 
# station for the previous year of data. Return a JSON list of temperature observations for the previous year.

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    """Return temperature observations for the most active station in the last 12 months"""
    # Get the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()
    most_active_station_id = most_active_station[0]
    
    # Get the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query to get temperature observations
    temperature_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id)\
        .filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert results to a list of dictionaries
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
    
    return jsonify(temperature_list)

# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum 
# temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates 
# from the start date to the end date, inclusive.

@app.route('/api/v1.0/<start>')
def start_date(start):
    session = Session(engine)

    """Return temperature statistics for the given start date"""
    # Query to calculate the min, avg, and max temperatures from the start date onward
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    session.close()

    # Return as a dictionary
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temperature_stats)


@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    session = Session(engine)

    """Return temperature statistics for the given start and end date"""
    # Query to calculate the min, avg, and max temperatures for the given date range
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Return as a dictionary
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)