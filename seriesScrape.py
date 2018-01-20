#!/usr/bin/python3
import os
import sys
import json
import time
import shutil
import urllib
import random
import requests
import threading
from bs4 import BeautifulSoup
from selenium import webdriver


# "Nice" hosts
# speedvid ('video',{'class':'jw-video jw-reset'})['src']
# vidlox ('content',{'class':'row'}) -> script var player src
# daclips ('video',{'id':'flvvideo_html5_api'})['src']
# vidoza ('video',{'class':'jw-video jw-reset'})['src']
# youwatch ('video',{'class':'jw-video jw-reset'})['src']
nice_hosts = ['speedvid', 'vidoza', 'youwatch']

class SeriesScrape:
	def __init__(self, title: str):
		self.driver = None
		self.title = title
		self.session = requests.session()
		self.episode_links_dict = {}
		self.headers = {
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}

	def start_driver(self):
		profile = webdriver.ChromeOptions()
		profile.add_experimental_option('prefs', {"download.default_directory": "NUL", "download.prompt_for_download": False, })
		self.driver = webdriver.Chrome(f'{os.getcwd()}/chromedriver', chrome_options=profile) # chromedriver bin must be in folder of invocation
		self.driver.set_page_load_timeout(10)

	def parse_episodes(self, base_episode_url: str, episode_title: str):
		print(f'Parsing/building host urls dict for {episode_title}...')
		table_soup = BeautifulSoup(requests.request('GET', base_episode_url, headers=self.headers).content, "html5lib")
		url_js = table_soup.findAll('a',{'class':'btn btn-danger btn-sm'})
		episode_links = []
		for url in url_js:
			if 'https' in url["onclick"]:
				episode_links.append('https'+url["onclick"].split("https")[1].split("'")[0])
			else:
				episode_links.append('http'+url["onclick"].split("http")[1].split("'")[0])
		self.episode_links_dict[episode_title] = episode_links

	def download_episode(self, e_url: str='', e_title: str=''):
		if self.episode_links_dict == {}:
			self.search()

		if self.driver is None:
			self.start_driver()
		try:
			self.driver.get(e_url)
		except:
			self.driver.refresh()
		soup = BeautifulSoup(self.driver.page_source, "html5lib")
		if 'speedvid' in e_url or 'vidoza' in e_url or 'youwatch' in e_url:
			host_url = soup.findAll('video',{'class':'jw-video jw-reset'})[0]['src']
		print(f'{e_title} {host_url} from {e_url}')

	def teardown(self):
		self.driver.quit()
		shutil.rmtree('NUL')

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
		print('')
		for e in self.episode_links_dict:
			rand_e_url = random.choice(self.episode_links_dict[e])
			while rand_e_url.split('//')[1].split('.')[0] not in nice_hosts:
				rand_e_url = random.choice(self.episode_links_dict[e])
			d_thread = threading.Thread(target=self.download_episode, args=(rand_e_url, e,))
			d_thread.start()
			d_thread.join()
		self.teardown()

print(f'Usable hosts: {nice_hosts}\n')
SeriesScrape('show title here').search()
