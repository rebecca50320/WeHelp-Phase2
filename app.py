from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import mysql.connector
import jwt
import datetime

app= FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

## DB connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="mysql123$",
  database= "taipei_day_trip"
)
cursor = mydb.cursor()
SECRET_KEY = 'hihihi'

## functions
def image_url(url_str):
    split = url_str.split("\"")
    url_list = []
    for url in split:
        if "http" in url:
            url_list.append(url)
    return url_list


## APIs for Taipei-Day-Trip
# search attractions by keyword
@app.get("/api/attractions")
async def get_attraction(request: Request,keyword: Optional[str] = Query(None),page: int = 0):
    try:
        page_size = 12
        start = page * page_size
        end = (page+1)*page_size
        if keyword:
            sql_command = 'select * from attraction where name like %s or mrt = %s limit %s offset %s'
            cursor.execute(sql_command,(f'%{keyword}%',keyword,page_size+1,start))
            result = cursor.fetchall()
        else:
            sql_command = 'select * from attraction limit %s offset %s'
            cursor.execute(sql_command,(page_size+1,start))
            result = cursor.fetchall()
        attraction_list = []
        for row in result[:page_size]:
            attraction = {
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "description": row[3],
                "address": row[4],
                "transport": row[5],
                "mrt": row[6],
                "lat": row[7],
                "lng": row[8],
                "images":image_url(row[9])
            }
            attraction_list.append(attraction)
        next_page = page+1 if len(result) > page_size else None
        return {"nextPage":next_page,"data": attraction_list}
    except:
        raise HTTPException(status_code=500, detail="internal error")
    
# search attraction by id
@app.get("/api/attraction/{attractionId}")
async def get_attractionbyID(request: Request,attractionId:int):
    try:
        sql_command = 'select * from attraction where id = %s'
        cursor.execute(sql_command,(attractionId,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="景點編號不正確")
        data = {
            "id": result[0],
            "name": result[1],
            "category": result[2],
            "description": result[3],
            "address": result[4],
            "transport": result[5],
            "mrt": result[6],
            "lat": result[7],
            "lng": result[8],
            "images":image_url(result[9])
        }
        return {"data":data}
    
    except HTTPException as e: #有定義的error
        raise e
    
    except Exception as e: #未定義的error顯示為500
        raise HTTPException(status_code=500, detail="Internal Error")

# 取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序
@app.get("/api/mrts")
async def get_mrt(request:Request):
    try:
        sql_command = 'select mrt,count(*) as cnt from attraction where mrt is not null group by mrt order by cnt desc'
        cursor.execute(sql_command)
        result = cursor.fetchall()
        mrt_list = []
        for station in result:
            mrt_list.append(station[0])
        return {"data":mrt_list}
    
    except Exception as e: #未定義的error顯示為500
        raise HTTPException(status_code=500, detail="Internal Error")

# 新會員註冊
@app.post("/api/user")
async def sign_up(name:str = Form(...),email:str = Form(...), password:str = Form(...)):
    try:
        sql_command = "select count(*) from member where email = %s"
        cursor.execute(sql_command,(email,))
        result = cursor.fetchone()
        if result[0] >0:
            raise HTTPException(status_code=400, detail="此信箱已註冊")
        else:
            sql_command = "insert into member(name,email,password) values(%s,%s,%s)"
            val = (name,email,password)
            cursor.execute(sql_command,val)
            mydb.commit()
            return {"ok":"true"}
        
    except HTTPException as e: #有定義的error
        raise e
    except Exception as e: #未定義的error顯示為500
        raise HTTPException(status_code=500, detail="Internal Error")

# 會員狀態檢查
@app.get("/api/user/auth")
async def check_status():
    pass


# 會員登入
@app.put("/api/user/auth")
async def sign_in(email:str = Form(...), password:str = Form(...)):
    try:
        sql_command = "select count(*) from member where email = %s "
        cursor.execute(sql_command,(email,))
        result = cursor.fetchone()
        if result[0]>0: #有註冊
            sql_command = "select id,name,password from member where email = %s"
            cursor.execute(sql_command,(email,))
            result = cursor.fetchone()
            if result[2] == password:
                id = result[0]
                name = result[1]
                payload = {
                'id': id,
                'name': name,
                'email': email,
                'password': password,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)  # Token expiration time
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                return {"token":token}
            else:
                raise HTTPException(status_code=400, detail="密碼不正確")

        else:
            raise HTTPException(status_code=400, detail="此信箱尚未註冊")
    except HTTPException as e: #有定義的error
        raise e
    except Exception as e: #未定義的error顯示為500
        raise HTTPException(status_code=500, detail="Internal Error")
        
        

    

@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 400:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": exc.detail}
        )
    elif exc.status_code == 500:
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": exc.detail}
        )





###############################################################
# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")