import sqlite3
import configparser
import datetime
from pytimeparse.timeparse import timeparse

config = configparser.ConfigParser()
config.read('config.ini')
database = config['DATA']['database']

def getTopNFromDate(topN, date):
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    cursor.execute("SELECT * FROM (SELECT * FROM tracker WHERE LOG_TIME LIKE \"" + date + "%\") GROUP BY ID ORDER BY MAX(DURATION) DESC LIMIT " + str(topN) + ";")
    data = cursor.fetchall()
    cursor.close()
    return data

def getAccumFromTopN(raw_topN_data):
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    accum_dict = {}
    print(raw_topN_data)
    
    for entity in raw_topN_data:
            ID = entity[2]
            date = entity[1][0:10]
            cursor.execute("SELECT DURATION FROM (SELECT * FROM tracker WHERE LOG_TIME LIKE \"" + date + "%\") WHERE ID = " + str(ID) + ";")
            duration_list = cursor.fetchall()
            sum_time = datetime.timedelta()
            for data in duration_list:
                parsed = timeparse(data[0])
                parsed_timedelta = datetime.timedelta(seconds=parsed)
                sum_time += parsed_timedelta
                #print(parsed, data[0])
            accum_dict[ID] = str(sum_time)
    
    return accum_dict


    cursor.close()
