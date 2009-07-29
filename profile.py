#!/usr/local/bin/python2.5
import pstats
p = pstats.Stats('profiling.txt')

p.strip_dirs()
p.sort_stats('time').print_stats(100)
p.print_callers(200)
p.sort_stats('cumulative').print_stats(100)
p.print_callers(40)
