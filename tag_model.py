from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import couchdb
import time
import sys
import subprocess
import threading
import socket
import model


class TreeItem(object):
    def __init__(self, text, parent=None):
        self.parentItem = parent
        self.text = text
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class TagModel(QAbstractItemModel):
    def __init__(self):
        super(TagModel, self).__init__()
        self.rootItem = TreeItem("root")

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.text

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, tree_model):
        self.beginResetModel()
        self.rootItem.childItems = []
        tags_set = set()
        map = "function(doc) { \
                    if (doc.text && doc.text.indexOf(':') != -1) \
                        emit(doc, null); \
                }"
        res = tree_model.db.query(map)
        for row in res:
            word_list = row.key['text'].split()
            for word in word_list:
                if word[0] == ':':
                    tags_set.add(word)

        for tag in tags_set:
            self.rootItem.appendChild(TreeItem(tag, self.rootItem))
        self.endResetModel()


