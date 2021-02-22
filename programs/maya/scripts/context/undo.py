import pymel.core as pymel


class UndoContext(object):
	def __enter__(self, *args, **kwargs):
		pymel.undoInfo(openChunk=True)

	def __exit__(self, *args, **kwargs):
		pymel.undoInfo(closeChunk=True)

# TODO: Repeatable Context
