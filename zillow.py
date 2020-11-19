# ref - https://github.com/scrapehero/zillow_real_estate
# usage - python3 zillow.py https://www.zillow.com/homedetails/<listing_params>

from lxml import html
import requests
import unicodecsv as csv
import argparse
import browsercookie
import pyperclip
import time
import re
import webbrowser

cj = browsercookie.chrome()

def get_html(url):
	headers= {
		'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'accept-encoding':'gzip, deflate, sdch, br',
		'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
		'cache-control':'max-age=0',
		'upgrade-insecure-requests':'1',
		'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	}
	response = requests.get(url,headers=headers,cookies=cj)
	document = html.fromstring(response.text)
	return document

def generate_map_from_list(text_list):
	text_map = {}
	i = 0
	while i < len(text_list):
		colon_pos = text_list[i].find(':')
		if colon_pos < 0:
			i += 1
			continue

		if text_list[i][:colon_pos] in text_map:
			print("Overwritten attribute ", text_list[i][:colon_pos])
		text_map[text_list[i][:colon_pos]] = text_list[i + 1]
		i += 2
	return text_map

def get_listing_output(url):
	print(url)
	document = get_html(url)
	if url.find('www.zillow.com/community') >= 0:
		print("community listing not supported. skip")
		return

	# summary section
	summary = document.xpath("//div[@class='ds-home-details-chip']")[0]
	price = ''.join(summary.xpath(".//div[@class='ds-summary-row']//span//text()")[:1])
	if not price:
		price = ''.join(summary.xpath(".//span[contains(@class, 'ds-status-details')]//text()")[0:3])

	area = summary.xpath(".//span[@class='ds-bed-bath-living-area']//text()")[6]
	bds = summary.xpath(".//span[@class='ds-bed-bath-living-area']//text()")[0]
	bas = summary.xpath(".//span[@class='ds-bed-bath-living-area']//text()")[3]

	address_list = summary.xpath("//div[@class='ds-price-change-address-row']//h1//span//text()")[0:3];
	address = ''.join(address_list)
	city_state_zip = address_list[2]
	city = city_state_zip[:city_state_zip.find(',')]
	zipcode = city_state_zip[city_state_zip.find(',')+5:]

	# facts and feature section
	facts_and_features = document.xpath("//div[contains(@class, 'ds-home-facts-and-features')]")[0]
	facts_list = facts_and_features.xpath("./div/div[1]//text()")
	facts_map = generate_map_from_list(facts_list)

	details_list = facts_and_features.xpath("./div/div[2]//text()")
	details_map = generate_map_from_list(details_list)

	# school score section
	school_list = document.xpath("//ul[@class='ds-nearby-schools-list']")[0]
	if len(school_list.xpath(".//li")) < 3:
		print("school score incomplete. skip")
		return

	school_score_format = './li[{num}]//span[1]//text()'
	school_name_format = './li[{num}]//a//text()'
	schools = []
	for i in [1, 2, 3]:
		schools.append({
			'score': school_list.xpath(school_score_format.format(num=i))[0],
			'name': school_list.xpath(school_name_format.format(num=i))[0],
		})

	# filter listing by certain criteria
	if (int(re.sub(r'\D', '', price)) > 800000 or int(schools[0].get('score')) < 7):
		print("criteria not met. skip")
		return

	# output
	na = 'n/a'
	output_params = {
		'url': url,
		'address': address,
		'city': city,
		'zipcode': zipcode,
		'price': price,
		'hoa': facts_map.get('HOA', na),
		'area': area,
		'bedrooms': bds,
		'bathrooms': bas,
		'year_built': facts_map.get('Year built', na),
		'elementary_school': schools[0]['score'],
		'middle_school': schools[1]['score'],
		'high_school': schools[2]['score'],
		'parking': facts_map.get('Parking', na),
		'tax': details_map.get('Annual tax amount', na),
		'lot': facts_map.get('Lot', na),
		'facts_map': facts_map,
		'details_map': details_map,
		'schools': schools,
	}
	output_format = '\t'.join(map(lambda x: "{{{param}}}".format(param=x), [*output_params]))
	output_text = output_format.format(**output_params)
	return output_text

def get_listing_urls():
	with open("search_urls.txt", "r") as f:
		search_urls = f.readlines()

	listing_urls = []
	for search_url in search_urls:
		print(search_url)
		webbrowser.open_new_tab(search_url)
		time.sleep(5)
		document = get_html(search_url)
		listings = document.xpath("//div[@class='list-card-info']//a")
		listing_urls.extend([listing.get("href") for listing in listings])
		time.sleep(5)
	return set(listing_urls)

argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argparser.add_argument('url', nargs='?')
args = argparser.parse_args()

if args.url:
	output_text = get_listing_output(args.url)
	if output_text:
		print(output_text)
		pyperclip.copy(output_text)

else:
	listing_urls = get_listing_urls()
	print(listing_urls)
	
	f = open("results.txt", "a")
	for listing_url in listing_urls:
		listing_output = get_listing_output(listing_url)
		if listing_output:
			f.write(listing_output + "\n")
		time.sleep(5)
	f.close()