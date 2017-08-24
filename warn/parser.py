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

	def parse_warning_files(self, files):
		warndict = {}
		for file in files:
			match = re.match(".*warnings-.*-(\d+(\.\d+)?)\.txt", file)
			if match:
				version = Version(match.group(1))
				with open(file, 'r') as f:
					for line in f:
						line = line.strip()
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

	def parse_vs_warnings_versions(self, file):
		warndict = {}
		version  = Version("0")
		with open(file, 'r') as f:
			for line in f:
				version_match = re.match(".*__\/Wv:([\d.]+)__.", line)
				if version_match:
					version  = Version(version_match.group(1))
				warning_match = re.match("(C[\d]+)\|(.*)", line)
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
					warning_match = re.match("\|\[?Compiler [Ww]arning ?(\(.*\))? ?(C\d+)(\]\(.*\))?.*\|(.*)\|", line)
					if warning_match:
						name = warning_match.group(2)
						desc = warning_match.group(4)
						if name not in warndict:
							warndict[name] = warning.Warning(self.compiler, name, Version("13"), desc) # We guess that they have been there a long time.
		return warndict