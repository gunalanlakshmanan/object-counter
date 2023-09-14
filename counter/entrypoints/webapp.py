from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

app = Flask(__name__)

count_action = config.get_count_action()
detect_action = config.get_detect_action()


@app.route('/object-count', methods=['POST'])
def object_detection_count():
    uploaded_file = request.files['file']
    threshold = float(request.form.get('threshold', 0.5))
    image = BytesIO()
    uploaded_file.save(image)
    count_response = count_action.execute(image, threshold)
    return jsonify(count_response)


@app.route('/object-detect', methods=['POST'])
def object_detection():
    uploaded_file = request.files['file']
    threshold = float(request.form.get('threshold', 0.5))
    image = BytesIO()
    uploaded_file.save(image)
    detect_response = detect_action.execute(image, threshold)
    return jsonify(detect_response)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
