#!/usr/bin/python3
import sys
import json
import urllib
import requests
from bs4 import BeautifulSoup


class SeriesScrape:
	def __init__(self, title):
		self.title = title
		self.session = requests.session()
		self.headers = {
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}
	def search(self):
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
			print(f'Episode id: {episode["id"]}')
			print(episode.findAll('span', {'itemprop':'name'})[0].text)
			print(episode.findAll('a')[0]['href'])
			print('\n')

		# return list of available links?

SeriesScrape('show title here').search()