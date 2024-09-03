#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2024-08-29            #
# Build  : 2024-08-29            #
# What   : 网站签到         #
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


class via_ablesci():
    def __init__(self):
        self.prefix = self.__class__.__name__  # 类的名字
        # device
        self.mynode = Settings.mynode
        self.totalnode = Settings.totalnode
        self.LINK = Settings.LINK_dict[Settings.mynode]
        self.移动端 = deviceOB(mynode=self.mynode, totalnode=self.totalnode, LINK=self.LINK)
        self.设备类型 = self.移动端.设备类型
        self.APPID = "mark.via"
        self.APPOB = appOB(APPID=self.APPID, big=True, device=self.移动端)
        self.Tool = DQWheel(var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.prefix}.txt",
                            mynode=self.mynode, totalnode=self.totalnode)
        #
        self.dayFILE = f"{self.prefix}.txt"
        self.timelimit = 60*10
        self.运行时间 = [3.0, 4.0]
        self.today = self.Tool.time_getweek()
        self.yesterday = (self.today-1) % 7
    #

    def stop(self):
        self.APPOB.关闭APP()
    #

    def run(self, times=0):
        if not connect_status():
            self.移动端.连接设备()
        if times == 0:
            self.today = self.Tool.time_getweek()
            self.yesterday = (self.today-1) % 7
            try:
                self.yesterday = int(self.Tool.readfile(self.dayFILE)[0].strip())
            except:
                TimeECHO(f"未能从{self.dayFILE}中获取到上次运行时间")
            self.Tool.timelimit(timekey="RUN", limit=self.timelimit, init=True)
        #
        if self.Tool.timelimit(timekey="RUN", limit=self.timelimit, init=False):
            TimeECHO(f"{self.prefix}.运行超时")
            self.Tool.touchfile(self.dayFILE, content=str(self.yesterday))
            return
        #
        if times > 8:
            TimeECHO("失败次数太多，停止")
            self.Tool.touchfile(self.dayFILE, content=str(self.yesterday))
            return
        #
        times = times + 1
        # 重新打开via浏览器
        self.APPOB.重启APP()
        #
        # ------------------------------------------------------------------------------
        # 不存在对应图片则设置为None
        书签图标 = Template(r"tpl1724917367398.png", record_pos=(-0.234, 0.136), resolution=(960, 540))
        签到入口 = Template(r"tpl1724917379162.png", record_pos=(0.266, -0.036), resolution=(960, 540))
        今日签到 = Template(r"tpl1724917393304.png", record_pos=(0.155, 0.132), resolution=(960, 540))
        主页入口 = Template(r"tpl1724918907933.png", record_pos=(-0.398, -0.18), resolution=(960, 540))
        网站主页元素 = []
        网站主页元素.append(主页入口)
        网站主页元素.append(签到入口)
        # ------------------------------------------------------------------------------
        # 打开网站
        self.Tool.existsTHENtouch(书签图标, self.prefix+"书签图标", savepos=False)
        # 检测是否打开成功
        存在, 网站主页元素 = self.Tool.存在任一张图(网站主页元素, self.prefix+"网站主页元素")
        for i in range(10):
            if 存在:
                break
            # 有则更新，无则采用旧的入口
            self.Tool.存在任一张图([主页入口], self.prefix+"主页入口", savepos=True)
            self.Tool.existsTHENtouch(主页入口, self.prefix+"主页入口", savepos=True)
            sleep(5)
            存在, 网站主页元素 = self.Tool.存在任一张图(网站主页元素, self.prefix+"网站主页元素")
        #
        if not 存在 and times < 5:
            TimeECHO("打开主页失败")
            return self.run(times)
        # ------------------------------------------------------------------------------
        #
        if 签到入口:
            # 有则更新，无则采用旧的入口
            self.Tool.存在任一张图([签到入口], self.prefix+"签到入口", savepos=True)
            self.Tool.existsTHENtouch(签到入口, self.prefix+"签到入口", savepos=True)
        #
        if self.Tool.existsTHENtouch(今日签到, self.prefix+"今日签到", savepos=False):
            self.yesterday = self.today
        else:
            if self.yesterday == self.today:
                TimeECHO("找不到今日签到，应该签到过了")
            else:
                TimeECHO("找不到今日签到，再次尝试签到")
                return self.run(times)
        #
        self.Tool.touchfile(self.dayFILE, content=str(self.yesterday))
        return
    #

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
    ce = via_ablesci()
    ce.run()
    exit()
