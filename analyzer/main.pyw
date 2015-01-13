#!/usr/bin/env python
# file name: main.pyw
# created by: Ventura Del Monte 
# purpose:  main GUI
# last edited by: Ventura Del Monte 24-09-2014

import sip
sip.setapi('QVariant', 2)

from PyQt4 import QtCore
from PyQt4 import QtGui

import sys
import time
import random
import logging
import getpass
from multiprocessing.pool import ThreadPool

from tools import *
from internal_browser import InternalBrowser
from form_analyzer import BASE_WAIT_TIME
from google_search import GoogleSearch
from utils import *
from views import *
from config import ConfigManager

import pyperclip

logger = logging.getLogger(__name__)
stdout_logger = logging.getLogger('STDOUT')
stderr_logger = logging.getLogger('STDERR')

APPLICATION_VERSION = "**BETA** (internal use only)"
APPLICATION_TITLE = "Static WebSites Analyzer " + APPLICATION_VERSION

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

class ConsoleWindowLogHandler(logging.Handler):
	def __init__(self, sigEmitter):
		super(ConsoleWindowLogHandler, self).__init__()
		self.sigEmitter = sigEmitter
	
	def emit(self, logRecord):
		message = "%s: %s" % (time.strftime("%X"), str(logRecord.getMessage()))
		self.sigEmitter.emit(QtCore.SIGNAL("logMsg(QString)"), message)
	

class MainWindow(QtGui.QMainWindow):
	
	TOOL_READY = 0
	TOOL_RUNNING = 1
	TOOL_DONE = 2
	TOOL_FAILED = 3
	
	STATUS = ("Ready", "Running", "Done", "Failed")
	REVERSE_STATUS =  {"Ready" : 0, "Running" : 1, "Done" : 2, "Failed" : 3}
	
	COLORS =  {
				"Ready"   : QtGui.QColor(255, 165, 0,   100),  # orange
				"Running" : QtGui.QColor(0,   0,   128, 100),  # dark cyan
				"Done"    : QtGui.QColor(0,   128, 0,   100),  # green
				"Failed"  : QtGui.QColor(255, 0,   0,   100),  # red
				"Threat"  : QtGui.QColor(255, 0,   0,   100), # red
	}  
	
	def __init__(self, manager, config):
		super(MainWindow, self).__init__()
		self.config = config
		self.manager = manager
		self.setWindowTitle(_fromUtf8(APPLICATION_TITLE))
		self.showMaximized()
	#	self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)


	def createGui(self):

		#self.setStyleSheet('font-size: 10pt; font-family: Arial;')
	
		self.models = {}
		widget = QtGui.QWidget()
		self.setCentralWidget(widget)
		
		self.progressBar = QtGui.QProgressBar(self)
		
		self.sourceView = QtGui.QTreeView()
		self.sourceView.setRootIsDecorated(False)
		self.sourceView.setAlternatingRowColors(True)
		self.sourceView.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
		self.sourceView.clicked.connect(self.onItemClicked)
		
		sourceLayout = QtGui.QHBoxLayout()
		sourceLayout.addWidget(self.sourceView)
		box = QtGui.QGroupBox(_fromUtf8("Target WebSites"))
		box.setLayout(sourceLayout)
		
		self.createActions()
		self.createMenu()
		self.createStatusBar()
		
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(box)
		self.createLogger(mainLayout)
		widget.setLayout(mainLayout)
		
		self.targets = Dicty()
		self.currentTargetsCount = 0
		self.progessMax = 0
		self.currentProgress = 0
		
		self.started = False
		
		self.createModel()
		
		#self.connectionTimer = QtCore.QTimer()
		#QtCore.QObject.connect(self.connectionTimer, QtCore.SIGNAL(_fromUtf8("timeout()")), self.checkForInternetConnection)
		#self.connectionTimer.start(5000)
	
	def createLogger(self, parent):
		# Logger
		textBox = QtGui.QTextBrowser()
		loggerLayout = QtGui.QHBoxLayout()
		loggerLayout.addWidget(textBox)
		box = QtGui.QGroupBox(_fromUtf8("Log"))
		box.setFixedHeight(200)
		box.setLayout(loggerLayout)
		parent.addWidget(box)
		
		 # Console handler
		dummyEmitter = QtCore.QObject()
		self.connect(dummyEmitter, QtCore.SIGNAL("logMsg(QString)"), textBox.append)
		handler = ConsoleWindowLogHandler(dummyEmitter)
		for _logger in (logger, stdout_logger, stderr_logger):
			_logger.addHandler(handler)
	
	def createMenu(self):
		# File
		self.fileMenu = self.menuBar().addMenu(_fromUtf8("&File"))
		self.fileMenu.addAction(self.addOneSiteAct)
		self.fileMenu.addAction(self.addMultiSiteAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.showSearchDialogAct)
		self.fileMenu.addAction(self.showOptionsDialogAct)
		#self.fileMenu.addAction(self.setTestsToPerformAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)
		# Process
		self.fileMenu = self.menuBar().addMenu(_fromUtf8("&Process"))
		self.fileMenu.addAction(self.startAct)
		#self.fileMenu.addAction(self.stopAct)
		#self.fileMenu.addAction(self.resumeAct)
		# Help
		self.aboutMenu = self.menuBar().addMenu(_fromUtf8("&Help"))
		self.aboutMenu.addAction(self.aboutAct)
	
	def createStatusBar(self):
		self.statusBar().showMessage("Ready")
		self.progressBar.setRange(0, 1)
		self.statusBar().addPermanentWidget(self.progressBar)
		
	def createActions(self):
		# file menu
		self.addOneSiteAct = QtGui.QAction(_fromUtf8("&Add one..."), self, shortcut = "Ctrl+O", statusTip = _fromUtf8("Add a target site"), triggered = self.addOne)
		self.addMultiSiteAct = QtGui.QAction(_fromUtf8("&Add multi..."), self, shortcut = "Ctrl+L", statusTip = _fromUtf8("Add a list of sites"), triggered = self.addList)
		self.setTestsToPerformAct = QtGui.QAction(_fromUtf8("&Configure tests"), self, statusTip = _fromUtf8("Configure tests"), triggered = self.setTestsToPerform)
		self.showSearchDialogAct = QtGui.QAction(_fromUtf8("&Search"), self, statusTip = _fromUtf8("Search on google"), triggered = self.showSearchDialog)
		self.showOptionsDialogAct = QtGui.QAction(_fromUtf8("&Options"), self, triggered = self.showOptionsDialog)
		self.exitAct = QtGui.QAction(_fromUtf8("E&xit"), self, shortcut = "Ctrl+Q", statusTip = _fromUtf8("Exit the application"), triggered = self.close)
		# execute menu
		self.startAct = QtGui.QAction(_fromUtf8("&Start"), self, shortcut = "Ctrl+A", statusTip = _fromUtf8("Start"), triggered = self.start)
		self.stopAct = QtGui.QAction(_fromUtf8("&Stop"), self, statusTip = _fromUtf8("Stop"), triggered = self.stop)
		self.resumeAct = QtGui.QAction(_fromUtf8("&Resume"), self, statusTip = _fromUtf8("Resume"), triggered = self.resume)
		# help menu
		self.aboutAct = QtGui.QAction("&About", self, statusTip=_fromUtf8("Show the application's About box"), triggered = self.about)
	
	def addOne(self):
		text, ok = QtGui.QInputDialog.getText(self, 'Add one url', 'Enter your target website:')
		if ok:
			self.internalAdd(str(text))
	
	def internalAdd(self, text, errMsg = 'The URL you have just typed is malformatted.'):
		text = QtCore.QString(text.strip())
		if not text.startsWith("http"):
			text = "http://" + text
		if isValidUrl(text):
			self.targets[text] = { "index": self.addItem(text), "done": False }
			self.currentTargetsCount += 1
		else:
			QtGui.QMessageBox.critical(self, _fromUtf8("Malformed URL!"), _fromUtf8(text))

	def addList(self):
		fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', './', filter="Text Files (*.txt)")
		
		if not fname.endsWith(".txt") or fname == "":
			QtGui.QMessageBox.critical(self, _fromUtf8("Error"), _fromUtf8("File not Valid!"))
			return
			
		with open(fname,'r') as f:
			for line in f.readlines():
				if not line.startswith("#"):
					self.internalAdd(line, "Malformed url in file")
		f.close()
	
		
	def setTestsToPerform(self):
		pass
		
	def start(self):
		if len(self.targets) == 0:
			return
		self.pool = QtCore.QThreadPool.globalInstance()
		self.pool.setMaxThreadCount(self.getMaxRunnableTargets())
		self.progressMax = self.currentTargetsCount 
		self.currentTargetsCount = 0
		self.currentProgress = 0
		self.progressBar.setRange(0, self.progressMax * self.manager.count())
		self.progressBar.setValue(0)
		i = 0
		count = len(self.targets)
		for url in self.targets:
			if not self.targets[url].done:
				runnable = ToolsExecutor(url, self.targets[url].index, self.manager, count - i)
				runnable.worker.signal.connect(self.onTargetAnalyzed)
				self.pool.start(runnable, count - i)
				i += 1
		#self.poolStatus = self.STARTED
		#self.pool.waitForDone()
	
	def resume(self):
		pass
		
	def stop(self):
		pass
	
	def showOptionsDialog(self):
		dlg = OptionsDialog(self, self.config)
		dlg.exec_()
	
	def showSearchDialog(self):
		dlg = SearchDialog(self)
		dlg.exec_()
	
	def onResultFound(self, item):
		print item[0]
		self.internalAdd(item[0])
	
	def processSearch(self, query):
		runner = SearcherThread(query)
		runner.notifier.signal.connect(self.onResultFound)
		self.pool = QtCore.QThreadPool.globalInstance()
		self.pool.setMaxThreadCount(self.getMaxRunnableTargets())
		self.pool.start(runner)
		
	@QtCore.pyqtSlot(QtCore.QModelIndex)
	def onItemClicked(self, modelIndex):
		index, toolIndex = modelIndex.row(), modelIndex.column()
		if toolIndex == 0:
			pyperclip.copy(self.model.data(modelIndex))
		if self.model.data(modelIndex) != self.STATUS[self.TOOL_DONE]:
			return
		dlg = PopupDialog(self)
		dlg.setViewFromModel(*self.models[index][toolIndex][:3])
		dlg.exec_()
	
	
	def onTargetAnalyzed(self, index, url, tool, state, res):
		rowTool = self.dataIndexes[tool.name if isinstance(tool, BaseTool) else tool]
		self.model.setData(self.model.index(index, rowTool), _fromUtf8(self.STATUS[state]))
		
		#row = self.model.item(index, 0)
		urlCell = self.model.item(index, 0)
		cell = self.model.item(index, rowTool)
		
		if state == self.TOOL_RUNNING:
			#row.setBackground(QtGui.QColor(self.COLORS["Running"]))
			cell.setBackground(self.COLORS["Running"])
		elif state == self.TOOL_DONE:
			self.models[index][self.dataIndexes[tool.name]] = (tool.createModel())
			#row.setBackground(QtGui.QColor(self.COLORS["Done"]))
			cell.setBackground(self.COLORS["Done"])

			if res is True:
				urlCell.setBackground(self.COLORS['Threat'])

		elif state == self.TOOL_FAILED:
			#row.setBackground(QtGui.QColor(self.COLORS["Failed"]))
			cell.setBackground(self.COLORS["Failed"])
		
		if state == self.TOOL_FAILED or state == self.TOOL_DONE:
			self.currentProgress += 1
			self.progressBar.setValue(self.currentProgress)
			self.targets[url].done = True
		
	
	def setHeader(self, index, data, font, width):
		self.model.setHeaderData(index, QtCore.Qt.Horizontal, _fromUtf8(data))
		self.model.setHeaderData(index, QtCore.Qt.Horizontal, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, QtCore.Qt.TextAlignmentRole)
		self.model.setHeaderData(index, QtCore.Qt.Horizontal, font, QtCore.Qt.FontRole)
		#self.sourceView.resizeColumnToContents(index)
		self.sourceView.setColumnWidth(index, width)
	
	def createModel(self):
		def internalCreateModel():
			self.model = QtGui.QStandardItemModel(0, self.manager.count() + 1, self)
			self.sourceView.setModel(self.model)
			self.dataIndexes = {}
			width = self.sourceView.width() / (self.manager.count() + 1)
			font = QtGui.QFont(self.font())
			font.setWeight(QtGui.QFont.Bold)
		
			self.setHeader(0, "URL", font, width)
			i = 1
			for tool in self.manager.yieldToolsNames():
				self.dataIndexes[tool] = i
				self.setHeader(i, tool, font, width)
				i += 1
		#if sys.platform.startswith('linux'):
		QtCore.QTimer.singleShot(250, internalCreateModel)
		# else:
			# internalCreateModel()
	
	
	def addItem(self, url):
		index = self.model.rowCount()
		self.model.insertRow(index)
		base = self.model.index(index, 0)
		self.model.setData(base, url)
		self.model.itemFromIndex(base).setEditable(False)
		self.model.itemFromIndex(base).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		#self.sourceView.resizeColumnToContents(0)
		#self.model.item(index,0).setBackground(QtGui.QColor(self.COLORS["Ready"]))
		for i in range(self.manager.count()):
			pos = self.model.index(index, i + 1)
			item = self.model.itemFromIndex(pos)
			self.model.setData(pos, _fromUtf8(self.STATUS[self.TOOL_READY]))
			item.setEditable(False)
			item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
			#self.sourceView.resizeColumnToContents(i + 1)
			item.setBackground(self.COLORS["Ready"])
			self.models[index] = {}
		return index
		
	def getMaxRunnableTargets(self):
		return self.config.getInt("max_runnable_targets", 2)
		
	def checkForInternetConnection(self):
		if not checkInternetConnection():
			QtGui.QMessageBox.critical(None, "Fatal error", "No internet connection")
			self.close()
	
	def about(self):
		QtGui.QMessageBox.about(self, _fromUtf8("About Menu"),
			 _fromUtf8("The <b>Menu</b> example shows how to create menu-bar menus and context menus."))
	

class WorkerObject(QtCore.QObject):
	signal = QtCore.pyqtSignal(int, str, object, object, object)

class ToolsExecutor(QtCore.QRunnable):
	
	def __init__(self, url, index, manager, prio):
		QtCore.QRunnable.__init__(self)
		self.url = url
		self.index = index
		self.manager = manager
		self.prio = prio
		self.worker = WorkerObject()

	def run(self):
		browser = InternalBrowser()
		try:
			browser.open(str(self.url))
		except Exception as e:
			for name in manager.registeredToolsByName():
				self.worker.signal.emit(self.index, self.url, name, MainWindow.TOOL_FAILED, None)
			print e
			return
		
		
		def internalRun(tool):
			print "processing " + tool.name
			toolBrowser = browser
			
			try:
				self.worker.signal.emit(self.index, self.url, tool, MainWindow.TOOL_RUNNING, None)
				if tool.refreshNeeded():
					'''
					mutex = QtCore.QMutex()
					mutex.lock()
					mutex.tryLock(BASE_WAIT_TIME + random.randint(0, 5))
					'''
					time.sleep(BASE_WAIT_TIME + random.randint(0, 5))
					toolBrowser = InternalBrowser()
					try:
						toolBrowser.open(str(self.url))
					except:
						self.worker.signal.emit(self.index, self.url, tool, MainWindow.TOOL_FAILED, None)
						return
				res = tool.run(toolBrowser)
				self.worker.signal.emit(self.index, self.url, tool, MainWindow.TOOL_DONE, res)
			except ToolException as ex:
				# handle ex
				self.worker.signal.emit(self.index, self.url, tool, MainWindow.TOOL_FAILED, None)
				print ex
		
		pool = ThreadPool(manager.count())
		pool.map(internalRun, [ tool for tool in manager.yieldTools()])
	


class NotifierObject(QtCore.QObject):
	signal = QtCore.pyqtSignal(object)

class SearcherThread(QtCore.QRunnable):
	def __init__(self, query):
		QtCore.QRunnable.__init__(self) 
		self.query = query
		self.notifier = NotifierObject()
	def run(self):
		searcher = GoogleSearch()
		data = searcher.search(self.query)
		for item in data:
			self.notifier.signal.emit(item)
	
class StreamToLogger(object):
	"""
	Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, log_level = logging.INFO):
		self.logger = logger
		self.log_level = log_level
		self.linebuf = ''
	
	def write(self, buf):
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())

if __name__ == "__main__":

	import sys
	
	app = QtGui.QApplication(sys.argv)
	
	random.seed(time.time())
	
	logging.basicConfig(
		level = logging.DEBUG,
		format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s',
		filename = "log_%s.log" % (getpass.getuser()),
		filemode = 'w'
	)

	sys.stdout = StreamToLogger(stdout_logger, logging.INFO)
	sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)
	

	config = ConfigManager()
	config.load("config.cfg")

	#print config.get("version")

	manager = ToolsManager(config)
	window = MainWindow(manager, config)
	
	
#	manager.register("test", "my_tool", "MyTool")

	manager.register("FormAnalyzer", "form_analyzer", "FormAnalyzer")
	manager.register("WhoIs", "WhoIsTool", "WhoIsTool")
	manager.register("SSLCertificateCheck", "SSLCertificateCheckTool", "SSLCertificateCheckTool")
	manager.register("BannerAnalyzer", "BannerTool", "BannerTool")
	manager.register("RedirectionAnalyzer", "redirect_tool", "RedirectionAnalyzer")

	
	
	if not checkInternetConnection(tout = config.getFloat("connection_timeout")):
		QtGui.QMessageBox.critical(None, "Fatal error", "No internet connection")
		sys.exit(1)

	print sys.platform
	
	# On OS X, this call is needed to bring the application window to the front.
	if sys.platform.startswith('darwin'):
		window.raise_()
	else:
		window.show()
	window.createGui()
	sys.exit(app.exec_())
	


