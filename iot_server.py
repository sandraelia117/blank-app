from flask import Flask, request, jsonify

app = Flask(__name__)

iot_data = []

@app.route('/iot', methods=['POST'])
def receive_iot():
    global iot_data
    data = request.json

    data["source"] = "ESP32"
    iot_data.append(data)

    return "OK"

@app.route('/iot-data', methods=['GET'])
def get_iot():
    return jsonify({"data": iot_data})

app.run(host="0.0.0.0", port=5000)