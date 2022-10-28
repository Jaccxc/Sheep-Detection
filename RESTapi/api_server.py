from flask import Flask, request, send_file
from flask_cors import CORS
from utils.sql_fetcher import getTopNFromDate, getAccumFromTopN
from utils.dataToJson import trackerToJson

app = Flask(__name__)
CORS(app)

@app.route('/getTopN', methods=['GET'])
def getTopNFromDateAPI():
    topN = request.args.get('N')
    date = request.args.get('date')
    raw_topN_data = getTopNFromDate(topN, date)
    #print(raw_topN_data)
    dict_accum_data = getAccumFromTopN(raw_topN_data)
    json_response = trackerToJson(raw_topN_data, dict_accum_data)
    return json_response

@app.route('/getImage', methods=['GET'])
def getImageAPI():
    base = '/mnt/sda/goatData/images/image '
    img_id = request.args.get('IMG_ID')
    return send_file(base+img_id+'.jpg', mimetype='image/jpg')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
