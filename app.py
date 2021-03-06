### Step 2- Climate App

#Designing a Flask API based on the queries that we have just developed in climate_starter.,,,:

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd

from flask import Flask, jsonify

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine,reflect=True)

# Assign the demographics class to a variable called `Demographics`
Station = Base.classes.station
Measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home_page():
    return (f"<h1>Welcome to my Home Page</h1><br/>"
            f"<strong>Available Routes:</strong><br/><br/>"
            f"<strong>1- </strong>/api/v1.0/precipitation<br/>"
            f"<strong>2- </strong>/api/v1.0/stations<br/>"
            f"<strong>3- </strong>/api/v1.0/tobs<br/>"
            f"<strong>4- </strong>/api/v1.0/<start>/<end>"  
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp)\
              .filter(Measurement.date >=dt.date(2016,8,23)).all()
              
    session.close()
                
    # Create a dictionary from the results date as keys and prcp as values   
    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp
    return jsonify(prcp_dict)      

@app.route("/api/v1.0/stations")                
def satations():
    
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close() 
    return jsonify(results)

                                      
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    active_stations = pd.DataFrame(session.query(Measurement.station, Measurement.prcp),\
                      columns=['Station','Observation Counts']).groupby('Station').count()\
                     .sort_values('Observation Counts', ascending = False)
    activest_station = active_stations.index[0]
    results = session.query(Measurement.tobs).filter(Measurement.date >= dt.date(2016,8,23))\
             .filter(Measurement.station==activest_station).all()
    session.close()
    return jsonify(results)
                                                       
@app.route("/api/v1.0/<start>/<end>")
def start_end_tobs(start,end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    print(start_date)
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    session = Session(engine)
    date_results = session.query(Measurement.date).all()
    session.close()
    all_dates = [item[0] for item in date_results]
    count = 0
    for date in all_dates: 
        date = dt.datetime.strptime(date, '%Y-%m-%d')
        if date==start_date and count==0:
            count +=1
        if end_date == date and count==1:
            count +=1
    if count == 2 and start_date < end_date: 
        session = Session(engine)
        results = session.query(Measurement.tobs).filter(Measurement.date>=start_date)\
                  .filter(Measurement.date <=end_date)   
        session.close()
        all_temps = [item[0] for item in results]
        TMIN = min(all_temps)
        TMAX = max(all_temps)
        TAVG = sum(all_temps)/len(all_temps)
        temp_info = {"Date":"from "+str(start_date)+" to \n"+str(end_date),
                     "Minimum Temperature": TMIN,
                     "Maximum Temperature": TMAX,
                     "Average Temperature": round(TAVG,2)
                    }
        return jsonify(temp_info)
    return jsonify({"error": f"temperature information from {start_date} to {end_date} not found."}), 404





if __name__ == "__main__":
    app.run(debug = False)


