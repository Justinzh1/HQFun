import gsearch as g
import time

averages = []
now = None

gSearch = g.GSearch()

question = "Which of the following is a citrus fruit"
choices = [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")] 
for i in range(10):
	now = time.time()
	gSearch.query(question, choices)
	elapsed = time.time() - now
	print("Elapsed time: {}".format(elapsed))
	averages.append(elapsed)
print("Average time: {}".format(sum(averages)/float(len(averages))))