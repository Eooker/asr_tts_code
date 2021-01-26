
# coding=utf-8
import os
import time
import sys
import serial
import RPi.GPIO as GPIO
import subprocess
sys.path.append("/home/pi/my_ASR_TTS/snowboy/examples/Python3")
import snowboydecoder

#print(time.localtime())#获取当前时间

#彩色输出函数
def color_print (color,text):          #参数：color 字体颜色 text 输出文本   颜色编号：0黑色 1红色 2绿色 3棕色 4蓝色 5紫色 6青色 7白色
	color=str(color+30)
	print("\033[1;"+color+"m"+text+"\033[0m")

color_print(7,"欢迎使用优希亚机器人！\n正在配置环境，请稍等...")

interrupted = False
model="/home/pi/snowboy/examples/Python3/resources/models/snowboy.umdl"
def interrupt_True():
    global interrupted
    interrupted = True
def interrupt_callback():      #这个函数没有实际意义，就是返回interrupted变量，因为detector.start函数要求输入的参数是函数，所以才写成函数形式
    global interrupted
    return interrupted
detector = snowboydecoder.HotwordDetector(model, sensitivity=1)

#检查Arduino是否连接
Arduino_status=subprocess.getstatusoutput("ls /dev/ttyUSB*")     #获取连接状态
if Arduino_status[0] == 0:       #指令正确执行则返回0
    Arduino_USB=Arduino_status[1]    #获取Arduino端口
else:
    print("\033[1;31mArduino未连接\033[0m")       #未连接则直接退出程序
    sys.exit(0)

#配置USB,连接Arduino
ser=serial.Serial(Arduino_USB,9600,timeout=2)
time.sleep(2)

#配置GPIO，连接按键
button=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(button,GPIO.IN)


#获取error.txt最后修改时间，服务于error_check()函数，用于判断是否产生错误信息
file_data=os.stat("/home/pi/my_ASR_TTS/error/error.txt")      #获取文件信息   数据格式：st_ino索引号 st_dev设备号 st_nlink st_uid所有者的用户id st_gid所有者的组id st_size文件大小（单位：字节） st_atime最后一次访问时间 st_mtime最后一次修改时间 st_ctime最后一次状态变化时间
file_start_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(file_data.st_mtime))   #获取最后一次修改时间，并将时间格式化
#print("file_start_time:"+file_start_time)     #file_start_time是标志常量，用于比较

#检查函数，用于检测程序是否出错
def error_check():
    file_data=os.stat("/home/pi/my_ASR_TTS/error/error.txt")
    filetime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(file_data.st_mtime))       #获取最后修改时间并格式化
    #print("filetime:"+filetime)
    if filetime != file_start_time :        #与file_start_time进行比较，判断是否有修改错误信息，结果为真则表示程序出错，播放失败提示，并退出程序
        os.system("python3 /home/pi/my_ASR_TTS/error/error.py")
        os.system("omxplayer /home/pi/my_ASR_TTS/error/error.wav")
        sys.exit(0)

#控制Arduino函数，用于指示Arduino作出相应动作
def arduino_control(command):       #目前可用指令：前进、后退
    if ser.isOpen():
        b_command=command.encode('utf-8')
        ser.write(b_command)
        b_arduino_data=ser.readline()   #读取Arduino发过来的数据
        arduino_data=b_arduino_data.decode('utf-8')
        print(arduino_data)
        b_arduino_data=ser.readline()
        arduino_data=b_arduino_data.decode('utf-8')
        print(arduino_data)                         
        if arduino_data=="无效指令":
            os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/invalid_command.wav")
    else:
        print("Arduino未连接")

print("配置完成")
print("请按下黑色按键开始互动")

#按下按键开始
while True:
    if GPIO.input(button) == 0 :
        while GPIO.input(button) == 0:        #等待按键松开
            pass
        break

def all_main():
    while True:
        color_print(7,"开始聆听...")
        os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/warning_tone.mp3") #录音提示音
        os.system("arecord -r 16000 -c 1 -d 3 -f S16_LE -t wav /home/pi/my_ASR_TTS/input/input.wav")   #录音3秒，修改-d可修改录音时间(单位：秒)
        color_print(7,"聆听结束")
        os.system("python3 /home/pi/my_ASR_TTS/code/asr_json.py")    #识别录音内容
        error_check()   #检查识别结果
        asr_result_data=os.stat("/home/pi/my_ASR_TTS/process/asr_result.txt")       #检查识别结果是否为空
        if asr_result_data.st_size != 0:
            break
        else:
            color_print(7,"没听清你在说什么。")
            os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/what_you_said.wav")

    with open("/home/pi/my_ASR_TTS/process/asr_result.txt","r") as asr_result_file:
        asr_result = asr_result_file.read()
    if asr_result == "拍照。":          #判断识别内容是否为指令
        os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/ok.wav")
        os.system("raspistill -t 2000 -o /home/pi/my_ASR_TTS/photograph/image.jpg")        #注意，每次拍照会覆盖原图片
    elif asr_result == "退出。":
        os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/goodbye.wav")
        sys.exit(0)   #退出程序
    elif asr_result == "天气。":
        os.system("python3 /home/pi/my_ASR_TTS/code/wether.py")
        error_check()
    elif asr_result == "前进。":
        arduino_control("前进")
    elif asr_result == "后退。":
        arduino_control("后退")
    elif asr_result == "加速。":
        arduino_control("加速")
    elif asr_result == "减速。":
        arduino_control("减速")
    elif asr_result == "停止。":
        arduino_control("停止")
    elif asr_result == "关机。":          #收到关机指令时需要第二次确认
        os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/confirm_shutdown.wav")    #播放再次确认提示音
        os.system("arecord -r 16000 -c 1 -d 2 -f S16_LE -t wav /home/pi/my_ASR_TTS/input/input.wav")   #录音两秒
        os.system("python3 /home/pi/my_ASR_TTS/code/asr_json.py")      #识别录音，确认是否确定关机
        error_check()
        with open("/home/pi/my_ASR_TTS/process/asr_result.txt","r") as asr_result_file:
            asr_result = asr_result_file.read()
        if asr_result == "是" or "对" or "确定" or "关机":
            os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/goodbye.wav")     #播放再见提示音   
            os.system("sudo shutdown now")         #关机
        elif asr_result == "不" or "不是" or "取消":
            os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/cancel_shutdown.wav")     #取消关机
        else:
            os.system("omxplayer /home/pi/my_ASR_TTS/common_voice/unsure_cancel_shutdown.wav")    #没有收到确切指令，拒绝关机
    else:                     #不是指令则进入聊天模式
        os.system("python3 /home/pi/my_ASR_TTS/code/chat.py")     #将识别内容发送至青云客，返回聊天数据
        error_check()
        os.system("python3 /home/pi/my_ASR_TTS/code/tts.py")      #将聊天内容合成语音
        error_check()
        os.system("omxplayer /home/pi/my_ASR_TTS/output/tts_result.wav")   #播放合成语音
    print("over")


#my_callback=[lambda:snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING),all_main]
detector.start(detected_callback=all_main,interrupt_check=interrupt_callback)
detector.terminate()
