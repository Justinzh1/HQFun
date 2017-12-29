# Dependencies 
import requests
import json
import re
from collections import Counter
from bs4 import BeautifulSoup
import sys

# Debugging
import pdb
import time

# Link regex
is_link = re.compile("http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

class GSearch:

	def normalize(self, counter):
		normalized = {}
		n = 0
		for k,v in counter.items():
			n += v
		max_value, max_option = 0, None
		for k,v in counter.items():
			update = round((v + 1)/(float(n) + 1),4)
			if update > max_value:
				max_value, max_option = round, k
			normalized[k] = update
		return normalized, max_option

	def get_top_links(self, question, keywords):
		url = "https://www.google.com/search?q="
		searchables = []
		base_question = ''.join([url,question])	
		searchables.append(base_question)
		for key in keywords:
			searchables.append(''.join([base_question,' ',key]))
		return searchables

	def create_soup(self, urls, question, keywords, links, cap):
		for url in urls:
			res = requests.get(url)
			if res.status_code == 200:
				body = BeautifulSoup(res.text, 'html.parser')
				link_area = body.find("div", { "id" : "search" })
				self.find_links(link_area, links, cap)

	def filter_links(self, url):
		return is_link.match(url) is not None and 'google' not in url and 'youtube' not in url and 'pdf' not in url

	def find_links(self, soup, links, cap):
		for i,link in enumerate(soup.find_all('a')):
			if i > cap:
				return
			url = link.get('href').split('=')[1].split('&')[0]
			if self.filter_links(url.lower()):
				links.add(url)

	def query(self, question, keywords, cap=10):
		print("Beginning search")
		keywords = [k.lower()for k in keywords]
		keyword_count = Counter()
		for key in keywords:
			keyword_count[key] = 0
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
				i += 1
				continue
			if i % 3 == 0:
				normalized, best = self.normalize(keyword_count)
				print(best.upper(), normalized)
			i += 1

	def keyword_query(self, link, keywords, keyword_count):

		try:
			res = requests.get(link)
		except requests.exceptions.Timeout:
			res = None
		except requests.exceptions.RequestException as e:
			sys.exit(1)

		if res and res.status_code == 200:
			page = BeautifulSoup(res.text, 'html.parser')
			self.scan_body(page, keywords, keyword_count)
			return 200


	def scan_body(self, page, keywords, keyword_count):
		page_counter = Counter(page.text.split(' '))
		n = len(page_counter.keys())
		for key in keywords:
			keyword_count[key] += page_counter[key]

# query("Which of the following is a citrus fruit", [unicode("Watermelon","utf-8"), unicode("Potato","utf-8"),unicode("Orange","utf-8")], 10)


