import threading
import time
import sublime, sublime_plugin

refreshThreads = {}

class EnableAutoRefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = sublime.load_settings('AutoRefresh.sublime-settings')
		refreshRate = settings.get('auto_refresh_rate')
		if refreshRate == None or not isinstance(refreshRate, (int, float)):
			print("Invalid auto_refresh_rate setting, using default 3")
			refreshRate = 3

		global refreshThreads
		if refreshThreads.get(self.view.id()) == None or not refreshThreads.get(self.view.id()).enabled:
			refreshThreads[self.view.id()] = RefreshThread(self, edit, refreshRate)
			refreshThreads[self.view.id()].start()

class DisableAutoRefreshCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global refreshThreads
		if refreshThreads.get(self.view.id()) != None:
			refreshThreads[self.view.id()].enabled = False

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