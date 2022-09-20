import sqlite3

def getTopNFromDate(topN, date):
    sqliteConnection = sqlite3.connect('/home/server-goat/Sheep-Detection/sheepRecognition/yolov7-deepsort/goatTracking.db')
    cursor = sqliteConnection.cursor()
    cursor.execute("SELECT * FROM (SELECT * FROM tracker WHERE LOG_TIME LIKE \"" + date + "%\") GROUP BY ID ORDER BY MAX(DURATION) DESC LIMIT " + str(topN) + ";")
    data = cursor.fetchall()
    cursor.close()
    
    return data
