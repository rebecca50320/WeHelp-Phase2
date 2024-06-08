import urllib.request as req
import json
import mysql.connector

## DB connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="mysql123$",
  database= "taipei_day_trip"
)
cursor = mydb.cursor()


## 打開json 
def open_file(file_url):
    with req.urlopen(file_url) as response:
        return json.load(response)

## filter image url
def get_imgURL(file_list):
    splitted_urls = file_list.split("https://")
    img_list = []
    for url in splitted_urls:
        if url[-3:].lower() == "png" or url[-3:].lower() == "jpg":
            #print(url)
            img_list.append("https://"+url)
    return str(img_list)


## 將data存入DB
def import_DB(data):
    sql_command = 'insert into attraction (id,name,category,descrip,address,transport,mrt,lat,lng,image) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    val = (
        data["_id"],
        data["name"],
        data["CAT"],
        data["description"],
        data["address"],
        data["direction"],
        data["MRT"],
        data["latitude"],
        data["longitude"],
        get_imgURL(data["file"])
    )
    cursor.execute(sql_command,val)
    mydb.commit()


## main code

file_url = 'https://raw.githubusercontent.com/rebecca50320/WeHelp-Phase2/main/data/taipei-attractions.json'
attraction_data = open_file(file_url)

for row in attraction_data["result"]["results"]:
    import_DB(row)



