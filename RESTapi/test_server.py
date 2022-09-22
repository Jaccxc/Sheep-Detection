from flask import Flask, request
from flask_cors import CORS
from utils.sql_fetcher import getTopNFromDate
from utils.dataToJson import trackerToJson

app = Flask(__name__)
CORS(app)

@app.route('/TEST', methods=['GET'])
def testServer():
    return 1



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
