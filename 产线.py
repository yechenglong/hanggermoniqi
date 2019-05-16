import codecs
import select
import sys
import threading
from PyQt5 import QtWidgets
import socket,time
import 产线UI
from  uitl import *
from 协议 import *

'''
MotorLan模拟器 v1.0.0
'''
class MotorLan(QtWidgets.QWidget, 产线UI.Ui_Form):
    def __init__(self):
        super(MotorLan, self).__init__()
        self.setupUi(self)
        self.log = Logger('产线.log')
        self.ip = self.lineEdit_6.text()
        self.port = int(self.lineEdit_7.text())
        self.ADDR = (self.ip,self.port)
        self.tcp_socket = None
        self.action()
        self.yijiashuliang=0
        self.socket_lock = threading.Lock()



    #点击按钮
    def action(self):

        # self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.registe)
        self.pushButton_3.clicked.connect(self.fasonghuiguirfidsaoma)
        self.pushButton_4.clicked.connect(self.fasongqigangyali)
        self.pushButton_5.clicked.connect(self.fasongtuiganjiancexinhao)
        self.pushButton_6.clicked.connect(self.xintiao)
        self.pushButton_7.clicked.connect(self.yichangjinggao)
        self.pushButton.clicked.connect(self.close)

    #关闭连接
    def close(self):
        self.socket_lock.acquire()
        self.tcp_socket.close()
        self.tcp_socket = None
        self.socket_lock.release()

    #连接吊挂服务器
    def connect(self):
        self.tcp_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
        try:
            # self.tcp_socket.bind(('192.168.35.219',1024))
            self.tcp_socket.connect(self.ADDR)
            # 创建一个线程去读取数据
            read_thread = threading.Thread(target=self.recvmsg)
            read_thread.setDaemon(True)
            read_thread.start()
            # read_thread.join()

        except Exception as ret:
            self.log.logger.debug('连接失败： '+str(ret))
        self.log.logger.debug('连接吊挂服务器')

    #接收服务端数据
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
            rs,_,_ = select.select([self.tcp_socket], [], [], 10)
            for r in rs:  # 我们这里只监听读事件，所以只管读的返回句柄数组
                self.socket_lock.acquire() # 在读取之前先加锁，锁定socket对象（sock是主线程和子线程的共享资源，锁定了sock就能保证子线程在使用sock时，主线程无法对sock进行操作）
                if not self.tcp_socket: # 这里需要判断下，因为有可能在select后到加锁之间socket被关闭了
                    self.socket_lock.release()
                    break
                data = r.recv(1024) # 读数据，按自己的方式读
                data1 = str(codecs.encode(data, 'hex_codec'), encoding='utf-8')
                self.log.logger.debug('收到服务器消息： ' + str(data1))
                if data1[14:18] == '0001':
                    self.qidong()
                elif data1[14:18] == '0002':
                    self.tingzhi()
                elif data1[14:18] == '0003':
                    self.zanting()
                elif data1[14:18] == '0004':
                    self.fuwei()
                elif data1[14:18] == '0005':
                    self.duquchanxianxitongzhaungtai()
                elif data1[14:18] == '0006':
                    self.duquchanxianbanbenxinxi()
                elif data1[14:18] == '0007':
                    self.duquchanxianhelpzhiling()
                elif data1[14:18] == '0008':
                    self.shezhichanxianqingyijia()
                elif data1[14:18] == '0009':
                    self.shezhichanxiantuichuqingyijia()
                else:
                    pass
                self.socket_lock.release() # 读取完成之后解锁，释放资源
                if not data:
                    self.log.logger.debug('server close')
                # else:
                #     self.log.logger.debug (data)



    #发送消息
    def sendmsg(self,msg):
        try:
            self.log.logger.debug('发送消息: ' + msg)
            self.tcp_socket.send(codecs.decode(msg, 'hex_codec'))
            data = self.tcp_socket.recv(1024)
            data1 = str(codecs.encode(data, 'hex_codec'), encoding='utf-8')
            self.log.logger.debug('接收消息: ' + data1)
            return data1
        except Exception as ret:
            self.log.logger.debug('发送失败： '+str(ret))

    # 协各个议一样的部分
    def shezhixieyineirong(self,msg): 
        msg.yuanmac = self.lineEdit.text().replace('-','')
        msg.benjishebeileixing = '02'
        minglingmas = ['0001','0002','0003','0004','0008','0009']
        if msg.minglingma not in minglingmas:
            msg.chanxiandizhi = self.lineEdit_50.text()
            msg.gongzhandizhi = self.lineEdit_49.text()
        msgcrc = msg.jiamileixing+msg.benjishebeileixing+msg.yuanmac+msg.mudimac+\
                 msg.chanxiandizhi+msg.gongzhandizhi+msg.shebeiyunxingzhuangtai+msg.banbenhao+\
                 msg.bancihao+msg.fabuhao+msg.helpzhiling+msg.rfid+msg.qigangyalishifouzhengchang+\
                 msg.mac+msg.zhanneiyijiashuliang+msg.tiaoxingma+msg.deluleixing+\
                 msg.yuangongbianhao+msg.fangonggongxushuliang+msg.fangonggongxubianhao+\
                 msg.dingdanpicibianma+msg.guzhangma
        if len(str(hex(int(len(msgcrc) / 2)))[2:4]) == 2:
            msg.baowenchangdu = "00" + str(hex(int(len(msgcrc) / 2)))[2:4]
        else:
            msg.baowenchangdu = "000" + str(hex(int(len(msgcrc) / 2)))[2:4]
        msg.crc = crc16(msgcrc)
        send_msg = msg.getSendMsg(msg)
        return send_msg

    # 注册产线
    def registe(self):
        # 注册的消息内容
        self.connect()
        self.log.logger.debug('注册产线')
        msg = tongxunxieyi()
        msg.mac = self.lineEdit.text().replace('-','')
        msg.minglingma = '0090'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        if self.sendmsg(msgs)[-6:-4] == '01':
            self.lineEdit_2.setStyleSheet("color:green")
            self.lineEdit_2.setText('成功')
            self.log.logger.debug('注册成功')
            faxintiao = threading.Thread(target=self.xintiao)
            faxintiao.start()
            # faxintiao.join()
        else:
            self.lineEdit_2.setStyleSheet("color:red")
            self.lineEdit_2.setText('失败')
            self.log.logger.debug('注册失败')



    # PC控制MotorLan启动(0x0001)
    def qidong(self):
        self.log.logger.debug("启动")
        msg = tongxunxieyi()
        msg.minglingma = '0001'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("启动成功")

    # PC控制MotorLan停止(0x0002)
    def tingzhi(self):
        self.log.logger.debug("停止")
        msg = tongxunxieyi()
        msg.minglingma = '0002'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("停止成功")

    # PC控制MotorLan暂停(0x0003)
    def zanting(self):
        self.log.logger.debug("暂停")
        msg = tongxunxieyi()
        msg.minglingma = '0003'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("暂停成功")

    # PC控制MotorLan复位(0x0004)
    def fuwei(self):
        self.log.logger.debug("复位")
        msg = tongxunxieyi()
        msg.minglingma = '0004'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("复位成功")

    # PC读取MotorLan系统状态(0x0005)
    def duquchanxianxitongzhaungtai(self):
        self.log.logger.debug("读取MotorLan系统状态")
        msg = tongxunxieyi()
        msg.shebeiyunxingzhuangtai = '01'
        msg.minglingma = '0005'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MotorLan系统状态成功")

    # PC读取MotorLan版本信息(0x0006)
    def duquchanxianbanbenxinxi(self):
        self.log.logger.debug("读取MotorLan版本信息")
        msg = tongxunxieyi()
        msg.banbenhao= 'V1'
        msg.bancihao = '01'
        msg.fabuhao = '01'
        msg.minglingma = '0006'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MotorLan版本信息成功")

    # PC读取MotorLan Help指令(0x0007)
    def duquchanxianhelpzhiling(self):
        self.log.logger.debug("读取MotorLan Help指令")
        msg = tongxunxieyi()
        msg.helpzhiling= '01'
        msg.minglingma = '0007'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("读取MotorLan Help指令成功")

    # PC设置MotorLan清衣架模式(0x0008)
    def shezhichanxianqingyijia(self):
        self.log.logger.debug("设置MotorLan清衣架模式")
        msg = tongxunxieyi()
        msg.minglingma = '0008'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MotorLan清衣架模式成功")

    # PC设置MotorLan退出清衣架模式(0x0009)
    def shezhichanxiantuichuqingyijia(self):
        self.log.logger.debug("设置MotorLan退出清衣架模式")
        msg = tongxunxieyi()
        msg.minglingma = '0009'
        msg.gongnengma = '7F'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("设置MotorLan退出清衣架模式成功")

    # MotorLan发送回归RFID扫码(0x0031)
    def fasonghuiguirfidsaoma(self):
        self.log.logger.debug("发送回归RFID扫码")
        msg = tongxunxieyi()
        msg.rfid = self.lineEdit_4.text()
        msg.minglingma = '0031'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("发送回归RFID扫码成功")

    #MotorLan发送推杆检测信号(0x0032)
    def fasongtuiganjiancexinhao(self):
        self.log.logger.debug("发送推杆检测信号")
        msg = tongxunxieyi()
        msg.minglingma = '0032'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("发送推杆检测信号成功")

    #MotorLan发送气缸压力(0x0033)
    def fasongqigangyali(self):
        self.log.logger.debug("发送气缸压力")
        msg = tongxunxieyi()
        msg.qigangyalishifouzhengchang = self.lineEdit_9.text()
        msg.minglingma = '0033'
        msg.gongnengma = '01'
        msgs = self.shezhixieyineirong(msg)
        self.log.logger.debug(msgs)
        self.tcp_socket.send(codecs.decode(msgs, 'hex_codec'))
        self.log.logger.debug("发送气缸压力成功")

    # MotorLan发送产线心跳(0x0034)
    def xintiao(self):
        while True:
            self.log.logger.debug('产线心跳开始')
            msg = tongxunxieyi()
            # msg.mac = self.lineEdit.text().replace('-','')
            msg.minglingma = '0034'
            msg.gongnengma = '01'
            msgs = self.shezhixieyineirong(msg)
            time.sleep(3)
            self.sendmsg(msgs)
            self.log.logger.debug('产线心跳结束')

    # MotorLan、MainControl发送异常告警(0x00F1)
    def yichangjinggao(self):
        self.log.logger.debug('异常警告')
        msg = tongxunxieyi()
        msg.minglingma = '00F1'
        msg.gongnengma = '01'
        msg.guzhangma = self.lineEdit_3.text()
        msgs = self.shezhixieyineirong(msg)
        self.sendmsg(msgs)
        self.log.logger.debug('异常警告完成')



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MotorLan()
    win.show()
    sys.exit(app.exec_())