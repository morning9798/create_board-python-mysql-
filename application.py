from flask import Flask, render_template, request,redirect,url_for
import pymysql
import sys
from datetime import datetime


app = Flask(__name__)

# 전역변수로 db,cur을 지정하고 계속 사용하려 했으나 에러가 뜸
# db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8") 
# cur = db.cursor()


@app.route('/')   # 127.0.0.1:5000 들어갔을 때 메인 화면
def index():
  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")   # db에 접속하는 부분, db는 스키마를 연결해야 함
  cur = db.cursor()   # cursor 의 줄임말 cur 변수를 db 랑 연결

  # 게시글을 중간에 삭제하면 1,2,3,4 num 순서가 1,3,4 이렇게 변하기 때문에 수정하려 했지만 에러
  # reset = "alter table board auto_increment = 1"
  # cur.execute(reset)
  # cnt = ("0","0")
  # replace = "update board set board.num = %s := %s +1"
  # cur.execute(replace,cnt)

  sql = "select * from board"   # 실행할 sql 문 을 변수에 문자열로 저장
  cur.execute(sql)    # sql 실행

  data_list = cur.fetchall()    # 실행한 sql 문을 리스트 형식으로 data_list의 저장

  db.commit()
  db.close()  # db,cur 를 사용했으면 닫아줘야 충돌이 안나는듯 함
  cur.close()

  # 연결 할 웹페이지 파일명 리턴, list.html 에 data_list 변수를 넘겨주는 부분
  return render_template('list.html',data_list = data_list)


@app.route('/list_search',methods=['POST'])   # 검색값을 받아와서 처리해줄 부분
def list_search():
  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")
  cur = db.cursor()

  # 웹페이지에서 넘어온 값 받아와서 변수에 저장하는 부분
  search_type = request.form["choice_value"]  
  cont = request.form["search"]


  if search_type == "title":  # 제목으로만 검색 할 경우
    sql = "select * from board where title = %s" 
  elif search_type == "cont": # 내용으로만 검색 할 경우
    sql = "select * from board where context = %s" 
  else:                       # 제목과 내용에 포함될 경우
    sql = "select * from board where title or context = %s" 
    

  val = (cont)  # 검색할 내용을 튜플형식의 변수에 저장
  cur.execute(sql,val)
  data_list = cur.fetchall()

  db.close()
  cur.close()

  # 검색한 내용들만 갖고 다시 메인화면에 넘겨줌
  return render_template('list.html',data_list = data_list)



@app.route("/view.html/<int:index>/")   # 게시글 내용을 보는 페이지, 주소창에 정수를 같이 받아오기    예시: 127.0.0.1/view.html/1/ 
def view(index):
  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")
  cur = db.cursor()

  sql = "select * from board where num = %s"  # 테이블의 키값(num) 을 받아와서 해당 내용들을 가져옮
  cur.execute(sql,[index])

  data_list = cur.fetchall()

  db.close()
  cur.close()

  return render_template("view.html", data_list = data_list)



@app.route("/write",methods=['POST','GET'])   # 글쓰기 페이지 부분
def write():
  return render_template("write.html")


@app.route("/write_done",methods=['POST'])  # 글 작성된 값 처리(저장)하는 부분
def write_done():

  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")
  cur = db.cursor()

  # 글 쓰기 페이지에서 넘어온 값 변수에 할당
  title = request.form["jemok"]
  writer = request.form["writer"]
  passwd = request.form["passwd"]
  detail = request.form["detail"]

  # insert 문으로 위에서 select 와는 다르게 한번에 저장하는 방식
  # sql board에 date타입 저장형태에 맞게 datetime모듈을 사용해서 현재시간 저장
  sql = "insert into board (title, writer,date,passwd,context) values('%s','%s','%s','%s','%s')" % (title,writer,datetime.today().strftime("%Y-%m-%d"),passwd,detail)
  cur.execute(sql)

  db.commit()   # insert 등 db 가 수정될 경우 commit을 해서 db에 적용 시켜야함
  db.close()
  cur.close()
  
  return redirect(url_for("index"))   # 끝났으면 redirect,url_for 모듈을 사용하여 메인화면으로


@app.route("/edit/<int:index>/")    # 수정 페이지 부분
def edit(index):

  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")
  cur = db.cursor()

  # 글 내용보는 화면에서랑 똑같이 넘겨온 값 받아서 보여줌
  sql = "select * from board where num = %s"
  cur.execute(sql,[index])

  data_list = cur.fetchall()

  db.close()
  cur.close()

  return render_template("edit.html", data_list = data_list)


# 수정 페이지에서 넘어온 값들 처리하는 부분
@app.route("/edit_done/<int:index>/",methods=['POST'])
def edit_done(index):

  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")
  cur = db.cursor()

  title = request.form["jemok"]
  writer = request.form["writer"]
  passwd = request.form["passwd"]
  detail = request.form["detail"]


  # update 문을 쓰지만 수정되지 않고 추가로 저장되는 에러가 발생
  sql = "update board set (title, writer,date,passwd,context) where num = (index) values('%s','%s','%s','%s','%s','%s')" % (title,writer,datetime.today().strftime("%Y-%m-%d"),passwd,detail,index)

  cur.execute(sql)

  # 해결을 아직 못했으니 임시적으로 기존걸 삭제하는 방법으로 처리 
  # sql = "delete from board where num = %s"
  # cur.execute(sql)

  db.commit()
  db.close()
  cur.close()
  
  return redirect(url_for("index"))


# 삭제버튼 누르면 처리할 부분
@app.route("/edit/<int:index>/del_done/",methods=['POST'])
def del_done(index):
  db = pymysql.connect(host="127.0.0.1", user="root", passwd="12345678", db="notice_board", charset="utf8")
  cur = db.cursor()

  sql = "delete from board where num = %s"
  val = (index)
  cur.execute(sql,val)

  db.commit()
  db.close()
  cur.close()
  
  return redirect(url_for("index"))



if __name__ == '__main__':
  app.run(debug=True)