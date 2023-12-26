from flask import Flask, render_template as rt

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():  # put application's code here
    #return rt('home.html')
    return rt('home.html')


@app.route('/stream')
def stream_page():  # put application's code here
    return rt('stream.html')


if __name__ == '__main__':
    app.run()
