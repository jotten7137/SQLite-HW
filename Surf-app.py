#Dependencies

#numpy for calc
import numpy as np
import pandas as pd

#datetime for real-time analysis
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Flask
import flask
from flask import Flask, jsonify

#Database Engine
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine,reflect=True)

#Classes that automap to each table
Measurement = Base.classes.Measurement
Station = Base.classes.stations

#Session
session = Session(engine)

#-----------------------------------------------#
#Flask setup
app = Flask(__name__)


#Flask Routes
@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )


#Convert the query results to a Dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date="2017-08-23"
    min_date="2016-08-23"
    measurement_date = []
    precip = []

    # Query to retrieve the data and precipitation scores
    for row in session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date<=max_date,Measurement.date>= min_date).all(): #1 year of data
        #print(row)
        measurement_date.append(row[0])
        precip.append(row[1])
    
    #print(measurement_date)
    #print(precip)

    #Query results to Pandas DataFrame and set the index to the date column
    precip_df = pd.DataFrame({'Date':measurement_date,'Precipitation':precip})
    precip_df.set_index('Date',inplace = True)
return jsonify(precip_df)



#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    active_station = np.array(session.query(Measurement.station).all())
    unique_element, counts_elements = np.unique(active_station,return_counts=True)
    #print(unique_element)
    #print(counts_elements)
    #print(np.asarray(unique_element,counts_elements))
    station_count_df = pd.DataFrame({"Station":unique_element,"Count":counts_elements})
    station_count_df.sort_values(by='Count',ascending = False, inplace = True)
    indexed_station = station_count_df.set_index("Station")
return jsonify(indexed_station)



#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs(max_date):
    max_date="2017-08-23"
    min_date="2016-08-23"
    station_high = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date<=max_date,Measurement.date>= min_date).\
                filter(Measurement.station == max_station).all()
    #print(station_high)
    station_high_df = pd.DataFrame(np.array(station_high), columns = (["Date","Temp"]))
    station_high_df.Temp = station_high_df.Temp.astype(float)
    station_high_df.set_index("Date")
return jsonify(station_high_df)
    


#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/start_date")
def temp_start(min_date):
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= min_date).all()
    
    data = []
    for i in results:
        tempstart_dict = {}
        tempstart_dict['Date'] = result[0]
        tempstart_dict['Avg Temp'] = float(result[0])
        tempstart_dict['Max Temp'] = float(result[1])
        tempstart_dict['Min Temp'] = float(result[2])
        data.append(row)
return jsonify(data)



@app.route("/api/v1.0/start_date/end_date")
def temperature(min_date,max_date):
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= min_date,Measurement.date <= max_date).all()
    data = []
    for i in results:
        temp_dict = {}
        temp_dict['Date'] = result[0]
        temp_dict['Avg Temp'] = float(result[0])
        temp_dict['Max Temp'] = float(result[1])
        temp_dict['Min Temp'] = float(result[2])
        data.append(row)
return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)