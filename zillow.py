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
		colon_pos = text_list[i].find(':')
		if colon_pos < 0:
			i += 1
			continue

		if text_list[i][:colon_pos] in text_map:
			print("Overwritten attribute ", text_list[i][:colon_pos])
		text_map[text_list[i][:colon_pos]] = text_list[i + 1]
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

# summary section
summary = document.xpath("//div[@class='ds-summary-row']")[0]
price = summary.xpath(".//span[@class='ds-value']//text()")[0]
area = summary.xpath(".//span[@class='ds-bed-bath-living-area']//text()")[6]
# print(price, area)

# facts and feature section
facts_and_features = document.xpath("//div[contains(@class, 'ds-home-facts-and-features')]")[0]
facts_list = facts_and_features.xpath("./div/div[1]//text()")
# print(generate_map_from_list(facts_list))

details_section = facts_and_features.xpath("./div/div[2]//text()")
# print(generate_map_from_list(details_section))

# school score section
school_list = document.xpath("//ul[@class='ds-nearby-schools-list']")[0]
school_score_format = './li[{num}]//span[1]//text()'
school_name_format = './li[{num}]//a//text()'
schools = []
for i in [1, 2, 3]:
	schools.append({
		'score': school_list.xpath(school_score_format.format(num=i))[0],
		'name': school_list.xpath(school_name_format.format(num=i))[0],
	})
# print(schools)

