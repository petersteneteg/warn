import os
import sys
import argparse
import glob
import re

import warn.warning
import warn.parser

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Generate warning include files")
	parser.add_argument("-t", "--templates", type=str, dest="templates", default="templates",
						help="Template file")
	parser.add_argument("-g", "--gcc_warnings", type=str, dest="gcc_warnings", default="ext/barro/gcc",
						help="GCC Warnings")
	parser.add_argument("-c", "--clang_warnings", type=str, dest="clang_warnings", default="ext/barro/clang",
						help="Clang Warnings")
	parser.add_argument("-v", "--vs_warnings", type=str, dest="vs_warnings", default="ext/VS",
						help="VS Warnings")
	parser.add_argument("-w", "--warnings", type=str, dest="warnings", default="warnings.md",
						help="Warnings Table")
	parser.add_argument("-e", "--extra_warnings", type=str, dest="extra_warnings", nargs="*", default=[],
						help="Extra Warning Tables")
	parser.add_argument("-f", "--folder_name", type=str, dest="folder_name", default="warn",
						help="base path")
	parser.add_argument("-i", "--ignore_name", type=str, dest="ignore_name", default="ignore",
						help="ignore folder name")
	parser.add_argument("-x", "--prefix", type=str, dest="prefix", default="",
						help="include guard prefix")
	parser.add_argument("-o", "--output_dir", type=str, dest="output_dir", default="output",
						help="Output destination")
	parser.add_argument("--header", type=str, dest="header", default=None,
						help="Optional header file to include at start of each file")
	args = parser.parse_args()

	parsers = {
		"clang" : warn.parser.ClangWarningParser("clang", args.clang_warnings), 
		"gcc" : warn.parser.GCCWarningParser("gcc", args.gcc_warnings),
		"vs" : warn.parser.VSWarningParser("vs", args.vs_warnings)
	}

	table = warn.warning.parse_warning_table(args.warnings, parsers)

	for extra in args.extra_warnings:
		table.update(warn.warning.parse_warning_table(extra, parsers))

	header = ""
	if args.header:
		with open(args.header, "r") as f:
			header = f.read()

	base = os.path.abspath(args.output_dir)
	if not os.path.exists(base): os.mkdir(base)
	warn_dir = base + "/" + args.folder_name
	if not os.path.exists(warn_dir): os.mkdir(warn_dir)
	ignore_dir = warn_dir + "/" + args.ignore_name
	if not os.path.exists(ignore_dir): os.mkdir(ignore_dir)

	with open(args.templates + "/template", "r") as f:
		template = f.read()
		for name, w in table.items():
			guard_str = "WARN_IGNORE_" + name.upper().replace("-","_")
			contents = header + template.format(
				path = args.folder_name, 
				ignore=args.ignore_name, 
				name = name, 
				prefix=args.prefix, 
				guard=guard_str,
				contents = w.format())
			with open(ignore_dir + "/" + name, "w") as o: o.write(contents)

	with open(args.templates + "/push", "r") as f:
		push_template = f.read()
		contents = header + push_template.format(prefix=args.prefix, path = args.folder_name)
		with open(warn_dir + "/push", "w") as o: o.write(contents)

	with open(args.templates + "/pop", "r") as f:
		pop_template = f.read()
		undefs = "\n".join([args.prefix + "#undef WARN_IGNORE_" + name.upper().replace("-","_") for name in table.keys()])
		contents = header + pop_template.format(prefix=args.prefix, path = args.folder_name, undefs = undefs)
		with open(warn_dir + "/pop", "w") as o: o.write(contents)

	with open(ignore_dir + "/all", "w") as o: 
		contents = header + "\n".join(["#include <" + args.folder_name + "/" + args.ignore_name + "/" +  name + ">" for name in table.keys()])
		o.write(contents)

