from PySide2 import QtWidgets, QtCore, QtGui
import pymel.core as pm
import maya.cmds as cmds
from functools import partial


class MayaFrameWidget(QtWidgets.QFrame):

	def popUpMessage(self, message):
		QtWidgets.QMessageBox.information(
			self,
			'Information',
			message,
			QtWidgets.QMessageBox.Ok)

	def popUpQuestion(self, question):
		result = QtWidgets.QMessageBox.question(
			self,
			'Information',
			question,
			QtWidgets.QMessageBox.Yes,
			QtWidgets.QMessageBox.No)

		return result == QtWidgets.QMessageBox.Yes

	def popUpError(self, *error):
		errorText = ' '.join([str(e) for e in error])
		errorBox = QtWidgets.QMessageBox(
			QtWidgets.QMessageBox.Critical,
			'Error',
			errorText,
			buttons=QtGui.QMessageBox.Ok,
			parent=self,
			flags=QtCore.Qt.WindowStaysOnTopHint
		)
		errorBox.exec_()
		return errorBox
