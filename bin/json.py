import commentjson
import os
import sys


def saveToJson(data, filepath):
	with open(filepath, 'w') as f:
		f.write(str(data))


def loadFromJson(filepath):
	with open(filepath) as f:
		# Should return as dict, check
		return commentjson.load(f)


def formatJson(data):
	return commentjson.dumps(
		data,
		sort_keys=True,
		indent=4,
		default=repr,
		separators=(', ', ': ')).replace('    ', '\t')
