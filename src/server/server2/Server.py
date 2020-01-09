from flask import Flask

app = Flask(__name__)


@app.route("/", methods=['HEAD'])
def index():
    return "HEAD Test"


if __name__ == '__main__':
    app.run(host='192.168.1.35', port=5000)
