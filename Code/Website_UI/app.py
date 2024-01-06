from flask import Flask, render_template as rt, request
import pymongo, bson

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://PeterFarkas:tEiOltcXCGih8y7U@midstationdb0.8jpo7hd.mongodb.net/?retryWrites=true&w=majority")
db = client['mid-station']
user = dict(db.User.find_one({"email": "a.b@gmail.com"}, {}))
email = user['email']

# streaming platform URLs
URL_YOUTUBE = "rtmp://a.rtmp.youtube.com/live2/"
URL_TWITCH = "rtmp://live.twitch.tv/app/"
URL_FACEBOOK = "rtmp://live-api-s.facebook.com:443/rtmp/"

@app.route('/')
@app.route('/home')
def home():
    return rt('home.html', settings=enumerate(user['streamSetting']))

@app.route('/stream', defaults={'settingIdx': None})
@app.route('/stream/', defaults={'settingIdx': None})
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
        
    return rt('stream.html', settings=list(enumerate(user['streamSetting'])))

@app.route('/new-setting', methods=["GET", "POST"])
def createNewSetting():
    # get user
    user = dict(db.User.find_one({"email": email}, {}))
    
    if request.method == "POST":
        title = request.form['stream-title']
        numSettings = len(user['streamSetting'])
        user['streamSetting'].insert(numSettings, {'name': title, 'active': False, 'streamingPlatforms':[]})
        db.User.update_one( {"email": email}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])))

@app.route('/edit-setting', methods=["GET", "POST"])
def editSetting():
    # get user
    user = dict(db.User.find_one({"email": email}, {}))

    if request.method == "POST":
        oldTitle = request.form['stream-title-old']
        title = request.form['stream-title']
        for setting in user['streamSetting']:
            if setting['name'] == oldTitle:
                setting['name'] = title
        
        db.User.update_one( {"email": email}, {"$set": {"streamSetting": user['streamSetting']}})
    
    return rt('stream.html', settings=list(enumerate(user['streamSetting'])))

@app.route('/new-target', methods=["GET", "POST"])
def createTarget():

    # get user
    user = dict(db.User.find_one({"email": email}, {}))

    if request.method == "POST":
        streamTitle = request.form['stream-title']
        title = request.form['target-title']
        platform = request.form['platform']
        streamKey = request.form['stream-key']
        url = ""

        if platform == "YouTube":
            url = URL_YOUTUBE
        elif platform == "Twitch":
            url = URL_TWITCH
        elif platform == "Facebook":
            url = URL_FACEBOOK

        if url == "":
            print("Error in URL")
            return rt('stream.html', settings=list(enumerate(user['streamSetting'])))

        for setting in user['streamSetting']:
            if setting['name'] == streamTitle:
                numTargets = len(setting['streamingPlatforms'])
                setting['streamingPlatforms'].insert(numTargets, {'_id': bson.ObjectId(), 'platform': platform, 'URL': url, 'streamKey': streamKey, 'title': title})

        db.User.update_one( {"email": email}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])))

@app.route('/edit-target', methods=["GET", "POST"])
def editTarget():

    # get user
    user = dict(db.User.find_one({"email": email}, {}))

    if request.method == "POST":
        streamTitle = request.form['stream-title']
        objectId = request.form['object-id']
        title = request.form['target-title']
        platform = request.form['platform']
        streamKey = request.form['stream-key']
        url = ""

        if platform == "YouTube":
            url = URL_YOUTUBE
        elif platform == "Twitch":
            url = URL_TWITCH
        elif platform == "Facebook":
            url = URL_FACEBOOK

        if url == "":
            return rt('stream.html', settings=list(enumerate(user['streamSetting'])))

        for setting in user['streamSetting']:
            if setting['name'] == streamTitle:
                for target in setting['streamingPlatforms']:
                    if str(target['_id']) == objectId:
                        target['platform'] = platform
                        target['URL'] = url
                        target['streamKey'] = streamKey
                        target['title'] = title

        db.User.update_one( {"email": email}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])))


if __name__ == '__main__':
    app.run()
