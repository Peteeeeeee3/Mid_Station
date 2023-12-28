from flask import Flask, render_template as rt, request
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://PeterFarkas:tEiOltcXCGih8y7U@midstationdb0.8jpo7hd.mongodb.net/?retryWrites=true&w=majority")
db = client['mid-station']
user = dict(db.User.find_one({"email": "a.b@gmail.com"}, {}))

@app.route('/')
@app.route('/home')
def home():  
    #return rt('home.html')
    return rt('stream.html', settings=enumerate(user['streamSetting']))

@app.route('/stream', methods=['POST', 'GET'])
def stream_page():  
    if request.method == 'POST':
        for idx, status in request.form.items():
            user['streamSetting'][int(idx)]['active'] = True if status=='on' else False
    return rt('stream.html', settings=enumerate(user['streamSetting']))

# @app.route('/set-active-stream', methods=['POST'])
# def setActiveStream():
#     if request.method == 'POST':
#         # middleware logic -> session active


#         # redirect
#         print(request.form['peter'])
#         return 'hello'
#     else:
#         return 'fuckoff' 


if __name__ == '__main__':
    app.run()
