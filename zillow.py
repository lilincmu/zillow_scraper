# ref - https://github.com/scrapehero/zillow_real_estate
# usage - python3 zillow.py https://www.zillow.com/homedetails/<listing>

from lxml import html
import requests
import unicodecsv as csv
import argparse
import browsercookie

def generate_map_from_list(text_list):
	text_map = {}
	i = 0
	while i < len(text_list):
		if text_list[i].find(': ') < 0:
			i += 1
			continue

		text_map[text_list[i][:len(text_list[i]) - 2]] = text_list[i + 1]
		i += 2
	return text_map

argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argparser.add_argument('url')
args = argparser.parse_args()

cj = browsercookie.chrome()
headers= {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'accept-encoding':'gzip, deflate, sdch, br',
	'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
	'cache-control':'max-age=0',
	'upgrade-insecure-requests':'1',
	'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}
response = requests.get(args.url,headers=headers,cookies=cj)
document = html.fromstring(response.text)

facts_and_features = document.xpath("//div[contains(@class, 'ds-home-facts-and-features')]")[0]
facts_list = facts_and_features.xpath("./div/div[1]//ul")[0]
second_span_format = './li[{num}]//span[2]//text()'
house_type = facts_list.xpath(second_span_format.format(num=1))[0]
year_built = facts_list.xpath(second_span_format.format(num=2))[0]
heating = facts_list.xpath(second_span_format.format(num=3))[0]
cooling = facts_list.xpath(second_span_format.format(num=4))[0]
parking = facts_list.xpath(second_span_format.format(num=5))[0]
hoa_fee = facts_list.xpath(second_span_format.format(num=6))[0]
lot_size = facts_list.xpath(second_span_format.format(num=7))[0]

# print(house_type, year_built, heating, cooling, parking, hoa_fee, lot_size)

details = facts_and_features.xpath("./div/div[2]//text()")
# print(generate_map_from_list(details))


