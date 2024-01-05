from flask import Flask, render_template as rt, request
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://PeterFarkas:tEiOltcXCGih8y7U@midstationdb0.8jpo7hd.mongodb.net/?retryWrites=true&w=majority")
db = client['mid-station']
user = dict(db.User.find_one({"email": "a.b@gmail.com"}, {}))
email = user['email']

@app.route('/')
@app.route('/home')
def home():
    return rt('stream.html', settings=enumerate(user['streamSetting']))

@app.route('/stream', defaults={'settingIdx': None})
@app.route('/stream/<int:settingIdx>')
def stream_page(settingIdx=None):
    # get users settings
    user = dict(db.User.find_one({"email": email}, {}))

    # user trying to change current setting
    if settingIdx is not None:

        # resolve new settings (active)
        for idx, setting in enumerate(user['streamSetting']):
            if idx != settingIdx:
                setting['active'] = False
            else:
                if setting['active']:
                    setting['active'] = False
                else:
                    setting['active'] = True

        # update database
        db.User.update_one( { "email": email }, {"$set": {"streamSetting": user['streamSetting']}})
    return rt('stream.html', settings=enumerate(user['streamSetting']))

@app.route('/new-setting', methods=["GET", "POST"])
def createNewSetting():

    # get user
    user = dict(db.User.find_one({"email": email}, {}))
    
    if request.method == "POST":
        title = request.form['stream-title']
        numSettings = len(user['streamSetting'])
        user['streamSetting'].insert(numSettings, {'name': title, 'active': False})
        db.User.update_one( {"email": email}, {"$set": {"streamSetting": user['streamSetting']}})
    return rt('stream.html', settings=enumerate(user['streamSetting']))

@app.route('/edit-setting', methods=["GET", "POST"])
def editSetting():
    # get user
    user = dict(db.User.find_one({"email": email}, {}))

    if request.method == "POST":
        # old_title = # add name of correct setting here
        # title = request.form['stream-title']
        # for setting in user['streamSetting']:
        #     if setting['name'] == old_title:
        #         setting['name'] = title
        
        db.User.update_one( {"email": email}, {"$set": {"streamSetting": user['streamSetting']}})
    
    return rt('stream.html', settings=enumerate(user['streamSetting']))


if __name__ == '__main__':
    app.run()
