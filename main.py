import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sqlite3
import datetime

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        self.login.clicked.connect(self.gotologin)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
    
    
    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user)==0 or len(password)==0:
            self.error.setText("Please input all fields.")
        
        else:
            conn = sqlite3.connect("test.db")
            cur = conn.cursor()
            query = 'SELECT password FROM login_info WHERE username =\''+user+"\'"
            cur.execute(query)
            result_pass = cur.fetchone()[0]
            if result_pass == password:
                print("Successfully logged in.")
                self.gotoactivityscreen()
                self.error.setText("")
            else:
                self.error.setText("Invalid username or password")
    
    def gotoactivityscreen(self):
        activity_screen = ActivityScreen()
        widget.addWidget(activity_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)


        
class ActivityScreen(QDialog):
    def __init__(self):
        super(ActivityScreen, self).__init__()
        loadUi("activities.ui",self)
        self.New.clicked.connect(self.gotoaddactivity)
        self.row_id = 0
        self.tracking_time = 0
        self.counter_hour = 0
        self.counter = 0
        self.hour = '00'
        self.minute = '00'
        self.second = '00'
        self.count = '00'
        self.startWatch = False
        self.row = 0
 
        self.now = QDate.currentDate()
        self.currentdate = self.now.toString(Qt.DefaultLocaleLongDate)
        self.date.setText(self.currentdate)
        self.productive_time = "Productive Hours :00:00:00"
        self.showactivity()
        hour = 0
        minute = 0
        second = 0

        mysum = datetime.timedelta()
        for i in self.productive_hours:
            (h, m, s) = i.split(':')
            d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            mysum += d
        self.productive_time = str(mysum)
        self.hours.setText("Productive Hours :" + self.productive_time)

    def showCounter(self):
        
            if self.startWatch:
                self.counter += 1

                cnt = int((self.counter/10 - int(self.counter/10))*10)
                self.count = '0' + str(cnt)
                

                if int(self.counter/10) < 10 :
                    self.second = '0' + str(int(self.counter / 10))
                else:
                    self.second = str(int(self.counter / 10))

                    if self.counter / 10 == 60.0 :
                        self.counter_hour = self.counter_hour + self.counter
                        self.second == '00'
                        self.counter = 0
                        if int(self.minute) < 60:
                            min = int(self.minute) + 1
                        else:
                            min = 1
                        if min < 10 :
                            self.minute = '0' + str(min)
                        else:
                            self.minute = str(min)

                            if self.counter_hour / 10 == 3600.0 :
                                self.minute=='00'
                                self.counter_hour = 0
                                self.counter = 0
                                ho = int(self.hour) + 1
                                if ho < 10 :
                                    self.hour = '0' + str(ho)
                                else:
                                    self.hour = str(ho)

      
            text = self.hour + ':' + self.minute + ':' + self.second+ ':' + self.count
            self.timer.setText('<h3 style="color:black">' + text + '</h3>')
        

    def Start_new(self):
        self.startWatch = True
    
    def Stop_new(self):
        self.startWatch = False
        self.tracker_end_time = QTime.currentTime()
        self.save_track_time(self.tracker_end_time.toString(),self.row_id)

    
    def save_track_time(self,end_time,id):
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        activity = ( end_time, id)
        cur.execute('UPDATE activity SET endtime=? WHERE oid=?', activity)
        conn.commit()
        conn.close()
        
        self.tracking_time = self.timer.text()

    def gotoaddactivity(self):
        Add_activity = AddActivityScreen()
        widget.addWidget(Add_activity)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def time_diffrence(self,start,end):
        time_1 = datetime.datetime.strptime(start,"%H:%M:%S")
        time_2 = datetime.datetime.strptime(end,"%H:%M:%S")
        time_interval = time_2 - time_1
        return str(time_interval)


    def showactivity(self):
        conn = sqlite3.connect("test.db")
        queryCurs = conn.cursor()
        queryCurs.execute('SELECT rowid,starttime,endtime,project,task,tasktitle,tasklink,description FROM activity WHERE date =\''+self.currentdate+"\'") 
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnWidth(0,130)
        self.tableWidget.setColumnWidth(1,130)
        self.tableWidget.setColumnWidth(2,100)
        self.tableWidget.setColumnWidth(4,130)
        
        self.productive_hours = []
        
        for row, data in enumerate(queryCurs):
            self.timer = QLabel()

            timer = QTimer(self)
            timer.timeout.connect(self.showCounter)
            timer.start(100)

            self.row_id = data[0]
            self.tableWidget.insertRow(row)
            
            if data[2] == '':
                self.Start_new()
                self.start = QPushButton('Stop')
                self.start.clicked.connect(self.Stop_new)
            
            else:
                conn = sqlite3.connect("test.db")
                queryCurs = conn.cursor()
                queryCurs.execute('SELECT starttime,endtime,project,task,tasktitle,tasklink,description FROM activity WHERE rowid =\''+str(self.row_id)+"\'") 
                for item in queryCurs:
                    total_time=self.time_diffrence(item[0],item[1])
                    self.productive_hours.append(total_time)
                    
                    self.timer.setText('<h3 style="color:black">' + total_time + '</h3>')
                    self.start = QPushButton('Start')
                    self.start.setEnabled(False)

            self.tableWidget.setCellWidget(row,5, self.timer)
            self.tableWidget.setCellWidget(row,6, self.start)
            
            for column, item in enumerate(data[1:]):  
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(item))) 
        

class AddActivityScreen(QDialog):
    def __init__(self):
        super(AddActivityScreen, self).__init__()
        loadUi("add_activity.ui",self)
        self.close.clicked.connect(self.closeactivity)
        self.save.clicked.connect(self.saveactivitytodb)
        self.activityscreen = ActivityScreen()

        self.Addproject.addItem("Select Project")
        self.Addproject.addItem("RDvault")
        self.Addproject.addItem("Estimator")
        
        self.Addtask.addItem("Select Task")
        self.Addtask.addItem("Coordination")
        self.Addtask.addItem("Lunch Break")
        self.Addtask.addItem("Tea Break")
        self.Addtask.addItem("Other Break")
        self.Addtask.addItem("Fun Activity")
        self.Addtask.addItem("Demo Projects")
        self.Addtask.addItem("Training Topics")
        self.Addtask.addItem("Client Call")
        self.Addtask.addItem("R&D Work")
        self.Addtask.addItem("Outside of office for personal work")
        self.Addtask.addItem("Learn New Technology")
        self.Addtask.addItem("Electricity Failure")


    def closeactivity(self):
        activityscreen = ActivityScreen()
        widget.addWidget(activityscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)  

    def saveactivitytodb(self):
        activityscreen = ActivityScreen()
        project = self.Addproject.currentText()
        task = self.Addtask.currentText()
        task_title = self.Tasktitlefield.text()
        task_link = self.Tasklinkfield.text()
        description = self.Descriptionfield.text()
        start_time = self.starttimefield.text()
        end_time = self.endtimefield.text()
        date = activityscreen.currentdate
        if start_time == '':
            start_time = QTime.currentTime().toString()
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        activity = [project, task, task_title, task_link, description, start_time, end_time, date]
        cur.execute('INSERT INTO activity (project, task, tasktitle, tasklink, description, starttime, endtime, date) VALUES (?,?,?,?,?,?,?,?)', activity)
        
        conn.commit()
        conn.close()

        activityscreen = ActivityScreen()
        widget.addWidget(activityscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)


app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(600)
widget.setFixedWidth(800)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
