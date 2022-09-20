from flask import jsonify

def trackerToJson(data):
    fullDict = {}
    
    n = 1

    for entity in data:
        trackerDict = {}
        dateDict = {}
        timeDict = {}

        dateString = entity[1]
        timeString = entity[3]

        dateDict['year'] = dateString[0:4]
        dateDict['month'] = dateString[5:7]
        dateDict['day'] = dateString[8:10]

        timeDict['hour'] = timeString[0:1]
        timeDict['minute'] = timeString[2:4]
        timeDict['second'] = timeString[5:7]


        trackerDict['T_ID'] = entity[0]
        trackerDict['ID'] = entity[2]
        trackerDict['IMG_ID'] = entity[4]
        trackerDict['LOG_TIME'] = dateDict
        trackerDict['DURATION'] = timeDict
        fullDict[str(n)] = trackerDict

        n += 1
    
    return jsonify(fullDict)
