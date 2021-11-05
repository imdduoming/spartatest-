from datetime import datetime

from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import os


import jwt
import datetime
import hashlib
from datetime import datetime, timedelta
app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.dbStock

SECRET_KEY = 'sooyoung'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index2():
    # return render_template('1page.html')
    token_receive = request.cookies.get('mytoken')
    print(token_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        user_info = db.users.find_one({"username": payload["id"]}, )
        username = user_info['username']
        popular = list(db.sample.find({}, {'_id': False}).sort([("heart_count", -1)]).limit(5))
        print(popular)
        return render_template('index.html', username=username, token=token, places=popular)


    except:
        print('실패')
        return render_template('index.html')

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['userId']
    password_receive = request.form['userPw']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호

    }
    db.users.insert_one(doc)
    return render_template('index.html')

#
# # 아이디 중복확인
# @app.route('/sign_up/check_dup', methods=['POST'])
# def check_dup():
#     username_receive = request.form['username_give']
#     exists = bool(db.users.find_one({"username": username_receive}, {'_id': False}))
#     return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    print(username_receive,password_receive)
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=700)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        username=payload['id']
        return jsonify({'result': 'success', 'token': token,'msg':'로그인이 되었습니다','username':username})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/article', methods=['POST'])
def save_post():
    title = request.form.get('title')
    content = request.form.get('content')
    article_count = db.article.count()
    if article_count == 0:
        max_value = 1
    else:
        max_value = db.article.find_one(sort=[("idx", -1)])['idx'] + 1

    post = {
        'idx': max_value,
        'title': title,
        'content': content,
        'read_count': 0,
        'reg_date': datetime.now()
    }
    db.article.insert_one(post)
    return {"result": "success"}


@app.route('/articles', methods=['GET'])
def get_posts():
    order = request.args.get('order')
    per_page = request.args.get('perPage')
    cur_page = request.args.get('curPage')
    search_title = request.args.get('searchTitle')
    search_condition = {}
    if search_title is not None:
        search_condition = {"title": {"$regex": search_title}}

    limit = int(per_page)
    skip = limit * (int(cur_page) - 1)
    total_count = db.article.find(search_condition).count()
    total_page = int(total_count / limit) + (1 if total_count % limit > 0 else 0)

    if order == "desc":
        articles = list(db.article.find(search_condition, {'_id': False})
                        .sort([("read_count", -1)]).skip(skip).limit(limit))
    else:
        articles = list(db.article.find(search_condition, {'_id': False})
                        .sort([("reg_date", -1)]).skip(skip).limit(limit))

    for a in articles:
        a['reg_date'] = a['reg_date'].strftime('%Y.%m.%d %H:%M:%S')

    paging_info = {
        "totalCount": total_count,
        "totalPage": total_page,
        "perPage": per_page,
        "curPage": cur_page,
        "searchTitle": search_title
    }

    return jsonify({"articles": articles, "pagingInfo": paging_info})


@app.route('/article', methods=['DELETE'])
def delete_post():
    idx = request.args.get('idx')
    db.article.delete_one({'idx': int(idx)})
    return {"result": "success"}


@app.route('/article', methods=['GET'])
def get_post():
    idx = request.args['idx']
    article = db.article.find_one({'idx': int(idx)}, {'_id': False})
    return jsonify({"article": article})


@app.route('/article', methods=['PUT'])
def update_post():
    idx = request.form.get('idx')
    title = request.form.get('title')
    content = request.form.get('content')
    db.article.update_one({'idx': int(idx)}, {'$set': {'title': title, 'content': content}})
    return {"result": "success"}


@app.route('/article/<idx>', methods=['PUT'])
def update_read_count(idx):
    #idx를 찾아 read_count에 1더하기
    db.article.update_one({'idx': int(idx)}, {'$inc': {'read_count': 1}})
    article = db.article.find_one({'idx': int(idx)}, {'_id': False})
    return jsonify({"article": article})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)