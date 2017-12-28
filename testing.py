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

question = "Which of the following is a citrus fruit"
choices = [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")] 
for i in range(20):
	now = time.time()
	with suppress_stdout():
		g.query(question, choices)
	elapsed = time.time() - now
	print("Elapsed time: {}", elapsed)
	averages.append(elapsed)