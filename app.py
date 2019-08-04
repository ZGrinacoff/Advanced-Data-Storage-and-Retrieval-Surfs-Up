# Python script uses flask and SQL alchemy to create API requests for weather data from Honolulu, HI.

# Import dependencies.
import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start_date/end_date/<start_date>/<end_date>/"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON where (Key: date / Value: precipitation)"""

    print("Precipitation API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the most recent date in dataset.
    # Convert to datetime object for calculation below.
    max_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).limit(1).all()
    max_date = max_date[0][0]
    max_date = dt.datetime.strptime(max_date, "%Y-%m-%d")

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = max_date - dt.timedelta(days=366)

    # Perform a query to retrieve the last 12 months of precipitation data.
    precipitations = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
            filter(func.strftime("%Y-%m-%d", Measurement.date) >= year_ago).all()

    # Iterate through precipitations to append all key/values to precipitation dictionary.
    # Append precipitation dictionary to list, then return jsonify. 
    all_precipitations = []
    for date, prcp in precipitations:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON API for all stations in dataset."""

    print("Stations API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations in the dataset.
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Iterate through stations to append all key/values to station dictionary.
    # Append station dictionary to list, then return jsonify. 
    all_stations = []
    for id, station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        
        all_stations.append(station_dict)

    return jsonify(all_stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    """Return JSON API for the dates and temperature observations for a year from the last data point"""

    print("Temp. obs. API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the most recent date in dataset.
    # Convert to datetime object for calculation below.
    max_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).limit(1).all()
    max_date = max_date[0][0]
    max_date = dt.datetime.strptime(max_date, "%Y-%m-%d")

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = max_date - dt.timedelta(days=366)

    # Retrieve temperature observations from all stations for the last year in dataset.
    temperatures = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= year_ago).all()

    # Iterate through temperatures to append all key/values to temperature dictionary.
    # Append temperature dictionary to list, then return jsonify.
    all_temperatures = []
    for station, date, tobs in temperatures:
        temperature_dict = {}
        temperature_dict["station"] = station
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs
        all_temperatures.append(temperature_dict)

    return jsonify(all_temperatures)    

@app.route("/api/v1.0/start/<start>/")
def calc_start_temps(start):
    """Return a JSON API of the minimum temperature, the average temperature, and the max temperature...
    for all dates greater than and equal to the start date."""

    print("Calculate Start Temps. API request received.")
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query will accept start date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for all dates from that date.
    start_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Iterate through start temps to append all key/values to Start (Date) Calc Temp dictionary.
    # Append Start (Date) Calc Temp dictionary to list, then return jsonify.
    start_calc_temps = []
    for result in start_temps:
        start_calc_temp_dict = {}
        start_calc_temp_dict["min_temp."] = result[0]
        start_calc_temp_dict["avg_temp."] = result[1]
        start_calc_temp_dict["max_temp."] = result[2]
        start_calc_temps.append(start_calc_temp_dict)

    return jsonify(start_calc_temps)

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>/")
def calc_temps(start_date, end_date):
    """Return a JSON API of the minimum temperature, the average temperature, and the max temperature...
    for dates between the start and end date inclusive."""

    print("Calculate Start/End Temps. API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query will accept start and end dates in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for all dates in that range.
    start_end_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Iterate through start temps to append all key/values to Start (Date) Calc Temp dictionary.
    # Append Start (Date) Calc Temp dictionary to list, then return jsonify.
    start_end_calc_temps = []
    for result in start_end_temps:
        start_end_calc_temp_dict = {}
        start_end_calc_temp_dict["min_temp."] = result[0]
        start_end_calc_temp_dict["avg_temp."] = result[1]
        start_end_calc_temp_dict["max_temp."] = result[2]
        start_end_calc_temps.append(start_end_calc_temp_dict)

    return jsonify(start_end_calc_temps)

if __name__ == '__main__':
    app.run(debug=True)
