import glob
import re

from distutils.version import LooseVersion as Version

from . import warning

class WarningParser:
	def	__init__(self, compiler, path):
		self.compiler = compiler
		self.path = path
		self.warnings = []

class BaseWarningParser(WarningParser):
	def __init__(self, compiler, path):
		WarningParser.__init__(self, compiler, path)

	def try_get_warning(self, name):
		if name in self.warnings:
			return True, self.warnings[name]
		else:
			return False, None

	def parse_warning_files(self, files):
		if not files:
		    print("Warning, no files for %s in %s" % (self.compiler, self.path))
		warndict = {}
		for file in files:
			match = re.match(r".*warnings-.*-(\d+(\.\d+)?)\.txt", file)
			if match:
				version = Version(match.group(1))
				with open(file, 'r') as f:
					for line in f:
						line = line.split("#")[0].strip()
						dummy = re.match(".*DUMMY.*", line)
						if dummy: continue

						need_value = re.match(".*=", line)
						if need_value: continue

						warning_match = re.match("-W(.*)", line)
						if warning_match:
							name = warning_match.group(1)
							if len(name) == 0: continue
							if name in warndict:
								if version < warndict[name].version:
									warndict[name].version = version
							else: 
								warndict[name] = warning.Warning(self.compiler, name, version)
		return warndict

class ClangWarningParser(BaseWarningParser):
	def __init__(self, compiler, path):
		BaseWarningParser.__init__(self, compiler, path)
		files = glob.glob(self.path + "/warnings-clang-unique-*.txt")
		self.warnings = self.parse_warning_files(files)

class GCCWarningParser(BaseWarningParser):
	def __init__(self, compiler, path):
		BaseWarningParser.__init__(self, compiler, path)
		files = glob.glob(self.path + "/warnings-gcc-unique-*.txt")
		self.warnings = self.parse_warning_files(files)

class VSWarningParser(WarningParser):
	def __init__(self, compiler, path):
		WarningParser.__init__(self, compiler, path)
		self.warnings = self.parse_vs_warnings(self.path)

	def try_get_warning(self, name):
		if name in self.warnings:
			return True, self.warnings[name]
		elif re.match(r"C2\d\d\d\d", name): # c++ core guideline check
			return True, warning.Warning(self.compiler, name, Version("15"), name)
		else:
			return False, None

	def parse_vs_warnings_versions(self, file):
		warndict = {}
		version  = Version("0")
		with open(file, 'r') as f:
			for line in f:
				version_match = re.match(r"These warnings.*`\/Wv:([\d.]+)`.", line)
				if version_match:
					version  = Version(version_match.group(1))
				warning_match = re.match(r"\|\s*(C\d+)\s*\|\s*`(.*)`", line)
				if warning_match:
					name = warning_match.group(1)
					desc = warning_match.group(2)
					if name not in warndict:
						warndict[name] = warning.Warning(self.compiler, name, version, desc)
		return warndict

	def parse_vs_warnings(self, warning_dir):
		versions =  warning_dir + "/compiler-warnings-by-compiler-version.md"
		files = glob.glob(warning_dir + "/compiler-warnings-c*.md")
	
		warndict = self.parse_vs_warnings_versions(versions)
		for file in files:
			with open(file, 'r') as f:
				for line in f:
					warning_match = re.match(r"\|\[?Compiler [Ww]arning ?(\(.*\))? ?(C\d+)(\]\(.*\))?.*\|(.*)\|", line)
					if warning_match:
						name = warning_match.group(2)
						desc = warning_match.group(4)
						if name not in warndict:
							# We guess that they have been there a long time.
							warndict[name] = warning.Warning(self.compiler, name, Version("13"), desc) 

		cppcheck2 =  warning_dir + "/CoreCheckers.md"
		with open(cppcheck2, 'r') as f:
			for line in f:
				warning_match = re.match(r"\s*WARNING_(\S+)\s*=\s*(\d{5}).*", line)
				if warning_match:
					name = "C" + warning_match.group(2)
					desc = warning_match.group(2).lower()
					# don't have a version for the CPP-check stuff, put it in 2017...
					warndict[name] = warning.Warning(self.compiler, name, Version("15"), desc)

		return warndict