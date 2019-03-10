import requests
import datetime
import sqlite3


class LoginSystem:
    """this class return dictionary with cookies. This class calls in extractor and buy modules"""
    # def login(self):
    #     session = requests.session()
    #     data = {'email': 'valendaanatoli@gmail.com',
    #             'password': 'star4309',
    #             'continue': 'https://account.my.com/login_continue/?with_fb=1&with_tw=1&lang=en_'
    #             'US&client_id=wf.my.com&'
    #                         'continue=https%3A%2F%2Fwf.my.com%2Fen%2F',
    #                         'failure': 'https://account.my.com/login/?with_fb=1&with_tw=1&lang=en_US&client_id='
    #                                    'wf.my.com&continue=https%3A%2F%2Fwf.my.com%2Fen%2F',
    #             'nosavelogin': 0
    #     }
    #     headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #                'Accept-Encoding': 'gzip, deflate, br',
    #                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    #                'Cache-Control': 'max-age=0',
    #                'Connection': 'keep-alive',
    #                'Content-Length': '414',
    #                'Content-Type': 'application/x-www-form-urlencoded',
    #                'Cookie': 'amc_lang=en_US; p=AQAAAHsnBAAA; _ym_uid=1549468471640890375; _ym_d=1549468471; _'
    #                          'fbp=fb.1.1549468471746.939243932; _gcl_au=1.1.440179849.1549520189; _ga='
    #                          'GA1.2.774220765.1550310268; s=dpr=0.800000011920929; ssdc='
    #                          '7750dd29443a4ac3ba0ab6ced7af5042; mrcu=1E445C74D99939689CE86EA47CB2; '
    #                          '_ym_visorc_42397399=w; mr1lad=5c7baa49aada345-0-0-; t_0=1; _ym_isad=2',
    #                'DNT': '1',
    #                'Host': 'auth-ac.my.com',
    #                'Origin': 'https://wf.my.com',
    #                'Referer': 'https://wf.my.com/en/',
    #                'Upgrade-Insecure-Requests': '1',
    #                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                              'Chrome/72.0.3626.119 Safari/537.36'
    #     }
    #     r = session.post('https://auth-ac.my.com/auth', json=data, headers=headers)
    #     session.close()
    #     return r
    #
    # def urllogin(self):
    #     url = 'http://www.someserver.com/auth/login'
    #     values = {'email-email': 'john@example.com',
    #               'password-clear': 'Combination',
    #               'password-password': 'mypassword'}
    #
    #     data = urllib.urlencode(values)
    #     cookies = cookielib.CookieJar()
    #
    #     opener = urllib2.build_opener(
    #         urllib2.HTTPRedirectHandler(),
    #         urllib2.HTTPHandler(debuglevel=0),
    #         urllib2.HTTPSHandler(debuglevel=0),
    #         urllib2.HTTPCookieProcessor(cookies))
    #
    #     response = opener.open(url, data)
    #     the_page = response.read()
    #     http_headers = response.info()

    def get_cookies(self):
        """"""
        # You can get it after login on wf.my.com, than enter https://wf.my.com/minigames/marketplace/api/all
        #  into web browser, press f12 and search ms, sdcs cookies
        self.mc = 'aad830b8600870cfb3e0130bfc036db918db413234383632'
        self.sdcs = 'FA10BDNrjOWH3YpQ'
        tmpdict = {
            'User-Agent': 'Mozilla/5.0 (Windows  NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/66.0.3359.181 Safari/537.36',  # not critical, but better stay here
            'Cookie': 'mc=' + self.mc + '; ' + 'sdcs=' + self.sdcs + ';'  # account identificator
        }
        return tmpdict


class Extractor(LoginSystem):
    """this class extract data from wf.my.com"""
    # I will need to create container for data transfer. structure {datastatus: '', data: datadict}

    def getjson(self):
        def add_datetime(dict):
            """add time parameter to data dict in json file"""
            tmpdate = datetime.datetime.now()
            for i in dict['data']:
                i['datetime'] = str(tmpdate)
            return dict

        def get_data(url = 'https://wf.my.com/minigames/marketplace/api/all'):  # data file url
            """get data in json format from site wf.my.com"""
            session = requests.session()
            # url for getting json file with data
            browser_headers = self.get_cookies()
            data = session.get(url, headers=browser_headers)  # get data from site
            session.close()
            return data
        #  need to add 'status' check !!!
        tmpdate = add_datetime(get_data().json())
        return tmpdate['data']


class data_compare:
    pass


class dbinstruments:
    """first of all, i need to change sqlite to postgree sql for saving full json data"""
    def __init__(self):
        self.dbfile = "data\\mpdatabase.db"
        self.logfile = "log\\log.txt"

    def connect(self):
        self.conn = sqlite3.connect(self.dbfile)
        self.cur = self.conn.cursor()

    def disconnect(self):
        """close with commit"""
        self.conn.commit()
        self.conn.close()

    def read_last_record(self, entity_id):
        self.cur.execute("SELECT * FROM id_" + str(entity_id) + " ORDER BY rec_id DESC LIMIT 1;")
        lst = self.cur.fetchone()
        if lst is not None:
            return self.list_to_dict(lst)
        else:
            return None

    def list_to_dict(self, list):
        """This function convert data which reading from database like list to dictionary"""
        return {
            'type': list[1],
            'entity_id': list[2],
            'title': list[3],
            'min_cost': list[4],
            'count': list[5],
            'item)id': list[6],
            'kind': list[7],
            'class': list[8],
            'datetime': list[9],
            }

    def create_new_table(self, entity_id):
        self.cur.execute("CREATE TABLE IF NOT EXISTS id_" + str(entity_id) + " (rec_id integer PRIMARY KEY, "
                                                                                  "type text, "
                                                                                  "entity_id text, "
                                                                                  "title text, "
                                                                                  "min_cost text, "
                                                                                  "count text, "
                                                                                  "item_id text, "
                                                                                  "kind text, "
                                                                                  "class text, "
                                                                                  "datetime text);")

    def write_data(self, json_data):
        i = json_data
        self.cur.execute("INSERT INTO id_" + str(i['entity_id']) +  # add only if first record on database
                         " (type, entity_id, title, min_cost, count, item_id, kind, class, datetime ) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [i['type'], i['entity_id'], i['title'],
                                                                i['min_cost'], i['count'], i['item_id'], i['kind'],
                                                                i['class'], i['datetime']])

    def fill_database(self, data):
        self.connect()
        for i in data:
            # create new table if not exist
            self.create_new_table(i['entity_id'])
            # read table. Better read last record. Potential slowest place in code
            last_row = self.read_last_record(i['entity_id'])
            # print(db_row[4], ' ', db_row[5])
            if last_row is None:
            # true means that table is empty = > wright all data
                self.write_data(i)
            elif int(last_row['min_cost']) != i['min_cost'] or int(last_row['count']) != i['count']:
            # if table is not empty - add new record only when change price or count of items
                self.write_data(i)
        self.disconnect()

    def read_table(self):
        pass


if __name__ == '__main__':
    db = dbinstruments()
    data = Extractor()
    db.fill_database(data.getjson())
