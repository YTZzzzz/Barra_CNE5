# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 07:01:33 2018

@author: YTZzz
"""
from final import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import Part1
import Part2
import Part3
import Part4
import pandas as pd
import numpy as np


path = 'D:\\citics\\Barra\\data\\'

Exposure = pd.read_csv(path + 'FactorExposure.csv',encoding='utf-8_sig')
FactorReturn = pd.read_csv(path + 'FactorReturn.csv', index_col = 0)
raw = pd.read_csv(path + 'dataall.csv')
#Specific =pd.read_csv(path+'specific_risk.csv')
#tvalue = pd.read_csv(path + 'tvalue.csv',index_col = 0)
#VIF = pd.read_csv(path + 'VIF.csv',inb


        
class mywindow(QtWidgets.QMainWindow):  
    def __init__(self):  
        super(mywindow,self).__init__()  
        
        self.firstUi = Part1.Ui_MainWindow()
        self.secondUi = Part2.Ui_MainWindow()
        self.thirdUi = Part3.Ui_MainWindow()
        self.fourthUi = Part4.Ui_MainWindow()
        
        tabWidget=QTabWidget(self)

        w3 = QMainWindow()  
        self.thirdUi.setupUi(w3)        
        w1 = QMainWindow()  
        self.firstUi.setupUi(w1)
        w2 = QMainWindow()  
        self.secondUi.setupUi(w2)
        w4 = QMainWindow()  
        self.fourthUi.setupUi(w4)
        
        tabWidget.addTab(w3,"因子更新") 
        tabWidget.addTab(w1,"因子收益归因")  
        tabWidget.addTab(w2,"因子风险预测")  
        tabWidget.addTab(w4,"有效因子筛选")         
        
        tabWidget.resize(1311, 810)
        
        self.firstUi.push_button.clicked.connect(self.Attribution)
        self.secondUi.push_button.clicked.connect(self.RiskForecast)
        self.fourthUi.push_button.clicked.connect(self.EffectiveFactor)
        
    def Attribution(self):
        factorName= self.firstUi.factor_box.currentText()
        startdate = self.firstUi.calendar_start.selectedDate().toPyDate()
        enddate = self.firstUi.calendar_end.selectedDate().toPyDate()
        pofo  = self.firstUi.portfolio_box.toPlainText()
        portfolio_return = portfolio_dcp(pofo, [factorName], Exposure, FactorReturn,str(startdate), str(enddate))
        print(portfolio_return)
        Hheader = portfolio_return.columns.tolist()
        Vheader = portfolio_return.index.tolist()
        print(Hheader)
        n = portfolio_return.shape[0]
        m = portfolio_return.shape[1]
        self.firstUi.resulttable.setRowCount(n)
        self.firstUi.resulttable.setColumnCount(m)
        self.firstUi.resulttable.setHorizontalHeaderLabels(Hheader)
        self.firstUi.resulttable.setVerticalHeaderLabels(Vheader)
        for i in range(n):
            for j in range(m):
                self.firstUi.resulttable.setItem(i, j, QtWidgets.QTableWidgetItem(str(portfolio_return.iloc[i,j])))
                self.firstUi.resulttable.setColumnWidth(j,200)
        self.firstUi.label_pic.setPixmap(QPixmap('D:\\citics\\Barra\\code\\' +'factor_attribution.png'))
        self.firstUi.label_pic.setScaledContents(True)
        
    def RiskForecast(self):

        factorName= self.secondUi.factor_box.currentText()
        startdate = self.secondUi.calendar_start.selectedDate().toPyDate()
        enddate = self.secondUi.calendar_end.selectedDate().toPyDate()
        Thalf = int(self.secondUi.halflife_box.toPlainText())
        cmp = risk_validate(FactorReturn, factorName,str(startdate), str(enddate), TF= Thalf)   
        self.secondUi.label_pic.setPixmap(QPixmap('D:\\citics\\Barra\\code\\' +'risk_forecast.png'))
        self.secondUi.label_pic.setScaledContents(True)
        
    def EffectiveFactor(self):
        factorName= self.fourthUi.factor_box.currentText()
        startdate = self.fourthUi.calendar_start.selectedDate().toPyDate()
        enddate = self.fourthUi.calendar_end.selectedDate().toPyDate()
        index  = self.fourthUi.index_box.toPlainText()
        riskfree = float(self.fourthUi.rf_box.toPlainText())
        ngroup = int(self.fourthUi.number_box.toPlainText())
        group = groupvalidate(Exposure, raw,factorName, str(startdate), str(enddate), riskfree, index, ngroup)
        group = group.stack().unstack(0)
        print(group)
        Hheader = group.columns.tolist()
        Vheader = group.index.tolist()
        Hheader = [str(x) for x in Hheader]
        Vheader
        print(Hheader)
        n = group.shape[0]
        m = group.shape[1]
        self.fourthUi.resulttable.setRowCount(n)
        self.fourthUi.resulttable.setColumnCount(m)
        self.fourthUi.resulttable.setHorizontalHeaderLabels(Hheader)
        self.fourthUi.resulttable.setVerticalHeaderLabels(Vheader)
        for i in range(n):
            for j in range(m):
                self.fourthUi.resulttable.setItem(i, j, QtWidgets.QTableWidgetItem(str(group.iloc[i,j])))
                self.fourthUi.resulttable.setColumnWidth(j,80)        


        
if __name__=="__main__":
    import sys

    app=QtWidgets.QApplication(sys.argv)
    myshow=mywindow()
    myshow.show()
    sys.exit(app.exec_())
    
