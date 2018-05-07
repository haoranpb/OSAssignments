"""
Last modified: 2018/5/6
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
        self.LENGTH = 200
        self.HEIGHT = 33
        self.elevator_list = []
        self.elevator_button_list = []
        self.floor_button_list = []

        self.initUI()


    def initUI(self):

        for i in range(0, 5):
            self.create_elevator(i+1)
        self.create_elevator_button()
        self.create_label()
        self.create_floor_button()

        self.setGeometry(100, 50 ,1200, 759) # 前两位是生成位置坐标，后两位是生成窗口大小
        self.setWindowTitle('Elevator Simulator')
        self.show()


    def create_elevator(self, number):
        cell_list = []
        for i in range(0, 20):
            cell = QLabel(self)
            cell.resize(self.LENGTH, self.HEIGHT)
            cell.setText(str(20 - i) + '层') # 内容
            cell.setAlignment(Qt.AlignCenter) # 居中
            cell.setStyleSheet('background-color:white;font-size:15px') # UI待完善
            cell.move((number - 1) * self.LENGTH, i * self.HEIGHT)
            cell_list.append(cell)
        self.elevator_list.append(cell_list)

    
    def create_elevator_button(self):
        for i in range(0, 5):
            elevator_button = QPushButton('电梯' + str(i + 1), self) # UI待完善
            elevator_button.setCheckable(True)
            elevator_button.resize(self.LENGTH, self.HEIGHT + 10)
            elevator_button.move(i * self.LENGTH, 20 * self.HEIGHT)

            elevator_button.clicked.connect(self.select_elevator) # 连接按下后的出发事件
            if i == 0: # 默认第一个按钮被按下
                elevator_button.click()
                self.selected_elevator = elevator_button # 标记被按下的按钮
            self.elevator_button_list.append(elevator_button)


    def create_label(self): # 创建那两个不会发生任何变化的按钮
        pass


    def create_floor_button(self): # 创建楼层按钮
        pass

    
    def select_elevator(self): # 电梯移动
        source = self.sender()
        self.selected_elevator = source # 标记被按下的电梯
        for elevator_button in self.elevator_button_list: # 一个电梯按下后，其他的需要弹起
            if elevator_button.isChecked() and elevator_button != source: # source 是 pushButton 类型
                elevator_button.nextCheckState() # 不能用click，因为再一次点击，所以会把所有的按钮都弹起。需要使用nextCheckState
        


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    elevator = ElevatorSimulator()
    sys.exit(app.exec_())
