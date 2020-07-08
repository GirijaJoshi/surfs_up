from flask import Flask

app = Flask(__name__)

# create a first starting point as a root
@app.route('/')
def hello_world():
    return 'Hello world'
