import requests
import datetime
import sqlite3
import time


def get_data():
    """requests:
	oauth - почитать
    https://wf.my.com/sdc?token=ffa9bfa0fd29d10b79f34ac8e46cdc68
    login realized by cookie.
    https://wf.cdn.gmru.net/static/wf.mail.ru/img/main/items/****.png
    """
    url = 'https://wf.my.com/minigames/marketplace/api/all'
    session = requests.session()
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows  NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/66.0.3359.181 Safari/537.36',  # not critical, but better stay here
        'Cookie':
            'mc=982f30b0311a7c53a3c26c44c877de5318db413234383632;'
            'sdcs=ODPhKeNwWy6j71ZT;'
    }
    try:
        r = session.get(url, headers=browser_headers)  # add exception
        session.close()
    except:
        return "E1"  # connection lost
    # add connection lost unit

    if r.json()['state'] == 'Fail':
        return "E2" #login error
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


def insert_data(db_file, data):
    """add data to database only if current stage has changed"""
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    f = open('log.txt', 'a+', encoding='utf-8')
    for i in data:
        cur.execute("CREATE TABLE IF NOT EXISTS id_" + str(i['entity_id']) + " (rec_id integer PRIMARY KEY, "
                                                                             "type text, "
                                                                             "entity_id text, "
                                                                             "title text, "
                                                                             "min_cost text, "
                                                                             "count text, "
                                                                             "item text, "
                                                                             "kind text, "
                                                                             "class text, "
                                                                             "year text, "
                                                                             "month text, "
                                                                             "day text, "
                                                                             "hour text, "
                                                                             "min text);")
        db_row = cur.execute("SELECT * FROM id_" + str(i['entity_id']) + ";").fetchall()

        # db_cols = cur.execute("SELECT * FROM id_" + str(i['entity_id'])+" WHERE type = 'colomn';").fetchall()
        # print(db_cols)
        if len(db_row) == 0:
            cur.execute("INSERT INTO id_" + str(i['entity_id']) +  # add only if first record on database
                        " (type, entity_id, title, min_cost, count, item, kind, class, year, month, day, hour, min) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        [i['type'], i['entity_id'], i['title'], i['min_cost'], i['count'], i['item'], i['kind'],
                         i['class'], i['year'], i['month'], i['day'], i['hour'], i['min']])
        elif int(db_row[len(db_row) - 1][4]) != i['min_cost'] or int(db_row[len(db_row) - 1][5]) != i['count']:
            cur.execute("INSERT INTO id_" + str(i['entity_id']) +  # add only if first record on database
                        " (type, entity_id, title, min_cost, count, item, kind, class, year, month, day, hour, min) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        [i['type'], i['entity_id'], i['title'], i['min_cost'], i['count'], i['item'], i['kind'],
                         i['class'], i['year'], i['month'], i['day'], i['hour'], i['min']])
            temp = ls2dict(db_row[len(db_row) - 1])
            # print(db_row[len(db_row) - 1])
            
            if int(temp['min_cost']) > int(i['min_cost'])*2:
                print('BINGO!!!')
                f.write('BINGO!!!\n')
            elif int(temp['min_cost']) > int(i['min_cost'])*1.5:
                print('CHECKED 50%')
                f.write('CHECKED 50%\n')
            elif int(temp['min_cost']) > int(i['min_cost'])*1.3:
                print('CHECKED 30%')
                f.write('CHECKED 30%\n')
            print('ttl: ' + temp['title'] + '; cst:' + str(temp['min_cost']) + '; cnt:' + str(
                temp['count']) + '; ' + conv_date(temp))
            print(
                'ttl: ' + i['title'] + '; cst:' + str(i['min_cost']) + '; cnt:' + str(i['count']) + '; ' + conv_date(i))
            f.write('ttl: ' + temp['title'] + 
                '; cst:' + str(temp['min_cost']) + '; cnt:' + str(temp['count']) + '; ' + conv_date(temp)+'\n')
            f.write('ttl: ' + i['title'] + '; cst:' + str(i['min_cost']) + '; cnt:' + str(i['count']) + '; ' + conv_date(i)+'\n')
            

    conn.commit()
    conn.close()
    f.close


def conv_date(data):
    return data['year'] + '.' + data['month'] + '.' + data['day'] + ' ' + data['hour'] + ':' + data['min']


def read_last_data(dbaddr):
    tmp = {}
    conn = sqlite3.connect(dbaddr)
    curr = conn.cursor()
    names = curr.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for name in names:
        tmp = curr.execute("SELECT * FROM " + name[0] + ";").fetchall()
        # print(tmp) #print all records
        print(ls2dict(tmp[len(tmp) - 1]))
    curr.close()


def get_table_names(dbname):
    conn = sqlite3.connect(dbname)
    curr = conn.cursor()
    names = curr.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    curr.close()
    return names


def ls2dict(db_data):
    """convert list data to dictionary"""
    temp = {
        'type': db_data[2],
        'entity_id': db_data[1],
        'title': db_data[3],
        'min_cost': db_data[4],
        'count': db_data[5],
        'item': db_data[6],
        'kind': db_data[7],
        'class': db_data[8],
        'year': db_data[9],
        'month': db_data[10],
        'day': db_data[11],
        'hour': db_data[12],
        'min': db_data[13]
    }
    return temp

	
if __name__ == '__main__':
    addr = "data\\mpdatabase.db"
    # addr = "mpdatabase.db"
    try:
        while True:
            req = get_data()
            if req == "E1" or req == "E2":
                print('GET data error. ')
                if req == "E2":
                    print("Token is end")
                #exit()
                    break
                time.sleep(60)
				
            else:
                insert_data(addr, req)
                time.sleep(5)
            # read_last_data(addr)
    except KeyboardInterrupt:
        print("interrupt")

