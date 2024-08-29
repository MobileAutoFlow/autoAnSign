#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2024-08-29            #
# Build  : 2024-08-29            #
# What   : 基于via浏览器的网站签到 #
##################################
try:
    from airtest_mobileauto.control import *
except ImportError:
    print("模块[airtest_mobileauto]不存在, 尝试安装")
    import pip
    try:
        pip.main(['install', 'airtest_mobileauto', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'])
    except:
        print("安装失败")
        exit(1)
import sys
import importlib

class run_via():
    def __init__(self):
        # device
        self.mynode = Settings.mynode
        self.totalnode = Settings.totalnode
        self.LINK = Settings.LINK_dict[Settings.mynode]
        self.移动端 = deviceOB(mynode=self.mynode, totalnode=self.totalnode, LINK=self.LINK)
        self.设备类型 = self.移动端.设备类型
        self.APPID = "mark.via"
        self.APPOB = appOB(APPID=self.APPID, big=True, device=self.移动端)
        self.Tool = DQWheel(var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.mynode}.ce.txt",
                            mynode=self.mynode, totalnode=self.totalnode)
        #
        self.prefix="via"
        self.初始化FILE=f"{self.prefix}.{self.mynode}初始化FILE.txt"
        self.失败FILE=f"{self.prefix}.{self.mynode}运行失败FILE.txt"
        self.Tool.removefile(self.失败FILE)
        self.timelimit = 60*10
        self.运行时间 = [3.0, 4.0]

    def check_status(self):
        if not connect_status():
            self.移动端.连接设备()
            return connect_status()
        return True
    #
    def stop(self):
        self.APPOB.关闭APP()
    #
    def run(self):
        if not self.check_status():
            TimeECHO("无法连接设备，退出")
            return False
        #
        taglist=["via_ablesci","via_muchong"]
        for tag in taglist:
            if not os.path.exists(tag+".txt"):
                TimeECHO(f"不进行{tag}")
                continue
            TimeECHO(f"=>>>>{tag}<<<<="*3)
            try:
                # 动态导入模块
                module = importlib.import_module(tag)
                # 获取模块中与模块名相同的类
                tag_class = getattr(module, tag)
                tag_object = tag_class()  # 假设类构造函数不需要参数
                # 使用类来创建一个对象实例
                tag_object.APPOB.big=False
                tag_object.run()
                tag_object.stop()
            except:
                traceback.print_exc()
                continue



    def looprun(self, times=0):
        times = times + 1
        startclock = self.运行时间[0]
        endclock = self.运行时间[1]
        while True:
            leftmin = self.Tool.hour_in_span(startclock, endclock)*60.0
            if leftmin > 0:
                TimeECHO("剩余%d分钟进入新的一天" % (leftmin))
                self.APPOB.关闭APP()
                self.移动端.重启重连设备(leftmin*60)
                continue
            times = times+1
            TimeECHO("="*10)
            self.run()


if __name__ == "__main__":
    config_file = ""
    if len(sys.argv) > 1:
        config_file = str(sys.argv[1])
    Settings.Config(config_file)
    ce = run_via()
    ce.run()
    #ce.looprun()
    #exit()
