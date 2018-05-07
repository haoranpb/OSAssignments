"""
Last modified: 2018/5/7
Author: 孙浩然
Description: Elevator Simulator, Assignment for Operating System
Issues:
    1. 莫名无法读取相对路径。为防止qss在不同机器上失效，暂时将qss直接写到程序中
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class ElevatorSimulator(QWidget):

    def __init__(self):
        super().__init__()
        #self.setStyleSheet('background-color: white')
        self.ELEVATOR_LENGTH = 200
        self.HEIGHT = 33
        self.FLOOR_LENGTH = 120

        self.elevator_list = [] # 五个电梯
        self.elevator_button_list = []
        self.floor_button_list = []
        self.up_down_list = []
        self.selected_floor_list = []

        self.initUI()


    def initUI(self):

        for i in range(0, 5):
            self.create_elevator(i+1)
        self.create_elevator_button()
        self.create_label()
        self.create_floor_button()
        self.create_up_down_button()
        self.setGeometry(100, 50 ,1200, 759) # 前两位是生成位置坐标，后两位是生成窗口大小
        self.setWindowTitle('Elevator Simulator')
        self.show()


    def create_elevator(self, number):
        cell_list = [] # 每个电梯的20层
        for i in range(0, 20):
            cell = QLabel(str(20 - i) + '层', self)
            cell.resize(self.ELEVATOR_LENGTH, self.HEIGHT)
            cell.setAlignment(Qt.AlignCenter) # 居中
            cell.setStyleSheet('background-color:white;font-size:15px') # UI待完善
            cell.move((number - 1) * self.ELEVATOR_LENGTH, i * self.HEIGHT)
            cell_list.append(cell)
        self.elevator_list.append(cell_list)

    
    def create_elevator_button(self):
        for i in range(0, 5):
            elevator_button = QPushButton('电梯' + str(i + 1), self) # UI待完善
            elevator_button.setCheckable(True)
            elevator_button.resize(self.ELEVATOR_LENGTH + 15, self.HEIGHT + 10)
            elevator_button.move(i * self.ELEVATOR_LENGTH - 6, 20 * self.HEIGHT - 3)

            elevator_button.clicked.connect(self.select_elevator) # 连接按下后的触发事件
            if i == 0: # 默认第一个按钮被按下
                elevator_button.click()
                self.selected_elevator = elevator_button # 标记被按下的按钮
            self.elevator_button_list.append(elevator_button)


    def create_label(self): # 创建那个不会发生任何变化的按钮
        button = QLabel('上下按钮', self)
        button.resize(self.ELEVATOR_LENGTH, self.HEIGHT)
        button.setAlignment(Qt.AlignCenter)
        button.setStyleSheet('background-color:grey') # UI待完善
        button.move(5 * self.ELEVATOR_LENGTH, 20 * self.HEIGHT)


    def create_floor_button(self): # 创建楼层按钮
        for i in range(0, 10): # UI待完善
            floor_button = QPushButton(str(i + 1), self)
            floor_button.setCheckable(True)
            floor_button.resize(self.ELEVATOR_LENGTH + 5, self.HEIGHT + 12)
            floor_button.move(i * self.FLOOR_LENGTH - 10, 21 * self.HEIGHT -5)

            floor_button.clicked.connect(self.select_floor)
            self.floor_button_list.append(floor_button)

        for i in range(0, 10):
            floor_button = QPushButton(str(i + 11), self)
            floor_button.setCheckable(True)
            floor_button.resize(self.ELEVATOR_LENGTH + 5, self.HEIGHT + 13)
            floor_button.move(i * self.FLOOR_LENGTH - 10, 22 * self.HEIGHT - 5)

            floor_button.clicked.connect(self.select_floor)
            self.floor_button_list.append(floor_button)


    def create_up_down_button(self):
        for i in range(0, 20):
            up_down_set = []
            up_button = QPushButton(self)
            up_button.setCheckable(True)
            up_button.resize(20, 20)
            up_button.setStyleSheet('background-color: grey') # 三角形最后再变吧
            up_button.move(5* self.ELEVATOR_LENGTH + 60, self.HEIGHT * i +10)
            up_down_set.append(up_button)

            down_button = QPushButton(self)
            down_button.setCheckable(True)
            down_button.resize(20, 20)
            down_button.setStyleSheet('background-color: grey') # 三角形最后再变吧
            down_button.move(5 * self.ELEVATOR_LENGTH + 120, self.HEIGHT * i +10)
            up_down_set.append(down_button)
            self.up_down_list.append(up_down_set)

    
    def select_elevator(self): # 电梯移动
        source = self.sender()
        self.selected_elevator = source # 标记被按下的电梯
        for elevator_button in self.elevator_button_list: # 一个电梯按下后，其他的需要弹起
            if elevator_button.isChecked() and elevator_button != source: # source 是 pushButton 类型
                elevator_button.nextCheckState() # 不能用click，因为再一次点击，所以会把所有的按钮都弹起。需要使用nextCheckState
    

    def select_floor(self):
        source = self.sender()
        pass


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    elevator = ElevatorSimulator()
    sys.exit(app.exec_())
