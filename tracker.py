from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QAbstractItemView, QLabel, QListWidget, QLineEdit, QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QApplication
from selenium import webdriver

target_number = ""
total_list = []

def month_string_to_number(string):
    m = {
        'jan': "01",
        'feb': "02",
        'mar': "03",
        'apr': "04",
        'may': "05",
        'jun': "06",
        'jul': "07",
        'aug': "08",
        'sep': "09",
        'oct': "10",
        'nov': "11",
        'dec': "12"
        }

    s = string.strip()[:3].lower()
    out = m[s]

    return out

class MyMainGUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.search_button = QPushButton("검색")
        self.tracking_num = QLineEdit(self)
        self.tracking_list = QListWidget(self)

        self.status_label = QLabel("", self)

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        hbox.addWidget(self.tracking_num)
        hbox.addWidget(self.search_button)
        hbox.addStretch(0)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.tracking_list)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        vbox.addWidget(self.status_label)

        self.setLayout(vbox)

        self.setWindowTitle('PyTracker')
        self.setGeometry(300, 300, 500, 300)


class MyMain(MyMainGUI):
    add_sec_signal = pyqtSignal()
    send_instance_singal = pyqtSignal("PyQt_PyObject")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.search_button.clicked.connect(self.search)
        self.tracking_list.setSelectionMode(QAbstractItemView.MultiSelection)

        self.tracking_num.textChanged[str].connect(self.title_update)

        self.th_search = searcher(parent=self)
        self.th_search.updated_list.connect(self.list_update)
        self.th_search.updated_label.connect(self.status_update)

        self.show()
    
    def title_update(self, input):
        global target_number
        target_number = input

    @pyqtSlot()
    def search(self):
        global total_list

        total_list = []

        self.tracking_list.clear()
        self.th_search.start()

    @pyqtSlot(str)
    def list_update(self, msg):
        self.tracking_list.addItem(msg)
    
    @pyqtSlot(str)
    def status_update(self, msg):
        self.status_label.setText(msg)


class searcher(QThread):
    updated_list = pyqtSignal(str)
    updated_label = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent

    def __del__(self):
        self.wait()
    
    def Global_Order_Tracking(self, track_num):
        global total_list

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.implicitly_wait(5)

        driver.get(url='https://global.cainiao.com/detail.htm?mailNoList=' + track_num)

        for indx in range(100):
            try:
                _item = (driver.find_element_by_xpath('//*[@id="waybill_path"]/li[{}]/p[1]'.format(indx + 1))).text
                _time = (driver.find_element_by_xpath('//*[@id="waybill_path"]/li[{}]/p[2]'.format(indx + 1))).text

                total_list.append((_item, _time))
                
            except:
                break
        
        driver.close()
    
    def ACT(self, track_num):
        global total_list

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.implicitly_wait(5)

        driver.get(url='http://exp.actcore.com/member/loginTracing.do?fwdCode=KACT&bound=OI&langCode=KOR&DeliveryCode=EMS&HBLNO=' + track_num)

        for indx in range(100):
            try:
                _time1 = (driver.find_element_by_xpath('//*[@id="{}"]/td[2]'.format(indx + 1))).text
                _time2 = (driver.find_element_by_xpath('//*[@id="{}"]/td[3]'.format(indx + 1))).text

                _time = "{} {}:00".format(_time1, _time2)

                _item1 = (driver.find_element_by_xpath('//*[@id="{}"]/td[5]'.format(indx + 1))).text
                _item2 = (driver.find_element_by_xpath('//*[@id="{}"]/td[6]'.format(indx + 1))).text

                _item = "{}({})".format(_item1, _item2)

                total_list.append((_item, _time))
                
            except:
                break
        
        driver.close()
    
    def ePOST(self, track_num):
        global total_list

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.implicitly_wait(5)

        driver.get(url='https://service.epost.go.kr/iservice/usr/trace/usrtrc001k01.jsp?displayHeader=N')

        search_box = driver.find_element_by_xpath('//*[@id="sid1"]')
        search_box.send_keys(track_num)

        search = driver.find_element_by_xpath('//*[@id="frmDomRigiTrace"]/div/dl/dd/a')
        search.click()

        for indx in range(100):
            try:
                _time1 = (driver.find_element_by_xpath('//*[@id="processTable"]/tbody/tr[{}]/td[1]'.format(indx + 1))).text
                _time1 = _time1.replace(".", "-")
                _time2 = (driver.find_element_by_xpath('//*[@id="processTable"]/tbody/tr[{}]/td[2]'.format(indx + 1))).text

                _time = "{} {}:00".format(_time1, _time2)

                _item1 = (driver.find_element_by_xpath('//*[@id="processTable"]/tbody/tr[{}]/td[3]/a'.format(indx + 1))).text
                _item2 = (driver.find_element_by_xpath('//*[@id="processTable"]/tbody/tr[{}]/td[4]'.format(indx + 1))).text
                _item2 = _item2.replace("\n", "")
                _item = "{}({})".format(_item1, _item2)

                total_list.append((_item, _time))

            except:
                break
        
        driver.close()
    
    def _4PX(self, track_num):
        global total_list

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36')

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.implicitly_wait(5)

        driver.get(url='https://track.aftership.com/trackings?courier=4px&tracking-numbers=' + track_num)

        for indx in range(100):
            try:
                _item = (driver.find_element_by_xpath('//*[@id="checkpoints-container"]/ul/li[{}]/div[2]/div[1]/div'.format(indx + 1))).text
                _time = (driver.find_element_by_xpath('//*[@id="checkpoints-container"]/ul/li[{}]/div[2]/div[2]/div[1]/p'.format(indx + 1))).text
                
                month = _time.split(" ")[0]
                month = month_string_to_number(month)

                date = "{}-{}-{}".format(_time.split(" ")[2], month, _time.split(" ")[1])
                
                if _time.split(" ")[3] != "12:00":
                    hour = (_time.split(" ")[3]).split(":")[0]
                    min = (_time.split(" ")[3]).split(":")[1]

                    if _time.split(" ")[4] == "pm":
                        hour = int(hour) + 12

                        new_time = "{}:{}:00".format(hour, min)
                    
                    elif _time.split(" ")[4] == "am":
                        new_time = "{}:{}:00".format(hour, min)
                
                else:
                    hour = (_time.split(" ")[3]).split(":")[0]
                    min = (_time.split(" ")[3]).split(":")[1]

                    new_time = "{}:{}:00".format(hour, min)
                
                _time = "{} {}".format(date, new_time)

                total_list.append((_item, _time))
                
            except:
                break
        
        driver.close()
    
    def ePOST_ems(self, track_num):
        global total_list

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.implicitly_wait(5)

        driver.get(url='https://service.epost.go.kr/trace.RetrieveEmsRigiTrace.comm?displayHeader=N')

        search_box = driver.find_element_by_xpath('//*[@id="POST_CODE"]')
        search_box.send_keys(track_num)

        search = driver.find_element_by_xpath('//*[@id="frmEmsRigiTrace"]/div/dl/dd/a')
        search.click()

        for indx in range(100):
            try:
                _time1 = (driver.find_element_by_xpath('//*[@id="print"]/table[2]/tbody/tr[{}]/td[1]'.format(indx + 1))).text
                _time1 = _time1.replace(".", "-")
                _time = "{}:00".format(_time1)

                _item1 = (driver.find_element_by_xpath('//*[@id="print"]/table[2]/tbody/tr[{}]/td[2]'.format(indx + 1))).text
                _item2 = (driver.find_element_by_xpath('//*[@id="print"]/table[2]/tbody/tr[{}]/td[3]'.format(indx + 1))).text
                _item = "{}({})".format(_item1, _item2)

                total_list.append((_item, _time))

            except:
                break
        
        driver.close()
        
    def run(self):

        global target_number
        global total_list
        
        if target_number != "":
            self.updated_label.emit("Global Order Tracking에서 검색 중...")
            self.Global_Order_Tracking(target_number)

            self.updated_label.emit("에이씨티앤코아물류에서 검색 중...")
            self.ACT(target_number)

            self.updated_label.emit("우체국 택배에서 검색 중...")
            self.ePOST(target_number)

            self.updated_label.emit("우체국 택배(EMS)에서 검색 중...")
            self.ePOST_ems(target_number)

            self.updated_label.emit("4PX에서 검색 중...")
            self._4PX(target_number)

            total_list.sort(key = lambda x : x[1])

            for i in range(len(total_list)):
                strOut = "%-20s%-20s" % (total_list[i][1], total_list[i][0])
                self.updated_list.emit(strOut)
            
            self.updated_label.emit("검색 완료!")
                
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MyMain()
    app.exec_()