from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from base64 import b64encode
import requests
import json
from sqlalchemy import or_, desc
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chris:funkytown@192.168.1.106/evesde1'
app.debug = False # disable this in production!
app.config['SECRET_KEY'] = 'super-secret-foolish-fool212'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['POOL_SIZE'] = 100
app.config['MAX_OVERFLOW'] = 0
app.config['ISOLATION_LEVEL'] = 'READ UNCOMMITTED'
app.config['POOL_RECYCLE'] = 3600

db = SQLAlchemy(app)

class forge_market(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    duration = db.Column(db.Integer())
    is_buy_order = db.Column(db.Boolean())
    issued = db.Column(db.DateTime())
    location_id = db.Column(db.String(100))
    min_volume = db.Column(db.Integer())
    order_id = db.Column(db.String(100))
    price = db.Column(db.Numeric())
    range = db.Column(db.String(100))
    system_id = db.Column(db.String(100))
    type_id = db.Column(db.String(100))
    volume_remain = db.Column(db.Integer())
    volume_total = db.Column(db.Integer())

    def __init__(self, dureation, is_buy_order, issued, location_id, min_volume, order_id, price, range, system_id, type_id, volume_remain, volume_total):
        self.duration = dureation
        self.is_buy_order = is_buy_order
        self.issued = issued
        self.location_id = location_id
        self.min_volume = min_volume
        self.order_id = order_id
        self.price = price
        self.range = range
        self.system_id = system_id
        self.type_id = type_id
        self.volume_remain = volume_remain
        self.volume_total = volume_total

def get_marketValue(type_id, queryType):
    marketValue = 0

    if queryType == 'buy': 
        buy_or_sell = "false" 
    else:
        buy_or_sell = "true"

    myQuery = db.session.execute("SELECT ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY price)::numeric, 2) AS median_price FROM forge_market WHERE type_id = '" + str(type_id)+"' AND is_buy_order = '" + buy_or_sell + "';")

    for item in myQuery:
        marketValue = item[0]

    return marketValue
        

def fetch_market_data():
    existing = db.session.query(forge_market).delete()
    db.session.commit()

    myDump = get_market_dump()
    for item in myDump:
        #print item['type_id']
        if item =='error' or item=='timeout':
            print ('Problem fetching market data from EVE.')
            break
        else:
            #print item['location_flag']
            entry = forge_market(item['duration'], item['is_buy_order'], item['issued'], item['location_id'], item['min_volume'], item['order_id'], item['price'], item['range'], item['system_id'], item['type_id'], item['volume_remain'], item['volume_total'])
            db.session.add(entry)
            db.session.commit()

    print('Seccessfully imported market dump for the forge region')
    return 0

def get_market_dump():
    jsonData = []
    listLengthPrev = 0
    listLengthCurrent = 0
    for n in range(1, 300):
        payload = {'datasource':'tranquility', 'order_type':'all', 'page':n}
        response = requests.get('https://esi.evetech.net/latest/markets/10000002/orders', params=payload)
        print ('Dumping market data - page: ' + str(n) + ' - ' + str(response.status_code) )

        jsonData += json.loads(response.text)
        
        listLengthCurrent = len(jsonData)
        if listLengthCurrent > listLengthPrev:
            listLengthPrev = listLengthCurrent
        else:
            break

    return jsonData

if __name__ == '__main__':
    fetch_market_data()