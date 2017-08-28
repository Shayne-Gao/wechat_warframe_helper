#!/usr/bin/python
# -*- coding:utf-8 -*- 
import sys
reload(sys)
sys.path.append("..")
sys.setdefaultencoding('utf-8')

import json
import urllib
import MySQLdb
import types
import urllib2
import time
from wftools.translator import WmTranslator
from wftools.pricer import WmPricer
class warframe(object):
    MAX_RECORD_NUM = 10
    MAX_RECORD_PRICE_NUM = 2 
    def timestamp_datetime(self,value):
        value = int(value)
        format = '%Y-%m-%d %H:%M:%S'
        #value为传入的值为时间戳(整形)，如：1332888820
        value = time.localtime(value)
        ## 经过localtime转换后变成
        ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
        # 最后再经过strftime函数转换为正常日期格式。
        dt = time.strftime(format, value)
        return dt

    def getZhWikiUrl(self,nameZh,nameEn,itemType):
        baseUrl = 'http://warframe.huijiwiki.com/wiki/'
        pageName = ""
        tempList = nameEn.split('Prime')
        baseName = tempList[0]
        #if nameZh is not None:
        #    pageName = nameZh
        #elif nameEn is not None:
        #    pageName = nameEn
        pageName = baseName
        return baseUrl+pageName

            
    def getInfoByName(self,itemName):
        resStr = ""
        #尝试直接翻译
        trans = WmTranslator()
        directNameZh = trans.en2zh(itemName)
        if directNameZh != itemName:
            resStr += "您的输入也可以直接被翻译为:"+directNameZh+"\n\n"

        db = MySQLdb.connect("localhost","root","eas140900","warframe",charset='utf8' )

        # 使用cursor()方法获取操作游标 
        cursor = db.cursor()
        sql = """SELECT * from item where name_zh like '%%%s%%' or name_en like '%%%s%%' """ %(itemName,itemName)
          # 执行SQL语句
        print sql   
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        #print results
        if len(results)==0:
            #尝试用输入找wiki
            wikiZH = self.getZhWikiUrl("",itemName,"")
            wikiZH = "【<a href='"+wikiZH+"'>Wiki</a>】"
            resStr += "未找到"+itemName+",您可以试试模糊搜索，减少搜索的字试试看\n尝试为您找到了"+wikiZH
            return resStr
        #这里限制长度，因为微信太长的记录显示会出错
        if len(results) > self.MAX_RECORD_NUM:
            resStr += "【提示】共搜索到%s条记录，因微信限制，只显示前%s条\n"%(len(results),self.MAX_RECORD_NUM)
            results = results[0:self.MAX_RECORD_NUM]
        isFirst = True
        pricer = WmPricer()
        checkPrice = True
        #这里限制询价的长度，因为太多的记录询价会很慢
        if len(results) >self.MAX_RECORD_PRICE_NUM:
            #checkPrice = False
            resStr += "【提示】搜索到的记录太多，只显示前%s物品价格，请完善关键词，如#wf Ash Prime Set\n\n"%(self.MAX_RECORD_PRICE_NUM)
        listCount = 0;
        for r in results:
            name_en=r[1]
            name_zh=r[2]
            itemType = r[3]
            wikiZH = self.getZhWikiUrl(name_zh,name_en,itemType)
            wikiZH = "【<a href='"+wikiZH+"'>Wiki</a>】"
            resStr += "-------------------------------\n"
            resStr += "类别: %s\n名称: %s\n英文名: %s\n %s\n"%(itemType,name_zh,name_en,wikiZH)
            #get price
            listCount += 1
            if listCount <= self.MAX_RECORD_PRICE_NUM:
                itemPrice = pricer.getPrice(name_en,itemType)
                if itemPrice is not None:
                    resStr += "售价：\n最低：%s  前20平均售价：%s x %s个\n 前3位的卖家：\n%s"%(itemPrice['cheapest_price'],itemPrice['top_avg'],itemPrice['top_sum'],itemPrice['top_rec'])
                else:
                    resStr += "未查询到售价\n"
        return resStr

    def getAlarm(self):
        
        req=urllib2.Request('http://deathsnacks.com/wf/data/alerts_raw.txt')
        resp =urllib2.urlopen(req)
        html = resp.read()
        alarms = html.split('\n')
        resStr = ""
        trans = WmTranslator()
        for ala in alarms:
            tempL = ala.split('|')
            if len(tempL)<9:
                continue
            starName = trans.en2zh(tempL[2])
            mapName = tempL[1]
            lvl = tempL[5] +' - '+tempL[6]
            taskType = trans.en2zh(tempL[3])
            monsType = tempL[4]
            reward = trans.en2zh(tempL[9])
            endTime = self.timestamp_datetime(tempL[8])
            resStr += "%s(%s) - %s(%s)\nLv:%s\n结束于:%s\n奖励:%s \n" %(starName,mapName,taskType,monsType,lvl,endTime,reward)
            resStr +="--------------------------\n"
        return resStr

      
   

    

def test():
    wf = warframe()
    print wf.getPrice('Ash Prime Set','Set')
#------------------------------------------
#test()
#wf = warframe()
#print wf.getInfoByName('nek')




