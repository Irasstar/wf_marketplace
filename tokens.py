import requests


class LoginSystem:
    """that class return dictionary with cookies"""

    def getheaders(self):
        """this function connect to site and take mc(account odentificator) and sdcs(login token)
        I call it in exctraktor for login wf.my.com"""
        mc = '29b0ffdf23427b1a9e04d17ba781912218db413234383632'
        sdcs = 'AB7W4QiT6KuYUq5v'
        return {
            'User-Agent': 'Mozilla/5.0 (Windows  NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/66.0.3359.181 Safari/537.36',  # not critical, but better stay here
            'Cookie':
                'mc=' + mc + ';'  # account identificator
                'sdcs=' + sdcs + ';'
        }


class Extractor:
    """this class extract data from wf.my.com"""
# I will need to create container for data transfer. structure {datastatus: '', data: datadict}
# datastatus == 'OK' mean, that all data is accept
    def getdata(self):
# get headers for login wf.my.com
        headers = LoginSystem().getheaders()
# create new session
        session = requests.session()
# url for getting json file with data
        url = 'https://wf.my.com/minigames/marketplace/api/all'
        try:
# try get data
            data = session.get(url, headers=headers)
        except:
#  void data if exception
            data = None
            return data
        session.close()
        if data.json()['state'] == 'Fail':




    # add connection lost unit

    if r.json()['state'] == 'Fail':
        return "E2"  # login error
    tmp = r.json()['data']
    for i in tmp:
        i['year'] = str(datetime.datetime.now().date().year)
        i['month'] = str(datetime.datetime.now().date().month)
        i['day'] = str(datetime.datetime.now().date().day)
        i['hour'] = str(datetime.datetime.now().hour)
        i['min'] = str(datetime.datetime.now().minute)
        if i['item'] != None:
            i['item'] = i['item']['id']
        else:
            i['item'] = 'None'
        if i['class'] == None:
            i['class'] = 'None'
        # print(i)
    return tmp







if __name__ == '__main__':
    login = LoginSystem()
    print(login.getheaders())
