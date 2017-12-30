import gsearch as g
import time

averages = []
now = None

gSearch = g.GSearch()

question = "Which of the following is a citrus fruit"
choices = [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")] 

## Testing for query speed
# for i in range(5):
#     now = time.time()
#     gSearch.threaded_query(question, choices, 10, 15)
#     elapsed = time.time() - now
#     print("Elapsed time: {}".format(elapsed))
#     averages.append(elapsed)
# a1 = sum(averages)/float(len(averages))

now = time.time()
gSearch.prototype_query(question, choices, 10)
elapsed = time.time() - now
print("Elapsed time: {}".format(elapsed))

# averages = []
# for i in range(5):
#     now = time.time()
#     gSearch.threaded_query(question, choices, 10, 16)
#     elapsed = time.time() - now
#     print("Elapsed time: {}".format(elapsed))
#     averages.append(elapsed)
# a2 = sum(averages)/float(len(averages))


# averages = []
# for i in range(5):
#     now = time.time()
#     gSearch.threaded_query(question, choices, 7, 16)
#     elapsed = time.time() - now
#     print("Elapsed time: {}".format(elapsed))
#     averages.append(elapsed)
# a3 = sum(averages)/float(len(averages))

# print("Average time 15 threads:{}, 16 threads: {}, 16 threads 7 cap: {}".format(a1,a2,a3))
