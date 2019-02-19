import json
"""This module analize current and past price. If it satisfied all conditions - return true.
"""



settings = {
    'moneylimit': 1000, # money limit for spending
    'items': [['gun1', 1234], ['gun2', 4321]]  # items list [<itemname>, <itemid>]
    }


def writepurchasetolog(filename):
    pass


def init_settings_file(filename='itemslist.json'):  # init file structure for
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(itemslist))
        outfile.close()


def read_settings(filename='itemslist.json'):  # read items list for purchasing
    with open(filename, 'r') as outfile:
        data = json.load(outfile)
        outfile.close()
    return data


def ifpurchase(item_id, current_cost, past_cost):  # return true if purchase.
    pass  # need to



if __name__ == '__main__':
    print(read_itemslist())
