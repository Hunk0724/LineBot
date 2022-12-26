# # -*- coding: utf-8 -*-
# #載入LineBot所需要的套件
from flask import Flask, request, abort, send_file
from dotenv import load_dotenv
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import re
import json,requests
import random


from fsm import TocMachine
import os
load_dotenv()
machine = TocMachine(
    states=["idle", "weather", "city"],
    transitions=[
        {
            "trigger": "advance",
            "source": "idle",
            "dest": "weather",
            "conditions": "is_going_to_weather",
        },
        {
            "trigger": "advance",
            "source": "fortune",
            "dest": "name",
            "conditions": "is_going_to_fortune",
        },
        {  "trigger": "advance",
            "source": "weather",
            "dest" : "city", 
            "conditions" : "is_going_to_city"
        },
        {   "trigger": "advance",
            "source": "idle",
            "dest" : "fortune",
            "conditions":"is_going_to_fortune"
        },
        {"trigger": "go_back", "source": ["weather", "city", "fortune","name"], "dest": "idle"},
    ],
    initial="idle",
    auto_transitions=False,
    show_conditions=True,
)
app = Flask(__name__)

channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi(channel_access_token)
# 必須放上自己的Channel Secret
handler = WebhookHandler(channel_secret)

region=""
state="idle"
name = ""
sign = ""
# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
        
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']
def get(city):
    token = 'CWB-F1343576-D288-4C36-A25C-383E72A80481'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    #Python 的 JSON 套件將字串轉換成 dict
    Data = (json.loads(Data.text,encoding='utf-8'))['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res

#訊息傳遞區塊
line_bot_api.push_message('Uc58783194ae42125c3e691cbeedb84b1', TextSendMessage(text='美好的一天從現在開始!\n想知道甚麼資訊呢?\n輸入:\n 天氣(提供未來36小時之預報~\n 運勢(抽個大吉!開心一下!\n 試試看吧!'))

##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global state,region,name,sign
    
    reply_token = event.reply_token
    message =text= event.message.text
        
    if re.match(message, '天氣') or re.match(state,'weather')or re.match(state,'city'):
        if re.match(state,'idle'):
            state="weather"
            line_bot_api.reply_message(reply_token,TextSendMessage(text='選擇地區:\n 北部\n 中部\n 南部\n 東部\n 外島'))
        elif re.match(state,'weather'):
            if re.match(message, '北部'):
                region="北部"
                state='city'
        
                line_bot_api.reply_message(reply_token,TextSendMessage(text='選擇縣市:\n 基隆市\n 臺北市\n 新北市\n 新竹市\n 新竹縣\n 桃園縣\n 苗栗縣'))
            elif re.match(message, '中部'):
                region="中部"
                state='city'
               
                line_bot_api.reply_message(reply_token,TextSendMessage(text='選擇縣市:\n 臺中市\n 彰化縣\n 南投縣\n 雲林縣\n 嘉義市\n 嘉義縣'))
            elif re.match(message, '南部'):
                region="南部"
                state='city'
         
                line_bot_api.reply_message(reply_token,TextSendMessage(text='選擇縣市:\n 台南市\n 高雄市\n 屏東縣'))
            elif re.match(message, '東部'):
                region="東部"
                state='city'
            
                line_bot_api.reply_message(reply_token,TextSendMessage(text='選擇縣市:\n 宜蘭縣\n 花蓮縣\n 臺東縣')) 
            elif re.match(message, '外島'):
                region="南部"
                state='city'
               
                line_bot_api.reply_message(reply_token,TextSendMessage(text='選擇縣市:\n 澎湖縣\n 金門縣\n 連江縣'))  
            else :
                    region=""
                    state="idle"
                    line_bot_api.reply_message(reply_token,TextSendMessage(text="格式錯誤，重新輸入:\n 天氣\n 運勢"))
        elif re.match(state,'city'):
            if message != "":
                city = message[0:3]

                city = city.replace('台','臺')
                if(not (city in cities)):
                    region=""
                    state="idle"
                    line_bot_api.reply_message(reply_token,TextSendMessage(text="格式錯誤，重新輸入:\n 天氣\n 運勢"))
                else:
                    
                    res = get(city)
                    region=""
                    state="idle"
                    line_bot_api.reply_message(reply_token, TemplateSendMessage(
                        alt_text = city + '未來 36 小時天氣預測',
                        template = CarouselTemplate(
                            columns = [
                                CarouselColumn(
                                    thumbnail_image_url = 'https://i.imgur.com/Ex3Opfo.png',
                                    title = '{} ~ {}'.format(data[0]['startTime'][5:-3],data[0]['endTime'][5:-3]),
                                    text = '{}\n天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(city,data[0]['parameter']['parameterName'],data[2]['parameter']['parameterName'],data[4]['parameter']['parameterName'],data[1]['parameter']['parameterName']),
                                    actions = [
                                        URIAction(
                                            label = '詳細內容',
                                            uri = 'https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                        )
                                    ]
                                )for data in res
                            ]
                        )
                    ))
                    
                   
            else: 
                line_bot_api.reply_message(reply_token, TextSendMessage(text="尚未選擇縣市，重新輸入:\n 天氣\n 運勢")) 
                region=""
                state="idle"
    elif re.match(message,'運勢') or re.match(state,'fortune') or re.match(state,'name'):
            
        if re.match(state,'fortune') :
            state = 'name'
            name = message
            line_bot_api.reply_message(reply_token,TextSendMessage(text='請輸入您的星座'))
        elif re.match(state,'name') :
            state = 'idle'
            sign = message
            fortune = random.choice(['大凶', '凶', '末吉', '吉','小吉','中吉','大吉'])
            line_bot_api.reply_message(reply_token,TextSendMessage(text='經過我深思熟慮後，{}的{}，其運勢為:{}'.format(sign,name,fortune)))
        elif re.match(state,'idle'):
            name=sign=""
            state = "fortune"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="我將為您抽取一張運勢卡片，請問您的名字是?"))  
        else:
            state = 'idle'
            line_bot_api.reply_message(reply_token,TextSendMessage(text='請重新輸入:\n 天氣\n 運勢'))
    else :
        state = "idle"
        region=""
        line_bot_api.reply_message(reply_token,TextSendMessage(text='請重新輸入:\n 天氣\n 運勢'))

@app.route("/show_fsm", methods=['POST'])            
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")                

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
