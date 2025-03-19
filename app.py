from flask import Flask, render_template, request, jsonify
from runner import running_test_config
import uuid
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run-tests', methods=['POST'])
def run_tests():
    if 'config' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['config']
    config_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.yaml")
    file.save(config_path)

    try:
        results = running_test_config(config_path)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
