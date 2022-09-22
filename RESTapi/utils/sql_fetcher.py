import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def getTopNFromDate(topN, date):
    sqliteConnection = sqlite3.connect(config['DATA']['database'])
    cursor = sqliteConnection.cursor()
    cursor.execute("SELECT * FROM (SELECT * FROM tracker WHERE LOG_TIME LIKE \"" + date + "%\") GROUP BY ID ORDER BY MAX(DURATION) DESC LIMIT " + str(topN) + ";")
    data = cursor.fetchall()
    cursor.close()
    
    return data
