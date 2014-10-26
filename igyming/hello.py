from flask import Flask, render_template, redirect, request
import httplib,json, urlparse, urllib, ConfigParser, os

app = Flask(__name__)

qq_end = {"base_url" : "graph.qq.com",
      "callback_url" : "bigtaro.asuscomm.com:8000%2Fhome",
      "request_token_url" : "",
      "access_token_url" : "",
      "authorize_url" : "",
      "consumer_key" : "101152993",
      "consumer_secret" : "",
      "request_token_params" : "" }

def getAccessToken(authCode):
    headers = {"Content_Type" : "text/html"}
    conn = httplib.HTTPSConnection("graph.qq.com")
    url = "/oauth2.0/token?grant_type=authorization_code&client_id=101152993&client_secret=39e34e7ced96d128c8ecc0f68c705db8&code=" + authCode +"&redirect_uri=www.igyming.com%2Fhome&state=1"
    conn.request("GET", url, '', headers)
    resp = conn.getresponse()
    body = resp.read()
    o = urlparse.parse_qs(body)
    return o['access_token'][0]

def getTaobaoAccessToken(authCode):
    headers = {"Content_Type" : "text/html"}
    conn = httplib.HTTPSConnection("oauth.taobao.com")
    url = "/token?client_id=23028821&client_secret=2dc45d9aaa6de08af22f39d9be3962d6&grant_type=authorization_code&code=" + authCode + "&redirect_uri=www.igyming.com%2Ftaobaohome&state=123"
    conn.request("POST", url, '', headers)
    resp = conn.getresponse()
    body = resp.read()
    oJson = json.loads(body)
    return oJson['access_token']

def getOpenID(accessToken):
    headers = {"Content_Type" : "text/html"}
    conn = httplib.HTTPSConnection("graph.qq.com")
    url = "/oauth2.0/me?access_token=" + accessToken
    conn.request("GET", url, '', headers)
    resp = conn.getresponse()
    body = resp.read()
    if "callback" in body :
        lPos = body.find('(')
        rPos = body.find(')')
        strJson = body[lPos+1:rPos]
        decoded = json.loads(strJson)
        return decoded['openid']
    else:
        return "false"

def getUserInfo(accessToken, openID):
    headers = {"Content_Type" : "text/html"}
    conn = httplib.HTTPSConnection("graph.qq.com")
    url = "/user/get_user_info?access_token=" + accessToken + "&oauth_consumer_key=101152993" + "&openid=" + openID
    conn.request("GET", url, '', headers)
    resp = conn.getresponse()
    body = resp.read()
    decoded = json.loads(body)
    return json.dumps(decoded, sort_keys=True, indent=4)

@app.route("/")
def default():
    return render_template('login.html')

@app.route("/home", methods=['GET'])
def home():
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    accessToken = getAccessToken(code)
    openID = getOpenID(accessToken)
    getUserInfo(accessToken, openID)
    return  render_template('home.html')

@app.route("/taobaohome", methods=['GET'])
def taobaohome():
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    accessToken = getTaobaoAccessToken(code)
    return accessToken

@app.route("/oauth/qq")
def qqlogin():

    currentPath = os.path.dirname(__file__)
    configFilePath = os.path.join(currentPath, 'config.ini')

    cf = ConfigParser.ConfigParser()
    cf.read(configFilePath)
    redirectUri = cf.get('oauth', 'callback_url')

    params = { "response_type" : "code",
              "client_id" : "101152993",
               "state" : "1" }

    params['redirect_uri'] = redirectUri

    query_string = urllib.urlencode(params)
    unparseURL =  urlparse.urlunparse( ( "https", "graph.qq.com", "oauth2.0/authorize", '', query_string, '' ) )
    print  unparseURL
    return redirect(unparseURL)

@app.route("/oauth/taobao")
def tabaoLogin():
    return redirect("https://oauth.taobao.com/authorize?response_type=code&client_id=23028821&redirect_uri=http://www.igyming.com/taobaohome&state=123&view=web")

@app.route("/asus")
def redirectAsus() :
    unparseURL = urlparse.urlunparse( ("http", "bigtaro.asuscomm.com:8000","home", '', request.query_string,'' ) )
    return redirect(unparseURL)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

