from islpy import *

schedule = UnionMap("{Stmt[i,j] -> [o0, o1]: 0 <= i < 5 and 0 <= i < j and o0 = i and o1 = j}")

schedule_domain = schedule.range()

s = Set.from_union_set(schedule_domain)

schedule_domain.dim_min(0)
schedule_domain.dim_min(1)
schedule_domain.dim_max(0)
schedule_domain.dim_max(1)

def f(x): print(x)
l = []
schedule_domain.foreach_point(l.append)
print(l)

schedule.intersect_range(Set.from_point(l[0])).domain()

