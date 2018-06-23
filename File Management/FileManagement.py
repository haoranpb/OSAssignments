 #!/usr/bin/python3
"""
Last Modified: 2018/6/20
Author: 孙浩然
Description: File Management, Assignment for Operating System
Storage: Total 2048 Bytes = 128 Blocks * 16 Bytes, Every char for 1 Bytes
"""

import sys, os
from PyQt5.QtWidgets import (QApplication, QWidget, QInputDialog, QFileDialog, 
        QLabel, QPushButton, QMessageBox, QMenu, QAction)
from PyQt5 import QtCore
import math, shutil


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
        self.HEIGHT = 20
        self.LENGTH = 550
        self.selectBtn = ''
        self.storageRemain = 2048
        self.currentPath = ''


        self.initUI()
        self.initLogic()

        
    def initUI(self):

        infoWindow = QLabel(self)
        self.pathWindow = QLabel('PATH:', self)
        self.storageWindow = QLabel('Free:\n2048', self)
        infoTitle = QLabel('       文件名      |     文件类型      |     起始块     |      大小', self)

        infoWindow.setObjectName('info')
        self.pathWindow.setObjectName('path')
        self.storageWindow.setObjectName('storage')
        infoTitle.setObjectName('infoTitle')

        infoWindow.setFixedSize(550, 300)
        self.pathWindow.setFixedWidth(300)
        infoTitle.setFixedSize(550, 20)

        infoWindow.move(25, 80)
        infoTitle.move(25, 80)
        self.pathWindow.move(55, 55)
        self.storageWindow.move(625, 120)

        # button func list
        formatBtn = QPushButton('格式化', self)
        backBtn = QPushButton('返回上一级', self)
        createFileBtn = QPushButton('创建文本文件', self)
        createDirBtn = QPushButton('创建子目录', self)
        quitBtn = QPushButton('保存并退出', self)
        selectFileBtn = QPushButton('选择工作目录', self)

        formatBtn.clicked.connect(self.formatAction)
        backBtn.clicked.connect(self.backAction)
        createFileBtn.clicked.connect(self.createTextFileAction)
        createDirBtn.clicked.connect(self.createDirAction)
        quitBtn.clicked.connect(self.writeIntoDisk)
        selectFileBtn.clicked.connect(self.selectFile)

        backBtn.move(50, 15)
        createFileBtn.move(180, 15)
        createDirBtn.move(320, 15)
        formatBtn.move(450, 15)
        selectFileBtn.move(600, 290)
        quitBtn.move(600, 330)
        quitBtn.setFixedSize(120, 32)


        self.loadQss()
        self.setGeometry(300, 200 ,750, 400)
        self.setWindowTitle('File Management')
    
        self.show()

    def initLogic(self):

        # init Menu
        self.popMenu = QMenu(self)
        openFileAction = QAction('打开', self)
        deletFileAction = QAction('删除', self)
        openFileAction.triggered.connect(self.openFileAction)
        deletFileAction.triggered.connect(self.deleteFileAction)
        self.popMenu.addAction(openFileAction)
        self.popMenu.addAction(deletFileAction)

    def refreshUI(self): # every file or Dir is a pushbtn, cause they will response to click event

        # the file or dir to be displayed are sons of the self.pointer and its fileList
        for btn in self.currentBtn:
            btn.deleteLater()
        self.currentBtn.clear()

        self.pathWindow.setText('PATH:' + self.currentPath)
        self.storageWindow.setText('Free:\n' + str(self.storageRemain))

        count = 1
        for file in self.pointer.son: # dir
            name = file.dirName + (18 - len(file.dirName)) * ' ' +'folder'
            btn = QLabel(name, self)
            btn.setFixedSize(self.LENGTH, self.HEIGHT)
            btn.setObjectName('current')
            btn.move(25, 80 + count * self.HEIGHT)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(self.showPopMenu)
            btn.show()
            self.currentBtn.append(btn)
            count = count + 1

        for file in self.pointer.fileList:
            name = str(file[0]) + (18 - len(file[0]))*' ' + 'textFile' + ' '*9 + str(file[1]) + (14 - math.ceil(file[1]/10))*' ' + str(self.getTextFileSize(file[1]))
            btn = QLabel(name, self)
            btn.setFixedSize(self.LENGTH, self.HEIGHT)
            btn.setObjectName('current')
            btn.move(25, 80 + count * self.HEIGHT)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(self.showPopMenu)
            btn.show()
            self.currentBtn.append(btn)
            count = count + 1

    def selectFile(self):

        self.PATH = QFileDialog.getExistingDirectory(self, 'Choose a file for File Management', '/home') # Add README before pop up 
        
        # check wether the dir is empty before init!!
        if os.path.exists(self.PATH + '/.FAT_BitMap_list'):
            with open(self.PATH + '/.FAT_BitMap_list', 'r') as f:
                for line in f.readlines():
                    if len(line) == 1: # skip the last \n
                        continue
                    result = line.split()
                    block = Block()
                    if len(result)>1:
                        block.next = int(result[0])
                        block.str = result[1]
                        self.storageRemain -= 16
                    else:
                        block.next = int(result[0])
                        block.str = ''
                    self.FAT_Bitmap_list.append(block)

            self.ROOT = Node('Root' ,None)
            self.pointer = self.ROOT
            self.restoreFileTree(self.ROOT, self.PATH)
            self.refreshUI()
        else: # init
            for i in range(0, 128):
                block = Block()
                self.FAT_Bitmap_list.append(block) # init FAT_Bitmap_list
                self.ROOT = Node('Root' ,None)
                self.pointer = self.ROOT

    def restoreFileTree(self, dirNode, path):
        with open(os.path.join(path, '.index'), 'r') as f:
            for line in f.readlines():
                tmp1, tmp2 = line.split()
                dirNode.fileList.append((tmp1, int(tmp2)))
        
        for file in os.listdir(path):
            if (file == '.index') or (file == '.FAT_BitMap_list') or ('.txt' in file):
                continue
            else:
                newNode = Node(file, dirNode)
                dirNode.son.append(newNode)
                self.restoreFileTree(newNode, os.path.join(path, file))

    def loadQss(self):
        style_sheet = ''
        with open('./stylesheet.qss', 'r') as f:
            for line in f.readlines():
                style_sheet += line
        self.setStyleSheet(style_sheet)

    def formatAction(self): # delete everything
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:
            self.pointer = self.ROOT
            self.deleteDir(self.ROOT)
            self.currentPath = ''
            self.refreshUI()

    def backAction(self): # go to its father node
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:
            if self.pointer.father == None:
                QMessageBox.information(self, 'Warning', '您已经处于根目录了！')
            else:
                self.pointer = self.pointer.father
                pos = self.currentPath.rfind('/')
                self.currentPath = self.currentPath[0:pos]
                self.refreshUI()

    def createTextFileAction(self):
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:    
            fileName, ok = QInputDialog.getText(self, 'Input Dialog', 'Please input new file name:')

            if ok and str(fileName).isalnum() and len(fileName) <= 10:
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
                        QMessageBox.information(self, 'Warning', '储存空间不足！')
                    else:
                        self.pointer.fileList.append((str(fileName) + '.txt', start))
                        self.refreshUI()
                else: # already exists
                    QMessageBox.information(self, 'Warning', '该文本文件名已存在！')
            else: # Please input correct file name
                if '.txt' in str(fileName):
                    QMessageBox.information(self, 'Warning', '文件名中无需含有.txt！')
                elif len(fileName) > 10:
                    QMessageBox.information(self, 'Warning', '文件名长度应在10个字符以下！')
                else:
                    QMessageBox.information(self, 'Warning', '请您输入正确的文本文件名！')

    def createDirAction(self):
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:
            dirName, ok = QInputDialog.getText(self, 'Input Dialog', 'Please input new directory name:')

            if ok and str(dirName).isalnum() and len(dirName) <= 10:
                mark = True
                for child in self.pointer.son: # check for duplicate name
                    if child.dirName == str(dirName):
                        mark = False
                        break

                if mark:
                    newNode = Node(str(dirName), self.pointer)
                    self.pointer.son.append(newNode)
                    self.refreshUI() # refresh UI
                else:
                    QMessageBox.information(self, 'Warning', '该文件名已存在！') # directory already exits
            else:
                if len(dirName) > 10:
                    QMessageBox.information(self, 'Warning', '文件名长度应在10个字符以下！')
                else:
                    QMessageBox.information(self, 'Warning', '请您输入正确的文件名！') # Please input correct file name

    def openFileAction(self): # Action in popMenu self.selectBtn
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:
            if '.txt' in self.selectBtn.text(): # file
                selectedFile = ''
                for file in self.pointer.fileList:
                    if file[0] == self.selectBtn.text()[0:11].replace(' ', ''): # remember to parse filename
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
                        self.refreshUI()
                else:
                    pass
            else: # dir
                for child in self.pointer.son:
                    if child.dirName == self.selectBtn.text()[0:11].replace(' ', ''): # text need to add slice !!!
                        self.pointer = child
                        self.currentPath = self.currentPath + '/' + child.dirName
                        self.refreshUI()
                        break

    def getTextFileSize(self, startBlockNum):
        size = 0
        blockPointer = self.FAT_Bitmap_list[startBlockNum]
        while True:
            if blockPointer.next == -1:
                if len(blockPointer.str) == 0: # empty
                    break
                else:
                    size += 16
                    break
            else:
                size += 16
                blockPointer = self.FAT_Bitmap_list[blockPointer.next]
        return size

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
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:
            if '.txt' in self.selectBtn.text():
                selectedFile = ''
                for file in self.pointer.fileList:
                    if file[0] == self.selectBtn.text()[0:11].replace(' ', ''): # remember to parse filename
                        selectedFile = file
                        break
                self.releaseTextFile(selectedFile[1])
                self.pointer.fileList.remove(selectedFile)
                self.refreshUI()
            else:
                for child in self.pointer.son:
                    if child.dirName == self.selectBtn.text()[0:11].replace(' ', ''): # text need to add slice !!!
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
        dirNode.fileList.clear()
        for child in dirNode.son:
            self.deleteDir(child)
        dirNode.son.clear()

    def writeIntoDisk(self):
        # write everything into disk when quiting this system, consider to rm -rf everything and write everything again
        if self.ROOT == '':
            QMessageBox.information(self, 'Warning', '请先选择工作目录！')
        else:
            for file in os.listdir(self.PATH):
                    if '.' in file:
                        os.remove(os.path.join(self.PATH, file))
                    else:
                        shutil.rmtree(os.path.join(self.PATH, file))

            with open(os.path.join(self.PATH, '.FAT_BitMap_list'), 'w') as f:
                for block in self.FAT_Bitmap_list:
                    f.write(str(block.next) + ' ' + block.str + '\n')
            self.writeEveryDir(self.ROOT, self.PATH)
            sys.exit()

    def writeEveryDir(self, dirNode, path):
        with open(os.path.join(path, '.index'), 'w') as f:
            for file in dirNode.fileList:
                f.write(file[0] + ' ' + str(file[1]) + '\n')

        for file in dirNode.fileList:
            text = self.getText(file)
            with open(os.path.join(path, file[0]), 'w') as f:
                f.write(text)

        for child in dirNode.son:
            os.mkdir(os.path.join(path, child.dirName))
            self.writeEveryDir(child, os.path.join(path, child.dirName))
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = FileManagement()
    sys.exit(app.exec_())