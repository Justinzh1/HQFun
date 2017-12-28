# Dependencies 
import requests
import json
import re
from collections import Counter
from bs4 import BeautifulSoup

# Debugging
import pdb
import time
from multiprocessing.dummy import Pool as ThreadPool 

# Link regex
is_link = re.compile("http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

def normalize(counter):
	normalized = {}
	n = 0
	for k,v in counter.items():
		n += v
	for k,v in counter.items():
		normalized[k] = round((v + 1)/(float(n) + 1),4)
	return normalized

def get_top_links(question, keywords):
	url = "https://www.google.com/search?q="
	searchables = []
	base_question = ''.join([url,question])	
	searchables.append(base_question)
	for key in keywords:
		searchables.append(''.join([base_question,' ',key]))
	return searchables

def create_soup(urls, question, keywords, links, cap):
	for url in urls:
		res = requests.get(url)
		if res.status_code == 200:
			body = BeautifulSoup(res.text, 'html.parser')
			link_area = body.find("div", { "id" : "search" })
			find_links(link_area, links, cap)

def filter_links(url):
	return is_link.match(url) is not None and 'google' not in url and 'youtube' not in url and 'pdf' not in url

def find_links(soup, links, cap):
	for i,link in enumerate(soup.find_all('a')):
		if i > cap:
			return
		url = link.get('href').split('=')[1].split('&')[0]
		if filter_links(url.lower()):
			links.add(url)

def query(question, keywords, cap=10):
	print("Beginning search")
	keywords = [k.lower()for k in keywords]
	keyword_count = Counter()
	for key in keywords:
		keyword_count[key] = 0
	urls = get_top_links(question, keywords)
	links = set()
	create_soup(urls, question, keywords, links, cap)
	print("{} Sources found.".format(len(links)))

	""" TODO: Bottleneck issues
			- Multi thread search the different URLS
			- Threshold to stop when one Pr[keyword] > c
			- If exceeds 15 seconds terminate (Must account for latency)
	"""
	ptime, i = 3, 0
	# now = time.time()
	for link in links: # Multi threading
		keyword_query(link, keywords, keyword_count)
		if i % 3 == 0:
			print(normalize(keyword_count))
		i += 1
	# print("Elapsed time: {}", time.time() - now)

def keyword_query(link, keywords, keyword_count):

	try:
		res = requests.get(link, timeout=1)
	except:
		res = None

	if res and res.status_code == 200:
		page= BeautifulSoup(res.text, 'html.parser')
		scan_body(page, keywords, keyword_count)


def scan_body(page, keywords, keyword_count):
	page_counter = Counter(page.text.split(' '))
	n = len(page_counter.keys())
	for key in keywords:
		keyword_count[key] += page_counter[key]

# query("Which of the following is a citrus fruit", [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")], 10)


