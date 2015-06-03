#!/usr/bin/python3

#foreach statement
#	find all memrefs
#	are memrefs constant or domain dependent?
#	plot constant memrefs as single square, domain dependents as many squres

import re
import sys
import json
import math
import pprint

if len(sys.argv) < 2:
	print("Usage: " + sys.argv[0] +" inputfile")
	sys.exit(-1)

f = open(sys.argv[1], 'r')
scop = json.loads(f.read())
pp = pprint.PrettyPrinter(indent=4)

class Memory:
	'Represents a single memory object, i.e., an array or variable'

	def __init__(self, name):
		self.name = name
		self.used_with = {}
		self.lb = 0
		self.ub = 0

	def add_usage(self, index):
		self.used_with[index] = 1;

	def is_used_with(self, index):
		if index in self.used_with:
			return 1
		else:
			return 0

	def update_lb(self, lb):
		if lb < self.lb:
			self.lb = lb
	
	def update_ub(self, ub):
		if (ub > self.ub):
			self.ub = ub

class SCOPState:
	'Represents the memory state of a SCOP'
	
	def __init__(self, scopname):
		self.name = scopname
		self.memories = {}

	def add_memory_object(self, name):
		if not name in self.memories:
			mem = Memory(name)
			self.memories[name] = mem
			print("added memory object: " + name)
			return mem
		else:
			return self.memories[name]
	
	def get_memory_object(self, memname):
		if memname in self.memories:
			return self.memories[memname]

	def paint(self, outfile):
		# draw all memories with size=(lb-ub+1)
		# if size=1 give them the usage name, otherwise name them from lb to ub
		print(self.name)
		for k in sorted(self.memories):
			mem = state.get_memory_object(k)
			print(mem.name+": ", end="")
			memsize = mem.ub-mem.lb+1
			cells_per_dot = math.ceil(memsize/100)
			if cells_per_dot < 1:
				cells_per_dot = 1
			dots = max(1, math.floor(memsize/cells_per_dot))
			for i in range(1, dots+1):
				print(".", end="")
			print("")

		# signal state of each cell with color: red:write, green:read, grey:inactive

def get_lower_bound(usage_name, domain_desc):
	# i0 >= 0 and i0 <= 999
	match = re.search(usage_name + " >= (\d+)", domain_desc)
	print("lb of "+ usage_name + ": " + match.group(1))
	return int(match.group(1))

def get_upper_bound(usage_name, domain_desc):
	# i0 >= 0 and i0 <= 999
	match = re.search(usage_name + " <= (\d+)", domain_desc)
	print("ub of " + usage_name + ": " + match.group(1))
	return int(match.group(1))


# find all memrefs so that we can add them to a state object
state = SCOPState(sys.argv[1])
for stmt in scop['statements']:
	accs = stmt['accesses']
	for acc in accs:
		rel = acc['relation']
		match = re.search('MemRef_(.*?)\[(.*?)\]', rel)
		if match:
			mem = state.add_memory_object(match.group(1))
			mem.add_usage(match.group(2))
	# get the domain, so that we can estimate the size of the mem-objs
	domain = stmt['domain']
	match = re.search('\{ ' + stmt['name'] + '\[(.*)\] : (.*?) }', domain)
	usage_name = match.group(1)
	domain_desc = match.group(2)
	print("usage_name: " + usage_name)
	print("domain_desc: " + domain_desc)

	# now we need to get the lower and upper bound of the domain, 
	lower = get_lower_bound(usage_name, domain_desc)
	upper = get_upper_bound(usage_name, domain_desc)
	# now we iterate over all the memory objects and update the lower and upper
	# bounds if they are used by usage_name
	for mem in state.memories:
		if state.get_memory_object(mem).is_used_with(usage_name) == 1:
			print(mem+" is used with "+usage_name+" lb is "+str(lower)+" ub is ", str(upper))
			state.get_memory_object(mem).update_lb(lower)
			state.get_memory_object(mem).update_ub(upper)

state.paint("foo.svg");

