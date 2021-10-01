from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

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
    time_receive = request.form['time_give']
    idx=request.form['idx_give']

    doc = {
        'title': title_receive,
        'content': content_receive,
        'reg_date': time_receive,
        'idx':idx

    }
    db.test2.insert_one(doc)

    return {"result": "success",'msg':'저장완료'}



@app.route('/post', methods=['GET'])
def get_post():
    articles = list(db.test2.find({}, {'_id': False}))

    return {"result": "success","articles":articles}


@app.route('/post', methods=['DELETE'])
def delete_post():
    idx_receive = request.form['idx_give']
    print(idx_receive)
    db.test2.delete_one({'idx': idx_receive})
    return {"result": "success"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
