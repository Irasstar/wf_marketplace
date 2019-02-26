import requests
import datetime

class LoginSystem:
    """this class return dictionary with cookies. This class calls in extractor and buy modules"""


    def getcookies(self):
        """"""
        # You can get it after login on wf.my.com, than enter https://wf.my.com/minigames/marketplace/api/all
        #  into web browser, press f12 and search ms, sdcs cookies
        mc = 'e12e1300e1fe7ef98f94f9587d394e4618db413234383632'
        sdcs = 'uPDS29c1NlnReAzh'
        tmpdict = {
            'User-Agent': 'Mozilla/5.0 (Windows  NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/66.0.3359.181 Safari/537.36',  # not critical, but better stay here
            'Cookie': 'mc=' + mc + '; ' + 'sdcs=' + sdcs + ';'  # account identificator
        }
        return tmpdict


class Extractor(LoginSystem):
    """this class extract data from wf.my.com"""
    # I will need to create container for data transfer. structure {datastatus: '', data: datadict}

    def getjson(self):
        def add_datetime(dict={}):
            """add time parameter to data dict in json file"""
            tmpdate = datetime.datetime.now()
            for i in dict['data']:
                i['datetime'] = str(tmpdate)
            return dict

        def get_data(url = 'https://wf.my.com/minigames/marketplace/api/all'):
            """get data in json format from site wf.my.com"""
            session = requests.session()
            # url for getting json file with data
            browser_headers = self.getcookies()
            data = session.get(url, headers=browser_headers)  #get data from site
            session.close()
            return data
        #  need to add 'status' check !!!
        tmpdate = add_datetime(get_data().json())
        return tmpdate['data']


if __name__ == '__main__':
    login = Extractor()
    data = login.getjson()

    for i in data:
        print(i['datetime'])
    # date = datetime.datetime.now()
    # print(date)
    # print(date.year)