import codecs
import select
import sys
import threading
from PyQt5 import QtWidgets
import socket,time
from  uitl import *
import 工站UI
from 协议 import tongxunxieyi

'''
工站模拟器v1.0.0
'''
class gongzhan(QtWidgets.QWidget, 工站UI.Ui_Form):
    def __init__(self):
        super(gongzhan, self).__init__()
        self.setupUi(self)
        self.log = Logger('工站.log')
        self.ip = self.lineEdit_6.text()
        self.port = int(self.lineEdit_7.text())
        self.ADDR = (self.ip,self.port)
        self.tcp_socket = None
        self.action()
        self.yijiashuliang=0
        self.chanliang = 0
        self.socket_lock = threading.Lock()



    #点击按钮
    def action(self):
        # self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.registe)
        self.pushButton_3.clicked.connect(self.yichangjinggao)
        self.pushButton_4.clicked.connect(self.yuangongshangji)
        self.pushButton_6.clicked.connect(self.pici)
        self.pushButton_7.clicked.connect(self.gotostation)
        self.pushButton_8.clicked.connect(self.gotostationok)
        self.pushButton_9.clicked.connect(self.outstation)
        self.pushButton_10.clicked.connect(self.outstationok)
        self.pushButton_5.clicked.connect(self.yuangongxiaji)
        self.pushButton_13.clicked.connect(self.bindyijia)
        self.pushButton_11.clicked.connect(self.order)
        self.pushButton_12.clicked.connect(self.rework)
        self.pushButton.clicked.connect(self.close)

    #连接吊挂服务器
    def connect(self):
        self.tcp_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # self.tcp_socket.settimeout(30)
        # self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
        try:
            # self.tcp_socket.bind(('192.168.35.219', 6000))
            self.tcp_socket.connect(self.ADDR)
            # 创建一个线程去读取数据
            read_thread = threading.Thread(target=self.recvmsg)
            read_thread.setDaemon(True)
            read_thread.start()
        except Exception as ret:
            self.log.logger.debug('连接失败： '+str(ret))
        self.log.logger.debug('连接吊挂服务器')

    #关闭连接
    def close(self):
        self.socket_lock.acquire()
        self.tcp_socket.close()
        self.tcp_socket = None
        self.socket_lock.release()

    # 接收服务端数据
    def recvmsg(self):
        while True:
            if not self.tcp_socket:
                break
            # 使用select监听客户端（这里客户端需要不停接收服务端的数据，所以监听客户端）
            #  第一个参数是要监听读事件列表，因为是客户端，我们只监听创建的一个socket就ok
            #  第二个参数是要监听写事件列表，
            #  第三个参数是要监听异常事件列表，
            #  最后一个参数是监听超时时间，默认永不超时。如果设置了超时时间，过了超时时间线程就不会阻塞在select方法上，会继续向下执行
            #  返回参数 分别对应监听到的读事件列表，写事件列表，异常事件列表
            rs, _, _ = select.select([self.tcp_socket], [], [], 40)
            for r in rs:  # 我们这里只监听读事件，所以只管读的返回句柄数组
                self.socket_lock.acquire()  # 在读取之前先加锁，锁定socket对象（sock是主线程和子线程的共享资源，锁定了sock就能保证子线程在使用sock时，主线程无法对sock进行操作）
                if not self.tcp_socket:  # 这里需要判断下，因为有可能在select后到加锁之间socket被关闭了
                    self.socket_lock.release()
                    break
                data = r.recv(1024)  # 读数据，按自己的方式读
                data1 = str(codecs.encode(data, 'hex_codec'), encoding='utf-8')
                self.log.logger.debug('收到服务器消息： '+str(data1))
                if data1[14:18] == '0051':
                    self.qidonggongzhan()
                elif data1[14:18] == '0052':
                    self.tingzhigongzhan()
                elif data1[14:18] == '0061':
                    self.PCfasongshengchanpici()
                elif data1[14:18] == '0062':
                    self.PCfasongshengchangongxu()
                elif data1[14:18] == '0091':
                    self.PCtongbuxinhao()
                elif data1[14:18] == '0053':
                    self.zantinggongzhan()
                elif data1[14:18] == '0054':
                    self.fuweigongzhan()
                elif data1[14:18] == '0055':
                    self.duqugongzhanyijiashuliang()
                elif data1[14:18] == '0056':
                    self.duqugongzhanxitongzhuangtai()
                elif data1[14:18] == '0057':
                    self.duqugongzhanbanbenxinxi()
                elif data1[14:18] == '0058':
                    self.duqugongzhanhelpzhiling()
                elif data1[14:18] == '0059':
                    self.shezhigongzhanqingyijia()
                elif data1[14:18] == '005A':
                    self.shezhigongzhantuichuqingyijia()
                elif data1[14:18] == '005B':
                    self.shezhijinruhuancunzhan()
                elif data1[14:18] == '005C':
                    self.shezhituichuhuancunzhan()
                elif data1[14:18] == '005D':
                    self.shezhihuancunzhanchuzhan()
                else:
                    self.log.logger.debug('无法识别该指令')
                self.socket_lock.release()  # 读取完成之后解锁，释放资源
                if not data:
                    self.log.logger.debug('server close')
                # else:
                #     self.log.logger.debug(data)

    #发送消息
    def sendmsg(self,msg):
        try:
            self.log.logger.debug('发送消息: ' + msg)
            self.tcp_socket.send(codecs.decode(msg, 'hex_codec'))
            data = self.tcp_socket.recv(1024)
            data1 = str(codecs.encode(data, 'hex_codec'), encoding='utf-8')
            self.log.logger.debug('接收消息: '+data1)
            return data1
        except Exception as ret:
            self.log.logger.debug('发送失败： '+str(ret))

    # 协各个议一样的部分
    def shezhixieyineirong(self,msg):
        msg.yuanmac = self.lineEdit.text().replace('-','')
        msg.benjishebeileixing = '03'
        minglingmas = ['0051','0052','0053','0054','0059','005A','005B','005C','005D','0061','0062']
        if msg.minglingma not in minglingmas:
            msg.chanxiandizhi = self.lineEdit_50.text()
            msg.gongzhandizhi = self.lineEdit_49.text()
        msgcrc = msg.jiamileixing + msg.benjishebeileixing + msg.yuanmac + msg.mudimac + \
                 msg.chanxiandizhi + msg.gongzhandizhi + msg.shebeiyunxingzhuangtai + msg.banbenhao + \
                 msg.bancihao + msg.fabuhao + msg.helpzhiling + msg.rfid + msg.qigangyalishifouzhengchang + \
                 msg.mac + msg.zhanneiyijiashuliang + msg.tiaoxingma + msg.deluleixing + \
                 msg.yuangongbianhao + msg.fangonggongxushuliang + msg.fangonggongxubianhao + \
                 msg.dingdanpicibianma + msg.guzhangma
        if len(str(hex(int(len(msgcrc) / 2)))[2:4]) == 2:
            msg.baowenchangdu = "00" + str(hex(int(len(msgcrc) / 2)))[2:4]
        else:
            msg.baowenchangdu = "000" + str(hex(int(len(msgcrc) / 2)))[2:4]
        msg.crc = crc16(msgcrc)
        send_msg = msg.getSendMsg(msg)
        return send_msg

    # PC控制MainControl启动(0x0051)
    def qidonggongzhan(self):
        self.log.logger.debug("启动")
        msg = tongxunxieyi()
        msg.minglingma = '0051'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("启动成功")

    #PC控制MainControl停止(0x0052)
    def tingzhigongzhan(self):
        self.log.logger.debug("停止")
        msg = tongxunxieyi()
        msg.minglingma = '0052'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("停止成功")

    # PC控制MainControl暂停(0x0053)
    def zantinggongzhan(self):
        self.log.logger.debug("暂停")
        msg = tongxunxieyi()
        msg.minglingma = '0053'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("暂停完成")

    # PC控制MainControl复位(0x0054)
    def fuweigongzhan(self):
        self.log.logger.debug("复位")
        msg = tongxunxieyi()
        msg.minglingma = '0054'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("复位完成")

    # PC读取MainControl工站衣架数量(0x0055)
    def duqugongzhanyijiashuliang(self):
        self.log.logger.debug("读取MainControl工站衣架数量")
        msg = tongxunxieyi()
        msg.zhanneiyijiashuliang = self.yijiashuliang
        msg.minglingma = '0055'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MainControl工站衣架数量完成")

    # PC读取MainControl系统状态(0x0056)
    def duqugongzhanxitongzhuangtai(self):
        self.log.logger.debug("读取MainControl系统状态")
        msg = tongxunxieyi()
        msg.shebeiyunxingzhuangtai = '01'
        msg.minglingma = '0056'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MainControl系统状态成功")

    # PC读取MainControl版本信息(0x0057)
    def duqugongzhanbanbenxinxi(self):
        self.log.logger.debug("读取MainControl版本信息")
        msg = tongxunxieyi()
        msg.banbenhao = 'V1'
        msg.bancihao = '01'
        msg.fabuhao = '01'
        msg.minglingma = '0057'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MainControl版本信息成功")

    # PC读取MainControl Help指令(0x0058)
    def duqugongzhanhelpzhiling(self):
        self.log.logger.debug("读取MainControl Help指令")
        msg = tongxunxieyi()
        msg.helpzhiling = '01'
        msg.minglingma = '0058'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MainControl Help指令成功")

    # PC设置MainControl清衣架模式(0x0059)
    def shezhigongzhanqingyijia(self):
        self.log.logger.debug("设置MainControl清衣架模式")
        msg = tongxunxieyi()
        msg.minglingma = '0059'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MainControl清衣架模式成功")

    # PC设置MainControl退出清衣架模式(0x005A)
    def shezhigongzhantuichuqingyijia(self):
        self.log.logger.debug("设置MainControl退出清衣架模式")
        msg = tongxunxieyi()
        msg.minglingma = '005A'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MainControl退出清衣架模式成功")

    # PC设置MainControl进入缓存站模式(0x005B)
    def shezhijinruhuancunzhan(self):
        self.log.logger.debug("设置MainControl进入缓存站模式")
        msg = tongxunxieyi()
        msg.minglingma = '005B'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MainControl进入缓存站模式成功")

    # PC设置MainControl退出缓存站模式(0x005C)
    def shezhituichuhuancunzhan(self):
        self.log.logger.debug("设置MainControl退出缓存站模式")
        msg = tongxunxieyi()
        msg.minglingma = '005C'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MainControl退出缓存站模式成功")

    # PC设置MainControl缓存站衣架出站(0x005D)
    def shezhihuancunzhanchuzhan(self):
        self.log.logger.debug("设置MainControl缓存站衣架出站")
        msg = tongxunxieyi()
        msg.minglingma = '005D'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MainControl缓存站衣架出站成功")

    #PC发送生产批次到MainControl(0x0061)
    def PCfasongshengchanpici(self):
        self.log.logger.debug("返回生产批次")
        msg = tongxunxieyi()
        msg.minglingma = '0061'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("返回生产批次完成")

    #PC发送生产工序到MainControl(0x0062)
    def PCfasongshengchangongxu(self):
        self.log.logger.debug("返回生产工序")
        msg = tongxunxieyi()
        msg.minglingma = '0062'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("返回生产工序完成")

    # 衣架绑定
    def bindyijia(self):
        self.log.logger.debug('衣架绑定')
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_23.text()
        msg.tiaoxingma = self.lineEdit_16.text()
        msg.minglingma = '0071'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-6:-4] == '01':
            self.lineEdit_9.setStyleSheet("color:green")
            self.lineEdit_9.setText('成功')
            self.log.logger.debug('衣架绑定成功')
        else:
            self.lineEdit_9.setStyleSheet("color:red")
            self.lineEdit_9.setText('失败')
            self.log.logger.debug('衣架绑定失败')

    # 员工上机申请
    def yuangongshangji(self):
        self.log.logger.debug('员工上机申请')
        msg = tongxunxieyi()
        msg.deluleixing = self.lineEdit_10.text()
        msg.yuangongbianhao = self.lineEdit_11.text()
        msg.minglingma = '0072'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-38:-36] == '01':
            self.lineEdit_3.setText(msg.yuangongbianhao)
            self.lineEdit_14.setStyleSheet("color:green")
            self.lineEdit_14.setText('成功')
            self.log.logger.debug('员工上机成功')
        else:
            self.lineEdit_14.setStyleSheet("color:red")
            self.lineEdit_14.setText('失败')
            self.log.logger.debug('员工上机失败')

    # 衣架进站申请
    def gotostation(self):
        self.log.logger.debug('衣架进站申请')
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_26.text()
        if self.yijiashuliang < 10:
            msg.zhanneiyijiashuliang = '0' + str(self.yijiashuliang)
        else:
            msg.zhanneiyijiashuliang = str(self.yijiashuliang)
        msg.minglingma = '0073'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-6:-4] == '01':
            self.lineEdit_8.setStyleSheet("color:green")
            self.lineEdit_8.setText('成功')
            self.log.logger.debug('进站申请成功')
        else:
            self.lineEdit_8.setStyleSheet("color:red")
            self.lineEdit_8.setText('失败')
            self.log.logger.debug('进站申请失败')

    # 衣架进站完成
    def gotostationok(self):
        self.log.logger.debug('衣架进站')
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_35.text()
        msg.minglingma = '0074'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.yijiashuliang += 1
        self.log.logger.debug('衣架进站完成   衣架数量：' + str(self.yijiashuliang))

    # 衣架出站申请
    def outstation(self):
        self.log.logger.debug('衣架出站信息')
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_38.text()
        msg.minglingma = '0075'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.log.logger.debug('衣架出站信息完成   衣架数量：' + str(self.yijiashuliang))

    # 衣架出站完成
    def outstationok(self):
        self.log.logger.debug('衣架出站')
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_30.text()
        if self.yijiashuliang < 10:
            msg.zhanneiyijiashuliang = '0' + str(self.yijiashuliang)
        else:
            msg.zhanneiyijiashuliang = str(self.yijiashuliang)
        msg.minglingma = '0076'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.chanliang += 1
        self.lineEdit_5.setText(str(self.chanliang))
        if self.yijiashuliang < 1:
            self.yijiashuliang = 0
        else:
            self.yijiashuliang -= 1
        self.log.logger.debug('衣架出站完成   衣架数量：' + str(self.yijiashuliang))

    #衣架返工申请
    def rework(self):
        self.log.logger.debug('衣架返工申请')
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_42.text()
        if len(str(int(len(self.lineEdit_51.text())/3)))==1:
            msg.fangonggongxushuliang = '0'+str(int(len(self.lineEdit_51.text())/3))
        else:
            msg.fangonggongxushuliang =int(len(self.lineEdit_51.text()) / 3)
        for i in range(0, len(self.lineEdit_51.text()), 3):
            a = hex(int(self.lineEdit_51.text()[i:i+3]))[2:4]
            if len(a) == 1:
                a='0'+a
            msg.fangonggongxubianhao = msg.fangonggongxubianhao+a
        msg.minglingma = '0077'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-6:-4] == '01':
            self.lineEdit_15.setStyleSheet("color:green")
            self.lineEdit_15.setText('成功')
            self.log.logger.debug('衣架返工成功')
        else:
            self.lineEdit_15.setStyleSheet("color:red")
            self.lineEdit_15.setText('失败')
            self.log.logger.debug('衣架返工失败')

    # 工站心跳
    def xintiao(self):
        while True:
            self.log.logger.debug('工站心跳')
            msg = tongxunxieyi()
            msg.minglingma = '0078'
            msg.gongnengma = '01'
            if self.yijiashuliang < 10:
                msg.zhanneiyijiashuliang = '0'+str(self.yijiashuliang)
            else:
                msg.zhanneiyijiashuliang = str(self.yijiashuliang)
            msgs = self.shezhixieyineirong(msg)
            self.sendmsg(msgs)
            self.lineEdit_22.setText(str(self.yijiashuliang))
            self.log.logger.debug('工站心跳完成   衣架数量：' + str(self.yijiashuliang))
            time.sleep(10)

    # 员工下机申请
    def yuangongxiaji(self):
        self.log.logger.debug('员工下机申请')
        msg = tongxunxieyi()
        msg.deluleixing = self.lineEdit_13.text()
        msg.yuangongbianhao = self.lineEdit_12.text()
        msg.minglingma = '0079'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-6:-4] == '01':
            self.lineEdit_3.setText('')
            self.lineEdit_18.setStyleSheet("color:green")
            self.lineEdit_18.setText('成功')
            self.log.logger.debug('员工下机成功')
        else:
            self.lineEdit_18.setStyleSheet("color:red")
            self.lineEdit_18.setText('失败')
            self.log.logger.debug('员工下机失败')

    # 生产订单申请
    def order(self):
        self.log.logger.debug('生产订单申请')
        msg = tongxunxieyi()
        for i in range(len(self.lineEdit_17.text())):
            b = self.lineEdit_17.text()[i:i + 1]
            msg.dingdanpicibianma = msg.dingdanpicibianma + hex(ord(b))[2:4]
        msg.minglingma = '0081'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.log.logger.debug('生产订单申请成功')

    # 生产批次确认
    def pici(self):
        self.log.logger.debug('生产批次确认')
        msg = tongxunxieyi()
        for i in range(len(self.lineEdit_17.text())):
            b = self.lineEdit_17.text()[i:i + 1]
            msg.dingdanpicibianma = msg.dingdanpicibianma + hex(ord(b))[2:4]
        msg.minglingma = '0082'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.log.logger.debug('生产批次确认完成')

    #生产工序申请
    def shengchangongxu(self):
        self.log.logger.debug('生产工序申请')
        msg = tongxunxieyi()
        msg.minglingma = '0083'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.log.logger.debug('生产工序申请完成')


    # 注册工站
    def registe(self):
        # 注册的消息内容
        self.connect()
        self.log.logger.debug('注册工站')
        msg = tongxunxieyi()
        msg.mac = self.lineEdit.text().replace('-','')
        msg.minglingma = '0090'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-6:-4] == '01':
            self.lineEdit_19.setStyleSheet("color:green")
            self.lineEdit_19.setText('成功')
            self.log.logger.debug('注册成功')
            faxintiao = threading.Thread(target=self.xintiao)
            faxintiao.start()
        else:
            self.lineEdit_19.setStyleSheet("color:red")
            self.lineEdit_19.setText('失败')
            self.log.logger.debug('注册失败')

    # PC转发同步信号到MainControl(0x0091)
    def PCtongbuxinhao(self):
        self.log.logger.debug("PC转发同步信号到MainControl")

    # MotorLan、MainControl发送异常告警(0x00F1)
    def yichangjinggao(self):
        self.log.logger.debug('异常警告')
        msg = tongxunxieyi()
        msg.minglingma = '00F1'
        msg.gongnengma = '01'
        msg.guzhangma = self.lineEdit_21.text()
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.log.logger.debug('异常警告完成')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = gongzhan()
    win.show()
    sys.exit(app.exec_())