# coding=utf-8
import os
import json
import urllib
import urllib.request

params=urllib.parse.urlencode({'key':'kzhizmejso25ayds','location':'ip','unit':'c','language':'zh-Hans'})          #天气请求参数,key:私钥  location:地点  unit:单位  language:语言
api='https://api.seniverse.com/v3/weather/now.json'          #api
url=api+'?'+params     #将api和参数合成请求url，'?'是网址形式中代表参数开始的地方

try:
	result_data=urllib.request.urlopen(url)            #向url发送请求
	wether_data=result_data.read().decode('utf-8')     #读取返回结果并转换成中文编码
	wether_data=json.loads(wether_data)                #将结果恢复成字典形式

	location_data=wether_data['results'][0]['location']        #从结果字典中获取地址数据
	now_data=wether_data['results'][0]['now']                  #从结果字典中获取天气数据
	last_update_data=wether_data['results'][0]['last_update']  #从结果字典中获取更新时间数据

	result=location_data['name']+'天气：'+now_data['text']+'     '+'气温：'+now_data['temperature']+'度'          #将数据组合成文本字符串
	print("\033[1;36m"+result+"\033[0m")        #彩色打印结果
	with open("/home/pi/my_ASR_TTS/process/chat_result.txt","w") as result_file:         #将结果写进文件
		result_file.write(result)
	os.system("python3 /home/pi/my_ASR_TTS/code/tts.py")
	os.system("omxplayer /home/pi/my_ASR_TTS/output/tts_result.wav")   #播放合成语音
except:
    with open("/home/pi/my_ASR_TTS/error/error.txt","w") as error_file:            #发生错误则将错误写进error.txt文件
        error_file.write("查询天气请求失败。")
