from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Flask fonctionne dans Docker!'

@app.route('/healthz')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
