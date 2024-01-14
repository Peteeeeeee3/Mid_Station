import pymongo, bson, multiprocessing as Thread, string, random
from flask import Flask, render_template as rt, request, session, redirect
from authlib.integrations.flask_client import OAuth
from PyRTMPServer import SetupServer

DOMAIN = 'http://mid-station.com'
DOMAIN_NO_HTTPS = 'mid-station.com'
STREAM_PAGE_URL_ADDON = '/stream'

app = Flask(__name__)
app.secret_key = "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"
oauth = OAuth(app)

# generate random string to use as stream key
letters = string.ascii_lowercase
g_streamKey = ''.join(random.choice(letters) for i in range(16))


#Register google outh
google = oauth.register(
  name='google',
  server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
  # Collect client_id and client secret from google auth api
  client_id= "47097673803-rkl5o4uk9kr1rsabhjgh109chkkdk3bg.apps.googleusercontent.com",
  client_secret = "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",
  client_kwargs={
    'scope': 'openid email profile'
  }
)

db_client = pymongo.MongoClient("mongodb+srv://PeterFarkas:tEiOltcXCGih8y7U@midstationdb0.8jpo7hd.mongodb.net/?retryWrites=true&w=majority")
db = db_client['mid-station']
g_user = None
g_email = ""

# streaming platform URLs
URL_YOUTUBE = "rtmp://a.rtmp.youtube.com/live2/"
URL_TWITCH = "rtmp://live.twitch.tv/app/"
URL_FACEBOOK = "rtmp://live-api-s.facebook.com:443/rtmp/"

# global variable is stream live
g_isLive = False
thread = None


@app.route('/')
@app.route('/home')
def home():
    return rt('home.html')


@app.route('/stream', defaults={'settingIdx': None})
@app.route('/stream/', defaults={'settingIdx': None})
@app.route('/stream/<int:settingIdx>')
def stream_page(settingIdx=None):
    # get users settings
    user = dict(db.User.find_one({"email": session['email']}, {}))

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
        db.User.update_one( { "email": session['email'] }, {"$set": {"streamSetting": user['streamSetting']}})
        
    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/new-setting', methods=["GET", "POST"])
def createNewSetting():
    # get user
    user = dict(db.User.find_one({"email": session['email']}, {}))

    if request.method == "POST":
        title = request.form['stream-title']
        numSettings = len(user['streamSetting'])
        user['streamSetting'].insert(numSettings, {'name': title, 'active': False, 'streamingPlatforms':[]})
        db.User.update_one( {"email": session['email']}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/edit-setting', methods=["GET", "POST"])
def editSetting():
    # get user
    user = dict(db.User.find_one({"email": session['email']}, {}))

    if request.method == "POST":
        oldTitle = request.form['stream-title-old']
        title = request.form['stream-title']
        for setting in user['streamSetting']:
            if setting['name'] == oldTitle:
                setting['name'] = title
                break
        
        db.User.update_one( {"email": session['email']}, {"$set": {"streamSetting": user['streamSetting']}})
    
    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/delete-setting/<int:settingIdx>')
def deleteSetting(settingIdx):
    user = dict(db.User.find_one({"email": session['email']}, {}))
    
    del user['streamSetting'][settingIdx]     
    db.User.update_one( {"email": session['email']}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/new-target', methods=["GET", "POST"])
def createTarget():
    # get user
    user = dict(db.User.find_one({"email": session['email']}, {}))

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
            return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'])

        for setting in user['streamSetting']:
            if setting['name'] == streamTitle:
                numTargets = len(setting['streamingPlatforms'])
                setting['streamingPlatforms'].insert(numTargets, {'_id': bson.ObjectId(), 'platform': platform, 'URL': url, 'streamKey': streamKey, 'title': title})
                break

        db.User.update_one( {"email": session['email']}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streanKey'])


@app.route('/edit-target', methods=["GET", "POST"])
def editTarget():
    # get user
    user = dict(db.User.find_one({"email": session['email']}, {}))

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
            redirect(DOMAIN + STREAM_PAGE_URL_ADDON)
            return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])

        for setting in user['streamSetting']:
            if setting['name'] == streamTitle:
                for target in setting['streamingPlatforms']:
                    if str(target['_id']) == objectId:
                        target['platform'] = platform
                        target['URL'] = url
                        target['streamKey'] = streamKey
                        target['title'] = title
                        break

        db.User.update_one( {"email": session['email']}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/delete-target/<int:settingIdx>/<targetId>')
def deleteTarget(settingIdx, targetId):
    user = dict(db.User.find_one({"email": session['email']}, {}))
    idx = None
    for i, target in enumerate(user['streamSetting'][settingIdx]['streamingPlatforms']):
        if target['_id'] == bson.ObjectId(targetId):
            idx = i
            del target
            break
    
    if idx == None:
        print("Target Index Error " + targetId)
        return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])
    
    del user['streamSetting'][settingIdx]['streamingPlatforms'][idx]      
    db.User.update_one( {"email": session['email']}, {"$set": {"streamSetting": user['streamSetting']}})

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


def start_stream(email):
    url = ""
    user = dict(db.User.find_one({"email": email}, {}))

    for setting in user['streamSetting']:
        if setting['active']:
            for idx, item in enumerate(setting['streamingPlatforms']):
                if idx < len(setting['streamingPlatforms']) - 1:
                    url = url + item['URL'] + item['streamKey'] + ","
                elif idx == len(setting['streamingPlatforms']) - 1:
                    url = url + item['URL'] + item['streamKey']
    server = SetupServer(url, '0.0.0.0')
    server.GoLive()


@app.route('/stream/live', methods=["GET", "POST"])
def goLive():
    global g_isLive, thread
    user = dict(db.User.find_one({"email": session['email']}, {}))

    if not g_isLive:
        g_isLive = True
        thread = Thread.Process(target=start_stream, args=(session['email'],), daemon=True)
        thread.start()

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/stream/offline', methods=["GET", "POST"])
def goOffline():
    global g_isLive, thread
    user = dict(db.User.find_one({"email": session['email']}, {}))

    if g_isLive:
        g_isLive = False
        session['isLive'] = False
        thread.terminate()
        thread = None

    return rt('stream.html', settings=list(enumerate(user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])

@app.route('/login')
def googleLogin():
    redirect_uri = DOMAIN + '/authorize'
    google = oauth.create_client('google')
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    global g_email
    global g_user

    token = oauth.google.authorize_access_token()
    session['userToken'] = token
    google_user = token['userinfo']
    g_email = google_user['email']
    print("login email: " + g_email)
    g_user = db.User.find_one({"email": g_email}, {})
    
    # create new user 
    if g_user == None:
        userId = bson.ObjectId()
        db.User.insert_one( {'_id': userId, 'email': g_email, 'streamSetting': []})
        g_user = dict(db.User.find_one({"email": g_email}, {}))

    else:
        g_user = dict(g_user)

    session['email'] = g_email
    session['isLive'] = g_isLive
    session['streamKey'] = g_streamKey

    return rt('stream.html', settings=list(enumerate(g_user['streamSetting'])), isLive=session['isLive'], streamKey=session['streamKey'])


@app.route('/logout')
def logout():
    global g_user
    global g_email
    global g_isLive

    if session['isLive']:
        goOffline()

    session.clear()
    g_user = None
    g_email = None
    g_isLive = False
    return redirect(DOMAIN)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
