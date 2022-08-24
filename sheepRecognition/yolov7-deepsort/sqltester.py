import sqlite3
import datetime

def sql_save():
    con = sqlite3.connect('goatTracking.db')
    cursorObj = con.cursor()
    nowTime = datetime.datetime.now()
    logTime = nowTime.strftime("%Y/%m/%d, %H:%M:%S")
    trackID = 4
    duration = datetime.timedelta(seconds=32)
    logDuration = str(duration)
    imgID = 4726
    cursorObj.execute('create table if not exists TRACKER(LOG_TIME TEXT PRIMARY KEY NOT NULL, ID INT NOT NULL, DURATION TEXT NOT NULL, IMG_ID INT NOT NULL)')
    cursorObj.execute(f"INSERT INTO TRACKER VALUES('{logTime}', {trackID}, '{logDuration}', {imgID})")
    con.commit()
    con.close()

sql_save()

