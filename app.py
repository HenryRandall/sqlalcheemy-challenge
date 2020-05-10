# matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import datetime as dt
import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Design a query to retrieve the last 12 months of precipitation data and plot the results
# Find the last data listed in the data
last_date = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).first()
last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
# Calculate the date 1 year ago from the last data point in the database
last_year_date = (last_date - dt.timedelta(days=366))


# Homepage - Define Possible Flask Routes
@app.route("/")
def welcome():
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/[start]<br/>'
        f'/api/v1.0/[start]/[end]'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create Session
    session = Session(engine)

    # Query
    measurements= (Measurement.date, Measurement.prcp)
    prcp_data = session.query(*measurements).\
                filter(Measurement.date >= last_year_date).all()

    # Convert to list of dictionaries to jsonify
    prcp_list = {}

    for date, prcp in prcp_data:
        prcp_list[date] = prcp

    session.close()

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create Session
    session = Session(engine)

    stations = {}

    # Query
    results = session.query(Station.station, Station.name).all()

    # Convert to list of dictionaries to jsonify
    for station,name in results:
        stations[station] = name

    # Close session and display data
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create Session
    session = Session(engine)

    # Query
    tobs_data =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= last_year_date, Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()

    # Convert to list of dictionaries to jsonify
    tobs_list = {}

    for date, tobs in tobs_data:
        tobs_list[date] = tobs

    # Close session and display data
    session.close()
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    # Create Session
    session = Session(engine)

    # Query
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= last_date).all()

    # Convert to list of dictionaries to jsonify
    final={}
    final['Start Date']=start
    final['End Date']=last_date
    for min, avg, max in results:
        final["TMIN"] = min
        final["TAVG"] = avg
        final["TMAX"] = max

    # Close session and display data
    session.close()
    return jsonify(final)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    # Create Session
    session = Session(engine)

    # Query
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert to list of dictionaries to jsonify
    final={}
    final['Start Date']=start
    final['End Date']=end
    for min, avg, max in results:
        final["TMIN"] = min
        final["TAVG"] = avg
        final["TMAX"] = max

    
    session.close()
    return jsonify(final)

if __name__ == "__main__":
    app.run(debug=True)