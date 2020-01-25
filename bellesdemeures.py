# -*- coding: utf-8 -*-
"""
Script to retrieve data from the site bellesdemeures.com
"""
import requests
from bs4 import BeautifulSoup
import os
import re
import shadow_useragent
import unicodecsv as csv
import time
import random
import datetime
import numpy as np

# Define User Agent
ua = shadow_useragent.ShadowUserAgent()
# my_user_agent = ua.android
my_user_agent = ua.percent(0.03) 

headers = {
'User-Agent': '{}'.format(my_user_agent)
}  

class BellesDemeures(object):

    """
    Create an object soup by getting url of a page and it number 
    """

    def get_data_by_page(self,nb_page):

        # Bordeaux
        # url = f'https://www.bellesdemeures.com/recherche?ci=330063&idtt=2&tri=Selection&page={nb_page}
        # Gironde 
        # url = f'https://www.bellesdemeures.com/recherche?cp=33&idtt=2&tri=Selection&page={nb_page}'

        # Paris
        url = f'https://www.bellesdemeures.com/recherche?cp=75&idtt=2&tri=Selection&page={nb_page}'
        html = requests.get(url, headers=headers)
        self.soup = BeautifulSoup(html.content, 'html.parser')
    
    def scrap_pages(self,nbpage_start,nb_pages):

        nb_annonces = 0
        time_total = 0
        list_datas = []
        x = [i for i in range(nbpage_start, nbpage_start+nb_pages)]

        print(f"_________________________________________")
        print(f"####### SCRAPPING IMMO ###########")

        for nb_page in x :
            start_time = time.time()
            time.sleep(random.randrange(1,3))
            self.get_data_by_page(nb_page)
            j , datas = self.scrap_annonces()
            nb_annonces = nb_annonces + j
            list_datas.append(datas)
            time_total += time.time()-start_time
            print(f"Page {nb_page} / Temps d'execution {round(time.time()-start_time,2)} secondes pour {j} annonces")
            # self.pause_scrapper(nb_page,20)
        print(f"_________________________________________")
        print(f"Total annonces : {nb_annonces} annonces ")
        time_total_format = time.strftime("%H:%M:%S", time.gmtime(time_total))
        print(f"Temps total : {time_total_format}")

        # Verify if immos_paris_date.csv exists and choose wb or ab 
        if os.path.exists(f'immos_paris_{datetime.date.today()}.csv'):
            self.write_csv('ab',list_datas)
        else:
            self.write_csv('wb',list_datas)


    def write_csv(self,mode,list_datas):

        """ Write to a csv file """

        ### "wb" create a file and write into it / "ab" add data to an existing file
        ### list_datas = data to write in the csv file

        with open(f"immos_paris_{datetime.date.today()}.csv", mode) as csvfile:        
            fieldnames = ['typeof','surface','field_surface','rooms','bedrooms','terrace','balcony','pool','parking','district','nb_of_ad','agency','link','price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if mode == 'wb':
                writer.writeheader()
            for datas in list_datas:
                for row in datas:
                    writer.writerow(row)


    def search_nb_spec(self,specs,spec):

        """
        Searches for an occurrence in the moreinfos_split table and retrieves the associated number (eg 2, for 2 parking lots)
        NA when not indicated as for the land (may not be land as for the apartments) or land not large enough to be highlighted in the annonce
        field_surface , bedrooms , balcony , parking 
        """

        nbspec = "NA"

        for info in specs :
            # Search for the spec in the split data
            x = re.search(spec,info.strip())
            if(x):
                nbspec_list = re.findall("[0-9]+",info.strip())
                nbspec = nbspec_list[0]
        return nbspec


    def search_spec(self,specs,spec):

        # It does not say "1 Pool" but "Pool" when there is a pool
        # pool , terrace

        spec_exist = "NON"

        for info in specs :
            # search for spec in splitted infos
            x = re.search(spec,info.strip())
            if(x): 
                spec_exist = "OUI"
        return spec_exist
    
    def search_nb_ad(self,link):
        """
        takes an url and returns the ad number
        """
        link_split = link.split('/')
        for i in link_split:
                x = re.search('^[0-9]+$',i)
                if(x):
                    nb_of_ad = i
        return nb_of_ad

    def scrap_annonces(self):
        # debug 
        # stop_scrap = 1

        j = 0
        properties_list = []
        listAnnonces = self.soup.find('section', {'class': 'annonces'})

        # Scrap for each annonce
        for annonce in listAnnonces.find_all('div', {'class': 'detailsWrap'}):

            # # scrap only one advertisement for debug
            # if stop_scrap > 1:
            #     break

            #We check that the city is indeed Paris, if it is the case we recover the number of district, 
            #if not we pass to the next advertisement.

            localisation = annonce.find('div', {'class': 'location'}).text
            x = re.search('Paris',localisation)
            if not x:
                continue
            district_list = re.findall("[0-9]+",localisation)
            district = int(district_list[0])

            # Link
            link = annonce.find('a')['href']
            nb_of_ad = self.search_nb_ad(link)
 

            # Type
            typeof = annonce.find('div', {'class': 'type'}).text

            # Price
            price_str = annonce.find('div', {'class': 'price'}).text
            # Delete symbol "€"
            price = price_str.replace("€", "").strip()

            # Specs (Rooms, Surface)
            specs = annonce.find('div', {'class': 'specs'}).text

            # Some annonces don't have the same classic format rooms - surface... 
            # We can have only the number of rooms or only the surface , or sometimes none of them
            # Even if we dont have values for rooms and surface, the div class="specs" is in the code 
            if len(specs.strip()) == 0:
                rooms = "NA"
                surface = "NA"
            else:
                specs_split = specs.split("•")
                rooms = self.search_nb_spec(specs_split,"Pièces")
                surface = self.search_nb_spec(specs_split,"m²")

            # Agency
            agency = annonce.find('div', {'class': 'agency'}).text.strip()
            
            # More (Field Surface, Bedrooms, Balcony, Parking)
            moreinfos = annonce.find('div', {'class': 'more'})

            # Some annonces don't have div moreinfos
            # If moreinfo doesn't exists, we complete infos by NA or NON depending on the format
            if (moreinfos):
                moreinfos = annonce.find('div', {'class': 'more'}).text

                # Split moreinfos
                moreinfos_split = moreinfos.split("\n")

                field_surface = self.search_nb_spec(moreinfos_split,"Terrain")
                bedrooms = self.search_nb_spec(moreinfos_split,"chambre")
                balcony = self.search_nb_spec(moreinfos_split,"Balcon")
                parking = self.search_nb_spec(moreinfos_split,"parking")
                pool = self.search_spec(moreinfos_split,"Piscine")
                terrace = self.search_spec(moreinfos_split,"Terrasse")

            else:
                field_surface = "NA"
                bedrooms = "NA"
                balcony = "NA"
                parking = "NA"
                pool = "NON"
                terrace = "NON"

            data = {'typeof' : typeof,
                    'surface' : surface,
                    'field_surface' : field_surface,
                    'rooms' : rooms,
                    'bedrooms' : bedrooms,
                    'terrace' : terrace,
                    'balcony' : balcony,
                    'pool' : pool,
                    'parking' : parking,
                    'district' : district,
                    'nb_of_ad' : nb_of_ad,
                    'agency' : agency,
                    'link' : link,
                    'price' : price}

            properties_list.append(data)
            j += 1
            
            ### DEBUG ###
            # print(f"Type de bien : {typeof}")
            # print(f"Prix : {price}")
            # print(f"Surface du bien : {surface}")
            # print(f"Surface du terrain : {field_surface}")
            # print(f"Nombre de piéces : {rooms}")
            # print(f"Nombre de chambres :  {bedrooms}")
            # print(f"Terrasse : {terrace}")
            # print(f"Balcon : {balcony}")
            # print(f"Piscine : {pool}")
            # print(f"Parking : {parking}")
            # print(f"Arrondissement: {district}")
            # print(f"Numéro annonce : {nb_of_ad}")
            # print(f"Agence : {agency}")
            # print(f"Lien : {link}")
            # print(f"_________________________________________")

            # stop_scrap += 1 

        return j,properties_list


    def pause_scrapper(self,nb_page,duration):

        """
        Stop the scrapper every 5 pages and take a break of x seconds
        """

        if nb_page % 5 == 0 :
            print(f"*** Pause de {duration} secondes ***")
            time.sleep(duration)
            

bd = BellesDemeures()

"""
Scraping of one or many pages, starting to one given page and write data to a csv file
"""
# 138 pages

bd.scrap_pages(1,25)
# bd.scrap_pages(26,25)
# bd.scrap_pages(51,25)
# bd.scrap_pages(76,25)
# bd.scrap_pages(101,25)
# bd.scrap_pages(126,13)
