#!/usr/bin/python3
import sys
import json
import time
import urllib
import random
import requests
import threading
from bs4 import BeautifulSoup


class SeriesScrape:
	def __init__(self, title: str):
		self.title = title
		self.session = requests.session()
		self.episode_links_dict = {}
		self.headers = {
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}

	def parse_episodes(self, base_episode_url: str, episode_title: str):
		table_soup = BeautifulSoup(requests.request('GET', base_episode_url, headers=self.headers).content, "html5lib")
		url_js = table_soup.findAll('a',{'class':'btn btn-danger btn-sm'})
		episode_links = []
		for url in url_js:
			if 'https' in url["onclick"]:
				episode_links.append('https'+url["onclick"].split("https")[1].split("'")[0])
			else:
				episode_links.append('http'+url["onclick"].split("http")[1].split("'")[0])
		self.episode_links_dict[episode_title] = episode_links

	def search(self, download: bool=True):
		search_response = self.session.post('http://dwatchseries.to/show/search-shows-json', data={'term': self.title}, headers=self.headers)
		if len(search_response.json())>2 or len(search_response.json())==1:
			print('Multiple or No matches found! Exiting...')
			sys.exit(0)
		for match in search_response.json():
			if match['target_url'] != '_blank':
				series_path = urllib.parse.quote_plus(match['seo_url'])
		series_response = self.session.get(f'http://dwatchseries.to/serie/{series_path}', headers=self.headers)
		assert series_response.status_code == 200, "Error Message: Series page did not return 200"

		soup = BeautifulSoup(series_response.content, "html5lib")
		for episode in soup.findAll('li', {'itemprop':'episode'}):
			episode_id = episode["id"]
			# Non-breaking space characters in episode title
			episode_title = episode.findAll('span', {'itemprop':'name'})[0].text.replace('\u00a0',' ')
			base_episode_url = episode.findAll('a')[0]['href']
			episode_thread = threading.Thread(target=self.parse_episodes, args=(base_episode_url, episode_title,))
			episode_thread.start()
			episode_thread.join()
		print(json.dumps(self.episode_links_dict, indent=4))

SeriesScrape('show title here').search()
