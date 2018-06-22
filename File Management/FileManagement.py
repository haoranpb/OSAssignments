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
import math


class Block():
    def __init__(self):
        self.str = ''
        self.next = -1

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
        self.FAT_Bitmap_list = []
        self.ROOT = '' # file tree root
        self.pointer = ''
        self.currentBtn = []
        self.HEIGHT = 30
        self.LENGTH = 500
        self.selectBtn = ''
        self.storageRemain = 2048


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
        quitBtn = QPushButton('保存并退出', self)

        formatBtn.clicked.connect(self.formatAction)
        backBtn.clicked.connect(self.backAction)
        createFileBtn.clicked.connect(self.createTextFileAction)
        createDirBtn.clicked.connect(self.createDirAction)
        quitBtn.clicked.connect(self.writeIntoDisk)

        backBtn.move(30, 40)
        createFileBtn.move(135, 40)
        createDirBtn.move(230, 40)
        formatBtn.move(480, 40)
        quitBtn.move(500, 300)


        self.loadQss()
        self.setGeometry(300, 200 ,750, 400)
        self.setWindowTitle('File Management')
    
        self.show()

    def initLogic(self):
        
        self.PATH = QFileDialog.getExistingDirectory(self, 'Choose a file for File Management', '/home') # Add README before pop up 
        
        # check wether the dir is empty before init!!
        if os.path.exists(self.PATH + '/.FAT_BitMap_list'):
            pass # restore everything from disk
        else: # init
            for i in range(0, 128):
                block = Block()
                self.FAT_Bitmap_list.append(block) # init FAT_Bitmap_list
            self.ROOT = Node('Root' ,None)
            self.pointer = self.ROOT

        # init Menu
        self.popMenu = QMenu(self)
        openFileAction = QAction('打开', self)
        deletFileAction = QAction('删除', self)
        openFileAction.triggered.connect(self.openFileAction)
        deletFileAction.triggered.connect(self.deleteFileAction)
        self.popMenu.addAction(openFileAction)
        self.popMenu.addAction(deletFileAction)


    def loadQss(self):
        style_sheet = ''
        with open('./stylesheet.qss', 'r') as f:
            for line in f.readlines():
                style_sheet += line
        self.setStyleSheet(style_sheet)

    def formatAction(self): # delete everything
        self.pointer = self.ROOT
        self.deleteDir(self.ROOT)
        self.refreshUI()

    def backAction(self): # go to its father node
        if self.pointer.father == None:
            pass # this is the root
        else:
            self.pointer = self.pointer.father
            self.refreshUI()

    def createTextFileAction(self):
        fileName, ok = QInputDialog.getText(self, 'Input Dialog', 'Please input new file name:')
        
        if ok and str(fileName).isalnum():
            mark = True
            for file in self.pointer.fileList: # look for duplicate name
                if file[0] == str(fileName):
                    mark = False
                    break
  
            # check for available space!!
            start = -1
            for i in range(len(self.FAT_Bitmap_list)):
                if len(self.FAT_Bitmap_list[i].str) == 0:
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

        if ok and str(dirName).isalnum():
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


    def openFileAction(self): # Action in popMenu self.selectBtn
        # self.selectBtn.setStyleSheet('background-color: black')
        if '.txt' in self.selectBtn.text(): # file
            # pop up a text edit dialog && divide into block
            selectedFile = ''
            for file in self.pointer.fileList:
                if file[0] == self.selectBtn.text(): # remember to parse filename
                    selectedFile = file
                    break
            originText = self.getText(selectedFile) # get whole text from blocks
            self.releaseTextFile(selectedFile[1])

            text, ok = QInputDialog.getMultiLineText(self, '文本文件输入框', '请输入内容', originText)
            if ok:
                length = len(text)
                if len(text) % 16 ==0:
                    pass
                else:
                    length = math.floor(length/16 + 1) * 16

                if length > self.storageRemain:
                    pass # 
                else:
                    self.storageRemain -= length
                    blockPointer = self.FAT_Bitmap_list[selectedFile[1]]
                    for i in range(round(length/16)):
                        blockPointer.str = text[i*16:(i+1)*16]
                        if i == (round(length/16)-1):
                            break
                        for j in range(len(self.FAT_Bitmap_list)):
                            if len(self.FAT_Bitmap_list[j].str) == 0: # empty
                                blockPointer.next = j
                                blockPointer = self.FAT_Bitmap_list[j]
                                break
                # print(self.storageRemain)
                # for block in self.FAT_Bitmap_list:
                #     if len(block.str) != 0:
                #         print(block.str)
            else:
                pass
        else: # dir
            for child in self.pointer.son:
                if child.dirName == self.selectBtn.text(): # text need to add slice !!!
                    self.pointer = child
                    self.refreshUI()
                    break

    def releaseTextFile(self, startBlockNum):
        blockPointer = self.FAT_Bitmap_list[startBlockNum]
        while True:
            if blockPointer.next == -1:
                if len(blockPointer.str) == 0: # empty
                    break
                else:
                    blockPointer.str = ''
                    self.storageRemain += 16
                    break
            else:
                self.storageRemain += 16
                blockPointer.str = ''
                tmp = blockPointer.next
                blockPointer.next = -1
                blockPointer = self.FAT_Bitmap_list[tmp]


    def deleteFileAction(self): # Action in popMenu
        if '.txt' in self.selectBtn.text():
            selectedFile = ''
            for file in self.pointer.fileList:
                if file[0] == self.selectBtn.text(): # remember to parse filename
                    selectedFile = file
                    break
            self.releaseTextFile(selectedFile[1])
            self.pointer.fileList.remove(selectedFile)
            self.refreshUI()
            # print(self.storageRemain)
        else:
            for child in self.pointer.son:
                if child.dirName == self.selectBtn.text(): # text need to add slice !!!
                    # have to delete all files in that dir
                    self.deleteDir(child)
                    self.refreshUI()
                    break


    def showPopMenu(self, pos):
        source = self.sender()
        self.selectBtn = source
        self.popMenu.exec_(source.mapToGlobal(pos))

    def getText(self, selectedFile):
        string = ''
        i = selectedFile[1]
        while True:
            string += self.FAT_Bitmap_list[i].str
            i = self.FAT_Bitmap_list[i].next
            if i == -1:
                break
        return string

    def deleteDir(self, dirNode):
        for file in dirNode.fileList:
            self.releaseTextFile(file[1])
        dirNode.clear()
        for child in dirNode.son:
            self.deleteDir(child)

    def writeIntoDisk(self):
        # write everything into disk when quiting this system, consider to rm -rf everything and write everything again
        with open(self.PATH + '/.FAT_BitMap_list', 'w') as f:
            for block in self.FAT_Bitmap_list:
                f.write(str(block.next) + '\n')
        self.writeEveryDir(self.ROOT, self.PATH)
        sys.exit()

    def writeEveryDir(self, dirNode, path):
        with open(path + '/.index', 'w') as f:
            for file in dirNode.fileList:
                f.write(file[0] + ' ' + str(file[1]) + '\n')

        for file in dirNode.fileList:
            text = self.getText(file)
            with open(path + '/' + file[0], 'w') as f:
                f.write(text)

        for child in dirNode.son:
            os.mkdir(path + '/' + child.dirName)
            self.writeEveryDir(child, path + '/' + child.dirName)
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = FileManagement()
    sys.exit(app.exec_())