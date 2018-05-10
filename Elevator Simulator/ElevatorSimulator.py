"""
Last modified: 2018/5/10
Author: 孙浩然
Description: Elevator Simulator, Assignment for Operating System
Issues:
    1. 莫名无法读取相对路径。为防止qss在不同机器上失效，暂时将qss直接写到程序中
    2. 选择电梯时间过短，犹豫是否要多给一个周期
    3. 给一些类单独建一个文件夹

三角形qss：
    background-color: transparent;
    border: 10px solid white;
    border-top: 10px solid transparent;
    border-bottom: 20px solid red;
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPainter, QPen, QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, pyqtSignal, QObject, QTimer


class Communication(QObject):

    movement = pyqtSignal()


class BubbleButton(QPushButton):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.clickabel = 'True'


class Bubble(QLabel): # 可选楼层的气泡

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(190, 80)
        self.setAlignment(Qt.AlignCenter)
        self.button_list = []
        self.pressed_floor_list = []

        self.initUI()

    def initUI(self):
        text = QLabel('请选择您要去的楼层：',self)
        text.move(5, 8)
        text.setObjectName('text')
        for i in range(10):
            button = BubbleButton(self)
            button.setText(str(i+1))
            button.resize(15, 15)
            button.setObjectName('button')
            button.move(1 + i*19, 35)
            button.clicked.connect(self.choose_floor)
            self.button_list.append(button)

        for i in range(10):
            button = BubbleButton(self)
            button.setText(str(i+11))
            button.resize(15, 15)
            button.setObjectName('button')
            button.move(1 + i*19, 55)
            button.clicked.connect(self.choose_floor)
            self.button_list.append(button)


    def choose_floor(self):
        source = self.sender()
        if source.clickabel == 'False': # 无法点击
            return
        elif int(source.text()) not in self.pressed_floor_list: # 不可取消
            self.pressed_floor_list.append(int(source.text()))



class Elevator(QLabel): # 每个电梯都需要一个表示当前运动状态的变量
    def __init__(self, parent, number):
        super().__init__(parent)
        self.setText('1')
        self.setAlignment(Qt.AlignCenter)
        self.to_floor_list = [] # 记录 要去的楼层数 和 到达该楼层后会发生什么 0-到达后不进入等待状态 1-进入上行等待 2-下行等待
        self.current_floor = 1 # 当前楼层
        self.status = 0 # 当前运行状态 0-空闲 1-上行 2-下行 3-上行等待 4-下行等待


class UpDownButton(QPushButton): # 不需要checkable，不可取消

    def __init__(self, parent, number, n):
        super().__init__(parent)
        self.floor_num = number # 记录楼层数
        self.resize(20, 20)
        self.up_down = n


class ElevatorSimulator(QWidget):

    def __init__(self):
        super().__init__()
        self.LENGTH = 200
        self.HEIGHT = 33
        self.DOWN_TIME = 100
        self.UP_TIME = 200
        self.TIME = 1800
        self.timer = QTimer()
        self.elevator_list = []
        self.animation_list = []
        self.bubble_list = []
        self.bubble_animation_list = []

        self.up_list = [] # 用来储存按过向上的按钮的楼层数   只有电梯运行方向发生改变后，才会将等待的按键处理掉
        self.down_list = [] # 之后分配给相应的电梯

        self.initUI()


    def initUI(self):

        self.c = Communication()
        self.c.movement.connect(self.elevator_move) # 接受上下按钮的信号
        self.setWindowIcon(QIcon('./icon.jpeg'))

        self.create_elevator()
        self.create_up_down_button()
        self.create_bubble()
        self.load_qss()

        self.setGeometry(100, 50 ,1200, 768) # 前两位是生成位置坐标，后两位是生成窗口大小
        self.setWindowTitle('Elevator Simulator')

        self.show()

    
    def load_qss(self):
        style_sheet = ''
        with open('./stylesheet.qss', 'r') as f:
            for line in f.readlines():
                style_sheet+=line
        self.setStyleSheet(style_sheet)


    def create_bubble(self):
        for i in range(5):
            bubble = Bubble(self)
            #bubble.setStyleSheet("QWidget { border-radius: 4px; background-color: %s }" % self.color_list[i])
            bubble.move(i * self.LENGTH + 5,768) # 675
            bubble.setObjectName(str(i+1))
            self.bubble_list.append(bubble)

            animation1 = QPropertyAnimation(bubble, b'pos')
            animation2 = QPropertyAnimation(bubble, b'pos')
            animation1.setDuration(self.UP_TIME)
            animation2.setDuration(self.DOWN_TIME)
            animation1.setEndValue(QPoint(i * self.LENGTH + 5, 675)) # up
            animation2.setEndValue(QPoint(i * self.LENGTH + 5, 768)) # down
            animation_set = [animation1, animation2]
            self.bubble_animation_list.append(animation_set)

    
    def bubble_animation(self, n): # 传入电梯编号
        if self.elevator_list[n].status == 3: # 该向上了
            for i in range(20):
                if (i + 1) <= self.elevator_list[n].current_floor:
                    self.bubble_list[n].button_list[i].clickabel = 'False'
                else:
                    self.bubble_list[n].button_list[i].clickabel = 'True'
        else: # 该向下了
            for i in range(20):
                if (i + 1) >= self.elevator_list[n].current_floor:
                    self.bubble_list[n].button_list[i].clickabel = 'False'
                else:
                    self.bubble_list[n].button_list[i].clickabel = 'True'

        self.bubble_animation_list[n][0].start()


    def bubble_down(self):
        for i in range(5):
            self.bubble_animation_list[i][1].start()
        self.timer.singleShot(self.DOWN_TIME - 10, self.down_finished)
        

    def down_finished(self):
        is_stop = True
        for i in range(5): # 需要顺便检查电梯按钮按下情况
            for floor in self.bubble_list[i].pressed_floor_list:
                if ([floor, 0] in self.elevator_list[i].to_floor_list) or ([floor, 1] in self.elevator_list[i].to_floor_list) or ([floor, 2] in self.elevator_list[i].to_floor_list):
                    continue
                else:
                    self.elevator_list[i].to_floor_list.append([floor, 0])

            self.bubble_list[i].pressed_floor_list = []
            self.elevator_list[i].to_floor_list.sort() # 排序

            if len(self.elevator_list[i].to_floor_list) != 0:
                is_stop = False

        if len(self.up_list) != 0 or len(self.down_list) != 0:
            is_stop = False
        
        for i in range(5):
            if self.elevator_list[i].status == 0: # 状态不需要更改
                continue
            elif self.elevator_list[i].status == 1:
                if len(self.elevator_list[i].to_floor_list) == 0:
                    self.elevator_list[i].status = 0
            elif self.elevator_list[i].status == 2:
                if len(self.elevator_list[i].to_floor_list) == 0:
                    self.elevator_list[i].status = 0
            elif self.elevator_list[i].status == 3:
                if len(self.elevator_list[i].to_floor_list) == 0:
                    self.elevator_list[i].status = 0
                else:
                    self.elevator_list[i].status = 1
                    j_mark = -1
                    self.up_list.sort()
                    for j in range(len(self.up_list)):
                        if self.up_list[j] >= self.elevator_list[i].current_floor:
                            if j_mark == -1:
                                j_mark = j
                            self.elevator_list[i].append([self.up_list[j], 1])
                    if j_mark != -1:
                        self.up_list = self.up_list[0:j_mark]
                        self.elevator_list[i].sort()
            elif self.elevator_list[i].status == 4:
                if len(self.elevator_list[i].to_floor_list) == 0:
                    self.elevator_list[i].status = 0
                else:
                    self.elevator_list[i].status = 2
                    j_mark = -1
                    self.down_list.sort()
                    for j in range(len(self.down_list)):
                        if self.down_list[j] <= self.elevator_list[i].current_floor:
                            j_mark = j
                            self.elevator_list[i].append([self.down_list[j], 2])
                    if j_mark != -1: # 发生了if
                        self.down_list = self.down_list[j_mark+1:]
                        self.elevator_list[i].sort()
            if self.elevator_list[i].status == 0:
                if len(self.up_list) != 0:
                    self.up_list.sort()
                    if self.up_list[-1] < self.elevator_list[i].current_floor:
                        self.elevator_list[i].to_floor_list.append([self.up_list.pop(), 1])
                    else:
                        j_mark = -1
                        for j in range(len(self.up_list)):
                            if self.up_list[j] >= self.elevator_list[i].current_floor:
                                if j_mark == -1:
                                    j_mark = j
                                self.elevator_list[i].to_floor_list.append([self.up_list[j], 1])
                        self.elevator_list[i].to_floor_list.sort()
                        self.up_list = self.up_list[0:j_mark]
                if len(self.down_list) != 0 and len(self.elevator_list[i].to_floor_list) == 0: # 没分给
                    self.down_list.sort()
                    if self.down_list[0] > self.elevator_list[i].current_floor:
                        self.elevator_list[i].to_floor_list.append([self.down_list.pop(0), 2])
                    else:
                        j_mark = -1
                        for j in range(len(self.down_list)):
                            if self.down_list[j] < self.elevator_list[i].current_floor:
                                j_mark = j
                                self.elevator_list[i].to_floor_list.append([self.down_list[j], 2])
                        self.down_list = self.down_list[j_mark+1:]
                        self.elevator_list[i].to_floor_list.sort()

        # 在这里处理所有电梯的状态变化
        if not is_stop: # 是否应该在这里判断
            self.c.movement.emit() # 发送运动信号


    def elevator_move(self): # 电梯移动 每次一层
        for i in range(5):
            if len(self.elevator_list[i].to_floor_list) == 0: # 没有要去的地方，持续空闲状态
                continue
            if self.elevator_list[i].status == 0 and self.elevator_list[i].to_floor_list[0][0] == self.elevator_list[i].current_floor: # len=1 
                if self.elevator_list[i].to_floor_list[0][1] == 1:
                    self.elevator_list[i].status = 3 # 如果有按钮被按下，这个周期结束时状态应该变为1，没有为0
                    self.elevator_list[i].to_floor_list.pop()
                    self.bubble_animation(i)
                elif self.elevator_list[i].to_floor_list[0][1] == 2:
                    self.elevator_list[i].status = 4
                    self.elevator_list[i].to_floor_list.pop()
                    self.bubble_animation(i)

            elif self.elevator_list[i].status == 1 and self.elevator_list[i].to_floor_list[0][0] == self.elevator_list[i].current_floor:
                if self.elevator_list[i].to_floor_list[0][1] == 0:
                    self.elevator_list[i].to_floor_list.pop(0)
                elif self.elevator_list[i].to_floor_list[0][1] == 1:
                    self.elevator_list[i].status = 3 # 这个也已去掉，后面判断是否大于2，来决定是否继续执行
                    self.elevator_list[i].to_floor_list.pop(0)
                    self.bubble_animation(i)
                elif self.elevator_list[i].to_floor_list[0][1] == 2: # len == 1
                    self.elevator_list[i].status = 4
                    self.elevator_list[i].to_floor_list.pop(0)
                    self.bubble_animation(i)

            elif self.elevator_list[i].status == 2 and self.elevator_list[i].to_floor_list[-1][0] == self.elevator_list[i].current_floor:
                if self.elevator_list[i].to_floor_list[-1][1] == 0: # 是否需要判断len() == 1???
                    self.elevator_list[i].to_floor_list.pop()
                elif self.elevator_list[i].to_floor_list[-1][1] == 1: # len == 1
                    self.elevator_list[i].status = 3
                    self.elevator_list[i].to_floor_list.pop()
                    self.bubble_animation(i)
                elif self.elevator_list[i].to_floor_list[-1][1] == 2:
                    self.elevator_list[i].status = 4
                    self.elevator_list[i].to_floor_list.pop()
                    self.bubble_animation(i)

            if len(self.elevator_list[i].to_floor_list) == 0 or self.elevator_list[i].status > 2: # 前面再次清空了，或处于等待装填
                continue
            # 前面必须把电梯停在某个楼层处理好，下面的判断语句
            if self.elevator_list[i].to_floor_list[0][0] < self.elevator_list[i].current_floor: # 下行
                self.elevator_list[i].status = 2
                self.animation_list[i].setEndValue(QPoint(i * self.LENGTH, self.HEIGHT * (21-self.elevator_list[i].current_floor)))
                self.animation_list[i].start()
            if self.elevator_list[i].to_floor_list[0][0] > self.elevator_list[i].current_floor: # 上行
                self.elevator_list[i].status = 1
                self.animation_list[i].setEndValue(QPoint(i * self.LENGTH, self.HEIGHT * (19-self.elevator_list[i].current_floor)))
                self.animation_list[i].start()

        self.timer.singleShot(self.TIME + 200, self.bubble_down)

    def ele_animation_finished(self):
        source = self.sender()
        for i in range(5):
            if self.animation_list[i] == source:
                if self.elevator_list[i].status == 1:
                    self.elevator_list[i].current_floor += 1
                    self.elevator_list[i].setText(str(self.elevator_list[i].current_floor))
                else:
                    self.elevator_list[i].current_floor -= 1
                    self.elevator_list[i].setText(str(self.elevator_list[i].current_floor))

    
    def create_elevator(self):
        for i in range(5):
            elevator = Elevator(self, i)
            elevator.resize(self.LENGTH, self.HEIGHT)
            #elevator.setStyleSheet("QWidget { background-color: %s }" % self.color_list[i]) # qss 解决
            elevator.move(i * self.LENGTH, self.HEIGHT * 19)
            elevator.setObjectName(str(i+1))
            self.elevator_list.append(elevator)

            animation = QPropertyAnimation(elevator, b'pos')
            animation.setDuration(self.TIME)
            animation.finished.connect(self.ele_animation_finished)

            self.animation_list.append(animation)


    def create_up_down_button(self): # 创建上下按钮，无需记录下来
        for i in range(20):
            if i != 0:
                up_button = UpDownButton(self, 20 - i, 1)
                up_button.setText('↑')
                up_button.setObjectName('up')
                up_button.move(5* self.LENGTH + 60, self.HEIGHT * i +10)
                up_button.clicked.connect(self.up_down_pressed)

            if i !=19:
                down_button = UpDownButton(self, 20 - i, 2)
                down_button.setObjectName('down')
                down_button.setText('↓')
                down_button.move(5 * self.LENGTH + 120, self.HEIGHT * i +10)
                down_button.clicked.connect(self.up_down_pressed)


    def up_down_pressed(self): # 上下按钮 触发函数
        source = self.sender()
        # 判重
        is_same = False
        if source.up_down == 1: # 遍历等待队列
            for tmp in self.up_list:
                if tmp == source.floor_num:
                    is_same = True
        else:
            for tmp in self.down_list:
                if tmp == source.floor_num:
                    is_same = True

        for ele in self.elevator_list: # 遍历电梯
            if ele.status == source.up_down:
                for tmp in ele.to_floor_list:
                    if tmp[0] == source.floor_num and tmp[1] == source.up_down:
                        is_same = True
            elif ele.status == (source.up_down + 2) and ele.current_floor == source.floor_num:
                is_same = True
        if is_same:
            return

        is_all_leisure = True
        min_dist = 20 # 距离按下楼层的距离
        min_ele = -1

        for ele in self.elevator_list: # 遍历5个电梯
            if ele.status != 0: # 每个电梯都需要判断，决定了是否发送运动信号
                is_all_leisure = False
            if ele.status == 0 : # 空闲的电梯
                dis = abs(ele.current_floor - source.floor_num)
                if dis < min_dist:
                    min_dist = dis
                    min_ele = ele
            elif ele.status == 1 and source.up_down == 1: # 向上
                if ele.current_floor >= source.floor_num:
                    continue # 这个电梯不行

                avail_mark = True
                for stop in ele.to_floor_list:
                    if stop[1] == 2:
                        avail_mark = False
                        break

                if avail_mark:
                    dis = abs(ele.current_floor - source.floor_num)
                    if dis < min_dist:
                        min_dist = dis
                        min_ele = ele
                
            elif ele.status == 2 and source.up_down == 2: # 向下
                if ele.current_floor <= source.floor_num:
                    continue
                
                avail_mark = True
                for stop in ele.to_floor_list:
                    if stop[1] == 1:
                        avail_mark = True
                        break

                if avail_mark:
                    dis = abs(ele.current_floor - source.floor_num)
                    if dis < min_dist:
                        min_dist = dis
                        min_ele = ele

        if min_ele == -1: # 暂时无可用电梯，放入等候队列
            if source.up_down == 1:
                self.up_list.append(source.floor_num) # 暂时没想好是否需要排序
            else:
                self.down_list.append(source.floor_num) # 暂时没想好是否需要排序
        else: # 有可用
            min_ele.to_floor_list.append([source.floor_num, source.up_down])
            min_ele.to_floor_list.sort() # 按楼层排序

        if is_all_leisure: # 只有全部空闲，发送电梯运行信号
            self.c.movement.emit()


    def paintEvent(self, e): # 绘画操作开始
        qp = QPainter()
        qp.begin(self)
        self.draw_line(qp)
        qp.end()


    def draw_line(self, qp): # 电梯绳
        pen = QPen(Qt.black, 0.5, Qt.SolidLine)
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([4, 20])
        qp.setPen(pen)
        for i in range(5):
            qp.drawLine(100 + i * self.LENGTH, 0, 100 + i * self.LENGTH, 660)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    elevator_simulator = ElevatorSimulator()
    sys.exit(app.exec_())
