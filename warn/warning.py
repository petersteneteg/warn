import re
import itertools
from pathlib import Path

# Templates:
# Ref: http://nadeausoftware.com/articles/2012/10/c_c_tip_how_detect_compiler_name_and_version_using_compiler_predefined_macros

clang_warning = \
"""
#   if __clang_major__ > {clang_major} || (__clang_major__ == {clang_major}  && __clang_minor__ >= {clang_minor})
#       if __has_warning("-W{name}")
#           pragma clang diagnostic ignored "-W{name}"
#       endif
#   endif
""".strip()

gcc_warning = \
"""
#   if __GNUC__ > {gcc_major} || (__GNUC__ == {gcc_major}  && __GNUC_MINOR__ >= {gcc_minor})
#       pragma GCC diagnostic ignored "-W{name}"
#   endif
""".strip()

vs_warning = \
"""
#   if (_MSC_FULL_VER >= {version:0<9})
#       pragma warning(disable: {name})
#   endif
""".strip()

clang_all = """
#    pragma clang diagnostic ignored "-Weverything"
""".strip()

# Order is important, clang also defines __GNUC__
template = \
"""
#if defined(__clang__)
{clang}
#elif defined(__GNUC__)
{gcc}
#elif defined(_MSC_VER)
{vs}
#endif
""".strip()

class Warning:
	def	__init__(self, compiler:str, name:str, version = None, desc = None):
		self.compiler = compiler
		self.name = name
		self.desc = desc if desc != None else name
		self.version = version

	def __str__(self): 
		return "{:10} {:30} {:10} {:50}".format(self.compiler, self.name, str(self.version), str(self.desc))

	def format(self):
		v = self.version
		if self.compiler == "clang":
			return clang_warning.format(name = self.name, clang_major = v.major, clang_minor = v.minor)
		if self.compiler == "gcc":
			return gcc_warning.format(name = self.name, gcc_major = v.major, gcc_minor = v.minor)
		if self.compiler == "vs":
			return vs_warning.format(name = self.name[1:], version = str(v).replace('.', ''))

class WarningSet:
	def __init__(self, name:str, warnings):
		self.name = name
		self.warnings = warnings

	def __str__(self): 
		res = "{:30} : ".format(self.name)
		for w in self.warnings:
			res += "{0.compiler:5} {0.version:6} {0.name:30} ".format(w) 
		return res

	def format(self):
		strs = {"clang" : "//  Not available", "gcc" : "//  Not available", "vs" : "//  Not available"}
		for comp, w in self.warnings.items():
			strs[w.compiler] = w.format()
		return template.format(**strs)


def make_warning_set(parsers, name:str, clang_name:str, gcc_name:str, vs_name:str):
	warnings = {}

	def add_warning(comp, w_name):
		if w_name != "*no*":
			if w_name == "*same*": 
				w_name = name
			found, warning = parsers[comp].try_get_warning(w_name)
			if found: 
				warnings[comp] = warning
			else:
				print("Warning: Could not match warning: \"" + w_name + "\" for " + comp)

	add_warning("clang", clang_name)
	add_warning("gcc", gcc_name)
	add_warning("vs", vs_name)

	return WarningSet(name, warnings)

def parse_warning_table(file:Path, parsers):
	warning_sets = {}
	with open(file, "r") as f:
		f.readline() # skip header
		f.readline() # skip header
		for line in f:
			line_match = re.match(r"\s*(?P<name>\S+)\s*\|\s*(?P<clang>\S+)\s*\|\s*(?P<gcc>\S+)\s*\|\s*(?P<vs>\S+)\s*\|", line)
			if line_match:
				ws = make_warning_set(parsers, 
					name = line_match.group("name"), 
					clang_name = line_match.group("clang"), 
					gcc_name = line_match.group("gcc"), 
					vs_name = line_match.group("vs"))
				if ws.name in warning_sets:
					print("Error, duplicate warnings in: " + file)
				warning_sets[ws.name] = ws
	return warning_sets

def vs_all(table):
	def partition(x, n):
		y = list(x)
		return ((y[i:i+n] for i in range(0, len(y), n)))
	vs = [x.warnings['vs'] for n,x in table.items() if 'vs' in x.warnings.keys()]
	vs.sort(key=lambda w: w.version)
	def gen():
		for version, warnings in itertools.groupby(vs, key=lambda w:w.version):
			verstr = str(version).replace('.', '')
			res = f"#    if (_MSC_FULL_VER >= {verstr:0<9})\n"
			for sublist in partition(warnings, 13):
				names = ' '.join(i.name[1:] for i in sublist)
				res += f"#        pragma warning(disable: {names})\n"
			res += "#    endif"
			yield res
	return '\n'.join(gen())

def gcc_all(table):
	gcc = [x.warnings['gcc'] for n,x in table.items() if 'gcc' in x.warnings.keys()]
	gcc.sort(key=lambda w: w.version)
	def gen():
		for version, warnings in itertools.groupby(gcc, key=lambda w: w.version):
			v = version
			res = "#    if __GNUC__ > {major} || (__GNUC__ == {major}  && __GNUC_MINOR__ >= {minor})\n"
			res = res.format(major = v.major, minor=v.minor)
			for w in warnings:
				res += f"#        pragma GCC diagnostic ignored \"-W{w.name}\"\n"
			res += "#    endif"
			yield res
	return '\n'.join(gen())
