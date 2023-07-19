# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
# available api routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation Analysis: Precipitation from 23/08/2016 to 23/08/2017."""

    # Query to retrieve the data and precipitation scores
    prcp_scores = session.query(Measurement.date, Measurement.prcp).\
                        filter(Station.station==Measurement.station).\
                        filter(Measurement.date >= '2016-08-23').all()

    # Create a dictionary from the row data and append to a list of prcp_date
    prcp_date = []
    for date, prcp in prcp_scores:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_date.append(prcp_dict)

    # Return the JSON representation of dictionary
    return jsonify(prcp_date)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    """List of all stations."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to retrieve the list of all unique stations
    results = session.query(Station.station).filter(Station.station==Measurement.station).\
            group_by(Station.station).all()

     # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return a JSON list of stations from the dataset
    return jsonify(all_stations)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Temperature Analysis: Temperature of the most active station from 23/08/2016 to 23/08/2017."""

    # Query to retrieve the date and temperature of the most-active station for the previous year of data
    temp_date = session.query(Measurement.date, Measurement.tobs).\
                        filter(Station.station==Measurement.station).\
                        filter(Measurement.date >= '2016-08-23').\
                        filter(Station.station == "USC00519281").all()

    # Create a dictionary from the row data and append to a list of tobs_date
    tobs_date = []
    for date, tobs in temp_date:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_date.append(tobs_dict)

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_date)

# start route
@app.route("/api/v1.0/<start>")
def startroute(start):
    """Min, Max, and Average temperatures calculated from 
       the given start date to the end of the dataset"""

    # Query to retrieve the min, the max and the average from the given start date to the end of dataset
    q_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                        filter(Station.station==Measurement.station).\
                        filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of stats
    stats = []
    for min, max, avg in q_results:
        dict = {}
        dict["TMIN"] = min
        dict["TMAX"] = max
        dict["TAVG"] = avg
        stats.append(dict)

    # Return a JSON list of the min, max and average of temperatures
    return jsonify(stats)

# start end route
@app.route("/api/v1.0/<start>/<end>")
def startendroute(start, end):
    """Min, Max, and Average temperatures calculated from 
       the given start date to the given end date"""

    # Query to retrieve the min, the max and the average from the given start date to the given end date
    q_results_se = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                        filter(Station.station==Measurement.station).\
                        filter((Measurement.date >= start) & (Measurement.date <= end)).all()

    # Create a dictionary from the row data and append to a list of stats_se
    stats_se = []
    for min, max, avg in q_results_se:
        dict_se = {}
        dict_se["TMIN"] = min
        dict_se["TMAX"] = max
        dict_se["TAVG"] = avg
        stats_se.append(dict_se)

    # Return a JSON list of the min, max and average of temperatures
    return jsonify(stats_se)

#Close Session
session.close()

if __name__ == '__main__':
    app.run(debug=True)