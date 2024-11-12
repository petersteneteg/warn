from pathlib import Path
import re

from . import version

from . import warning

class WarningParser:
	def	__init__(self, compiler:str, path:Path):
		self.compiler = compiler
		self.path = path
		self.warnings = []

class BaseWarningParser(WarningParser):
	def __init__(self, compiler:str, path:Path):
		WarningParser.__init__(self, compiler, path)

	def try_get_warning(self, name:str):
		if name in self.warnings:
			return True, self.warnings[name]
		else:
			return False, None

	def parse_warning_files(self, files:list[Path]):
		if not files:
		    print("Warning, no files for %s in %s" % (self.compiler, self.path))
		warndict = {}
		for file in files:
			if match := re.match(r".*warnings-.*-(\d+(\.\d+)?)\.txt", str(file)):
				compilerVersion = version.Version(match.group(1))
				with open(file, 'r') as f:
					for line in f:
						line = line.split("#")[0].strip()
						
						if dummy := re.match(".*DUMMY.*", line):
							continue

						if need_value := re.match(".*=", line):
							continue

						if warning_match := re.match("-W(.*)", line):
							name = warning_match.group(1)
							if len(name) == 0: continue
							if name in warndict:
								if compilerVersion < warndict[name].version:
									warndict[name].version = compilerVersion
							else: 
								warndict[name] = warning.Warning(self.compiler, name, compilerVersion)
		return warndict

class ClangWarningParser(BaseWarningParser):
	def __init__(self, compiler:str, path:Path):
		BaseWarningParser.__init__(self, compiler, path)
		files = self.path.glob("warnings-unique-*.txt")
		self.warnings = self.parse_warning_files(files)

class GCCWarningParser(BaseWarningParser):
	def __init__(self, compiler:str, path:Path):
		BaseWarningParser.__init__(self, compiler, path)
		files = self.path.glob("warnings-unique-*.txt")
		self.warnings = self.parse_warning_files(files)

class VSWarningParser(WarningParser):
	def __init__(self, compiler:str, path:Path):
		WarningParser.__init__(self, compiler, path)
		self.warnings = self.parse_vs_warnings(self.path)

	def try_get_warning(self, name:str):
		if name in self.warnings:
			return True, self.warnings[name]
		elif re.match(r"C2\d\d\d\d", name): # c++ core guideline check
			return True, warning.Warning(self.compiler, name, version.Version("15"), name)
		else:
			return False, None

	def parse_vs_warnings_versions(self, file:Path):
		warndict = {}
		compilerVersion = version.Version("0")
		with open(file, 'r') as f:
			for line in f:
				if version_match := re.match(r"These warnings.*`\/Wv:([\d.]+)`.", line):
					compilerVersion  = version.Version(version_match.group(1))
				if warning_match := re.match(r"\|\s*(C\d+)\s*\|\s*`(.*)`", line):
					name = warning_match.group(1)
					desc = warning_match.group(2)
					if name not in warndict:
						warndict[name] = warning.Warning(self.compiler, name, compilerVersion, desc)
		return warndict

	def parse_vs_warnings(self, warning_dir:Path):
		versions =  warning_dir / "compiler-warnings-by-compiler-version.md"
		files = warning_dir.glob("compiler-warnings-c*.md")
	
		warndict = self.parse_vs_warnings_versions(versions)
		for file in files:
			with open(file, 'r') as f:
				for line in f:
					if warning_match := re.match(r"\|\s*\[?Compiler [Ww]arning ?(\(.*\))? ?(C\d+)(\]\(.*\))?.*\|(.*)\|", line):
						name = warning_match.group(2)
						desc = warning_match.group(4)
						if name not in warndict:
							# We guess that they have been there a long time.
							warndict[name] = warning.Warning(self.compiler, name, version.Version("13"), desc) 

		cppcheck2 =  warning_dir / "CoreCheckers.md"
		with open(cppcheck2, 'r') as f:
			for line in f:
				if warning_match := re.match(r"\s*WARNING_(\S+)\s*=\s*(\d{5}).*", line):
					name = "C" + warning_match.group(2)
					desc = warning_match.group(2).lower()
					# don't have a version for the CPP-check stuff, put it in 2017...
					warndict[name] = warning.Warning(self.compiler, name, version.Version("15"), desc)

		return warndict
