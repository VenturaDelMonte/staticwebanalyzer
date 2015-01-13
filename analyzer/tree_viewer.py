#!/usr/bin/env python
# file name: tree_viewer.py
# created by: Ventura Del Monte 
# purpose: Tree view model 
# last edited by: Ventura Del Monte 19-11-2014

from PyQt4 import QtCore, QtGui

class TreeItem(object):
	def __init__(self, data, parent = None):
		self._parent = parent
		self._items = data
		print data
		self._children = []

	def appendChild(self, item):
		self._children.append(item)

	def child(self, row):
		return self._children[row]

	def childCount(self):
		return len(self._children)

	def columnCount(self):
		return len(self._items)

	def data(self, column):
		try:
			return self._items[column]
		except IndexError:
			return None

	def parent(self):
		return self._parent

	def row(self):
		if self._parent:
			return self._parent._children.index(self)

		return 0


class TreeModel(QtCore.QAbstractItemModel):
	def __init__(self, data, parent = None, header = ("Key", "Value")):
		super(TreeModel, self).__init__(parent)

		self.rootItem = TreeItem(header)
		self.setupModelData(data, self.rootItem)

	def columnCount(self, parent):
		if parent.isValid():
			return parent.internalPointer().columnCount()
		else:
			return self.rootItem.columnCount()

	def data(self, index, role):
		if not index.isValid():
			return None

		if role != QtCore.Qt.DisplayRole:
			return None

		item = index.internalPointer()

		return item.data(index.column())

	def flags(self, index):
		if not index.isValid():
			return QtCore.Qt.NoItemFlags

		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return self.rootItem.data(section)

		return None

	def index(self, row, column, parent):
		if not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()

		if not parent.isValid():
			parentItem = self.rootItem
		else:
			parentItem = parent.internalPointer()

		childItem = parentItem.child(row)
		if childItem:
			return self.createIndex(row, column, childItem)
		else:
			return QtCore.QModelIndex()

	def parent(self, index):
		if not index.isValid():
			return QtCore.QModelIndex()

		childItem = index.internalPointer()
		parentItem = childItem.parent()

		if parentItem == self.rootItem:
			return QtCore.QModelIndex()

		return self.createIndex(parentItem.row(), 0, parentItem)

	def rowCount(self, parent):
		if parent.column() > 0:
			return 0

		if not parent.isValid():
			parentItem = self.rootItem
		else:
			parentItem = parent.internalPointer()

		return parentItem.childCount()

	def setupModelData(self, data, parent):
		for elem in data:
			for k, v in elem.iteritems():
				node = TreeItem([k, " "], parent)
				for kk, vv in v.iteritems():
					node.appendChild(TreeItem((kk, vv), node))
				parent.appendChild(node)
			
			
			
			
			
			

