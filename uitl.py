import logging
import time,csv
from binascii import *
from logging import handlers

from crcmod import *

# 读取csv里的数据
def read_data():
    with open('data.csv', 'r', encoding='utf-8')as csvfile:
        read = csv.reader(csvfile)
        rows = [row for row in read]
        return rows

#crc 16 1021校验

def crc16(read):
    crc16 =crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    readcrcout = hex(crc16(unhexlify(read))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')  # 位数不足补0
        crc_data = "".join(str_list[2:])
        # log.debug(crc_data)
        return crc_data
    else:
        crc_data = "".join(str_list[2:])
        # log.debug(crc_data)
        return crc_data

# 日志
class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='debug',when='D',backCount=3,fmt='%(asctime)s - %(levelname)s - %(message)s'):
        fliename_1 = time.strftime("%Y-%m-%d-", time.localtime())
        filename_2 = 'log/'+fliename_1+filename
        self.logger = logging.getLogger(filename_2)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename_2,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)

