from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import mysql.connector

app= FastAPI()

## DB connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="mysql123$",
  database= "taipei_day_trip"
)
cursor = mydb.cursor()

## APIs for Taipei-Day-Trip
# search attractions by keyword
@app.get("/attractions")
async def get_attraction(request: Request,keyword: Optional[str] = Query(None),page: int = 0):
	try:
		page_size = 12
		start = page * page_size
		end = (page+1)*page_size
		if keyword:
			sql_command = 'select * from attraction where name like %s or mrt = %s'
			cursor.execute(sql_command,(f'%{keyword}%',keyword))
			result = cursor.fetchall()
		else:
			sql_command = 'select * from attraction'
			cursor.execute(sql_command)
			result = cursor.fetchall()
		attraction_list = []
		for row in result:
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
				"images":row[9]
			}
			attraction_list.append(attraction)
		next_page = page+1 if end < len(attraction_list) else None
		return {"nextPage":next_page,"data": attraction_list[start:end]}
	except:
		raise HTTPException(status_code=500, detail="internal error")
	
# search attraction by id
@app.get("/attraction/{attractionId}")
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
			"images":result[9]
		}
		return {"data":data}
	
	except HTTPException as e: #有定義的error
		raise e
	
	except Exception as e: #未定義的error顯示為500
		raise HTTPException(status_code=500, detail="Internal Error")

# 取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序
@app.get("/mrts")
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






