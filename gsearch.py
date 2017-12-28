import requests
import json

def gen_urls(cxs, question):
	urls = []
	for cx in cxs:
		urls.append("https://www.googleapis.com/customsearch/v1?key=AIzaSyDClmhjpqg0QIaLymfPXIRUhqU-pU_RhDY&cx={}&q={}".format(cx,question))
	return urls

def keywords(cxs, question, keywords):
	count = {}
	for k in keywords:
		count[k.lower()] = 0

	urls = gen_urls(cxs, question)

	# n times
	for url in urls:
		res = requests.get(url)
		parsed_json = json.loads(res.text)
		# print(parsed_json)
		for site in parsed_json['items']:
			parse_site(site, count, url)

	print(question)
	print(count)
	return count

### Use restriction where keyword is included in query!

def parse_site(site, map, url):	
	if 'snippet' in site.keys():
		snippet = site['snippet']
		n = len(snippet)
		for i in snippet.split(' '):
			if i.lower() in map.keys():
				map[i.lower()] += 1

cxs = ["002520117602081589147:ddtyl9cubce", "008524428721710950532:nrwb0ttpsfi", "008524428721710950532:_dcanobvbuw"]
a = keywords(cxs, "Food with most Tryphtophan", ['Pumpkin Seeds', 'Turkey', 'Tuna'])
a = keywords(cxs, "Food with most Tryphtophan Pumpkin Seeds", ['Pumpkin Seeds', 'Turkey', 'Tuna'])
a = keywords(cxs, "Food with most Tryphtophan Turkey", ['Pumpkin Seeds', 'Turkey', 'Tuna'])
a = keywords(cxs, "Food with most Tryphtophan Tuna", ['Pumpkin Seeds', 'Turkey', 'Tuna'])