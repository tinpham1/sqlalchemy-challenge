# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, timedelta


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

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

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert query results from precipitation analysis to a dictionary using date as key and prcp as the value.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') - timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .filter(Measurement.date <= most_recent_date[0]).all()

    all_prec_results = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict["date"] = date
        prec_dict["prcp"] = prcp
        all_prec_results.append(prec_dict)
    
    # Return the JSON representation of your dictionary.
    return jsonify(all_prec_results)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    all_station_results = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_station_results.append(station_dict)
    
    return jsonify(all_station_results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') - timedelta(days=365)
    
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    most_active_station_id = most_active_stations[0][0]

    temperature_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id)\
        .filter(Measurement.date >= one_year_ago).all()

    temperatures = [{"date": date,"tobs": tobs} for date, tobs in temperature_data]

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end = None):
    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    if end:
        results = session.query(
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ).filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()
    else:
        results = session.query(
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ).filter(Measurement.date >= start).all()

    temp_data = results[0]
    temp_dict = {
        "start_date": start,
        "end_date": end if end else "Present",
        "TMIN": temp_data[0],
        "TAVG": temp_data[1],
        "TMAX": temp_data[2]
    }

    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)