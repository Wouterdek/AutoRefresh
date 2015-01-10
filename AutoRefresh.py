import threading
import time
import sublime, sublime_plugin

refreshThread = None

class EnableAutoRefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = sublime.load_settings('AutoRefresh.sublime-settings')
		refreshRate = settings.get('auto_refresh_rate')
		if refreshRate == None or (type(refreshRate) is not int and type(refreshRate) is not float):
			print("Invalid auto_refresh_rate setting, using default 3")
			refreshRate = 3

		global refreshThread
		if refreshThread == None or not refreshThread.enabled:
			refreshThread = RefreshThread(self, edit, refreshRate)
			refreshThread.start()

class DisableAutoRefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global refreshThread
		if refreshThread != None:
			refreshThread.enabled = False

class RefreshThread(threading.Thread):
	def __init__(self, cmd, edit, refreshRate):
		self.cmd = cmd
		self.edit = edit
		self.enabled = True
		self.refreshRate = refreshRate;
		threading.Thread.__init__(self)

	def run(self):
		while self.enabled:
			time.sleep(self.refreshRate)
			sublime.set_timeout(self.callback, 1)

	def callback(self):
		self.cmd.view.run_command('revert')