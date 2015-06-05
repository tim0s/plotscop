#!/usr/bin/python3

import re
import sys
import json
import islpy
import pprint
from collections import defaultdict




class JSCOPPlot:

	def __init__(self, jscopstr):
		self.memories = defaultdict(Memory)
		self.statement_names = defaultdict(int)
		self.statements = []

		scop = json.loads(jscopstr)
		for stmt in scop['statements']:

			schedule = islpy.UnionMap(stmt['schedule'])

			# generate all "states" for this stmt
			l = []
			schedule.range().foreach_point(l.append)

			for step in range(0, len(l)):

				for acc in stmt['accesses']:

					# enumerate all accesses in this timestep
					access = islpy.UnionMap(acc['relation'])
					tmp = schedule.intersect_range(islpy.Set.from_point(l[step])).domain()
					accstr = access.intersect_domain(tmp).range().to_str()

					# Extract memory name and subscript. I guess it is possible to do this in
					# ISL, but I could not find the right function :(
					match = re.search("MemRef_(.+)\[(.+)\]", accstr)
					if match:
						mem = match.group(1)
						subscript = match.group(2)
						access = self.add_memref(mem, subscript, acc['kind'])
						self.add_statement(stmt['name']).add_step(step).add_access(access)
					elif islpy.UnionSet(accstr).is_empty() == True:
						continue
					else:
						print("Got an access string from isl which I cannot parse: " + accstr)

	def add_access(self, access):
		mem = self.memories[name]
		#TODO check if subscript is a valid int!
		mem.update_bounds(int(subscript))
		return (name, subscript)

	def add_statement(self, stmtname):
		idx = self.statement_names[stmtname]
		if idx == 0:
			idx = len(self.statements)
			stmt = Statement()
			self.statements.append(stmt)
		return self.statements[idx]

class Memory:

	def __init__(self):
		self.lower_bound = 2 ** 64
		self.upper_bound = 0

	def update_bounds(self, subscript):
		if subscript < self.lower_bound:
			self.lower_bound = subscript
		if subscript > self.lower_bound:
			self.upper_bound = subscript


class Statement:

	def __init__(self):
		self.steps = defaultdict(Step)

	def add_step(self, stepnum):
		return self.steps[stepnum]

class Step:

	def __init__(self):
		self.accesses = [];

	def add_access(self, access):
		return Access(name, subscript, kind)

class Access:

	def __init__(self, name, subscript, kind):
		self.name = name
		self.subscript = subscript
		self.kind = kind
		return self



# die if we don't have an input file

if len(sys.argv) < 2:
	print("Usage: " + sys.argv[0] +" inputfile")
	sys.exit(-1)

f = open(sys.argv[1], 'r')
plot = JSCOPPlot(f.read())


