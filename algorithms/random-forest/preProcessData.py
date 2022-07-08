import pandas as pd

#read flights dataset
flights=pd.read_csv("flights.csv")
print(flights.head(10))

#drop some unrelated attributes
varaibles_to_remove=['YEAR','FLIGHT_NUMBER',
       'TAIL_NUMBER', 'DEPARTURE_TIME', 'TAXI_OUT', 
       'WHEELS_OFF', 'ELAPSED_TIME', 'AIR_TIME',
       'WHEELS_ON', 'TAXI_IN', 'ARRIVAL_TIME', 'DIVERTED', 'CANCELLED', 'CANCELLATION_REASON',
       'AIR_SYSTEM_DELAY', 'SECURITY_DELAY', 'AIRLINE_DELAY','SCHEDULED_TIME','SCHEDULED_ARRIVAL',
       'LATE_AIRCRAFT_DELAY', 'WEATHER_DELAY']
flights.drop(varaibles_to_remove,axis=1,inplace=True)
#read airport dataset
airport=pd.read_csv("airports.csv")

#For airports not listed in airport.csv, treat them as OTHER for simplicity.  
flights.loc[~flights.ORIGIN_AIRPORT.isin(airport.IATA_CODE.values),'ORIGIN_AIRPORT']='OTHER'
flights.loc[~flights.DESTINATION_AIRPORT.isin(airport.IATA_CODE.values),'DESTINATION_AIRPORT']='OTHER'

#because dataset is large enough, we just drop the records with missing values.
flights=flights.dropna()

dataframe=pd.DataFrame(flights)

#Build a dictionary of airport code to integer, each airport's integer value is their index in the file.
#there are totally 322 airpots in the airport file
airport_codes = airport['IATA_CODE']
airport_dict = {'OTHER': 323}
for index,code in enumerate(airport_codes):
    airport_dict[code] = index + 1

#Build a dictionary of airline code to integer, each airline's integer value is their index in the file.  
airlines=pd.read_csv("airlines.csv")
airline_codes = airlines['IATA_CODE']
airline_dict = {}
for index,code in enumerate(airline_codes):
    airline_dict[code] = index + 1
    
#randomly Select 10,000 rows    
sample_data = dataframe.sample(n=10000)  

#change category to numbers.
sample_data["AIRLINE"] = sample_data["AIRLINE"].map(lambda code: airline_dict[code])    
sample_data["ORIGIN_AIRPORT"] = sample_data["ORIGIN_AIRPORT"].map(lambda code: airport_dict[code])    
sample_data["DESTINATION_AIRPORT"] = sample_data["DESTINATION_AIRPORT"].map(lambda code: airport_dict[code])    


#Use Departure delay as class to be predicated, rearrange it to appear as last column
departure_data=sample_data.DEPARTURE_DELAY
data=sample_data.drop("DEPARTURE_DELAY",axis=1)
final_data=pd.concat([data,departure_data],axis=1)  

#change Arrival delay to 1 or 0.
final_data["DEPARTURE_DELAY"] = final_data["DEPARTURE_DELAY"].map(lambda i: 1 if i > 0 else 0)

final_data.to_csv('processed_data.csv', index=False)
    
