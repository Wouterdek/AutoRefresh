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

class SublimeEventHandler(sublime_plugin.EventListener):
	def on_pre_close(self, view):
		global refreshThreads
		if refreshThreads.get(view.id()) != None:
			refreshThreads[view.id()].enabled = False

class RefreshThread(threading.Thread):
	def __init__(self, cmd, edit, refreshRate):
		self.cmd = cmd
		self.edit = edit
		self.enabled = True
		self.refreshRate = refreshRate
		threading.Thread.__init__(self)

	def run(self):
		while self.enabled:
			sublime.set_timeout(self.reloadFile, 1) #Reload file
			sublime.set_timeout(self.setView, 10)	#Wait for file reload to be finished
			time.sleep(self.refreshRate)

	def reloadFile(self):
		row = self.cmd.view.rowcol(self.cmd.view.sel()[0].begin())[0] + 1
		rowCount = (self.cmd.view.rowcol(self.cmd.view.size())[0] + 1)

		if rowCount - row <= 3:
			self.moveToEOF = True
		else:
			self.moveToEOF = False
			#Sublime seems to have a bug where continuously reloading a file causes the viewport to scroll around
			#Any fixes to this problem seem to have no effect since viewport_position() returns an incorrect value causing the scrolling
			#What would probably work is to force focus on the cursor

		self.cmd.view.run_command('revert')

	def setView(self):
		if not self.cmd.view.is_loading():
			#Loading finished
			if self.moveToEOF:
				self.cmd.view.run_command("move_to", {"to": "eof", "extend": "false"})
		else:
			sublime.set_timeout(self.setView, 10)