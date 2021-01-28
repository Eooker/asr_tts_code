# coding=utf-8
import os
import json
import urllib.request

#彩色输出函数
def color_print (color,text):          #参数：color 字体颜色 text 输出文本   颜色编号：0黑色 1红色 2绿色 3棕色 4蓝色 5紫色 6青色 7白色
	color=str(color+30)
	print("\033[1;"+color+"m"+text+"\033[0m")

#聊天
def chat():
	with open('/home/pi/my_ASR_TTS/process/asr_result.txt','r') as asr_result_file:      #打开语音识别的结果文本
		chat_text=asr_result_file.read()    #获取文本内容
	chat_text=urllib.parse.quote(chat_text)     #将文本内容转换成适合于网络传输的形式
	chat_url="http://api.qingyunke.com/api.php?key=free&appid=0&msg=%s"%(chat_text)   #形成请求地址
	try:
		receive_data=urllib.request.urlopen(chat_url)     #发送请求并接收返回数据
		
		chat_data=receive_data.read()          #提取返回数据内容
		chat_data_str=str(chat_data,'utf-8')     #将提取内容转换为中文
		chat_data_dict=json.loads(chat_data_str)      #将提取内容恢复为python数据类型：字典
		if chat_data_dict['result'] == 0 :   #判断是否返回正确数据
			color_print(7,"成功收到回信！")
			color_print(5,"回复："+chat_data_dict['content'])
			with open("/home/pi/my_ASR_TTS/process/chat_result.txt","w") as result_file:
				result_file.write(chat_data_dict['content'])
			os.system("python3 /home/pi/my_ASR_TTS/code/tts.py")
			os.system("omxplayer /home/pi/my_ASR_TTS/output/tts_result.wav")   #播放合成语音
		else:    #返回数据错误，将错误提示写进error.txt
			color_print(1,"聊天数据错误")
			with open("/home/pi/my_ASR_TTS/error/error.txt","w") as error_file:
				error_file.write("聊天数据错误。")
	except:
		color_print(1,"聊天请求失败")
		with open("/home/pi/my_ASR_TTS/error/error.txt","w") as error_file:
			error_file.write("聊天请求失败。")

#播报天气
def weather(location='ip'):
	params=urllib.parse.urlencode({'key':'kzhizmejso25ayds','location':location,'unit':'c','language':'zh-Hans'})          #天气请求参数,key:私钥  location:地点  unit:单位  language:语言
	api='https://api.seniverse.com/v3/weather/now.json'          #api
	url=api+'?'+params     #将api和参数合成请求url，'?'是网址形式中代表参数开始的地方
	try:
		result_data=urllib.request.urlopen(url)            #向url发送请求
		wether_data=result_data.read().decode('utf-8')     #读取返回结果并转换成中文编码
		wether_data=json.loads(wether_data)                #将结果恢复成字典形式

		location_data=wether_data['results'][0]['location']        #从结果字典中获取地址数据
		now_data=wether_data['results'][0]['now']                  #从结果字典中获取天气数据
		last_update_data=wether_data['results'][0]['last_update']  #从结果字典中获取更新时间数据

		result=location_data['name']+'天气：'+now_data['text']+',\n气温：'+now_data['temperature']+'度'          #将数据组合成文本字符串
		color_print(6,result)        #彩色打印结果
		with open("/home/pi/my_ASR_TTS/process/chat_result.txt","w") as result_file:         #将结果写进文件
			result_file.write(result)
		os.system("python3 /home/pi/my_ASR_TTS/code/tts.py")
		os.system("omxplayer /home/pi/my_ASR_TTS/output/tts_result.wav")   #播放合成语音
	except:
		color_print(1,"查询天气请求失败")
		with open("/home/pi/my_ASR_TTS/error/error.txt","w") as error_file:            #发生错误则将错误写进error.txt文件
			error_file.write("查询天气请求失败。")

#播放音乐
def music(hotlist="热歌榜"):
	color_print(7,"请稍等...")
	text=hotlist
	text_b=urllib.parse.quote(text)
	try:
		result_data=urllib.request.urlopen('https://api.uomg.com/api/rand.music?sort=%s&format=json'%(text_b))
		music_data=result_data.read().decode('utf-8')
		music_data=json.loads(music_data)['data']
		
		music_name=music_data['name']
		if " " in music_name:                       #检查歌名中是否含空格，有则删除
			music_name=music_name.replace(" ","")
		song_url=music_data['url']
		filePath="/home/pi/my_ASR_TTS/music/"+music_name+".wav"      #音乐文件存储路径
		music_cmd = "wget '%s' -c -T 10 -t 3 -q -O '%s'" % (song_url, filePath)     #wget参数说明：-c断点续传 -T超时时间 -t重试次数 -q安静模式（不输出下载信息） -O数据写入指定文件名
		os.system(music_cmd.encode('utf-8'))      #执行wget命令，下载音乐文件
		
		color_print(6,"正在为您播放...")
		color_print(6,"歌名："+music_data['name'])
		color_print(6,"演唱者："+music_data['artistsname'])
		color_print(6,"播放地址："+music_data['url'])
		color_print(6,"榜单："+text)
		#music_download=urllib.request.urlopen(music_data['url']).read()
		#with open("/home/pi/my_ASR_TTS/music/music.wav","wb") as file:
		#	file.write(music_download)
		color_print(7,"(退出播放请按q)")
		os.system("omxplayer "+filePath)
		os.system("rm "+filePath)        #删除文件，以免文件积累挤占内存
	except:
		color_print(1,"播放音乐请求失败")
		with open("/home/pi/my_ASR_TTS/error/error.txt","w") as error_file:            #发生错误则将错误写进error.txt文件
			error_file.write("播放音乐请求失败。")
