from flask import Flask, render_template, request, jsonify, redirect,url_for
app = Flask(__name__)

import jwt
import datetime
import hashlib

import requests
from bs4 import BeautifulSoup

from datetime import datetime, timedelta

from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.enrwf.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.dbsparta
SECRET_KEY = 'sparta'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["user_id"]})
        return redirect(url_for("info"))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))

@app.route('/login')
def login():
        return render_template('login.html')


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    user_id_receive = request.form['user_id_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'user_id': user_id_receive, 'password': pw_hash})


    if result is not None:
        payload = {
         'user_id': user_id_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # .decode('utf-8')
        print(token)
        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    user_id_receive = request.form['user_id_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    print(user_id_receive,password_receive,nickname_receive)
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_id": user_id_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "nickname": nickname_receive                                # 닉네임
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_id_dup', methods=['POST'])
def check_id_dup():
    user_id_receive = request.form['user_id_give']
    print(user_id_receive)
    exists = bool(db.users.find_one({"user_id": user_id_receive}))
    print(exists)
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/check_nickname_dup', methods=['POST'])
def check_nickname_dup():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/main')
def info():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        print("main token_recieved??: ", token_receive)
        hotel_list = list(db.hotel.find({}, {'_id': False}))
        return render_template('main.html', rows=hotel_list)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route("/info", methods=["POST"])
def hotel_post():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        hotel_list = list(db.hotel.find({}, {'_id': False}))
        count = len(hotel_list) + 1
        hotel_image_receive = request.form['url_give']
        hotel_rate_receive = request.form['star_give']
        name_receive = request.form['title_give']
        address_receive = request.form['hotel_address_give']

        doc = {
            'hotel_image':hotel_image_receive,
            'hotel_rate':hotel_rate_receive,
            'name':name_receive,
            'address':address_receive,
            'hotel_id': count
        }
        db.hotel.insert_one(doc)

        return jsonify({'msg':'등록 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route("/info", methods=["GET"])
def hotel_get():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        print("token_recieved??: ", token_receive)
        hotel_list = list(db.hotel.find({}, {'_id': False}))
        return jsonify({'hotels': hotel_list})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/reviews')
def reviews():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        #hotel_id = request.args.get("num")
        #print("hotel_recieved: ",hotel_id)
        print("token_recieved??: ", token_receive)
        return render_template('reviews.html')
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))
    except UnboundLocalError:
        return redirect(url_for("login"))

#reviews
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        hotel_id = request.form["hotel_id_give"]
        print("hotel_recieved: ",hotel_id)
        
        print(token_receive)
        print("token_recieved??: ", token_receive)
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["user_id"]})
        comment_receive = request.form["comment_give"]
        comment_rate = request.form["comment_rate_give"]
        hotel_id = request.form["hotel_id_give"]
        print("comment_receive: ", comment_receive)
        print("comment_rate: ", comment_rate)
        print("hotel_recieved: ",hotel_id)
        doc = {
            "nickname": user_info["nickname"],
            "hotel_id": hotel_id,
            "comment": comment_receive,
            "comment_rate": comment_rate
        }
        db.comment.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))
    except UnboundLocalError:
        return redirect(url_for("login"))


@app.route("/get_posts", methods=['POST'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        hotel_id = request.form["hotel_id_give"]
        # hotel_id = request.args.get("num")
        # print("hotel_id: ", hotel_id)
        print("token_receive",token_receive)
        print("getting1")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.comment.find({'hotel_id': hotel_id}).limit(20))#내림차순 20개 가져오기
        for post in posts:
            post["_id"] = str(post["_id"])#고유값 이것을 항상 스트링으로 변경하기
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['user_id']}))
        print("getting2")
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.","posts":posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print(error)
        return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))
    except UnboundLocalError:
        return redirect(url_for("login"))

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    if token_receive == None:
        return redirect(url_for("login"))
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["user_id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "nickname": user_info["nickname"],
            "type": type_receive
        }
        if action_receive =="like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))
    except KeyError:
        return redirect(url_for("login"))
    except UnboundLocalError:
        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)