from flask import jsonify

def trackerToJson(raw_topN_data, dict_accum_data):
    fullDict = {}
    
    n = 1

    for entity in raw_topN_data:
        trackerDict = {}
        dateDict = {}
        timeDict = {}
        accumTimeDict = {}

        dateString = entity[1]
        timeString = entity[3].split('.')[0]
        accumTimeString = dict_accum_data[entity[2]].split('.')[0]

        dateDict['year'] = dateString[0:4]
        dateDict['month'] = dateString[5:7]
        dateDict['day'] = dateString[8:10]

        timeStringList = timeString.split(':')

        timeDict['hour'] = timeStringList[0]
        timeDict['minute'] = timeStringList[1]
        timeDict['second'] = timeStringList[2]
        timeDict['totalSeconds'] = str(int(timeStringList[0])*3600 + int(timeStringList[1])*60 + int(timeStringList[2]))

        #print('DURATION')
        #print('Hour:',timeDict['hour'], 'Min:', timeDict['minute'], 'Sec:', timeDict['second'])

        accumTimeStringList = accumTimeString.split(':') 

        accumTimeDict['hour'] = accumTimeStringList[0]
        accumTimeDict['minute'] = accumTimeStringList[1]
        accumTimeDict['second'] = accumTimeStringList[2]
        accumTimeDict['totalSeconds'] = str(int(accumTimeStringList[0])*3600 + int(accumTimeStringList[1])*60 + int(accumTimeStringList[2]))

        #print('ACCUM')
        #print('Hour:',accumTimeDict['hour'], 'Min:', accumTimeDict['minute'], 'Sec:', accumTimeDict['second'])


        trackerDict['T_ID'] = entity[0]
        trackerDict['ID'] = entity[2]
        trackerDict['IMG_ID'] = entity[4]
        trackerDict['LOG_TIME'] = dateDict
        trackerDict['DURATION'] = timeDict
        trackerDict['ACCUMULATION'] = accumTimeDict
        fullDict[str(n)] = trackerDict

        n += 1
    
    return jsonify(fullDict)
