# Dependencies 
import requests
import json
import re
from collections import Counter
from bs4 import BeautifulSoup
import sys
import multiprocessing
import re
import color as c

import ThreadedFetchLinks as t
import threading

TIMEOUT = 5

# Debugging
import pdb
import time

# Link regex
is_link = re.compile("http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
banned = set(['the', 'a'])

class GSearch:  
    def digest_print(self, question, best, normalized, weights, z, i):
        print("{}ITERATION {}{}".format("="*9, i, "="*9))
        print("{}".format(normalized))
        print("\n{}".format(c.prPurple(question)))
        print("\n MAXIMUM: {}\n".format(c.prCyan(best)))
        for k,v in normalized.items():
            zscore, key, value, weight = c.text_color(v * weights[k], v*weights[k]), k, c.text_color(v,v), c.text_color(weights[k], weights[k])
            print(" {}\n \t z:{} \t\t score:{} \t\t search_weight:{}".format(k, zscore, value, weight))
        print("\n")

    def weighted_normalize(self, counter, weights):
        normalized = Counter()
        n = 0.0
        for k,v in counter.items():
            normalized[k] = (v * weights[k])
            n += (v * weights[k])
        for k,v in counter.items():
            normalized[k] = normalized[k]/n

        return normalized

    def normalize(self, counter):
        normalized = Counter()
        n = 0
        for k,v in counter.items():
            n += v
        max_value, max_option = 0, None
        for k,v in counter.items():
            update = round((v + 1)/(float(n) + 1.0),4)
            if update > max_value:
                max_value, max_option = round, k
            normalized[k] += update
        return normalized, max_value, max_option

    def get_top_links(self, question, keywords):
        url = "https://www.google.com/search?q="
        searchables = []
        base_question = ''.join([url,question]) 
        searchables.append(base_question)
        for key in keywords:
            searchables.append(''.join([base_question[2:],' "',key, '"']))
        return searchables

    def parse_number(self, s):
        s = s.replace(',', '')
        return int(re.search(r'\d+', s).group()) 

    def create_soup(self, urls, question, keywords, links, cap):
        hits = Counter()
        for i, url in enumerate(urls):
            res = requests.get(url)
            if res.status_code == 200:
                body = BeautifulSoup(res.text, 'html.parser')
                link_area = body.find("div", { "id" : "search" })
                results_area = body.find("div", { "id" : "resultStats"})
                hit = self.parse_number(results_area.text)
                if i > 0:
                    hits[keywords[i-1]] = hit
                self.find_links(link_area, links, cap)
        return hits

    def filter_links(self, url):
        return is_link.match(url) is not None and 'google' not in url and 'youtube' not in url and 'pdf' not in url

    def find_links(self, soup, links, cap):
        for i,link in enumerate(soup.find_all('a')):
            if i > cap:
                return
            url = link.get('href').split('=')[1].split('&')[0]
            if self.filter_links(url.lower()):
                links.append(url)
        return links

    def process_keywords(self, keywords):
        keyword_count = {}
        keyword_parent = {}
        new_keywords = []
        for key in keywords:
            keys = [k for k in key.split(' ') if k not in banned]
            keyword_parent[key] = keys
            keyword_count[key] = 0
        return keyword_count, keyword_parent


    def query(self, question, keywords, cap=10):
        print("Beginning search")
        keywords = [k.lower()for k in keywords]
        keyword_count, parents = self.process_keywords(keywords)    
        urls = self.get_top_links(question, keywords)
        links = set()
        self.create_soup(urls, question, keywords, links, cap)
        print("{} Sources found.".format(len(links)))

        """ TODO: Bottleneck issues
                - Multi thread search the different URLS
                - Threshold to stop when one Pr[keyword] > c
                - If exceeds 15 seconds terminate (Must account for latency)
        """

        ptime, i = 3, 0
        normalized, best = None, None
        for link in links: # Multi threading
            err = self.keyword_query(link, keywords, keyword_count)
            if not err:
                print("timed out")
                i += 1
                continue
            if i % 3 == 0:
                normalized, best = self.normalize(keyword_count)
                print(best.upper(), normalized)
            i += 1

    def threaded_query(self, question, keywords, cap=10, processes=3):
        print("Beginning threaded search")
        keywords = [k.lower()for k in keywords]
        keyword_count, parents = self.process_keywords(keywords)

        urls = self.get_top_links(question, keywords)
        links = list()
        hits = self.create_soup(urls, question, keywords, links, 2 * cap)   

        weights, num_results, most_result = self.normalize(hits)
        fetch_pages = t.ThreadedFetch(links, processes)
        pages = fetch_pages.async()
        # print("{} {} {}".format(len(links), "~>", len(pages)))
        ptime, i = 3,0
        max_value, best_option, normalized, zscore = 0, None, None, None
        for page in pages:
            if page and page.text:
                self.scan_body_with_parents(page, keyword_count, parents)
                if i % ptime == 0:
                    normalized, value, option = self.normalize(keyword_count)
                    zscore = self.weighted_normalize(keyword_count, weights)
                    if value > best_option:
                         max_value, best_option = value, option
                    self.digest_print(question, best_option, normalized, weights, zscore, i)
                i += 1
        print("\n{}\n".format(c.prCyan("="*9 + "TERMINATED" + "=" * 9)))
        self.digest_print(question, best_option, normalized, weights, zscore, i)

    def keyword_query(self, link, keywords, keyword_count):
        try:
            res = requests.get(link, timeout=3)
        except requests.exceptions.Timeout:
            res = None
        except requests.exceptions.RequestException as e:
            sys.exit(1)

        if res and res.status_code == 200:
            page = BeautifulSoup(res.text, 'html.parser')
            self.scan_body(page, keywords, keyword_count)
            return 200


    def scan_body(self, page, keywords, keyword_count):
        page_counter = Counter(page.text.lower().split(' '))
        n = len(page_counter.keys())
        for key in keywords:
            value = page_counter[key]
            if value:
                keyword_count[key] += page_counter[key]

    def scan_body_with_parents(self, page, keyword_count, parents):
        page_counter = Counter(page.text.lower().split(' '))
        n = len(page_counter.keys())
        for key in parents.keys():
            key_components = parents[key]
            value = 0
            for k in key_components:
                value += page_counter[k]
            if value:
                keyword_count[key] += value

    def prototype_query(self, question, keywords, cap=10):
        print("Beginning threaded search")
        keywords = [k.lower() for k in keywords]
        keyword_count, parents = self.process_keywords(keywords)

        urls = self.get_top_links(question, keywords)
        links = set()

        # Parallelize this
        now = time.time()
        elapsed = time.time() - now
        print("First get time: {}".format(elapsed))

        weights, num_results, most_result = self.normalize(hits)
        pages = []
        page_lock = threading.Lock()
        for link in links:
            threading.Thread(target=self.push_to_pages, args=(pages, page_lock, link)).start()
        time.sleep(3)
        print("{} {} {}".format(len(links), "~>", len(pages)))
        ptime, i = 3, 0
        max_value, best_option = 0, None
        for page in pages:
            if page and page.text:
                self.scan_body_with_parents(page, keyword_count, parents)
                if i % ptime == 0:
                    normalized, value, option = self.normalize(keyword_count)
                    zscore = self.weighted_normalize(keyword_count, weights)
                    if value > best_option:
                        max_value, best_option = value, option
                    self.digest_print(question, best_option, normalized, weights, zscore)
                i += 1

    def links_query(self, qusetion, keywords, cap, timeout=3):
        question, keywords, timeout = args
        keywords = [k.lower() for k in keywords]
        keyword_count, parents = self.process_keywords(keywords)

        urls = self.get_top_links(question, keywords)

        # Parallelize this
        for url in urls:
            args = [url, keywords, cap, timeout]
            links = self.parallel_query(push_to_links, urls, args, timeout)

        elapsed = time.time() - now

        print("First get time: {}".format(elapsed))

    def page_bodies_query(self, links):
        return self.parallel_query(self.push_to_pages, links)

    def parallel_query(self, push_func, links, args=[], timeout=3):
        result = []
        lock = threading.Lock()
        for link in links:
            threading.Thread(target=push_func, args=args+[result, lock, link, timeout]).start()
        return result;

    # Finish this to do initial 4 searches
    def push_to_links(self, url, keywords, cap, timeout):
        try:
            res = requests.get(link, timeout)
        except requests.exceptions.Timeout:
            return
        except requests.exceptions.RequestException as e:
            return

        if res.status_code == 200:
            hits = Counter()
            body = BeautifulSoup(res.text, 'html.parser')
            link_area = body.find("div", { "id" : "search" })
            results_area = body.find("div", { "id" : "resultStats"})
            hit = self.parse_number(results_area.text)
            if i > 0:
                hits[keywords[i-1]] = hit
            self.find_links(link_area, links, cap)
        return hits

    def push_to_pages(self, args):
        args = args[0]
        pages = args[0]
        page_lock = args[1]
        link = args[2]
        timeout = args[3]
        try:
            res = requests.get(link, timeout)
        except requests.exceptions.Timeout:
            return
        except requests.exceptions.RequestException as e:
            return

        if res.status_code == 200:
            page = BeautifulSoup(res.text, "html.parser")
            page_lock.acquire()
            pages.append(page)
            page_lock.release()

# query("Which of the following is a citrus fruit", [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")], 10)


