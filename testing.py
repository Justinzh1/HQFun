import gsearch as g
import time

from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

averages = []
now = None

gSearch = g.GSearch()

question = "Which of the following is a citrus fruit"
choices = [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")] 
for i in range(10):
	now = time.time()
	with suppress_stdout():
		gSearch.query(question, choices)
	elapsed = time.time() - now
	print("Elapsed time: {}".format(elapsed))
	averages.append(elapsed)
print("Average time: {}".format(sum(averages)/float(len(averages))))