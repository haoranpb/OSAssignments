 #!/usr/bin/python3
"""
Last Modified: 2018/6/20
Author: 孙浩然
Description: File Management, Assignment for Operating System
Storage: Total 2048 Bytes = 128 Blocks * 16 Bytes, Every char for 1 Bytes

To-do:
1. check wether file and Dir names are available
"""

import sys, os
from PyQt5.QtWidgets import (QApplication, QWidget, QInputDialog, QFileDialog, 
        QLabel, QPushButton, QMessageBox, QMenu, QAction)
from PyQt5 import QtCore


class Block():
    def __init__(self):
        self.str = ''
        self.next = 0

class Node(): # node for dir tree
    def __init__(self, name, fatherNode):
        self.father = fatherNode
        self.son = []
        self.dirName = name
        self.fileList = [] # (fileName, startBlock)


class FileManagement(QWidget):

    def __init__(self):
        super().__init__()
        self.PATH = '' # path to file management root
        self.blockList = [] # the list to store 128 blocks
        self.FAT_Bitmap_list = []
        self.ROOT = '' # file tree root
        self.pointer = ''
        self.currentBtn = []
        self.HEIGHT = 30
        self.LENGTH = 500
        self.selectBtn = ''

        
        self.initUI()
        self.initLogic()
        
        
    def initUI(self):

        infoWindow = QLabel(self)

        infoWindow.setFixedSize(550, 300)
        infoWindow.move(25, 80)

        # button func list
        formatBtn = QPushButton('格式化', self)
        backBtn = QPushButton('返回上一级', self)
        createFileBtn = QPushButton('创建文本文件', self)
        createDirBtn = QPushButton('创建子目录', self)
        deleteBtn = QPushButton('删除', self)
        openBtn = QPushButton('打开', self)

        formatBtn.clicked.connect(self.formatAction)
        backBtn.clicked.connect(self.backAction)
        createFileBtn.clicked.connect(self.createFileAction)
        createDirBtn.clicked.connect(self.createDirAction)
        deleteBtn.clicked.connect(self.deleteAction)
        openBtn.clicked.connect(self.refreshUI)

        backBtn.move(30, 40)
        createFileBtn.move(135, 40)
        createDirBtn.move(230, 40)
        openBtn.move(340, 40)
        deleteBtn.move(410, 40)
        formatBtn.move(480, 40)


        self.loadQss()
        self.setGeometry(300, 200 ,600, 400)
        self.setWindowTitle('File Management')
    
        self.show()

    def initLogic(self):
        
        # self.PATH = QFileDialog.getExistingDirectory(self, 'Choose a file for File Management', '/home') # Add README before pop up 
        
        # check wether the dir is empty before init!!
        if os.path.exists(self.PATH + '/.FAT_Bitmap_list'):
            pass # restore everything from disk
        else: # init
            for i in range(0, 128):
                block = Block()
                self.blockList.append(block) # init blocks
                self.FAT_Bitmap_list.append(block.next) # init FAT_Bitmap_list
            self.ROOT = Node('Root' ,None)
            self.pointer = self.ROOT

        # init Menu
        self.popMenu = QMenu(self)
        openFileAction = QAction('打开', self)
        deletFileAction = QAction('删除', self)
        openFileAction.triggered.connect(self.openFileAction)
        deletFileAction.triggered.connect(self.deleteAction)
        self.popMenu.addAction(openFileAction)
        self.popMenu.addAction(deletFileAction)


    def loadQss(self):
        style_sheet = ''
        with open('./stylesheet.qss', 'r') as f:
            for line in f.readlines():
                style_sheet += line
        self.setStyleSheet(style_sheet)

    def formatAction(self): # delete everything
        pass

    def backAction(self): # go to its father node
        if self.pointer.father == None:
            pass # this is the root
        else:
            self.pointer = self.pointer.father
            self.refreshUI()

    def createFileAction(self):
        fileName, ok = QInputDialog.getText(self, 'Input Dialog', 'Please input new file name:')
        
        if ok and self.checkAvailName(fileName):
            mark = True
            for file in self.pointer.fileList: # look for duplicate name
                if file[0] == str(fileName):
                    mark = False
                    break
  
            # check for available space!!
            start = -1
            for i in range(len(self.FAT_Bitmap_list)):
                if self.FAT_Bitmap_list[i] == 0:
                    start = i
                    break
        
            if mark:
                if start == -1: # limited space
                    pass
                else:
                    self.pointer.fileList.append((str(fileName) + '.txt', start))
                    self.refreshUI()
            else: # already exists
                pass
        else: # Please input correct file name
            pass

    def createDirAction(self):
        dirName, ok = QInputDialog.getText(self, 'Input Dialog', 'Please input new directory name:')

        if ok and self.checkAvailName(dirName):
            mark = True
            for child in self.pointer.son: # check for duplicate name
                if child.dirName == str(dirName):
                    mark = False
                    break

            if mark:
                newNode = Node(str(dirName), self.pointer)
                self.pointer.son.append(newNode)
                print(dirName)
                self.refreshUI() # refresh UI
            else:
                pass # directory already exits
        else:
            pass # Please input correct file name


    def deleteAction(self):
        pass

    def openAction(self):
        pass

    def refreshUI(self): # every file or Dir is a pushbtn, cause they will response to click event
        # the file or dir to be displayed are sons of the self.pointer and its fileList
        for btn in self.currentBtn:
            btn.deleteLater()
        self.currentBtn.clear()

        count = 1
        for file in self.pointer.son: # dir
            btn = QPushButton(file.dirName, self)
            btn.setFixedSize(self.LENGTH, self.HEIGHT)
            btn.setCheckable(True)
            btn.setObjectName('current')
            btn.move(30, 40 + count * self.HEIGHT)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(self.showPopMenu)
            btn.show()
            self.currentBtn.append(btn)
            count = count + 1

        for file in self.pointer.fileList:
            btn = QPushButton(file[0], self)
            btn.setFixedSize(self.LENGTH, self.HEIGHT)
            btn.setCheckable(True)
            btn.setObjectName('current')
            btn.move(30, 40 + count * self.HEIGHT)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(self.showPopMenu)
            btn.show()
            self.currentBtn.append(btn)
            count = count + 1


    def checkAvailName(self, string):
        return True

    def dirDoubelCilckAction(self):
        pass

    def openFileAction(self): # Action in popMenu self.selectBtn
        # self.selectBtn.setStyleSheet('background-color: black')
        if '.txt' in self.selectBtn.text(): # file
            # pop up a text edit dialog && divide into block
            text, ok = QInputDialog.getMultiLineText(self, '文本文件输入框', '请输入内容')
            if ok:
                length = len(text)
                
            else:
                pass
        else: # dir
            for child in self.pointer.son:
                if child.dirName == self.selectBtn.text(): # text need to add slice !!!
                    self.pointer = child
                    self.refreshUI()
                    break

    def deletFileAction(self): # Action in popMenu
        if '.txt' in self.selectBtn.text():
            pass
        else:
            for child in self.pointer.son:
                if child.dirName == self.selectBtn.text(): # text need to add slice !!!
                    pass # have to delete all files in that dir

    def showPopMenu(self, pos):
        source = self.sender()
        self.selectBtn = source
        self.popMenu.exec_(source.mapToGlobal(pos))

    def writeIntoDisk(self):
        pass # write everything into disk when quiting this system, consider to rm -rf everything and write everything again



        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = FileManagement()
    sys.exit(app.exec_())