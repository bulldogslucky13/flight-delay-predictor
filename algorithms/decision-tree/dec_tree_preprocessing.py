# Author: DEREK STAHL

from pandas import *
import numpy as np
import matplotlib.pyplot as plt


# function used to calculate entropy of variables
def entropy_calc(series):
    value, counts = np.unique(series, return_counts=True)
    counts = counts / counts.sum()
    return (-counts * np.log2(counts)).sum()


def main_function():

    # read in csv file
    original_airlines = read_csv("flights.csv")
    airlines = original_airlines.sample(n=10000, random_state=45)
    # 31 for training
    # 45 for testing

    # PREPROCESSING-----------------------------------------------------------------------------------------------------

    columns = ['YEAR', 'MONTH',	'DAY',	'DAY_OF_WEEK',	'AIRLINE', 'FLIGHT_NUMBER',	'TAIL_NUMBER',	'ORIGIN_AIRPORT',
               'DESTINATION_AIRPORT',	'SCHEDULED_DEPARTURE', 'DEPARTURE_TIME',	'DEPARTURE_DELAY',	'TAXI_OUT',
               'WHEELS_OFF',	'SCHEDULED_TIME',	'ELAPSED_TIME',	'AIR_TIME', 'DISTANCE',	'WHEELS_ON',	'TAXI_IN',
               'SCHEDULED_ARRIVAL', 'ARRIVAL_TIME',	'ARRIVAL_DELAY',	'DIVERTED',	'CANCELLED',
               'CANCELLATION_REASON',	'AIR_SYSTEM_DELAY',	'SECURITY_DELAY', 'AIRLINE_DELAY',	'LATE_AIRCRAFT_DELAY',
               'WEATHER_DELAY']

    # The year is the same, so we delete this column
    del airlines['YEAR']
    airlines['AIR_SYSTEM_DELAY'].replace(np.nan, 0, inplace=True)
    airlines['SECURITY_DELAY'].replace(np.nan, 0, inplace=True)
    airlines['AIRLINE_DELAY'].replace(np.nan, 0, inplace=True)
    airlines['LATE_AIRCRAFT_DELAY'].replace(np.nan, 0, inplace=True)
    airlines['WEATHER_DELAY'].replace(np.nan, 0, inplace=True)

    delay_list = []
    for ind in airlines.index:
        if type(airlines['CANCELLATION_REASON'][ind]) != float:
            airlines.drop([ind], inplace=True)
            # skip to next line
            continue
        # if no data available about origin airport remove the line
        if type(airlines['ORIGIN_AIRPORT'][ind]) != str:  # or not airlines['ORIGIN_AIRPORT'][ind].isalpha():
            # airlines.drop([ind], inplace=True)
            # skip to the next line
            # continue
            airlines.replace(airlines['ORIGIN_AIRPORT'][ind], str(airlines['ORIGIN_AIRPORT'][ind]), inplace=True)
            airlines.replace(airlines['DESTINATION_AIRPORT'][ind],
                             str(airlines['DESTINATION_AIRPORT'][ind]), inplace=True)


        if airlines['DEPARTURE_DELAY'][ind] > 0:
            delay_list.append(1)
        else:
            delay_list.append(0)


    del airlines['CANCELLED']
    del airlines['CANCELLATION_REASON']
    del airlines['DEPARTURE_DELAY']
    del airlines['ARRIVAL_DELAY']
    print(airlines['ORIGIN_AIRPORT'])
    airlines['DELAYED'] = delay_list
    # drop any rows with missing data
    airlines.dropna(inplace=True)

    del airlines['DIVERTED']



    # plot months and days
    plt.hist(airlines['MONTH'].tolist(), bins=np.arange(14)-0.5, ec='black')
    plt.xlabel('Month')
    plt.ylabel('Frequency')
    plt.title('Flight Occurrences by Month')
    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
               labels=['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', ''])
    plt.show()
    plt.hist(airlines['DAY'].tolist(), bins=np.arange(33)-0.5, ec='black')
    plt.xlabel('Day of Month')
    plt.ylabel('Frequency')
    plt.title('Flight Occurrences by Day of Month')
    plt.show()

    airlines.to_csv('ENDOFPREPROC.csv', sep=',', encoding='utf-8')
    # 'ENDOFPREPROC.csv' for training model

    # END OF PREPROCESSING----------------------------------------------------------------------------------------------


main_function()
