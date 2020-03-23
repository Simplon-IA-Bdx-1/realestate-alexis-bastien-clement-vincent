import scrapy
import shadow_useragent
import pandas as pd
import csv
import os
import re
import time

from bs4 import BeautifulSoup
from os import path

class LogicImmoScraping(scrapy.Spider):

    """ Scraper logic-immo.com """

    offers_scrap_nb = 0
    offers_already_listed = 0

    name = 'logic-immo'
    name_csv = "logic_immo.csv"
    

    # Define User Agent
    ua = shadow_useragent.ShadowUserAgent()
    my_user_agent = ua.percent(0.03) 
    headers = {
    'User-Agent': '{}'.format(my_user_agent)
    }
    custom_settings={
        'FEED_URI': "logic_immo.csv",
        'FEED_FORMAT': 'csv'
    }

    fieldnames = ['id','area','rooms','district','price']

    if path.isfile(name_csv):
        mode = 'a'
        csv_file = open(name_csv,mode,newline='')
        writer = csv.DictWriter(csv_file, fieldnames)
    else:
        mode = 'w'
        csv_file = open(name_csv,mode,newline='')
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()

    def start_requests(self):

        url = "https://www.logic-immo.com/appartement-paris/vente-appartement-paris-75-100_1.html"
        yield scrapy.http.Request(url, headers=self.headers)

    def parse(self, response):

        list_urls = []

        # retrieving number of the last page 
        total_pages = response.xpath('//div[@class="numbers"]')
        last_page_nb = total_pages.xpath('.//a[last()]/text()').get()

        # add url of the first page
        list_urls.append('https://www.logic-immo.com/appartement-paris/vente-appartement-paris-75-100_1.html')

        # add url of each page from page 2 to the latest
        for i in range (2,int(last_page_nb)):
            list_urls.append(f'https://www.logic-immo.com/appartement-paris/vente-appartement-paris-75-100_1-{i}.html')
        
        for url in list_urls:
            yield response.follow(url, callback=self.parse_page, headers=self.headers, dont_filter=True)

    def parse_page(self,response):

        id_offers_list = []
        format_prices = []
        districts = []

        links_offers = response.xpath('//div[starts-with(@id,"header-offer")]/@id').extract()
        offers_prices = response.xpath('//p[@class="offer-price"]/span/text()').extract()
        areas = response.xpath('//span[@class="offer-area-number"]/text()').extract()
        rooms = response.xpath('//span[@class="offer-details-caracteristik--rooms"]/span["offer-rooms-number"]/text()').extract()
        bedrooms = response.xpath('//span[@class="offer-details-caracteristik--bedrooms"]/span["offer-rooms-number"]/text()').extract()
        postal_codes = response.xpath('//div[@class="offer-details-location"]')

        for link_offer in links_offers:
            id_offer = link_offer.replace('header-offer-','')
            id_offers_list.append(id_offer)

        for price in offers_prices:
            format_prices.append(price.replace('€','').replace(' ',''))

        for postal_code_str in postal_codes:
            soup = BeautifulSoup(postal_code_str.get(),'html.parser')
            text = soup.get_text().replace('\n',' ')
            postal_code = re.findall('[0-9]{5}', text)
            # keep 2 last numbers to get district
            districts.append(postal_code[0][-2:])

        for id_offer,area,nb_rooms,district,price in zip(id_offers_list,areas,rooms,districts,format_prices):
            scraped_info = {
                'id' : id_offer,
                'area': int(area),
                'rooms': int(nb_rooms),
                'district': district,
                'price': int(price)
            }
            
            # Create a new csv
            if self.mode == 'w':
                self.writer.writerow(scraped_info)
                self.offers_scrap_nb += 1 
            else:
                # Open csv with scraped data
                df = pd.read_csv(self.name_csv)
                # Check if offer is already listed in our dataset
                if any(df['id'] == scraped_info['id']):
                    self.offers_already_listed += 1
                else:
                    self.writer.writerow(scraped_info)
                    self.offers_scrap_nb += 1

    def closed(self,response):

        interval = time.time() - self.start_scrap_time

        print("End of Scraping")
        print(f"{self.offers_scrap_nb} offers added")
        print(f"{self.offers_already_listed} offers already listed in .csv")
        print(f'Elapsed time for scraping : {round(interval,2)} seconds')

