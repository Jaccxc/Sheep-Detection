from flask import Flask, request
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)