import gsearch as g
from collections import Counter

import grequests
from multiprocessing import Process, Manager

import thread
import concurrent.futures

import pdb

class ThreadedFetch: 
    def __init__(self, urls, processes):
        self.urls = urls
        self.processes = processes
        print(len(urls))

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def async(self):
        results = grequests.imap((grequests.get(u, timeout=1) for u in self.urls), exception_handler=self.exception, size=self.processes)
        return results

def process_args(lock, args):
    page, keywords, keyword_count = args
    page_counter = Counter(page.text.split(' '))
    n = len(page_counter.keys())
    for key in keywords:
        keyword_count[key].append(page_counter[key])
    return keyword_count

def threaded_scan_body(lock, args):
    return process_args(lock, args)

def construct_iterable(pages, keywords, keyword_count):
    arguments = []
    for p in pages:
        arguments.append([p, keywords, Counter(keyword_count)])
    return arguments

def sum_keys(counter, result):
    print(counter)
    for k,v in counter.items():
        result[k] = sum(counter[k])

