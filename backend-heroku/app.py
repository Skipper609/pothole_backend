from flask import Flask, jsonify, request
from flask_cors import CORS
import model as m
import json
import threading

app = Flask(__name__)
CORS(app)


@app.route('/data', methods=['POST'])
def predict():
    try:
        body = request.get_json()
        data = body["data"]
        threading.Timer(1,m.predictPotholes,args=(data,))
        m.predictPotholes(data)        
        # print(threading.active_count())

    except Exception as e:
        return jsonify("{Key : false}")
    
    return jsonify("{Key : true}")

if __name__ == "__main__":
    m.initialize()
    app.run(debug=True)
