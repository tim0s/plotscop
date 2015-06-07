#!/usr/bin/python3

import re
import sys
import json
import math
import time
import islpy
import pprint
import colorama
from collections import defaultdict

#######################################
#           helper functions          #
#######################################

def contains_val_in_range(intlist, rstart, rend):
	for i in intlist:
		if i >= rstart and i < rend:
			return True	
	return False

class JSCOPPlot:

	def __init__(self, jscopstr):
		self.ncols = 120    # output width in chars
		self.speed = 10     # time in ms each state is shown
		self.memories = defaultdict(Memory)
		self.statement_names = defaultdict(int)
		self.statements = []

		colorama.init()

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
					#TODO use get_tuple_name, set_dim_min(0)
					match = re.search("MemRef_(.+)\[(.+)\]", accstr)
					if match:
						mem = match.group(1)
						subscript = match.group(2)
						access = Access(mem, subscript, acc['kind'])
						self.add_access(access)
						self.add_statement(stmt['name']).add_step(step).add_access(access)
					elif islpy.UnionSet(accstr).is_empty() == True:
						continue
					else:
						print("Got an access string from isl which I cannot parse: " + accstr)

	def clearscreen(self):
		print("\033[2J\033[1;1f")

	def plot_mem_and_accs(self, mem, reads, writes):
		bytes_per_dot = 1
		memsize = self.memories[mem].get_size()
		if memsize <= self.ncols:
			bytes_per_dot = 1
		else:
			bytes_per_dot = math.ceil(memsize / self.ncols)
		dots = ""
		numdots = math.floor(memsize/bytes_per_dot)

		# produce dots in the right colors
		for dot in range(0, numdots):
			sstart = self.memories[mem].lower_bound + dot * bytes_per_dot
			send = self.memories[mem].lower_bound + (dot+1) * bytes_per_dot
			if contains_val_in_range(reads, sstart, send):
				dots += 'r'
			elif contains_val_in_range(writes, sstart, send):
				dots += 'w'
			elif contains_val_in_range(reads, sstart, send) and contains_val_in_range(writes, sstart, send):
				dots += 'b'
			else:
				dots += '.'

		legend = ". = " + str(bytes_per_dot) + "B"
		formatstr = "[%-12s] %-"+str(self.ncols)+"s (%s)\n"
		print(formatstr % (mem, dots, legend))

	def plot_step(self, stepnum, accesses):
		for mem in sorted(self.memories):
			reads = []
			writes = []
			# seperate accesses to mem into reads and writes
			for acc in accesses:
				if acc.name == mem and acc.kind == "read":
					reads.append(acc.subscript)
				if acc.name == mem and acc.kind == "write":
					writes.append(acc.subscript)
			self.plot_mem_and_accs(mem, reads, writes)

	def show(self):
		cnt = 0
		for statement in self.statements:
			for step in statement.steps:
				self.clearscreen()
				cnt += 1
				print(cnt)
				self.plot_step(cnt, statement.steps[step].accesses)
				time.sleep(self.speed/1000)
		self.clearscreen()

	def add_access(self, access):
		mem = self.memories[access.get_name()]
		mem.update_bounds(access.get_subscript())

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
		if subscript > self.upper_bound:
			self.upper_bound = subscript

	def get_size(self):
		return 1 + self.upper_bound - self.lower_bound

class Statement:

	def __init__(self):
		self.steps = defaultdict(Step)

	def add_step(self, stepnum):
		return self.steps[stepnum]

class Step:

	def __init__(self):
		self.accesses = [];

	def add_access(self, access):
		self.accesses.append(access)

class Access:

	def __init__(self, name, subscript, kind):
		self.name = name
		#TODO check if it is actually an integer
		self.subscript = int(subscript)
		self.kind = kind

	def get_name(self):
		return self.name
	
	def get_subscript(self):
		return self.subscript

#####################################
#            main                   #
#####################################

# die if we don't have an input file
if len(sys.argv) < 2:
	print("Usage: " + sys.argv[0] +" inputfile")
	sys.exit(-1)

f = open(sys.argv[1], 'r')
plot = JSCOPPlot(f.read())
plot.show()


