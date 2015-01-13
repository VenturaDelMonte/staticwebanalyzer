#!/usr/bin/env python
# file name: views.py
# created by: Ventura Del Monte 
# purpose: tool dialogs
# last edited by: Ventura Del Monte 26-09-2014

from PyQt4 import QtCore
from PyQt4 import QtGui

import pyperclip
import operator 

from tree_viewer import TreeModel

APPLICATION_TITLE = "Details"
try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

class PopupDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		super(PopupDialog, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
		self.setObjectName(_fromUtf8("PopupDialog"))
		self.resize(550, 300)
		self.setWindowTitle(_fromUtf8(APPLICATION_TITLE))
		self.buttonBox = QtGui.QDialogButtonBox()
		self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
		QtCore.QMetaObject.connectSlotsByName(self)
		
		self.sourceView = QtGui.QTreeView()
		#self.sourceView.setRootIsDecorated(False)
		#self.sourceView.setAlternatingRowColors(True)
		'''
		sourceLayout = QtGui.QHBoxLayout()
		sourceLayout.addWidget(self.sourceView)
		self.sourceView.clicked.connect(self.onItemClicked)
		box = QtGui.QGroupBox(_fromUtf8("Details"))
		box.setLayout(sourceLayout)
		'''
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(self.sourceView)
		mainLayout.addWidget(self.buttonBox)
		self.setLayout(mainLayout)
		
		self.model = None
		
		
	
	def setViewFromModel(self, mode, headers, data):
		self.isComplex = mode is False
		if mode is True:
			self.setSimpleViewFromModel(headers, data)
		else:
			self.setComplexViewFromModel(headers, data)
		
	def setComplexViewFromModel(self, headers, data):
		self.model = TreeModel(data, None, headers)
		self.sourceView.setModel(self.model)
	
	def setSimpleViewFromModel(self, headers, data):
		index = 0
		self.model = QtGui.QStandardItemModel(0, len(headers), self)
		self.sourceView.setModel(self.model)
	
		for i in range(len(headers)):
			self.model.setHeaderData(i, QtCore.Qt.Horizontal, _fromUtf8(headers[i]))
	
		for row in data:
			self.model.insertRow(index)
			for i in range(len(row)):
				cell = self.model.index(index, i)
				self.model.setData(cell, _fromUtf8(str(row[i])))
				self.model.itemFromIndex(cell).setEditable(False)
				self.sourceView.resizeColumnToContents(i)
			index += 1
			
	@QtCore.pyqtSlot(QtCore.QModelIndex)
	def onItemClicked(self, cell):
		if self.isComplex:
			pass # must be implemented !!!
		else:
			pyperclip.copy(self.model.data(cell))
		

class SearchDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		super(SearchDialog, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
		self.parent = parent
		self.setObjectName(_fromUtf8("SearchDialog"))
		self.resize(400, 229)
		self.setWindowTitle("Search Dialog")
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.setGeometry(QtCore.QRect(40, 190, 341, 32))
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
		
		self.formLayoutWidget = QtGui.QWidget(self)
		self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 381, 171))
		self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
		
		self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
		self.formLayout.setMargin(0)
		self.formLayout.setObjectName(_fromUtf8("formLayout"))
		
		label = QtGui.QLabel("Domain filter", self.formLayoutWidget)
		self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, label)
		
		self.siteLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
		self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.siteLineEdit)
		
		label = QtGui.QLabel("Query", self.formLayoutWidget)
		self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, label)
		
		self.queryTextEdit = QtGui.QTextEdit(self.formLayoutWidget)
		self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.queryTextEdit)
		
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
		#QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), parent.processSearch)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
		QtCore.QMetaObject.connectSlotsByName(self)
	
	
	def accept(self):
		super(SearchDialog, self).accept()
		site = str(self.siteLineEdit.text())
		query = str(self.queryTextEdit.toPlainText())
		if len(site) > 0:
			if site.startswith("-"):
				site = "-site:" + site[1:]  
			else:
				site = "site:" + site 
			self.parent.processSearch('%s AND "%s"' % (site, query))
		else:
			self.parent.processSearch('"%s"' % query)
			

class OptionsDialog(QtGui.QDialog):
	def __init__(self, parent = None, config = None):
		super(OptionsDialog, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
		self.parent = parent
		self.config = config
		self.newConfig = {}
		self.setObjectName(_fromUtf8("OptionsDialog"))
		self.resize(400, 229)
		self.setWindowTitle("Options Dialog")
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.grid.setSpacing(10)
		
		i = 0
		for k, v in self.config.getPairs().items():
			control = QtGui.QLineEdit(v)
			self.grid.addWidget(QtGui.QLabel(k.replace("_", " ")), i, 0)
			self.grid.addWidget(control, i, 1)
			QtCore.QObject.connect(control, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), lambda newValue : operator.setitem(self.newConfig, k, str(newValue)))
			self.newConfig[k] = v
			i += 1

		self.okButton = QtGui.QPushButton("Ok")
		self.cancelButton = QtGui.QPushButton("Cancel")
		self.grid.addWidget(self.okButton, i, 0)
		self.grid.addWidget(self.cancelButton, i, 1)
		
		self.okButton.clicked.connect(self.accept)
		self.cancelButton.clicked.connect(self.reject)
		QtCore.QMetaObject.connectSlotsByName(self)
		
		self.adjustSize()

	def accept(self):
		super(OptionsDialog, self).accept()
		self.config.updateConfig(self.newConfig)
	


