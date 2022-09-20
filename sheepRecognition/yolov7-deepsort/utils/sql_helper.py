import sqlite3
import datetime

def sql_save(logTime, trackID, duration, imgID):
    con = sqlite3.connect('goatTracking.db')
    cursorObj = con.cursor()

    '''
    nowTime = datetime.datetime.now()
    trackID = 4
    duration = datetime.timedelta(seconds=32)
    imgID = 4726
    '''

    logTime = logTime.strftime("%Y/%m/%d, %H:%M:%S")
    logDuration = str(duration)
    cursorObj.execute('create table if not exists tracker(T_ID INTEGER PRIMARY KEY AUTOINCREMENT, LOG_TIME TEXT, ID INT , DURATION TEXT , IMG_ID INT)')
    cursorObj.execute(f"INSERT INTO tracker VALUES(null, '{logTime}', {trackID}, '{logDuration}', {imgID})")
    con.commit()
    con.close()


