
from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbStock
## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('test1.html')


@app.route('/base/codes',method=['GET'])
def get_group_db():
    #db로부터 group 중복 제거해서 list 만들기
    codes=list(db.codes.find({}).distinct('group'))
    return jsonify(codes)

@app.route('/codes',method=['GET'])
def get_group_value():
    group=request.args.get('group')
    codes = list(db.codes.find({'group':group},{'_id': False}))
    #group을 찾아서 나열
    return jsonify(codes)












if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)
