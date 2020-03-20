import scrapy
import shadow_useragent
import re
from bs4 import BeautifulSoup
import os
from os import path

class LogicImmoScraping(scrapy.Spider):

    name = 'logic-immo'

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

    offers_scrap_nb = 0

    if path.isfile('logic_immo.csv'):
        os.remove("logic_immo.csv")
        print("previous version of the dataset deleted")


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
            
            self.offers_scrap_nb += 1
            yield scraped_info

    def closed(self,response):
        print("End of Scraping")
        print(f"{self.offers_scrap_nb} offers")

