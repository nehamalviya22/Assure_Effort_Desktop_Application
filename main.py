import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap,QRegExpValidator
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sqlite3
import datetime
from functools import partial
import re
from PyQt5 import QtGui, QtCore

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
        loadUi("activities_test.ui",self)
        self.setMouseTracking(True)
        
        self.New.clicked.connect(self.gotoaddactivity)
        self.row_id = 0
        self.counter_hour = 0
        self.counter = 0
        self.hour = '0'
        self.minute = '00'
        self.second = '00'
        self.count = '00'
        self.startWatch = False
        self.activity_on = False
        self.row = 0
 
        self.now = QDate.currentDate()
        self.currentdate = self.now.toString(Qt.DefaultLocaleLongDate)
        self.date.setText(self.currentdate)
       
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

        break_hours_sum = datetime.timedelta()
        for i in self.break_hours:
            (h, m, s) = i.split(':')
            d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            break_hours_sum += d
        self.break_time = str(break_hours_sum)
        self.breakHours.setText("Break Hours :" + self.break_time)

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
                                    self.hour = str(ho)
                                else:
                                    self.hour = str(ho)

            text = self.hour + ':' + self.minute + ':' + self.second
            self.timer.setText('<h3 style="color:black">' + text + '</h3>')      
    
    def Start_new(self):
        self.activity_on = True
        self.startWatch = True
    
    def Stop_new(self):
        self.startWatch = False
        current_time = QTime.currentTime().toString()
        converted_current_time = datetime.datetime.strptime(current_time,"%H:%M:%S")
        self.tracker_end_time = converted_current_time.strftime("%I:%M:%S %p")
        self.save_track_time(self.tracker_end_time,self.row_id)
        #self.showactivity()
        self.activity_on = False
        activityscreen = ActivityScreen()
        widget.addWidget(activityscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def save_track_time(self,end_time,id):
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        activity = (end_time, id)
        cur.execute('UPDATE activity SET endtime=? WHERE oid=?', activity)
        conn.commit()
        conn.close()
        
    def Reset(self):
        self.startWatch = False
        self.counter = 0
        self.minute = '00'
        self.second = '00'
        self.count = '00'
        self.timer.setText(str(self.counter))

    def gotoaddactivity(self):
        Add_activity = AddActivityScreen()
        widget.addWidget(Add_activity)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def time_diffrence(self,start,end):
        time_1 = datetime.datetime.strptime(start,"%H:%M:%S %p")
        time_2 = datetime.datetime.strptime(end,"%H:%M:%S %p")
        time_interval = time_2 - time_1
        return str(time_interval)

    def add_duplicate_Activity(self,project,task,description):
        date = self.currentdate
        end_time = ''
        current_time = QTime.currentTime().toString()
        converted_current_time = datetime.datetime.strptime(current_time,"%H:%M:%S")
        start_time = converted_current_time.strftime("%I:%M:%S %p")
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        activity = [project, task, description, start_time, end_time, date]
        cur.execute('INSERT INTO activity (project, task, description, starttime, endtime, date) VALUES (?,?,?,?,?,?)', activity)
        conn.commit()
        conn.close()
        activityscreen = ActivityScreen()
        widget.addWidget(activityscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def Edit(self,row_id):
        Edit_activity = EditActivityScreen(row_id)
        widget.addWidget(Edit_activity)
        widget.setCurrentIndex(widget.currentIndex()+1)
        

    def showactivity(self):
        
        conn = sqlite3.connect("test.db")
        queryCurs = conn.cursor()
        queryCurs.execute('SELECT rowid,starttime,endtime,project,task,description FROM activity WHERE date =\''+self.currentdate+"\'") 
       
        
        # self.tableWidget.verticalHeader().setVisible(False)
        # self.tableWidget.horizontalHeader().setVisible(False)
        # self.tableWidget.setColumnCount(8)
        # self.tableWidget.setRowCount(0)
        # self.tableWidget.setColumnWidth(0,100)
        # self.tableWidget.setColumnWidth(1,100)
        # self.tableWidget.setColumnWidth(2,100)
        # self.tableWidget.setColumnWidth(4,139)
        # self.tableWidget.setColumnWidth(5,70)
        
        self.productive_hours = []
        self.break_hours = []
        
        for row, data in enumerate(queryCurs):
            self.timer = QLabel()
            self.row_id = data[0]
            #self.tableWidget.insertRow(row)
            
            if data[2] == '':
                timer = QTimer(self)
                timer.timeout.connect(self.showCounter)
                timer.start(100)
                self.Start_new()
                self.start = QPushButton('Stop')
                self.start.setStyleSheet("background-color : rgb(97, 179, 255);color: rgb(0, 0, 0);border-radius:20px;")
                self.start.clicked.connect(self.Stop_new)
            
            else:
                conn = sqlite3.connect("test.db")
                queryCurs = conn.cursor()
                queryCurs.execute('SELECT starttime,endtime,project,task,description FROM activity WHERE rowid =\''+str(self.row_id)+"\'") 
                for item in queryCurs:
                    total_time=self.time_diffrence(item[0],item[1])
                    if (data[4] == 'Lunch Break' or data[4] == 'Tea Break' or data[4] == 'Other Break'):
                        self.break_hours.append(total_time)
                    else:
                        self.productive_hours.append(total_time)
                    self.timer.setText('<h3 style="color:black">' + total_time + '</h3>')
                    self.start = QPushButton('Start')
                    self.start.setStyleSheet("background-color : rgb(97, 179, 255);color: rgb(0, 0, 0);border-radius:20px;")
                    add_duplicate_activity = partial(self.add_duplicate_Activity,item[2],item[3],item[4])
                    self.start.clicked.connect(add_duplicate_activity)

            self.edit = QPushButton('Edit')
            edit_id = partial(self.Edit,self.row_id)
            self.edit.clicked.connect(edit_id)
            self.gridLayout.addWidget(self.timer, row,5)
            self.gridLayout.addWidget( self.start, row,6)
            self.gridLayout.addWidget(self.edit, row,7)
            
            for column, item in enumerate(data[1:]):  
                label = QLabel(str(item))
                self.gridLayout.addWidget(label,row,column)
                
        
        

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

        #reg_ex = QRegExp("^(1[0-2]|0?[1-9]):[0-5][0-9]:[0-5][0-9] [APap][mM]$") 12 hour format
        reg_ex_for_time = QRegExp("^([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9] [APap][mM]$")
        reg_ex_for_text = QRegExp("[a-zA-Z]+")

        input_validator = QRegExpValidator(reg_ex_for_time, self.starttimefield)
        self.starttimefield.setValidator(input_validator)

        input_validator = QRegExpValidator(reg_ex_for_time, self.endtimefield)
        self.endtimefield.setValidator(input_validator)

        self.Tasktitlefield.setMaxLength(60)
        input_validator = QRegExpValidator(reg_ex_for_text, self.Tasktitlefield)
        self.Tasktitlefield.setValidator(input_validator)

        input_validator = QRegExpValidator(reg_ex_for_text, self.Tasklinkfield)
        self.Tasklinkfield.setValidator(input_validator)

        # regexp = QRegExp(r'^[a-zA-Z]*$')
        # self.validator = QRegExpValidator(regexp)

        # def validation():
        #     regexp = QtCore.QRegExp('^([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$')
        #     valid=QtGui.QRegExpValidator.validate(regexp)
        #     if not valid:
        #         Ui_IPG_weld.Start_i.setPlainText('0')

        # self.Descriptionfield.textChanged.connect(validation)

        # input_validator = QRegExpValidator(reg_ex_for_text, self.Descriptionfield)
        # self.Descriptionfield.setValidator(input_validator)

    def closeactivity(self):
        activityscreen = ActivityScreen()
        widget.addWidget(activityscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)  

    def validate(self,time_text):
        try:
            return bool(datetime.datetime.strptime(time_text, "%H:%M:%S %p"))
        except ValueError:
            return False
    
    def converted_12h_to_24h(self,time):
        try:
            converted_time = datetime.datetime.strptime(time, "%I:%M:%S %p")
            new_time = converted_time.strftime("%H:%M:%S %p")
            return new_time
        except ValueError:
            return time

    def converted_24h_to_12h(self,time):
        converted_time = datetime.datetime.strptime(time, "%H:%M:%S %p")
        new_time = converted_time.strftime("%I:%M:%S %p")
        return new_time

    def saveactivitytodb(self):
       
        activityscreen = ActivityScreen()
        project_name = self.Addproject.currentText()
        task = self.Addtask.currentText()
        task_title = self.Tasktitlefield.text()
        task_link = self.Tasklinkfield.text()
        description = self.Descriptionfield.toPlainText()
        start_time = self.starttimefield.text()
        end_time = self.endtimefield.text()
        date = activityscreen.currentdate
        if len(task)==0 or task == 'Select Task':
            self.error.setText("must exist")
        else:
            if project_name == 'Select Project':
                project = project_name.replace('Select Project', 'Other Things')
            else:
                project = project_name

            if start_time != '' and end_time != '':
                validate_start_time_format = self.validate(start_time)
                if not validate_start_time_format:
                    self.start_time_error.setText("format should be correct.")
                else:
                    self.start_time_error.setText("")

                validate_end_time_format = self.validate(end_time)
                if not validate_end_time_format:
                    self.end_time_error.setText("format should be correct.")
                else:
                    current_time_zone = QTime.currentTime().toString()
                    converted_current_time = datetime.datetime.strptime(current_time_zone,"%H:%M:%S")
                    current_time = converted_current_time.strftime("%H:%M:%S %p")

                    start_time_new = self.converted_12h_to_24h(start_time)
                    end_time_new = self.converted_12h_to_24h(end_time)
                    previous_current_time = converted_current_time - datetime.timedelta(minutes=5)
                    prev_curr_time = previous_current_time.strftime("%H:%M:%S %p")
        
                    if start_time_new > current_time:
                        self.start_time_error.setText("not allow future time")
                    elif start_time_new < prev_curr_time or start_time_new > current_time:
                        self.start_time_error.setText("not allow previous time")

                    elif end_time_new < start_time_new:
                        self.end_time_error.setText("should be greater than start time")
                    elif end_time_new > current_time:
                        self.end_time_error.setText("not allow future time")
                    else:
                        if activityscreen.activity_on:
                            self.end_time_error.setText("can't be blank")
                        else:
                            start_time = self.converted_24h_to_12h(start_time_new)
                            conn = sqlite3.connect("test.db")
                            cur = conn.cursor()
                            activity = [project, task, task_title, task_link, description, start_time, end_time, date]
                            cur.execute('INSERT INTO activity (project, task, tasktitle, tasklink, description, starttime, endtime, date) VALUES (?,?,?,?,?,?,?,?)', activity)
                            conn.commit()
                            conn.close()
                            activityscreen = ActivityScreen()
                            widget.addWidget(activityscreen)
                            widget.setCurrentIndex(widget.currentIndex()+1)
            
            elif start_time != '':
                validate_time_format = self.validate(start_time)
                if not validate_time_format:
                    self.start_time_error.setText("..format should be correct")
                else:
                    current_time_zone = QTime.currentTime().toString()
                    converted_current_time = datetime.datetime.strptime(current_time_zone,"%H:%M:%S")
                    current_time = converted_current_time.strftime("%H:%M:%S %p")
                    start_time_new = self.converted_12h_to_24h(start_time)
                    previous_current_time = converted_current_time - datetime.timedelta(minutes=5)
                    prev_curr_time = previous_current_time.strftime("%H:%M:%S %p")

                    if start_time_new > current_time:
                        self.start_time_error.setText("not_allow_future_time")

                    elif start_time_new < prev_curr_time or start_time_new > current_time:
                        self.start_time_error.setText("not allow previous time")
                    else:
                        if activityscreen.activity_on:
                            self.start_time_error.setText("can't be blank")
                        else:
                            start_time = self.converted_24h_to_12h(start_time_new)
                            conn = sqlite3.connect("test.db")
                            cur = conn.cursor()
                            activity = [project, task, task_title, task_link, description, start_time, end_time, date]
                            cur.execute('INSERT INTO activity (project, task, tasktitle, tasklink, description, starttime, endtime, date) VALUES (?,?,?,?,?,?,?,?)', activity)
                            conn.commit()
                            conn.close()
                            activityscreen = ActivityScreen()
                            widget.addWidget(activityscreen)
                            widget.setCurrentIndex(widget.currentIndex()+1)

            else:
                current_time = QTime.currentTime().toString()
                converted_current_time = datetime.datetime.strptime(current_time,"%H:%M:%S")
                start_time = converted_current_time.strftime("%I:%M:%S %p")

                if activityscreen.activity_on:
                    self.end_time_error.setText("Can't be blank")
                else:
                    conn = sqlite3.connect("test.db")
                    cur = conn.cursor()
                    activity = [project, task, task_title, task_link, description, start_time, end_time, date]
                    cur.execute('INSERT INTO activity (project, task, tasktitle, tasklink, description, starttime, endtime, date) VALUES (?,?,?,?,?,?,?,?)', activity)
                    conn.commit()
                    conn.close()
                    activityscreen = ActivityScreen()
                    widget.addWidget(activityscreen)
                    widget.setCurrentIndex(widget.currentIndex()+1)

                
            
            
class EditActivityScreen(QDialog):
    def __init__(self,row_id):
        super(EditActivityScreen, self).__init__()
        loadUi("edit_activity.ui",self)
        self.unique_id = row_id

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

        conn = sqlite3.connect("test.db")
        queryCurs = conn.cursor()
        
        queryCurs.execute('SELECT starttime,endtime,project,task,tasktitle,tasklink,description FROM activity WHERE rowid =\''+str(row_id)+"\'") 
        for item in queryCurs:
            self.Addproject.setCurrentText(item[2])
            self.Addtask.setCurrentText(item[3])
            self.Tasktitlefield.setText(item[4])
            self.Tasklinkfield.setText(item[5])
            self.Descriptionfield.setText(item[6])

        self.close.clicked.connect(self.closeactivity)
        self.save.clicked.connect(self.saveactivitytodb)
        self.activityscreen = ActivityScreen()


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
        description = self.Descriptionfield.toPlainText()

        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        activity = (project, task, task_title, task_link, description,self.unique_id)
        cur.execute('UPDATE activity SET project=?, task=?, tasktitle=?, tasklink=?, description=? WHERE oid=?', activity)
        
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
