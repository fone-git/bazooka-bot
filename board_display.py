from threading import Thread

import flask
from waitress import serve

app = flask.Flask('Board')


@app.route('/')
def home():
    return flask.render_template('board.html', value="world")


def run():
    serve(app, host="0.0.0.0", port=8080)


def display_start():
    Thread(target=run).start()
