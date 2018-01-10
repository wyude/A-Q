##python3.6
##需要安装的库   python-opncv Pillow PyUserInput py-win32 baidu-aip
##使用：
####1.选择模式1手选答案2自动勾选答案
####2.通过鼠标点选题框选择截屏范围，第一下选择左上角，第二下选择右下角
####3.选择颜色监控位置
####4.running…………………………

import urllib as url
import string
import re
import json
import time
import cv2
from aip import AipOcr  
from PIL import ImageGrab
from pymouse import PyMouse


class NiuBiLe:
    def __init__(self):
        #自己注册，换成自己的，百度接口有调用频率限制
        APP_ID = '9851066'  
        API_KEY = 'LUGBatgyRGoerR9FZbV4SQYk'  
        SECRET_KEY = 'fB2MNz1c2UHLTximFlC4laXPg7CVfyjV'  
        # 初始化AipFace对象  
        self.aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)  
        self.SCREENSHOT_PATH = 'screenshot/screen.png'
        self.worddict={}
        self.word=''
        self.options = {'detect_direction': 'true', 'language_type': 'CHN_ENG',} 
        self.mode=1
        self.snapField=[]
        self.colorPos=[]
        self.color=[250,250,250]
        self.colorL=list(map(lambda x:x-10,self.color))

    def getPos(self):
        #在这里获取截图范围，鼠标点击或者识图
        #还有判断题目是否出现的颜色位置
        snap=[20,120,475,600]#startX startY width height 
        colorPos=[100,100]
        return snap,colorPos

    def init(self):
        #self.mode=input("选择答案操作模式1.看到答案后手选2.自动点击答案所在位置,输入后回车:")
       # print("模式",self.mode)
        self.snapField,self.colorPos=self.getPos()

    def snap(self):
        im=ImageGrab.grab(self.snapField)
        im.save(self.SCREENSHOT_PATH,'png') 

    def isTime(self):
        #是否开始出题了
        while(True):
            self.snap()
            img=cv2.imread(self.SCREENSHOT_PATH)#读图片为narray
            color=img[self.colorPos[0],self.colorPos[1]]
            print(color)
            if( color[0]>=self.colorL[0] and color[1]>=self.colorL[1] and color[2]>=self.colorL[2] ):
                return True
            else:
                time.sleep(0.1)

    def get_file_content(self,SCREENSHOT_PATH):  
        with open(SCREENSHOT_PATH, 'rb') as fp:  
            return fp.read() 

    def ocr(self):
        result = self.aipOcr.basicGeneral(self.get_file_content(self.SCREENSHOT_PATH), self.options)  
        re_str=json.dumps(result)#.decode("unicode-escape")
        #print(re_str.decode("unicode-escape")) 
        return re_str

    def baidu_search(self,keyword):
        p= {'wd': keyword}
        print(keyword)
        res=url.request.urlopen("http://www.baidu.com/s?"+url.parse.urlencode(p))
        html=res.read()
        return html 

    def getWords(self,input):
        self.worddict={}
        self.word=''
        text = json.loads(input)
        num = text.get('words_result_num')
        wordArr = text.get('words_result')
        for i in range(num):
            print(wordArr[i])
            if(i<num-3):
                self.word= self.word+wordArr[i]['words']
            else:
                #TODO 判断是否需要去除字母
                keystr=wordArr[i]['words']
                if(keystr.startswith('A') or keystr.startswith('B') or keystr.startswith('C') or 
                keystr.startswith('a') or keystr.startswith('b') or keystr.startswith('c') or
                keystr.startswith('1') or keystr.startswith('2') or keystr.startswith('3')):
                    self.worddict[keystr[2:]] =0
                else:
                    self.worddict[keystr] =0
        print(self.word)
        
        context = self.baidu_search(self.word.encode('utf8'))
        #print (context.count('比奇堡'))
        for i in self.worddict:
            self.worddict[i] = context.count(i.encode('utf8'))
            print(i,self.worddict[i])

    def loop(self):
        if(self.isTime()):
            self.getWords( self.ocr() )
            time.sleep(60*1)#答完一次题怎么的也得1分钟再出题吧

if __name__=="__main__":
    time1=time.time()    	
    test=NiuBiLe()
    test.init()
    while(time.time()-time1<60.0*20.0):
        time2=time.time()
        print( time2-time1 )
        test.loop()
    print('done')
    

