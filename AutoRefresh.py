import threading
import time
import sublime, sublime_plugin

refreshThread = None

class EnableAutoRefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global refreshThread
		refreshThread = RefreshThread(self, edit)
		refreshThread.start()

class DisableAutoRefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global refreshThread
		refreshThread.enabled = False

class RefreshThread(threading.Thread):
	def __init__(self, cmd, edit):
		threading.Thread.__init__(self)
		self.cmd = cmd
		self.edit = edit
		self.enabled = True

	def run(self):
		while self.enabled:
			time.sleep(3)
			sublime.set_timeout(self.callback, 1)

	def callback(self):
		self.cmd.view.run_command('revert')