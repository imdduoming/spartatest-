
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

from datetime import datetime


app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.dbtest


@app.route('/')
def index():
    return render_template('index.html')


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
        'idx':max_value,
        'show':0

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

@app.route('/post', methods=['GET'])
def get_high():
    #조회 수  높은 순대로 정렬
    articles = list(db.test2.find({}, {'_id': False}).sort([("show", -1)]))


    return {"result": "success","articles":articles}


@app.route('/post', methods=['DELETE'])
def delete_post():
    idx = request.args.get('idx')
    print(idx)
    db.test2.delete_one({'idx': int(idx)})

    return {"result":'success',"msg": "삭제되었습니다"}


@app.route('/show', methods=['POST'])
def show_post():
    title_receive = request.form['title_give']

    target_post = db.test2.find_one({'title': title_receive})
    current = target_post['show']

    new_show = current + 1
    print(new_show)

    db.test2.update_one({'title': title_receive}, {'$set': {'show': new_show}})

    return jsonify({'msg': title_receive})

@app.route('/change', methods=['POST'])
def change_post():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    org_title=request.form['org_title']




    db.test2.update_one({'title': org_title}, {'$set': {'title':title_receive ,'content':content_receive}})


    return jsonify({'msg': title_receive})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)