#!/usr/local/bin/python2.5
import pstats
p = pstats.Stats('profiling.txt')

p.strip_dirs()
p.sort_stats('time').print_stats(40)
p.sort_stats('cumulative').print_stats(40)

