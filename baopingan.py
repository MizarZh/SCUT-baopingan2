import requests
from bs4 import BeautifulSoup
import execjs, json, datetime

parameters = [
    'dRptDate', 'sPersonName', 'sPersonCode', 'sPhone', 'sParentPhone',
    'iIsGangAoTai', 'iIsOversea', 'sHomeProvName', 'sHomeProvCode',
    'sHomeCityName', 'sHomeCityCode', 'sHomeCountyName', 'sHomeCountyCode',
    'sHomeAddr', 'iSelfState', 'iFamilyState', 'sNowProvName', 'sNowProvCode',
    'sNowCityName', 'sNowCityCode', 'sNowCountyName', 'sNowCountyCode',
    'sNowAddr', 'iNowGoRisks', 'iRctRisks', 'iRctKey', 'iRctOut',
    'iRctTouchKeyMan', 'iRctTouchBackMan', 'iRctTouchDoubtMan', 'iRptState',
    'iPersonType', 'iSex', 'sCollegeName', 'sCampusName', 'sDormBuild',
    'sDormRoom', 'sMajorName', 'sClassName', 'iInSchool'
]

config = json.load(open('config.json'))

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}
submitHeaders = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=utf-8'
}

url = 'https://enroll.scut.edu.cn/door/health/h5/health.html'
loginPostUrl = 'https://sso.scut.edu.cn/cas/login?service=https://iamok.scut.edu.cn/cas/login'
getDataUrl = 'https://enroll.scut.edu.cn/door/health/h5/get'
postDataUrl = 'https://enroll.scut.edu.cn/door/health/h5/add'

session = requests.Session()
# 登录
req = session.get(url, headers=headers)
soup = BeautifulSoup(req.text, features='lxml')

# 获取验证登录的各个参数值
u = config['account']
p = config['password']
lt = soup.find(id='lt').attrs['value']
with open('./des.js') as f:
    ctx = execjs.compile(f.read())
    rsa = ctx.call('strEnc', u + p + lt, '1', '2', '3')
postData = {
    'rsa': rsa,
    'ul': len(u),
    'pl': len(p),
    'lt': lt,
    'execution': 'e1s1',
    '_eventId': 'submit',
}
loginReq = session.post(loginPostUrl, postData, headers=headers)

# 报平安
today = str(datetime.date.today())

data = json.loads(session.get(getDataUrl, headers=headers).text)['data']
modifiedData = {}
for tables in ('healthRptPerson', 'healthRptInfor', 'basePersonAttr'):
    temp = data[tables]
    for (k, v) in temp.items():
        if k in parameters:
            modifiedData[k] = v

modifiedData['dRptDate'] = today
submitReq = session.post(postDataUrl, modifiedData, headers=submitHeaders)
print(submitReq.text)
