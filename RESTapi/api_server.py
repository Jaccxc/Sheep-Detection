from flask import Flask, request, send_file
from flask_cors import CORS
from utils.sql_fetcher import getTopNFromDate
from utils.dataToJson import trackerToJson

app = Flask(__name__)
CORS(app)

@app.route('/getTopN', methods=['GET'])
def getTopNFromDateAPI():
    topN = request.args.get('N')
    date = request.args.get('date')
    raw_data = getTopNFromDate(topN, date)
    json_response = trackerToJson(raw_data)
    return json_response

@app.route('/getImage', methods=['GET'])
def getImageAPI():
    base = '/media/server-goat/GoatData/goatImages/'
    img_id = request.args.get('IMG_ID')
    return send_file(base+img_id+'.jpg', mimetype='image/jpg')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
