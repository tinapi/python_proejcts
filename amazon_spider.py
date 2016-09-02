# -*- coding: utf-8 -*-
import requests
from lxml import html
from mysql.connector import MySQLConnection, Error
import re
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

## Author: Tina Pi
## Date: 09/02/2016

config={
	'user': 'root',
	'password':'xxxxx',
	'host':'xxxx',
	'database':'xxx',
	'charset': 'utf8',
	'raise_on_warnings': True,
}

def save(product):
	try:
		cnx=MySQLConnection(**config)
		cursor = cnx.cursor()
		query="insert into product(title, price, rate, brand, reviewCount) values (%s, %s, %s, %s, %s)"
		cursor.execute(query, (product['title'], product['price'], product['rate'], product['brand'], product['reviewCount']))
		cnx.commit()
	except Error as error:
		print error
	finally:
		cursor.close()
		cnx.close()

def get_page(i):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	url = "https://www.amazon.cn/s/ref=sr_pg_3?fst=as%3Aoff&rh=n%3A746776051%2Cp_6%3AA2EDK7H33M5FFG%2Cp_n_special_merchandising_browse-bin%3A1414288071&page={}&bbn=&ie=UTF8&qid=".format(i)
	page = requests.get(url, headers=headers)

	doc = html.fromstring(page.content)

	product = doc.xpath('//div[@class="s-item-container"]')

	f = open('amazon_popular_export_products.txt', 'a')
	for p in product:
		price = p.xpath('.//span[@class="a-size-base a-color-price s-price a-text-bold"]/text()')
		name = p.xpath('.//h2[@class="a-size-base a-color-null s-inline  s-access-title  a-text-normal"]/text()')
		brand = p.xpath('.//span[position()=2]/text()')
		reviewCount = p.xpath('.//a[@class="a-size-small a-link-normal a-text-normal"]/text()')
		rate = p.xpath('.//span[@class="a-icon-alt"]/text()')

		# rate might be empty
		if len(rate) == 0:
			rate = ['0']
		if len(brand) == 0:
			brand = ['null']
		if len(reviewCount) == 0:
			reviewCount = ['0']

		try:
			product={
				'title': name[0].encode('utf-8'),
				'price': float(re.sub("[^0-9.]","",price[0].encode('utf-8'))),
				'rate': float(re.sub("[^0-9.]","",rate[0].encode('utf-8'))),
				'brand': brand[0].encode('utf-8'),
				'reviewCount': int(re.sub("[^0-9]","",reviewCount[0].encode('utf-8'))),
			}

			save(product)
		except ValueError as error:
			print "Error when converting values on page {} for product {}".format(i, product['title'])
			continue

		f.write(str(product['price']) + "\t" + product['title'] + "\t" + str(product['rate']) + "\t" + product['brand'] + "\t" + str(product['reviewCount']) +"\n")
		
	f.close()

def read_data():
	try:
		cnx=MySQLConnection(**config)
		cursor = cnx.cursor()
		query="select title, rate, reviewCount from product order by reviewCount desc, rate desc limit 3"
		cursor.execute(query)
		
		data={}
		for title, rate, reviewCount in cursor:
			data[title] = (rate, reviewCount)

		return data
	except Error as error:
		print error
	finally:
		cursor.close()
		cnx.close()

def plot_view():
	data = read_data()

	rates = [int(i[0]) for i in data.values()]
	reviews = [int(i[1]) for i in data.values()]

	fig, ax = plt.subplots()
	index = np.arange(len(data.keys()))
	bar_width = 0.35	# each bar is 0.35 wide
	opacity = 0.4
	error_config = {'ecolor': '0.3'}
	font=FontProperties('SimHei')

	rects1 = plt.bar(index, rates, bar_width, alpha=opacity, color='b', error_kw=error_config, label='Rate')
	rects2 = plt.bar(index+bar_width, reviews, bar_width, alpha=opacity, color='r', error_kw=error_config, label="Reviews")

	# display data value on each bar
	for i, r in enumerate(rates):
		plt.text(i+0.17, r+3, r, color='green', fontweight='bold')
	for i, v in enumerate(reviews):
		plt.text(i+bar_width+0.17, v+3, v, color="green", fontweight='bold')

	plt.xlabel("Product")
	plt.ylabel("rate&reviews")
	plt.title("most popular product")
	plt.xticks(index+bar_width, data.keys(), fontproperties=font)
	plt.legend()

	plt.tight_layout()
	plt.show()
		
def main():
	# fetch data from website
	for i in range(400):
	 	get_page(i)

	# view plot using matplotlib
	plot_view()

if __name__ == "__main__":
  main()



