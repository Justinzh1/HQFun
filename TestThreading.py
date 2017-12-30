import gsearch as g
from collections import Counter

import grequests
from multiprocessing import Process, Manager, Lock

import thread
import concurrent.futures


import pdb

gs = g.GSearch()
question = "Which of the following is a citrus fruit"
choices = [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")]

counter = Counter()

links = set()
domains = gs.get_top_links(question, choices)
gs.create_soup(domains, question, choices, links, 10)

class ThreadedFetch: 
    def __init__(self, urls):
        self.urls = urls

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def async(self):
        results = grequests.map((grequests.get(u) for u in self.urls), exception_handler=self.exception, size=5)
        return results

def process_args(args):
    page, keywords, keyword_count = args
    page_counter = Counter(page.text.split(' '))
    n = len(page_counter.keys())
    for key in keywords:
        keyword_count[key].append(page_counter[key])
    return keyword_count

def threaded_scan_body(args):
    return process_args(args)

def construct_iterable(pages, keywords, keyword_count):
    arguments = []
    for p in pages:
        arguments.append([p, keywords, Counter(keyword_count)])
    return arguments

def sum_keys(counter, result):
    print(counter)
    for k,v in counter.items():
        result[k] = sum(counter[k])

keyword_counter = Counter()

test = ThreadedFetch(links)
pages = test.async()

d = Counter()
for c in choices:
    d[c] = [0]

manager = Manager()

search_parings = construct_iterable(pages, choices, d)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(threaded_scan_body, args): args for args in search_parings}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
            sum_keys(data, keyword_counter)
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
            # print('%r page is %d bytes' % (url, len(data)))

print(keyword_counter)

# pool = concurrent.futures.ProcessPoolExecutor(5)
# future = [executor.submit(threaded_scan_body, item) for item in search_parings]
# concurrent.futures.wait(futures)

# print(futures)
