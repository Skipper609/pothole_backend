from flask import Flask, jsonify, request
from flask_cors import CORS
import model as m
import json

app = Flask(__name__)
CORS(app)


@app.route('/data', methods=['POST'])
def predict():
    try:
        body = request.get_json()
        data = body["data"]
        m.predictPotholes(data)        
    except Exception as e:
        pass
    
    
    return jsonify("{Key : true}")

if __name__ == "__main__":
    app.run(debug=True)
