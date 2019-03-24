import requests
import datetime
import sqlite3
import time
import json

class LoginSystem:

    def renew_cookies(self):
        """function create or rewrite new cookies to json file"""
        # transform cookie jar to dictionary
        cookie_dict = requests.utils.dict_from_cookiejar(self.get_login_cookies())
        js = json.dumps(cookie_dict)
        f = open(r"config\cookies.json", "w")
        f.write(js)
        f.close()

    @staticmethod
    def load_cookies():
        """function load cookie dict from file"""
        f = open(r"config\cookies.json", "r")
        cookie_dict = json.load(f)
        f.close()
        return cookie_dict

    @staticmethod
    def get_login_cookies():
        """function send two request to auth-ac.my.com/auth domain for getting cookies you need to login wf.my.com and
        return that cookies"""
        start_cookies = {
            "ssdc": "cee1a4d23db54820829ccc313f4ef28f",  # any random number with 32 symbols
            "_fbp": "fb.1.1553162178200.1427585602"
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "414",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            # "Host": "auth-ac.my.com",
            "Origin": "https://wf.my.com",
            "Referer": "https://wf.my.com/en/",  # didn't work without referer
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/66.0.3359.181 Safari/537.36"  # not critical, but better stay here
        }
        form_data = "email=valendaanatoli%40gmail.com&password=star4309&continue=https%3A%2F%2Faccount.my.com%2F" \
                    "login_continue%2F%3Fwith_fb%3D1%26with_tw%3D1%26lang%3Den_US%26client_id%3Dwf.my.com%26" \
                    "continue%3Dhttps%253A%252F%252Fwf.my.com%252Fen%252F&failure=https%3A%2F%2Faccount.my.com%2F" \
                    "login%2F%3Fwith_fb%3D1%26with_tw%3D1%26lang%3Den_US%26client_id%3Dwf.my.com%26continue%3D" \
                    "https%253A%252F%252Fwf.my.com%252Fen%252F&nosavelogin=0"
        session = requests.session()
        # add start cookies to session
        requests.utils.add_dict_to_cookiejar(session.cookies, start_cookies)
        session.post(url="https://auth-ac.my.com/auth", data=form_data, headers=headers)
        session.get("https://auth-ac.my.com/sdc?JSONP_call=jQuery1112002970201915748616_1553162182027&"
                    "from=https%3A%2F%2Fwf.my.com%2Fen%2F&_=1553162182028")
        session.close()
        return session.cookies


class Extractor:
    """this class extract data from wf.my.com"""

    def __init__(self):
        login = LoginSystem()
        login.renew_cookies()
        self.dict_cookies = login.load_cookies()

    def get_json(self):
        def add_datetime(json_data):
            """add time parameter to data dict in json file"""
            tmp_date = datetime.datetime.now()
            for i in json_data['data']:
                i['datetime'] = str(tmp_date)
            return json_data

        def get_data(url='https://wf.my.com/minigames/marketplace/api/all'):  # data file url
            """get data in json format from site wf.my.com"""
            session = requests.session()
            requests.utils.add_dict_to_cookiejar(session.cookies, self.dict_cookies)
            response = session.get(url=url)  # get data from site
            session.close()
            return response
        #  code is variable you need to check status code. .status_code == 200 mean that json data receive correctly
        code = get_data()
        if code.status_code == 200:
            tmp_date = add_datetime(code.json())
            return tmp_date['data']
        elif code.status_code == 401:
            print('Login error')
            return None
        else:
            print('Connection error')
            return None


class SQLInstruments:
    """first of all, i need to change sqlite to mongo database for saving data in json format"""
    def __init__(self, dbfile=r'data\mpdatabase.db'):
        self.logfile = r'log\log.txt'
        self.connect(dbfile)

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def connect(self, dbfile):
        self.conn = sqlite3.connect(dbfile)
        self.cur = self.conn.cursor()

    def disconnect(self):
        """close with commit"""
        self.conn.commit()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def get_tables_id_list(self):
        # request return tuple data format
        tuple_list = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        string_list = ['%s' % i for i in tuple_list]  # convert tuple list to string list. data format is id_xxxx
        ids = map(lambda x: x[3:], string_list)  # separate items ID
        return ids

    def get_table_data(self, entity_id):
        self.cur.execute("SELECT * FROM id_" + str(entity_id))
        lst = self.cur.fetchall()
        if lst is not None:
            result = []
            for i in lst:
                result.append(self.list_to_dict(i))  # create list of dict if I request more than one row
            return result
        else:
            return None

    def get_last_records(self, entity_id, rows_count=1):
        """this function return 'row_count' last records in 'entity_id table'"""
        self.cur.execute("SELECT * FROM id_" + str(entity_id) + " ORDER BY rec_id DESC LIMIT " + str(rows_count) + ";")
        lst = self.cur.fetchall()
        if len(lst) != 0:
            result = []
            for i in lst:
                result.append(self.list_to_dict(i))  # create list of dict if I request more than one row
            return result
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
            'item_id': list[6],
            'kind': list[7],
            'class': list[8],
            'datetime': list[9]
            }

    def create_new_table(self, entity_id):
        self.cur.execute("CREATE TABLE IF NOT EXISTS id_" + str(entity_id) + " (rec_id integer PRIMARY KEY, "
                                                                             "type text, "
                                                                             "entity_id text, "
                                                                             "title text, "
                                                                             "min_cost int, "
                                                                             "count int, "
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


class MarketCore:

    def fill_db(self, del_sec):
        sql = SQLInstruments()
        ext = Extractor()
        while True:
            input_data = ext.get_json()
            # none in input_data returns when function didnt get json file
            if input_data is None:
                break
            for dct in input_data:
                # create new table if not exist
                sql.create_new_table(dct['entity_id'])
                # read last record in table
                last_row = sql.get_last_records(dct['entity_id'], 1)
                if last_row is None:
                    # true means that table is empty => add new record
                    sql.write_data(dct)
                elif last_row[0]['min_cost'] != dct['min_cost'] or last_row[0]['count'] != dct['count']:
                    # last_row[0]['min_cost']. row[0] needs bk get_last_records return list of dicts
                    # if table is not empty - add new record only if price or count of items changes
                    sql.write_data(dct)
                    if last_row[0]['min_cost'] > dct['min_cost']*2:
                        print("BINGO!!!")
                    print('ttl: ' + last_row[0]['title'] + '; cst:' + str(last_row[0]['min_cost']) + '; cnt:' +
                          str(last_row[0]['count']) + ' date: ' + last_row[0]['datetime'])
                    print('ttl: ' + dct['title'] + '; cst:' + str(dct['min_cost']) + '; cnt:' +
                          str(dct['count']) + ' date: ' + dct['datetime'])
                    print('')
            sql.commit()
            # break
        time.sleep(del_sec)

    def run_core(self):
        # threading.Thread(target=self.fill_db(5)).start()
        self.fill_db(5)


class DataCompare:

    def __init__(self):
        pass

    def __del__(self):
        pass

    def buy_item(self, entity_id, cost, type):
        """example of input parameters: (2991, 40, inventory)"""
        url = 'https://wf.my.com/minigames/marketplace/api/buy'
        login = LoginSystem()
        dict_cookies = login.load_cookies()
        session = requests.session()
        # url for getting json file with data
        requests.utils.add_dict_to_cookiejar(session.cookies, dict_cookies)
        session.headers.update({'Origin': "https://wf.my.com", 'Referer': "https://wf.my.com/minigames/bpservices"})
        payload = 'entity_id=' + entity_id + '&cost=' + cost + '&type=' + type
        data = session.post(url, data=payload)
        session.close()
        print(data)

    def load_config(self):
        pass

    def save_config(self):
        pass

    def if_buy(self, new_dict, sql_dict):
        """return True if price is good"""
        pass


if __name__ == '__main__':
    sess = requests.session()
    login = LoginSystem()
    login.renew_cookies()
    start_cookies = login.load_cookies()
    buy_pay_load = "entity_id=11&cost=40&type=chest"
    url = "https://wf.my.com/minigames/marketplace/api/buy"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": "37",
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "Origin": "https://wf.my.com",
        "Referer": "https://wf.my.com/minigames/bpservices",  # didn't work without referer
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/71.0.3578.98 Safari/537.36"  # not critical, but better stay here
    }
    requests.utils.add_dict_to_cookiejar(sess.cookies, start_cookies)
    resp = sess.get("https://wf.my.com/minigames/bpservices")
    resp = sess.get("https://wf.my.com/minigames/user/info")
    mg_token = resp.json()['data']['token']
    requests.utils.add_dict_to_cookiejar(sess.cookies, {'mg_token': mg_token})
    resp = sess.post(url, data=buy_pay_load, headers=headers)

    sess.close()

