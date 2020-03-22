from flask import Flask, jsonify, request
from flask_cors import CORS
import model as m
import json

app = Flask(__name__)
CORS(app)


@app.route('/data', methods=['POST'])
def predict():
    # data = request.form["data"]
    if request.method == "POST":
        print(request.form)
    
    # data = body["data"]
    # res = m.predictPotholes(data)
    # return jsonify({"res": res})
    # return jsonify({"res":1})
    return 1

if __name__ == "__main__":
    app.run(debug=True)
