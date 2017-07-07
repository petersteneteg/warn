import os
import sys
import argparse
import glob
import re

import warn.warning
import warn.parser

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Generate warning include files")
	parser.add_argument("-t", "--template", type=str, dest="template", default="template.h",
						help="Template file")
	parser.add_argument("-g", "--gcc_warnings", type=str, dest="gcc_warnings", default="ext/barro/gcc",
						help="GCC Warnings")
	parser.add_argument("-c", "--clang_warnings", type=str, dest="clang_warnings", default="ext/barro/clang",
						help="Clang Warnings")
	parser.add_argument("-v", "--vs_warnings", type=str, dest="vs_warnings", default="ext/VS",
						help="VS Warnings")
	parser.add_argument("-w", "--warnings", type=str, dest="warnings", default="warnings.md",
						help="Warnings Table")
	args = parser.parse_args()

	parsers = {
		"clang" : warn.parser.ClangWarningParser("Clang", args.clang_warnings), 
		"gcc" : warn.parser.GCCWarningParser("GCC", args.gcc_warnings),
		"vs" : warn.parser.VSWarningParser("VS", args.vs_warnings)
	}

	table = warn.warning.parse_warning_table(args.warnings, parsers)

	for n, w in table.items():
		print(w)


