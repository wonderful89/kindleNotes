# coding : utf-8
# Author : VinylChloride
# Version : 1.0 Stable
# 主要处理文件

from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os
import sys
import sqlite3
import json
import getopt

# Define Log Moudle
import logging

os.system('[ ! -d "logs" ] && mkdir logs')
logFileName = "logs/" + (str(time.ctime()) + "_LOG.log").replace(":", "-").replace(
    " ", ""
)  # 日志文件名
logger = logging.getLogger(__name__)
logFormat = logging.Formatter("%(asctime)s %(levelname)-8s: %(message)s")
logHandler = logging.FileHandler(logFileName)
logHandler.setFormatter(logFormat)
logger.addHandler(logHandler)
# 日志级别
logger.setLevel(logging.DEBUG)


"""
	Database Col:
		Name TEXT , In this program is unicode.
		PanLink TEXT , In this program is string.
		PanPwd TEXT , In this program is string.
		isTransfered INT , In this program is bool.
	
"""


class dbOperation(object):
    # runMode:
    # 	0 : Normal Mode
    # 	-1 : Only The Error Link (isTransfered == -1)
    def __init__(self, dbFile=None, runMode=0):
        if not dbFile:
            logger.critical("Database Not Found.Exiting...")
            print("Database Not Found.Exiting...")
            sys.exit(1)
        self.dbConn = sqlite3.connect(dbFile)
        if not self.dbConn:
            logger.critical("Can not connect to databse,Exiting...")
            print("Can not connect to databse,Exiting...")
            sys.exit(1)
        self.dbCursor = self.dbConn.cursor()
        if not self.dbCursor:
            logger.critical("Can not get databse cursor,Exiting...")
            print(("Can not get databse cursor,Exiting..."))
            sys.exit(1)
        logger.info("Databse Initilized.")

        # Resources List :
        # 	element is dict
        # 	dict contains key:
        # 		Name , unicode
        # 		PanLink , string
        # 		PanPwd , string

        if runMode != 0:
            self.__runMode = -1
        else:
            self.__runMode = 0

        self.resList = []

        # self.__getDataFromDB()

    def getDataFromDB2(self, tableName=""):
        resDict = {}
        resDict["Name"] = "穿越者穿越了穿越者XX"
        resDict["PanLink"] = str("https://pan.baidu.com/s/1LjcHGwdo6bV-aoIDYy_qHA")
        resDict["PanPwd"] = str("eaq6")
        self.resList.append(resDict)

    def getDataFromDB(self, tableName=""):
        try:
            # 			print ("TableName : %s" % tableName)
            if tableName == "":
                return -1
            for dbItem in list(
                self.dbCursor.execute("SELECT * FROM %s" % tableName)
            ):  # dbItem Type : tuple
                # 	print (dbItem)
                if dbItem[3] != self.__runMode:
                    continue
                resDict = {}
                resDict["Name"] = dbItem[0]
                resDict["PanLink"] = str(dbItem[1])
                resDict["PanPwd"] = str(dbItem[2])
                self.resList.append(resDict)
        except:
            logger.exception("Error On Reading Database")
            print("Error On Reading Database , Please Check Log File.")
            sys.exit(1)


"""
Config.json:
	{
		"codeTextBoxXPath" : "XXX", #By XPath
		"codeEnterBtnXPath" : "XXX",	#By XPath
		"transferBtnClassName" : "XXX",
		"checkBoxClassName" : "XXX"

	}

"""


# MainFramework 类继承自 dbOperation。
class MainFramework(dbOperation):
    def __init__(self, dbFile=None, runMode=0, guiMode=0):

        # Parent:
        # 	self.resList
        # 	self.__getDataFromDB()

        dbOperation.__init__(self, dbFile, runMode)

        self.__webDri = None
        self.linkCount = 0
        self.errLinkCount = 0
        self.errLinkList = []
        self.bannedLinkCount = 0
        self.bannedLinkList = []
        self.doneLinkCount = 0

        self.tableName = ""

        self.__codeTextBoxXPath = ""
        self.__codeEnterBtnXPath = ""
        self.__transferBtnClassName = ""
        self.__transferBtnSelector = ""
        self.__checkBoxClassName = ""
        self.__fileTreeNodeClassName = ""
        self.__fileTreeDialogXPath = ""
        self.__destnationPath = ""
        self.__fileTreeConfirmClassName = ""
        self.__notFoundID = ""
        self.__baidu = {}

        self.__loadConfig()
        self.getDataFromDB(self.tableName)  # 获取列表数据
        self.linkCount = len(self.resList)

        if guiMode == 0:
            self.__guiMode = 0
        else:
            self.__guiMode = 1

        if self.linkCount == 0:
            print("No Link Found , Exiting...")
            logger.info("No Link Found , Exiting...")
            sys.exit(0)
        print("Found %d Links." % self.linkCount)
        logger.info("Found %d Links." % self.linkCount)
        print("Starting Chrome.")
        logger.info("Starting Chrome.")
        self.__webDri = webdriver.Chrome()  # This Script Only Tested On Chrome
        logger.info("Chrome Started.")

    # Resources List :
    # 	element is dict
    # 	dict contains key:
    # 		Name , unicode
    # 		PanLink , string
    # 		PanPwd , string
    # 主要入口
    def run(self, guiCallback=None):
        self.__login()
        for linkItem in self.resList:
            print("linkItem = {}".format(linkItem))
            resName = linkItem["Name"]
            panPwd = linkItem["PanPwd"]
            panLink = linkItem["PanLink"]
            retCode = self.__transfer(panLink, panPwd)
            if retCode == -1:
                self.__updateLinkStatus(panLink, -1)
                print("Error On Transfer Link : %s" % panLink)
                logger.error("Error On Transfer Link : %s" % panLink)
                self.errLinkList.append(panLink)
                self.errLinkCount += 1
                if guiCallback != None:
                    guiCallback(panLink, -1)
                continue
            elif retCode == -2:
                logger.warn("Link %s Has Been Banned." % panLink)
                print("Link %s Has Been Banned." % panLink)
                self.__updateLinkStatus(panLink, -2)
                self.bannedLinkList.append(panLink)
                self.bannedLinkCount += 1
                if guiCallback != None:
                    guiCallback(panLink, -2)
                continue
            self.__updateLinkStatus(panLink, 1)
            self.doneLinkCount += 1
            if guiCallback != None:
                guiCallback(panLink, 1)
            time.sleep(1)
        time.sleep(5)
        self.__webDri.quit()

    # 进行每一项转存的操作
    def __transfer(self, panLink, panPwd):
        print("Starting Transfer With Link : %s , Pwd : %s" % (panLink, panPwd))
        logger.info("Starting Transfer With Link : %s , Pwd : %s" % (panLink, panPwd))
        self.__webDri.get(panLink)
        try:
            # 查找确认的按钮
            enterCodeBtn = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__codeEnterBtnXPath))
            )
        except common.exceptions.TimeoutException:
            try:
                # 这里异常处理中做了什么？用id 又进行查找？
                WebDriverWait(self.__webDri, 5).until(
                    EC.presence_of_element_located((By.ID, self.__notFoundID))
                )
                return -2
            except common.exceptions.TimeoutException:
                pass

            logger.exception("Locate Code Enter Button Timeout.")
            print("Locate Code Enter Button Timeout.")
            return -1

        logger.debug("Code Enter Button Raw Data : %s" % str(enterCodeBtn))

        try:
            # 查找输入校验码的输入框元素
            codeTextBox = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__codeTextBoxXPath))
            )
        except common.exceptions.TimeoutException:
            logger.exception("Locate Code Text Box Timeout.")
            print(("Locate Code Text Box Timeout."))
            return -1

        logger.debug("Code Text Box Raw Data : %s" % str(codeTextBox))

        if codeTextBox != None:
            # 向输入框元素中填入校验码
            codeTextBox.send_keys(panPwd)
            logger.debug("Code %s Has Enter" % panPwd)
            # 点击确定
            enterCodeBtn.click()
        else:
            logger.error("Can not find code text box.")
            print("Can not find code text box.")
            return -1

        try:
            # 处理多选框的情况。这里没有考虑
            checkBox = WebDriverWait(self.__webDri, 2).until(
                EC.presence_of_element_located((By.XPATH, self.__checkBoxClassName))
            )
        except common.exceptions.TimeoutException:
            logger.exception("No Check Box Found Or Page Load Timeout.")
            print("No Check Box Found Or Page Load Timeout.")
        except:
            logger.exception("Error On Locating Check Box.")
            return -1
        else:
            logger.info("Located Check Box.")
            logger.debug("Check Box Raw Data : %s" % checkBox)
            checkBox.click()

        transferBtn = None
        # 转存按钮
        try:
            # 查找转存按钮元素
            transferBtn = WebDriverWait(self.__webDri, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.__transferBtnSelector)
                )
            )
        except common.exceptions.TimeoutException:
            logger.exception("Locate Transfer Button Timeout.")
            print("Locate Transfer Button Timeout.")

        if transferBtn == None:
            try:
                print("再次去选择transferBtn")
                selector2 = "#layoutMain > div.frame-content > div.module-share-header > div > div.slide-show-right > div > div > div.x-button-box > a.g-button.g-button-blue > span > span"
                transferBtn = WebDriverWait(self.__webDri, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector2))
                )
            except common.exceptions.TimeoutException:
                logger.exception("Locate Transfer Button Timeout.")
                print("Locate Transfer Button Timeout.")

        logger.debug("Transfer Button Raw Data : %s" % str(transferBtn))

        if transferBtn == None:
            logger.error("Transfer Button Not Found.")
            print("Transfer Button Not Found.")
            return -1
        """
		for btnItem in transferBtn:
			print repr(btnItem.get_attribute("title"))
			print btnItem.get_attribute("title")
			#Waiting for get raw unicode data
		"""
        logger.info("Located Transfer Button.")
        try:
            # 点击转存按钮
            transferBtn.click()
        except:
            logger.exception("Error On Clinking Transfer Button.")
            print("Error On Clinking Transfer Button.")
            return -1

        try:
            WebDriverWait(self.__webDri, 5).until(
                EC.presence_of_element_located((By.XPATH, self.__fileTreeDialogXPath))
            )
        except common.exceptions.TimeoutException:
            logger.error("Locate File Tree Dialog Timeout.")
            print("Locate File Tree Dialog Timeout.")
            return -1

        try:
            path = ""
            nodeList = self.__destnationPath.split("/")
            for i in range(1, len(nodeList)):
                path += "/" + nodeList[i]
                logger.debug("Current Path : %s " % path)
                if self.__findPath(path):  # 找到后，内部进行了选中
                    continue
                else:
                    logger.error("Error On Link : %s panLink")
                    print("Error On Link : %s panLink")
                    return -1
            """
			try:
				pathConfirmBtn = WebDriverWait(self.__webDri,2).until(
					EC.presence_of_element_located(
						(By.XPATH,self.__fileTreeConfirmBtnXPath)
					)
				)
			except common.exceptions.TimeoutException:
				logger.error("Can not locate path confirmation buttion.")
				print ("Can not locate path confirmation buttion.")
				return -1

			pathConfirmBtn.click()


			return
			"""
        except:
            logger.exception("Error On Finding Path.")
            print("Error On Finding Path.")
            return -1

        retryCount = 0
        while True:
            try:
                # 查找(确认,取消，新建文件夹）面板
                pathConfirmBtn = self.__webDri.find_elements_by_class_name(
                    self.__fileTreeConfirmBtnClassName
                )
            except common.exceptions.NoSuchElementException:
                retryCount += 1
                if retryCount > 4:
                    logger.error("Locate Path Confirmation Button Timeout.")
                    print("Locate Path Confirmation Button Timeout.")
                    return -1
                logger.warn(
                    "Can not Locate Path Confirmation Button , Trying %d Times."
                    % retryCount
                )
                time.sleep(1)
                continue
            except:
                logger.exception("Error On Locating Path Confirmation Button.")
                print("Error On Locating Path Confirmation Button.")
                return -1
            break

        for tmpItem in pathConfirmBtn:
            if tmpItem.get_attribute("title") == u"\u786e\u5b9a":  # 确定
                pathConfirmBtn = tmpItem  # 查找(确认) 元素
                break
        pathConfirmBtn.click()  # 点击确认完成缓存

    # 查找存储后目标的目录
    def __findPath(self, Path):
        try:
            isFound = False
            retryCount = 0
            while True:
                try:
                    # 所有文件目录树的节点
                    nodePaths = self.__webDri.find_elements_by_class_name(
                        self.__fileTreeNodeClassName
                    )
                    if retryCount > 3:
                        logger.error("Can not loacte destnation path %s" % Path)
                        print("Can not loacte destnation path %s" % Path)
                        return isFound
                    if len(nodePaths) == 1:
                        time.sleep(0.5)
                        retryCount += 1
                        continue
                    for nodeItem in nodePaths:
                        if nodeItem.get_attribute("node-path") == Path:
                            print("Located Destnation Path %s " % Path)
                            logger.info("Located Destnation Path %s " % Path)
                            logger.debug(
                                "Destnation Path Raw Data : %s" % str(nodeItem)
                            )
                            # 找到节点，进行点击
                            nodeItem.click()
                            isFound = True
                            return isFound
                    if not isFound:
                        retryCount += 1
                        time.sleep(1)
                except common.exceptions.NoSuchElementException:
                    retryCount += 1
                    if retryCount > 4:
                        logger.error("Destnation path %s not found." % Path)
                        print("Destnation path %s not found." % Path)
                        return False
                    logger.debug(
                        "Destnation Path Not Found , Trying %d Times" % retryCount
                    )
                    time.sleep(0.5)
                    continue
        except:
            logger.exception("Error On Locate Path %s " % Path)
            return False

    # 登录操作，这里还是手动，可以改成自动
    # 登录之后， input接收按键后进行下一步
    def __login(self):
        self.__loginBaidu()
        # self.__webDri.get("https://pan.baidu.com/")
        # print("Please Confirm Login And Switch The Page To Recyle Bin.")
        # input("[?] Hit The Fucking Enter When You Ready.")
        # logger.info("User Login.")
        # print("User Login.")

    def __loginBaidu(self):
        self.__webDri.get("https://pan.baidu.com/")
        delayDuration = 3
        time.sleep(delayDuration)
        try:
            # 查找切换登录方式按钮
            changeBtn = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__baidu["changeSecret"]))
            )
        except common.exceptions.TimeoutException:
            logger.exception("切换登录方式按钮 Timeout.")
            print(("切换登录方式按钮 Timeout."))
            return -1
        logger.debug("changeBtn Data : %s" % str(changeBtn))
        if changeBtn != None:
            changeBtn.click()

        time.sleep(delayDuration)
        try:
            # 查找账号输入框
            idBox = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__baidu["idBox"]))
            )
        except common.exceptions.TimeoutException:
            logger.exception("idBox Timeout.")
            print(("idBox Timeout."))
            return -1
        logger.debug("idBox Raw Data : %s" % str(idBox))
        if idBox != None:
            idBox.send_keys(self.__baidu["id"])

        time.sleep(delayDuration)
        try:
            # 查找账号输入框
            secretBox = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__baidu["secretBox"]))
            )
        except common.exceptions.TimeoutException:
            logger.exception("idBox Timeout.")
            print(("secretBox Timeout."))
            return -1
        logger.debug("secretBox Raw Data : %s" % str(secretBox))
        if secretBox != None:
            secretBox.send_keys(self.__baidu["secret"])

        time.sleep(delayDuration)
        try:
            # 查找确认登录按钮
            okBtn = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__baidu["ok"]))
            )
        except common.exceptions.TimeoutException:
            logger.exception("okBtn Timeout.")
            print(("okBtn Timeout."))
            return -1
        logger.debug("okBtn Raw Data : %s" % str(okBtn))
        if okBtn != None:
            okBtn.click()

        # 需要手动加入验证框
        time.sleep(8)
        time.sleep(delayDuration)
        try:
            # 介绍页，可能没有
            introBtn = WebDriverWait(self.__webDri, 3).until(
                EC.presence_of_element_located((By.XPATH, self.__baidu["intro"]))
            )
        except common.exceptions.TimeoutException:
            logger.exception("introBtn Timeout.")
            print(("introBtn Timeout."))
            return -1
        logger.debug("introBtn Raw Data : %s" % str(okBtn))
        if introBtn != None:
            introBtn.click()

    def __loadConfig(self):
        jsonData = {}
        with open("config.json") as configFile:
            jsonData = json.load(configFile)
            configFile.close()
        try:
            self.tableName = jsonData["dbTableName"]
            self.__codeTextBoxXPath = jsonData["codeTextBoxXPath"]
            self.__codeEnterBtnXPath = jsonData["codeEnterBtnXPath"]
            self.__transferBtnClassName = jsonData["transferBtnClassName"]
            self.__transferBtnSelector = jsonData["transferBtnSelector"]
            self.__checkBoxClassName = jsonData["checkBoxClassName"]
            self.__fileTreeDialogXPath = jsonData["fileTreeDialogXPath"]
            # 	self.__fileTreeConfirmBtnXPath = jsonData["fileTreeConfirmBtnXPath"]
            self.__fileTreeNodeClassName = jsonData["fileTreeNodeClassName"]
            self.__destnationPath = jsonData["destnationPath"]
            self.__fileTreeConfirmBtnClassName = jsonData["fileTreeConfirmBtnClassName"]
            self.__notFoundID = jsonData["notFoundID"]
            # self.__baidu["id"] = jsonData["baiduId"]
            # self.__baidu["secret"] = jsonData["baiduS"]
            self.__baidu["idBox"] = jsonData["baiduIdXpath"]
            self.__baidu["secretBox"] = jsonData["baiduSXpath"]
            self.__baidu["changeSecret"] = jsonData["baiduChangeSecret"]
            self.__baidu["ok"] = jsonData["baiduConfirm"]
            self.__baidu["intro"] = jsonData["baiduIntro"]
        except:
            logger.exception("Error On Load Configuartion File.")
            print("Error On Load Configuartion File , Please Check The Log File.")
            sys.exit(1)

        with open("profile.json") as configFile:
            jsonData = json.load(configFile)
            configFile.close()
        try:
            self.__baidu["id"] = jsonData["baiduId"]
            self.__baidu["secret"] = jsonData["baiduS"]
        except:
            logger.exception("Error On Load Profile File.")
            print("Error On Load Profile File , Please Check The Log File.")
            sys.exit(1)

    # Link Status :
    # 	0 : Untransfer
    # 	1 : Transfered
    # 	-1 : Link Error
    # 	-2 : Link Banned
    # 更新数据库中的状态
    def __updateLinkStatus(self, PanLink, status):
        try:
            sql = "UPDATE %s SET isTransfered='%d' WHERE PanLink = '%s'"
            data = (self.tableName, status, PanLink)
            cmd = sql % data
            logger.debug(cmd)
            self.dbCursor.execute(cmd)
            self.dbConn.commit()
        except:
            logger.exception("Error On Update Link Status With Link : %s" % PanLink)
            print(
                "Error On Update Link Status With Link : %s , Please Check The Log File"
                % PanLink
            )
            return -1

