from fastapi import FastAPI, Request , Form
from fastapi.templating import Jinja2Templates
import uvicorn
from typing_extensions  import Annotated # 3.8+ pip install python-multipart
# python 3.9+ use "from typing import Annotated"

from sqlalchemy import create_engine
                            # 'DB이름://아이디:비밀번호@IP:포트/데이터베이스'
db_connection = create_engine('mysql://root:1234@127.0.0.1:3306/test')

templates = Jinja2Templates(directory="templates")
app = FastAPI()

@app.get("/")
def hello():
    return {"message": "안녕하세요 fastAPI입니다." }

@app.get("/test")
def test(request: Request):
    print(request)
    return templates.TemplateResponse("test.html", {'request': request,'a':2})

@app.get("/test/{name}")
def get_arg_print(request: Request, name:str):
    print(name)
    return templates.TemplateResponse("test.html", {'request': request})

@app.get("/test_get")
def test_get(request: Request):
    return templates.TemplateResponse("post_test.html", {'request': request})

@app.post("/test_post")
def test_post(name: Annotated[str, Form()], pwd: Annotated[int, Form()]):
    print(name, pwd)


@app.get("/mysqltest")
def mysqltest(request: Request):
    query = db_connection.execute("select * from player")
    result_db = query.fetchall()
    
    result = []
    for data in result_db:
        temp = {'player_id':data[0], 'player_name' : data[1]}
        result.append(temp)
    return templates.TemplateResponse("sqltest.html", {'request': request,'result_table':result})



@app.get("/detail")
def test_post(request: Request, id:str, name:str):
    print(id, name)                                                                                  # sql 쿼리에서 작은따옴표 쿼리문에 넣으니까 넣어줘야 한다!
    query = db_connection.execute("select * from player where player_id = {} and player_name like '{}'".format(id,name))
    result_db = query.fetchall()

    result = []
    for i in result_db:   # i는 ('2012136', '오비나', 'K10', '', '', '', 'MF', 26, '', datetime.date(1990, 6, 3), '1', 169, 70) 들어옴
        temp = {'player_id':i[0],'player_name':i[1],'team_name':i[2],'height':i[-2],'weight':i[-1] }
        result.append(temp)
    return templates.TemplateResponse("detail.html", {'request': request,'result_table':result})

@app.post("/update")
def post_update(request: Request, id:str, name:str, pname: Annotated[str, Form()], tname: Annotated[str, Form()], weight: Annotated[int, Form()], height: Annotated[int, Form()]):

    if pname != '':                                   
        db_connection.execute("update player set player_name = '{}' where player_id = {} and player_name like '{}' ".format(pname,id,name))
        name = pname
    if tname != '': 
        db_connection.execute("update player set team_id = '{}' where player_id = {} and player_name like '{}' ".format(tname,id,name))                                                
    if weight != '':
        query = db_connection.execute("update player set weight = {} where player_id = {} and player_name like '{}' ".format(weight,id,name))                                                      
    if height != '':
        query = db_connection.execute("update player set height = {} where player_id = {} and player_name like '{}' ".format(height,id,name))      

    # 다시불러오기
    query = db_connection.execute("select * from player where player_id = {} and player_name like '{}'".format(id,name))
    result_db = query.fetchall()

    result = []
    for i in result_db:   # i는 ('2012136', '오비나', 'K10', '', '', '', 'MF', 26, '', datetime.date(1990, 6, 3), '1', 169, 70) 들어옴
        temp = {'player_id':i[0],'player_name':i[1],'team_name':i[2],'height':i[-2],'weight':i[-1] }
        result.append(temp)
    return templates.TemplateResponse("detail.html", {'request': request,'result_table':result})



@app.get("/delete")
def deletetest(request: Request, id:str, name:str):
    db_connection.execute("delete from player where player_id = {} and player_name like '{}'".format(id,name))

    # 삭제 후 목록들 다시가져오기
    query = db_connection.execute("select * from player")
    result_db = query.fetchall()

    result = [] 

    for i in result_db:   # i는 ('2012136', '오비나', 'K10', '', '', '', 'MF', 26, '', datetime.date(1990, 6, 3), '1', 169, 70) 들어옴
        temp = {'player_id':i[0],'player_name':i[1] }
        result.append(temp)

    return templates.TemplateResponse('sqltest.html',{'request': request,'result_table':result})


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)