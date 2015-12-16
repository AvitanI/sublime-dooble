import sublime, sublime_plugin, os
import re

class DoobleIO():
	@staticmethod
	def is_admin(file_name):
		lis = file_name.split("\\")
		if 'admin' in file_name:
			return True
		return False

	@staticmethod
	def is_content(file_name):
		lis = file_name.split("\\")
		if 'content' in file_name:
			return True
		return False

	@staticmethod
	def is_module(file_name):
		lis = file_name.split("\\")
		if 'module' in file_name:
			return True
		return False

	@staticmethod
	def is_ui(sel):
		return re.match(r'\[\[ui/?.+\]\]', sel, re.IGNORECASE)
		


	@staticmethod
	def cut_path(file_name):
		lis = []
		left_path = ""
		right_path = ""
		if 'sites' in file_name:
			lis = file_name.split('sites')
			left_path = lis[0]
			print('sites' + lis[1])
			right_path = 'sites' + lis[1]
		elif 'site' in file_name:
			lis = file_name.split('site')
			left_path = lis[0]
			right_path = 'site' + lis[1]

		return(left_path, right_path)

	@staticmethod
	def check_file_type(file_n):
		left_path, file_name = DoobleIO.cut_path(file_n)
		# print("left path: " + left_path)
		# print("file name of cut: " + file_name)

		a_type = ""

		if DoobleIO.is_module(file_name) or DoobleIO.is_content(file_name):
			a_type = '\\Content\\Modules'
			print("module file or content folder")
		elif DoobleIO.is_admin(file_name):
			a_type = '\\Admin'
			print("admin file")
		return a_type





class ModuleAutoCompleteCommand(sublime_plugin.EventListener):
	SCOPE_NAME = 'text.html.pp.module';
	

	def on_query_completions(self, view, prefix, locations):
		# print(locations)
		# print(view.scope_name(locations[0]))
		if self.SCOPE_NAME in view.scope_name(locations[0]):
			autocomplete_list = self.getDirs(view)
			return autocomplete_list

	def getDirs(self, view):
		# get user selection
		selection = self.user_selection(view)
		# check if it's ui controls
		is_ui = DoobleIO.is_ui(selection)

		modulesList = []
		folders = sublime.active_window().folders()
		# print (folders[0].lower().endswith('sites'))
		if folders[0].lower().endswith('sites'):
			folders = self.get_immediate_subdirectories(folders[0])
		# print(folders)
		# check if it's module or admin or ui
		file_name = sublime.active_window().active_view().file_name().lower()
		# print("file name: " + file_name)
		a_type = DoobleIO.check_file_type(file_name)
		# get all sites folders
		for x in folders:
			if x.endswith('dev'):
				continue
			# print("folder: " + x)
			# add module path to the sites 
			# fullPath = x+self.MODULES_ROOT
			fullPath = x + a_type
			# print("type: " + a_type)
			# print("full path: " + fullPath)
			# in case its ui
			if is_ui:
				print(x + '\\uicontrols')
				try:
					# get ui list
					ui_list = self.get_ui_files(x + '\\uicontrols')
					# remove duplicate from list
					ui_list = self.remove_duplicates(modulesList, ui_list)

					modulesList += ui_list
				except:
					print("There is no ui controls folder in the site or the master")
				
			else:
				ui_list  = []
				try:
					# get ui list
					ui_list = self.get_ui_files(x + '\\uicontrols')
					# remove duplicate from list
					ui_list = self.remove_duplicates(modulesList, ui_list)
				except:
					print("There is no ui controls folder in the site or the master")

				# get module list
				module_list = self.get_modules(fullPath)
				# remove duplicate from module list
				module_list = self.remove_duplicates(modulesList, module_list)

				modulesList += module_list + ui_list
		
		return modulesList

	def get_immediate_subdirectories(self, a_dir):
    		return [a_dir+'\\'+name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

	def get_modules(self, fullPath):
		modulesList = []
		for dir in os.listdir(fullPath):
			if '.' not in dir:
				# \Sites\natanzon\Content\Modules\API
				for fileName in os.listdir(fullPath+'\\'+dir):
					# print("file name: " + fileName)
					mPath = ""
					# if fileName != '$.config' and '.config' not in fileName:
					if  '.html' in fileName or \
						'.htm' in fileName or \
						'.hpp' in fileName:
						mPath = dir+'/'+os.path.splitext(fileName)[0]
						# print("mpath: " + mPath)
					if '.' not in mPath and mPath != "":
						# print([mPath,mPath])
						modulesList.append([mPath,mPath])
		return modulesList


	def user_selection(self, view):
		# get the current cursor point
		sel = view.sel()[0].begin()
		# get the line with current cursor
		get_line = view.line(sel)
		# convert the line to string
		sel = view.substr(get_line)
		# print("user selection: " + sel)
		return sel

	def get_ui_files(self, folder):
		modulesList = []
		for fileName in os.listdir(folder):
			mPath = 'ui/' + os.path.splitext(fileName)[0]
			modulesList.append([mPath,mPath])
		return modulesList

	def remove_duplicates(self, modulesList, lis):
		result = []
		for item in lis:
			if item not in modulesList:
				result.append(item)
		return result


