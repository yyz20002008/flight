from flask import Flask, render_template, request, jsonify,g
from logging import FileHandler,WARNING
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler 
import threading
import os

app = Flask(__name__, template_folder='template')
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
CORS(app)
import json
import time
#import subprocess
#import selenium


from bs4 import BeautifulSoup
import pandas as pd
#from playsound import playsound
import datetime 
import threading
#import pyodbc
import sqlite3


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flightinfo:AVNS_uFUktBnCUch08QtvNFr@app-2ca2e130-4001-4022-8d7a-024072e804f4-do-user-15044933-0.c.db.ondigitalocean.com:25060/flightinfo?sslmode=require'
#'postgresql://username:password@host:port/database_name' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#SQLALCHEMY_TRACK_MODIFICATIONS: A configuration to enable or disable tracking modifications of objects. 
# You set it to False to disable tracking and use less memory.
from models import FlightDB,db
db.init_app(app)
#The special __repr__ function allows you to give each object a string 
# representation to recognize it for debugging purposes.
""" Method 1
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
option = webdriver.ChromeOptions()
option.add_argument("--headless=new")
option.add_argument("--no-sandbox")
#option.add_argument('--ignore-certificate-errors')
#option.add_argument("--test-type")
#options.binary_location = "/usr/bin/chromium"
#option.add_argument('disable-notifications')
driver = webdriver.Chrome(options=option)
"""
""" #Method 2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
service = Service(executable_path='chromedriver.exe')
from selenium.webdriver.chrome.options import Options
option = Options()
option.add_argument("--headless=new")
option.add_argument("--no-sandbox") 
driver = webdriver.Chrome(service=service,options=option)
"""

#use below for DigitalOcean
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
option = Options()
option.add_argument("--headless=new")
option.add_argument("--no-sandbox") 
option.add_argument("--disable-dev-shm-usage")
#option.binary_location = "/usr/bin/google-chrome"
driver = webdriver.Chrome(options=option)




def search_cur_flight(dep,arr,date):
    print(f'''Input: Date:{date},Departure: {dep} - Arrival: {arr}''')
    temp_url = 'https://www.google.com/travel/flights?q=Flights%20from%20' #这里可以替换成任何你想搜的航班的google flight url

    base_url = temp_url + dep+'%20to%20'+arr+'%20on%20'+str(date)+'%20one%20way%20non%20stop'
    
    #https://www.google.com/travel/flights?q=Flights%20from%20sfo%20to%20shanghai%20on%202023-11-25%20one%20way%20non%20stop
    #business class can be add
    # roundtrip use https://www.google.com/travel/flights?q=Flights%20to%20SFO%20from%20HNL%20on%202022-09-13%20through%202022-09-17
    
    df_record = pd.DataFrame(columns=['出发时间','到达时间','始发机场','到达机场',
                                     '航空公司' ,'航班号','票价','官网购票链接'])  
    print("before webdriver.ChromeOptions()")
   
    my_url = base_url#.replace('2023-11-18', my_date) #前面的日期是你base_url里面的日期
    driver.get(my_url)
   
    #time.sleep(5) # set the time to wait till web fully loaded
    
    # wait for the close button to be visible and click it
    try:
        close_button = driver.find_element(By.XPATH, '//div[@class="I0Kcef"]')
        close_button.click()
    except:
        print("close is not found.")
    
    elem = driver.find_element("xpath","//*")
    source_code = elem.get_attribute("outerHTML")
    bs = BeautifulSoup(source_code, 'html.parser')
    
    #expand 
    drawing_url = bs.find_all('button', class_='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe LQeN7 nJawce OTelKf XPGpHc mAozAc')
    print(len(drawing_url))
    if len(drawing_url)==0: return
    else: print(base_url)
    
    for i in  range(len(drawing_url)):
        driver.find_element(By.XPATH, '//button[@class="VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe LQeN7 nJawce OTelKf XPGpHc mAozAc"]').click()
        #driver.execute_script('arguments[0].click()', button)
        time.sleep(1)
    
    elem = driver.find_element("xpath","//*")
    source_code = elem.get_attribute("outerHTML")
    
    new_bs = BeautifulSoup(source_code, 'lxml')
    flights = new_bs.find_all('li', class_ = 'pIav2d')
    for cur_flight in flights:
        #print(cur_flight)
        f_times = cur_flight.find_all('span', class_ = 'eoY5cb')
        d_time = f_times[0].text
        a_time = f_times[1].text
        
        carrier = cur_flight.find('span', class_ = 'Xsgmwe').text
        flightNum = cur_flight.find('span', class_ = 'Xsgmwe sI2Nye').text
        #flight_price=cur_flight.find('div', class_ = 'YMlIz FpEdX jLMuyc')
        try:
            cheapP = cur_flight.find('div', class_ = 'YMlIz FpEdX jLMuyc').text
        except AttributeError:
            cheapP = None
        try:
            Reg_price = cur_flight.find('div', class_ = 'YMlIz FpEdX').text
        except AttributeError:
            Reg_price = None
        if cheapP is None:
            f_price= Reg_price
        else:
            f_price= cheapP
        departure_airport = cur_flight.find('div', class_ = 'ZHa2lc tdMWuf y52p7d').text
        arrival_airport = cur_flight.find('div',class_="FY5t7d tdMWuf y52p7d").text
    
        stops = cur_flight.find('div', class_ = 'EfT7Ae AdWm1c tPgKwe').text
        print(f'''
            Departure: {departure_airport}
            Arrival: {arrival_airport}
            Departure_time: {d_time}
            Arrival_time: {a_time}
            Carrier: {carrier}
            FlightNum: {flightNum}
            Stops: {stops}
            Cheapest: {cheapP}
            Regular Price: {Reg_price}
        ''')
        
    #df_record = df_record.append({'出发时间':d_time,'到达时间':a_time, '始发机场':departure_airport,'到达机场':arrival_airport
    #                                 ,'航空公司':carrier, '航班号':flightNum, '票价':f_price, '官网购票链接':base_url+"%20"+carrier}, ignore_index=True)
         
        df_current =pd.DataFrame({'出发时间':[d_time],'到达时间':[a_time], '始发机场':[departure_airport],'到达机场':[arrival_airport]
                                      ,'航空公司':[carrier], '航班号':[flightNum], '票价':[f_price], '官网购票链接':[base_url+"%20"+carrier]})
        
        df_record=pd.concat([df_record, df_current], ignore_index=True)    
        print('after df_record')    
        dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_flight_info= FlightDB(
            DRP_DATETIME = d_time,
            ARR_DATETIME = a_time,
            DEP_AIRPORT = departure_airport,
            ARR_AIRPORT = arrival_airport,
            AIRLINE = carrier,    
            FLIGHTNUMBER = flightNum,
            PRICE =  f_price,     
            LINK = base_url+"%20"+carrier,        
            CREATEDDATE = dt_string) 
        with app.app_context():
            db.session.add(insert_flight_info)
            db.session.commit()
                
    #df_record.to_csv('flight_search_result.csv', encoding='utf_8_sig')
    #df_record['官网购票链接'] = df_record['官网购票链接'].apply(make_clickable, args = ('点击前往',))

    return df_record

def NorthAmerica(start,end):
    df1 = pd.DataFrame(columns=['出发时间','到达时间','始发机场','到达机场',
                                      '航空公司' ,'航班号','票价','官网购票链接'])  
    
    routes=[
        ['BOS',	'PEK']    
       ,['PEK', 'BOS']
       ]

    date = start
    while date <= end:
        for path in routes:
            d=path[0]
            a=path[1]
            print(date)
            df_search=search_cur_flight(d,a,date)
            df1=pd.concat([df1,df_search], ignore_index=True)
            print(f'''northamerica finish 1 path {d} to {a}''')
            #df1=df1.append(search(d,a,date))
        date=date+datetime.timedelta(days=1)
    return df1
def NA1():
    start = datetime.date.today()+ datetime.timedelta(days=1)  #set start and end time
    end= start + datetime.timedelta(days=10) 
    while True:
        NorthAmerica(start,end)
        time.sleep(3600)
        #df_na=NorthAmerica(start,end)
    #df_na.to_csv('flight_search_na.csv', encoding='utf_8_sig') 
    #return df_na

#--------------Web---------------------------
@app.route('/api')
def api():
    response = {'message': 'Hello, World!'}
    return render_template("test.html", jsonfile=json.dumps(response))
"""
@app.route("/flight")
def index():
    return render_template("index.html",flight_lists=[flight_list.to_html(classes='data')], titles=flight_list.columns.values)
"""
@app.route('/')
def index():
    thread1 = threading.Thread(target=NA1,name='NAThread')
    thread1.start()
    posts = FlightDB.query.all()
    return render_template('index.html', flight_lists=posts)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search_value = request.form.get('search_brand_model')
        print(search_value)
        cur_flights = FlightDB.query.filter_by(FlightDB.ARR_AIRPORT.like(f'%{search_value}%') | FlightDB.DEP_AIRPORT.like(f'%{search_value}%')).all()
        return render_template('search.html', flight_lists=cur_flights)
    else:
        return render_template('search.html')
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all() # <--- create db object.
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

#pip freeze requirements.txt
  
#driver.quit() 


""" #sqlite3 db definition
DATABASE='database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()

 with app.app_context():
            conn = get_db()
            cursor = conn.cursor() 
            cursor.execute("INSERT INTO FLIGHTINFO\
                            (DRP_DATETIME, ARR_DATETIME, DEP_AIRPORT,ARR_AIRPORT, AIRLINE,\
                            FLIGHTNUMBER, PRICE, LINK,CREATEDDATE)\
                            VALUES (?,?,?,?,?,?,?,?,?)", 
                            (d_time, a_time, departure_airport,arrival_airport, carrier, flightNum,f_price,\
                            base_url+"%20"+carrier,dt_string)) 
            conn.commit()
            cursor.close() 
"""
"""
['JFK',	'PVG']	
     
    ,['LAX',	'PVG']
    ,['SFO',	'PVG']	
    ,['SEA',	'PVG']	
    ,['DTW',	'PVG']	
    ,['DFW',	'PVG']
     
    
    ,['LAX',	'PEK']	
    ,['SFO',	'PEK']	
    ,['JFK',	'PEK']	
    
    ,['IAD',	'PEK']	
    ,['LAX',	'CAN']
    ,['JFK',	'CAN']	
    ,['LAX',	'SZX']	
    ,['SFO',	'WUH']
    ,['LAX',	'XMN']    
    ,['LAX',	'TFU']  
    
    ,['PVG',    'JFK']	
    ,['PVG',    'LAX']
    ,['PVG',    'SFO']	
    ,['PVG',    'SEA']	
    ,['PVG',    'DTW']	
    ,['PVG',    'DFW']
    ,['PEK',    'LAX']	
    ,['PEK',    'SFO']	
    ,['PEK',    'JFK']	
    
    ,['PEK',    'IAD']	
    ,['CAN',    'LAX']
    ,['CAN',    'JFK']	
    ,['SZX',    'LAX']	
    ,['WUH',    'SFO']
    ,['XMN',    'LAX']    
    ,['TFU',    'LAX'] 
"""