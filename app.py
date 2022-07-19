from email.mime import base
import numpy as np
import datetime as dt
from datetime import  datetime
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
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate API<br/>"
        f"Avaialbe routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt   &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp Note:Date format yyyy-mm-dd <br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt  &nbsp&nbsp&nbsp  Note:Date format yyyy-mm-dd <br/>"    
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all date and precipitation
    result=dict(session.query(Measurement.date,func.max(Measurement.prcp)).\
        group_by(Measurement.date).all())
    session.close()
    return jsonify(result)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query list of unique stations
    result=session.query(Measurement.station).distinct(Measurement.station).all()
    session.close()
    result = list(np.ravel(result))
    return jsonify(result)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the last year of data.
    lastest_data_date=session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()[0]
    one_year_ago=datetime.strptime(lastest_data_date,'%Y-%m-%d')-dt.timedelta(days=366)
    highest_temp_obs_station_id=session.query(Measurement.station,func.count(Measurement.tobs)).\
        filter(Measurement.date>one_year_ago).\
            group_by(Measurement.station).\
                order_by(func.count(Measurement.tobs).desc()).first()[0]
    result= session.query(Measurement.tobs).\
        filter(Measurement.date>one_year_ago).\
        filter(Measurement.station==highest_temp_obs_station_id).all()
    session.close()
    result = list(np.ravel(result))
    return jsonify(result)

@app.route("/api/v1.0/<start>")
def start_trip(start):
    session = Session(engine)
    try:
        start_date = datetime.strptime(start,'%Y-%m-%d')
    except:
        return jsonify({"error": "Start date is not in the correct format which is yyyy-mm-dd"}),404
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    result = list(np.ravel(result))
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def start_end_trip(start,end):
    session = Session(engine)
    try:
        start_date = datetime.strptime(start,'%Y-%m-%d')
    except:
        return jsonify({"error": f"Start date {start} is not in the correct format which is yyyy-mm-dd"}),404
    try:
        end_date = datetime.strptime(end,'%Y-%m-%d')
    except:
        return jsonify({"error": f"End date {end} is not in the correct format which is yyyy-mm-dd"}),404

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    result = list(np.ravel(result))
    return jsonify(result)

if __name__ == "__main__":
     app.run(debug=False)
