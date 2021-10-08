
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

from datetime import datetime


app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.dbtest


@app.route('/')
def index():
    return render_template('test2.html')


@app.route('/post', methods=['POST'])
def save_post():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']

    post_count = db.test2.count()
    if post_count == 0:
        max_value = 1
    else:
        #idx 역순대로 정렬해서 idx 따온 후 +1
        max_value = db.test2.find_one(sort=[("idx", -1)])['idx'] + 1

    doc = {
        'title': title_receive,
        'content': content_receive,
        'reg_date': datetime.now(),
        'idx':max_value

    }
    db.test2.insert_one(doc)

    return {"result": "success",'msg':'저장완료'}



@app.route('/post', methods=['GET'])
def get_post():
    #날짜 큰 순대로 정렬
    articles = list(db.test2.find({}, {'_id': False}).sort([("reg_date", -1)]))
    for a in articles:
        print(a['reg_date'])
        a['reg_date'] = a['reg_date'].strftime('%Y.%m.%d %H:%M:%S')

    return {"result": "success","articles":articles}


@app.route('/post', methods=['DELETE'])
def delete_post():
    idx = request.args.get('idx')
    print(idx)
    db.test2.delete_one({'idx': int(idx)})

    return {"result":'success',"msg": "삭제되었습니다"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

