import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# create engine to access sqlite
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()

# reflect the database:
Base.prepare(engine, reflect=True)

# create ref to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create a session link
session = Session(engine)

# setup Flask
app = Flask(__name__)


# create welcome route
@app.route('/')
def welcome():
    return (
        '''
    Welcome to the Climate Analysis API!<br>
    Available Routes:<br>
    /api/v1.0/precipitation<br>
    /api/v1.0/stations<br>
    /api/v1.0/tobs<br>
    /api/v1.0/temp/start<br>
    /api/v1.0/temp/start/end<br>
    /api/v1.0/stat/month_num<br>
    ''')


@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp). \
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    # converts results into list
    stations = list(np.ravel(results))
    # this formats list into json
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs). \
        filter(Measurement.station == 'USC00519281'). \
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # query to select the minimum, average, and maximum temperatures from our SQLite database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # In the following code, take note of the asterisk in the query next to the set list.
    # Here the asterisk is used to indicate there will be multiple results for our query:
    # minimum, average, and maximum temperatures.
    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


@app.route("/api/v1.0/stat/<month_num>")
def month_stat(month_num):
    year_sel = [func.min(Measurement.date), func.max(Measurement.date)]
    results = session.query(*year_sel).all()
    # print(f"start:{results[0][0].split('-')[0]}, end:{results[0][1].split('-')[0]}")
    # years = results[0][0].split('-')[0], results[0][1].split('-')[0]
    sel = [Measurement.date, Measurement.prcp, Measurement.tobs, Measurement.station]
    start = f"{results[0][0].split('-')[0]}-{month_num}-01"
    end = f"{results[0][1].split('-')[0]}-{month_num}-30"
    results = session.query(*sel).filter(Measurement.date >= results[0][0].split('-')[0]).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    stats = list(np.ravel(results))
    return jsonify(stats=stats)


# # create a first starting point as a root
# @app.route('/')
# def hello_world():
#     return 'Hello world'
