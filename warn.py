import os
import argparse
import glob
import re
import textwrap

import warn.warning
import warn.parser

def sdir():
	return os.path.dirname(os.path.realpath(__file__))

def toMacro(string):
	return string.upper().replace('-','_').replace('+', 'X')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog="warn", formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''
			Generate warning files
			Default directory structure:
			    output/                (output_dir)
			        warn/              (folder_name)
			            ignore/        (ignore_name)
			                all        (ignore all warnings)
			                warning1   (first name from warning table)
			                warning2   (second name from warning table)
			                ...        (etc for all name in table)
			            push           (push pragma state)
			            pop            (pop pragma state)
		'''))
	parser.add_argument("-w", "--warnings", type=str, dest="warnings", default= sdir() + "/warnings.md", 
						metavar="TABLE", help="warning table file (default: '%(default)s')")
	parser.add_argument("-e", "--extra_warnings", type=str, dest="extra_warnings", nargs="+", default=[],
						metavar="TABLE", help="extra warning table files")

	parser.add_argument("-o", "--output_dir", type=str, dest="output_dir", default="output",
						metavar="DIR", help="output destination (default: '%(default)s')")
	parser.add_argument("--folder_name", type=str, dest="folder_name", default="warn",
						metavar="NAME", help="base folder name (default: '%(default)s')")
	parser.add_argument("--ignore_name", type=str, dest="ignore_name", default="ignore",
						metavar="NAME", help="ignore folder name (default: '%(default)s')")
	parser.add_argument("--prefix", type=str, dest="prefix", default="",
						metavar="STR", help="include guard prefix (default: '%(default)s')")
	parser.add_argument("--header", type=str, dest="header", default=None,
						metavar = "FILE", help="optional header file to include at start of each file")

	parser.add_argument("--templates", type=str, dest="templates", default=sdir() + "/templates",
						metavar="DIR", help="template directory, should contain a 'template', 'push', and 'pop' file (default: '%(default)s')")
	parser.add_argument("--gcc_warnings", type=str, dest="gcc_warnings", default=sdir() + "/ext/barro/gcc",
						metavar="DIR", help="GCC warnings directory (default: '%(default)s')")
	parser.add_argument("--clang_warnings", type=str, dest="clang_warnings", default=sdir() + "/ext/barro/clang",
						metavar="DIR", help="Clang warnings directory (default: '%(default)s')")
	parser.add_argument("--vs_warnings", type=str, dest="vs_warnings", default=sdir() + "/ext/VS",
						metavar="DIR", help="VS warnings directory (default: '%(default)s')")

	args = parser.parse_args()

	# Parse and gather warning versions
	parsers = {
		"clang" : warn.parser.ClangWarningParser("clang", args.clang_warnings), 
		"gcc" : warn.parser.GCCWarningParser("gcc", args.gcc_warnings),
		"vs" : warn.parser.VSWarningParser("vs", args.vs_warnings)
	}

	# Collect warnings to generate
	table = warn.warning.parse_warning_table(args.warnings, parsers)
	for extra in args.extra_warnings:
		table.update(warn.warning.parse_warning_table(extra, parsers))

	# Optional header
	header = ""
	if args.header:
		with open(args.header, "r") as f:
			header = f.read()

	# Create output directories
	base = os.path.abspath(args.output_dir)
	if not os.path.exists(base): os.mkdir(base)
	warn_dir = base + "/" + args.folder_name
	if not os.path.exists(warn_dir): os.mkdir(warn_dir)
	ignore_dir = warn_dir + "/" + args.ignore_name
	if not os.path.exists(ignore_dir): os.mkdir(ignore_dir)

	# Gnerate warnings
	with open(args.templates + "/template", "r") as f:
		template = f.read()
		for name, w in table.items():
			guard_str = "WARN_IGNORE_" + toMacro(name)
			contents = header + template.format(
				folder = args.folder_name, 
				ignore = args.ignore_name, 
				name = name, 
				prefix = args.prefix, 
				guard = guard_str,
				contents = w.format())
			with open(ignore_dir + "/" + name, "w") as o: o.write(contents)

	# Generate igmore all
	with open(ignore_dir + "/all", "w") as o: 
		contents = header + "\n".join(["#include <" + args.folder_name + "/" + args.ignore_name + "/" +  name + ">" for name in table.keys()])
		o.write(contents)

	# Generate push
	with open(args.templates + "/push", "r") as f:
		push_template = f.read()
		contents = header + push_template.format(prefix = args.prefix, folder = args.folder_name)
		with open(warn_dir + "/push", "w") as o: o.write(contents)

	# Generate pop
	with open(args.templates + "/pop", "r") as f:
		pop_template = f.read()
		undefs = "\n".join([args.prefix + "#undef WARN_IGNORE_" + toMacro(name) for name in table.keys()])
		contents = header + pop_template.format(prefix = args.prefix, folder = args.folder_name, undefs = undefs)
		with open(warn_dir + "/pop", "w") as o: o.write(contents)


