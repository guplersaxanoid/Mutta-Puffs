from typing import NewType
from PyQt5 import QtGui
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPixmap
from constants import BUDGET, DRIVER, NETWORK, NUM_PROVIDERS, NUM_WAVES, SCHEDULE_SAVED, SUBNET_TAG
import sys 
from PyQt5 import QtWebEngineWidgets, QtWidgets, QtCore, QtWebChannel
from utils import *
import subprocess
import os 

class Backend(QtCore.QObject):
    inputReceived = QtCore.pyqtSignal(str)
    nextPage = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(str)
    def getInput(self,data:str):
        self.inputReceived.emit(data)
    
    @QtCore.pyqtSlot()
    def goToNextPage(self):
        self.nextPage.emit()

class Stream(QtCore.QObject):
    newLog = QtCore.pyqtSignal(str)
    
    def write(self,text):
        self.newLog.emit(str(text))

class GenerateSchedule(QtWidgets.QWidget):
    def __init__(self):
        super(GenerateSchedule,self).__init__()
        self.p = None
        self.layout = QtWidgets.QHBoxLayout(self)
        self.instructionBox = QtWidgets.QLabel()
        self.instructionBox.setStyleSheet("width: 33%; font-size: 20px")
        self.instructionBox.setText('Great! Now we have your list of teams.\n\
Mutta Puffs will put toghether an optimal schedule \
for your games by considering the following constraints:\n\n\
1.) The distance travelled by each teams for home and away games must be kept minimal\n\
2.) No teams will play more than 2 consecutive away mathces.\n\
3.) No two teams shall play each other in two consecutive round.\n\n\
The solution will be obtained by using Population-based Simulated Annealing Algorithm \
The search space will be divided and searched parallely on multiple providers in Golem.\
The best schedules from each providers will be downloaded back and the best of the best \
will be saved as the final schedule.\n\n\
The parallelized population based Simulated Annealing was proposed by:\n\
Van Hentenryck, Pascal, and Yannis Vergados. "Population-based simulated annealing for\
traveling tournaments." Proceedings of the National Conference on Artificial Intelligence.\
 Vol. 22. No. 1. Menlo Park, CA; Cambridge, MA; London; AAAI Press; MIT Press; 1999, 2007.')
        self.instructionBox.setWordWrap(True)
        self.computeButton = QtWidgets.QPushButton("compute")
        self.computeButton.clicked.connect(lambda: self.run_sa())
        self.settingsButton = QtWidgets.QPushButton("settings")
        self.settingsButton.clicked.connect(lambda: self.open_settings())
        self.logbox = QtWidgets.QPlainTextEdit()
        self.logbox.setReadOnly(True)
        self.errorMessage = QtWidgets.QLabel("An error was detected. Please check the errors and recompute.")
        self.errorMessage.setStyleSheet("color:red; font-size:10; height: fit-content")
        self.errorMessage.setHidden(True)
        self.errorMessage2 = QtWidgets.QLabel("The schedule that is computed so far has been saved to schedule.png")
        self.errorMessage2.setStyleSheet("color:red; font-size:10; height: fit-content")
        self.errorMessage2.setHidden(True)
        self.finishButton = QtWidgets.QPushButton("Open Schedule")
        self.finishButton.setEnabled(False)
        self.finishButton.clicked.connect(lambda: self.openSchedule())
        self.column1 = QtWidgets.QVBoxLayout()
        self.column1.addWidget(self.instructionBox, stretch=8)
        self.column1.addWidget(self.errorMessage, stretch=1)
        self.column1.addWidget(self.errorMessage2,stretch=1)
        self.column1.addWidget(self.computeButton, stretch=2)
        self.column1.addWidget(self.settingsButton, stretch=2)
        self.column1.addWidget(self.finishButton, stretch=2)
        self.column2 = QtWidgets.QVBoxLayout()
        self.column2.addWidget(self.logbox)
        self.layout.addLayout(self.column1, stretch=1)
        self.layout.addLayout(self.column2, stretch=2)
        self.setLayout(self.layout)

    def onUpdateLog(self,log):
        self.logbox.appendPlainText(log)

    @QtCore.pyqtSlot()
    def open_settings(self):
        SettingsWindow().show()

    @QtCore.pyqtSlot()
    def run_sa(self):
        if self.p is None:
            self.computeButton.setEnabled(False)
            self.errorMessage.setHidden(True)
            self.errorMessage2.setHidden(True)
            self.settingsButton.setEnabled(False)
            self.p = QtCore.QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.finished.connect(self.onFinished)
            self.p.start("python",["parallelizer.py"])


    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf-8")
        self.onUpdateLog(stdout)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf-8")
        self.onUpdateLog(stderr)

    def handle_state(self, state):
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")
    
    def onFinished(self):
        self.onUpdateLog("Process finished.")
        self.p = None
        self.computeButton.setEnabled(True)
        self.settingsButton.setEnabled(True)
        if not SCHEDULE_SAVED:
            self.errorMessage.setHidden(False)
            if os.path.exists(os.path.join(os.path.abspath("./"),"schedule.png")):
                self.errorMessage2.setHidden(False)
        self.finishButton.setEnabled(True)


    def openSchedule(self):
        if sys.platform.startswith('linux'):
            subprocess.call(['xdg-open', "schedule.png"])
        elif sys.platform.startswith('darwin'):
            subprocess.call(['open', "schedule.png"])
        elif sys.platform.startswith('win'):
            subprocess.call(['start', "schedule.png"], shell=True)



class SettingsWindow(QtWidgets.QWidget):
    def __init__(self):
        super(SettingsWindow,self).__init__()
        self.inputlist = QtWidgets.QVBoxLayout()
        self.num_providers = QtWidgets.QHBoxLayout()
        self.pvalidation = QtWidgets.QHBoxLayout()
        self.num_iterations = QtWidgets.QHBoxLayout()
        self.ivalidation = QtWidgets.QHBoxLayout()
        self.budget = QtWidgets.QHBoxLayout()
        self.bvalidation = QtWidgets.QHBoxLayout()
        self.network = QtWidgets.QHBoxLayout()
        self.driver = QtWidgets.QHBoxLayout()
        self.subnet = QtWidgets.QHBoxLayout()
        self.save = QtWidgets.QHBoxLayout()

        self.provider_label = QtWidgets.QLabel("Providers:")
        self.provider_box = QtWidgets.QLineEdit()
        self.provider_box.setText(str(NUM_PROVIDERS))
        self.provider_box.setValidator(QIntValidator(1,2147483647))
        self.num_providers.addWidget(self.provider_label)
        self.num_providers.addWidget(self.provider_box)

        self.pvalidation_label = QtWidgets.QLabel("")
        self.pvalidation_label.setStyleSheet("color:red; font-size:10;")
        self.pvalidation_label.setHidden(True)
        self.pvalidation.addWidget(self.pvalidation_label)

        self.iterations_label = QtWidgets.QLabel("Iterations:")
        self.iterations_box = QtWidgets.QLineEdit()
        self.iterations_box.setText(str(NUM_WAVES))
        self.iterations_box.setValidator(QIntValidator(1,2147483647))
        self.num_iterations.addWidget(self.iterations_label)
        self.num_iterations.addWidget(self.iterations_box)

        self.ivalidation_label = QtWidgets.QLabel("")
        self.ivalidation_label.setStyleSheet("color:red; font-size:10;")
        self.ivalidation_label.setHidden(True)
        self.ivalidation.addWidget(self.ivalidation_label)

        self.budget_label = QtWidgets.QLabel("Budget:")
        self.budget_box = QtWidgets.QLineEdit()
        self.budget_box.setText(str(BUDGET))
        self.budget_box.setValidator(QDoubleValidator(0,float('inf'),2))
        self.budget.addWidget(self.budget_label)
        self.budget.addWidget(self.budget_box)

        self.bvalidation_label = QtWidgets.QLabel("")
        self.bvalidation_label.setStyleSheet("color:red; font-size:10")
        self.bvalidation_label.setHidden(True)
        self.bvalidation.addWidget(self.bvalidation_label)

        self.network_label = QtWidgets.QLabel("Network:")
        self.network_box = QtWidgets.QComboBox()
        self.network_box.addItems(["mainnet","rinkeby"])
        self.network.addWidget(self.network_label)
        self.network.addWidget(self.network_box)

        self.driver_label = QtWidgets.QLabel("Driver:")
        self.driver_box = QtWidgets.QComboBox()
        self.driver_box.addItems(["zksync","erc20"])
        self.driver.addWidget(self.driver_label)
        self.driver.addWidget(self.driver_box)

        self.subnet_label = QtWidgets.QLabel("Subnet Tag:")
        self.subnet_box = QtWidgets.QLineEdit()
        self.subnet_box.setText(SUBNET_TAG)
        self.subnet.addWidget(self.subnet_label)
        self.subnet.addWidget(self.subnet_box)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(lambda: self.saveAndClose())
        self.save.addWidget(self.save_button)

        self.inputlist.addLayout(self.num_providers)
        self.inputlist.addLayout(self.pvalidation)
        self.inputlist.addLayout(self.num_iterations)
        self.inputlist.addLayout(self.ivalidation)
        self.inputlist.addLayout(self.budget)
        self.inputlist.addLayout(self.bvalidation)
        self.inputlist.addLayout(self.network)
        self.inputlist.addLayout(self.driver)
        self.inputlist.addLayout(self.subnet)
        self.inputlist.addLayout(self.save)
        self.setLayout(self.inputlist)

    @QtCore.pyqtSlot()
    def saveAndClose(self):
        if self.provider_box.text()=="" or int(self.provider_box.text())==0:
            self.pvalidation_label.setText("Providers cannot be 0 or empty")
            self.pvalidation_label.setHidden(False)
            return
        if self.iterations_box.text()=="" or int(self.iterations_box.text())==0:
            self.ivalidation_label.setText("Iterations cannot be 0 or empty")
            self.ivalidation_label.setHidden(False)
            return
        if self.budget_box.text()=="" or float(self.budget_box.text())==0:
            self.bvalidation_label.setText("Budget cannot be 0 or empty")
            self.bvalidation_label.setHidden(False)
            return
        NUM_PROVIDERS = int(self.provider_box.text())
        NUM_WAVES = int(self.iterations_box.text())
        BUDGET = float(self.budget_box.text())
        NETWORK = str(self.network_box.currentText())
        DRIVER = str(self.driver_box.currentText())
        SUBNET_TAG = str(self.subnet_box.text())
        self.close()

        

class TeamDetailsWindow(QtWebEngineWidgets.QWebEngineView):
    @QtCore.pyqtSlot(str)
    def onInputRecieved(self,data):
        process_user_input(data)




class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        page1 = TeamDetailsWindow()
        backend = Backend(self)
        backend.inputReceived.connect(page1.onInputRecieved)
        backend.nextPage.connect(self.openNextPage)
        channel = QtWebChannel.QWebChannel(self)
        channel.registerObject('backend',backend)
        page1.page().setWebChannel(channel)
        file = QtCore.QDir.current().absoluteFilePath("map.html")
        page1.load(QtCore.QUrl.fromLocalFile(file))
        #self.setCentralWidget(details_page)
        page2 = GenerateSchedule()
        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(page1)
        self.stack.addWidget(page2)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)

    @QtCore.pyqtSlot()
    def openNextPage(self):
        self.stack.setCurrentIndex((self.stack.currentIndex()+1) % 3)


if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec_())
