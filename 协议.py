#-*- coding:utf-8 -*-

'''
协议：
PC控制MotorLan启动(0x0001)、停止(0x0002)、暂停(0x0003)、复位(0x0004)
PC读取MotorLan系统状态(0x0005)，PC读取MotorLan版本信息(0x0006)
PC读取MotorLan Help指令(0x0007)
PC设置MotorLan清衣架模式(0x0008),退出清衣架模式(0x0009)
MotorLan发送回归RFID扫码(0x0031)
MotorLan发送推杆检测信号(0x0032)
MotorLan发送气缸压力(0x0033)
MotorLan发送心跳监测(0x0034)
PC控制MotorLan注册(0x0090)
工站控制，启动(0x0051)、停止(0x0052)、暂停(0x0053)、复位(0x0054)
PC读取MainControl工站衣架数量(0x0055)
PC读取MainControl系统状态(0x0056)
PC读取MainControl版本信息(0x0057)
PC读取MainControl Help指令(0x0058)
PC设置MainControl清衣架模式(0x0059),退出清衣架模式(0x005A),进入缓存站模式(0x005B),退出缓存站模式(0x005C),缓存站衣架出站(0x005D)
PC发送生产批次到MainControl(0x0061)
PC发送工序批次到MainControl(0x0062)
MainControl发送衣架、条码绑定申请(挂片站)(0x0071)
MainControl发送员工上机申请(0x0072)
MainControl发送衣架进站申请(0x0073)
MainControl发送衣架进站完成(0x0074)
MainControl发送衣架出站信息(0x0075)
MainControl发送衣架出站完成(0x0076)
MainControl发送衣架返工申请(0x0077)
MainControl发送心跳监测(0x0078)
MainControl发送员工下机申请(0x0079)
MainControl发送生产订单申请(0x0081)
MainControl发送当前生产批次确认(0x0082)
MainControl发送生产工序申请(0x0083)
MainControl发送工站生产实况查询申请(0x0084)
MainControl服务器网络注册(0x0090)
'''

class tongxunxieyi():
    def __init__(self):
        self.tongbutou = 'a55aa55a'
        self.gongnengma = ''
        self.baowenchangdu = ''
        self.minglingma = ''
        self.jiamileixing = '00'
        self.benjishebeileixing = ''
        self.yuanmac=''
        self.mudimac='FA163EC8C359'
        self.chanxiandizhi = ''
        self.gongzhandizhi = ''
        self.shebeiyunxingzhuangtai = ''
        self.banbenhao = ''
        self.bancihao = ''
        self.fabuhao = ''
        self.helpzhiling = ''
        self.rfid = ''
        self.qigangyalishifouzhengchang = ''
        self.mac = ''
        self.zhanneiyijiashuliang = ''
        self.tiaoxingma = ''
        self.deluleixing = ''
        self.yuangongbianhao = ''
        self.fangonggongxushuliang = ''
        self.fangonggongxubianhao = ''
        self.dingdanpicibianma = ''
        self.guzhangma = ''
        self.crc=''

    def getSendMsg(self, ac):
        msg = ac.tongbutou+ac.gongnengma+ac.baowenchangdu+ac.minglingma+ac.jiamileixing+ac.benjishebeileixing+\
              ac.yuanmac+ac.mudimac+ac.chanxiandizhi+ac.gongzhandizhi+ac.shebeiyunxingzhuangtai+ac.banbenhao+ac.bancihao+\
              ac.fabuhao+ac.helpzhiling+ac.rfid+ac.qigangyalishifouzhengchang+ac.mac+ac.zhanneiyijiashuliang+ac.tiaoxingma+\
              ac.deluleixing+ac.yuangongbianhao+ac.fangonggongxushuliang+ac.fangonggongxubianhao+ac.dingdanpicibianma+\
              ac.guzhangma+ac.crc
        return msg





