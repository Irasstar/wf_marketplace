import requests
import datetime
import sqlite3
import time
import json


class WebSystem:

    def __init__(self):
        self.current_login_cookies = []
        self.renew_cookies()

    def get_json(self):
        def add_datetime(json_data):
            """add time parameter to data dict in json file"""
            tmp_datetime = datetime.datetime.now()
            for i in json_data['data']:
                i['datetime'] = str(tmp_datetime)
            return json_data

        def get_data(url='https://wf.my.com/minigames/marketplace/api/all'):  # data file url
            """get data in json format from site wf.my.com"""
            session = requests.session()
            session.cookies = self.current_login_cookies
            response = session.get(url=url)  # get data from site
            if response.status_code is not 200:
                self.renew_cookies()
                requests.utils.add_dict_to_cookiejar(session.cookies, self.load_cookies())
                response = session.get(url=url)
            session.close()
            return response
        #  The code is a variable you need to check status code.
        #  .status_code == 200 mean that json data receive correctly
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

    # change insert parameters
    def buy_item(self, dct):
        sess = requests.session()
        buy_payload = "entity_id=" + str(dct["entity_id"]) + "&cost=" + str(dct["min_cost"]) + "&type=" + dct["type"]
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
        sess.cookies = self.current_login_cookies
        resp = sess.get("https://wf.my.com/minigames/user/info")
        if resp.status_code is not 200:
            self.renew_cookies()
            sess.cookies = self.current_login_cookies
            resp = sess.get("https://wf.my.com/minigames/user/info")
            if resp.status_code is not 200:
                return resp
        mg_token = resp.json()['data']['token']
        sess.get("https://wf.my.com/minigames/bpservices")
        requests.utils.add_dict_to_cookiejar(sess.cookies, {'mg_token': mg_token})
        resp = sess.post(url, data=buy_payload, headers=headers)
        sess.close()
        return resp

    def renew_cookies(self):
        """These function:
         1) get new login cookies from wf.my.com
         2) write(or renew) new cookies to the internal variable current_login_cookies
         3) transform cookiejar to a dict and write to a file
         """
        self.current_login_cookies = self.get_login_cookies()
        cookie_dict = requests.utils.dict_from_cookiejar(self.current_login_cookies)
        js = json.dumps(cookie_dict)
        f = open(r"config\cookies.json", "w")
        f.write(js)
        f.close()

    @staticmethod
    def load_cookies():
        """function load cookie dict from file, convert it to cookiejar and return"""
        f = open(r"config\cookies.json", "r")
        cookie_jar = {}
        requests.utils.add_dict_to_cookiejar(cookie_jar, json.load(f))
        f.close()

        return cookie_jar

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


class SQLInstruments:
    """first of all, i need to change sqlite to mongo database for saving data in json format"""
    def __init__(self, db_file=r'data\mpdatabase.db'):
        self.logfile = r'log\db_log.txt'
        self.connect(db_file)

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def connect(self, db_file):
        self.conn = sqlite3.connect(db_file)
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

    @staticmethod
    def list_to_dict(loaded_list):
        """This function convert data which reading from database like list to dictionary"""
        return {
            'type': loaded_list[1],
            'entity_id': loaded_list[2],
            'title': loaded_list[3],
            'min_cost': loaded_list[4],
            'count': loaded_list[5],
            'item_id': loaded_list[6],
            'kind': loaded_list[7],
            'class': loaded_list[8],
            'datetime': loaded_list[9]
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

    def get_most_tradable_items(self):
        """returns {count of records: ***, item: {item data}}"""
        tables_list = self.get_tables_id_list()
        trade_list = {}
        for table in tables_list:
            count = self.cur.execute("SELECT COUNT(*) FROM id_" + str(table)).fetchone()
            trade_list.update({table: count[0]})
        tpl = sorted(trade_list.items(), key=lambda t: t[1], reverse=True)
        items_list = self.get_all_last_records()
        new_list = []
        for key in tpl:
            new_list.append({'records': key[1], 'item': items_list[key[0]]})
        f = open(r'logs\tradable_items_data.txt', 'w')
        for i in new_list:
            f.write(str(i) + "\n")
        f.close()
        return new_list

    def get_all_last_records(self):
        """data = {'item_id': {data of item with this id}}"""
        items_id = self.get_tables_id_list()
        data = {}
        for i in items_id:
            data.update({i: self.get_last_records(i)[0]})
        return data


class MarketCore:

    @staticmethod
    def fill_db(del_sec=5):
        sql = SQLInstruments()
        ext = WebSystem()
        buy = DataCompare()
        while True:
            input_data = ext.get_json()
            # input_data return None when function doesn't get json file
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
                    if buy.if_buy(dct):
                        ext.buy_item(dct)
                        print("i buy it")
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

    def run_core(self, delay_time):
        # threading.Thread(target=self.fill_db(5)).start()
        self.fill_db(delay_time)


class DataCompare:

    def __init__(self):
        """the part of code will be move to json file"""
        self.buy_dict = {"money_limit": 1000,
                         "items": {"4245": 100,  # sai grai
                                   "3893": 300,  # beretta arx
                                   "4237": 40,  # at308 syndicate
                                   "4215": 40,  # synd mp5a5 custom
                                   "2891": 100,  # ak alfa
                                   "3232": 70,  # Supressor (KRISS Custom)
                                   "3014": 100,  # KRISS Custom
                                   "2832": 70,  # Supressor (AK "Alpha")
                                   "4251": 100,  # Carbon Magpul FMG-9
                                   "3899": 100,  # Syndicate Medic Helmet
                                   "3905": 100,  # Syndicate Shoes
                                   "3233": 70,  # Tactical silencer (KRISS Custom)
                                   "3911": 40,  # Syndicate Sniper Helmet
                                   "3903": 100,  # Syndicate Gloves
                                   "2833": 40,  # Tactical silencer (AK "Alpha")
                                   "4063": 300,  # CDX-MC Kraken
                                   "3913": 100,  # Syndicate Sniper vest
                                   "3895": 100,  # Syndicate Engineer Helmet
                                   "4059": 40,  # Sniper Rifle Scope (Kraken CDX MC)
                                   "3917": 100,  # Syndicate Rifleman Vest
                                   "4061": 100,  # ATACR 4.5x scope (Kraken CDX MC)
                                   "3915": 100,  # Syndicate Rifleman Helmet
                                   "3897": 100,  # Syndicate Engineer Vest
                                   "4253": 100,  # Carbon RPD Custom
                                   "4263": 100,  # Flor de Muerto Skin smg38
                                   "3901": 100,  # Syndicate Medic Vest
                                   "4257": 100,  # Carbon Orsis T-5000
                                   "4065": 100,  # Syndicate Fabarm XLR 5 Prestige
                                   "2975": 40,  # Absolute Desert Eagle
                                   "3919": 100,  # Syndicate Remington MSR
                                   "2985": 40  # kiwi gloves for test
                                   }
                         }

    def __del__(self):
        pass

    @staticmethod
    def load_buy_item_base():
        """The function will be use for load buy config file but now structure of the file is not ready"""
        f = open(r"config\items_base.json", "r")
        # base = json.load(f)
        base = f.read()
        f.close()
        return base

    @staticmethod
    def create_new_item_base(self):
        sql = SQLInstruments()
        data = sql.get_all_last_records()
        js = json.dumps(data)
        f = open(r"config\items_base.json", "w")
        f.write("{")
        for key in data:
            f.write("".join([str(key), ": ", str(data[key]), ", \n"]))
        f.write("}")
        f.close()

    def if_buy(self, web_dict):
        """return True if price is good"""
        if str(web_dict["entity_id"]) in self.buy_dict["items"].keys():  # if id in base
            if self.buy_dict["items"][str(web_dict["entity_id"])] >= web_dict["min_cost"]:  # if price is good
                if self.buy_dict["money_limit"] >= web_dict["min_cost"]:  # if i have money
                    self.buy_dict["money_limit"] -= web_dict["min_cost"]  # reduce money limit
                    return True
        return False


if __name__ == '__main__':
    core = MarketCore()
    core.run_core(1)
    # item = {"entity_id": 2985, "min_cost":40}
    # w = DataCompare()
    # w.if_buy(web_dict=item)
