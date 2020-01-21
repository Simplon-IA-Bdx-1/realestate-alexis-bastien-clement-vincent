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

ua = shadow_useragent.ShadowUserAgent()
# my_user_agent = ua.android
my_user_agent = ua.percent(0.03) 

headers = {
'User-Agent': '{}'.format(my_user_agent)
}  

class BellesDemeures(object):

    ### Crée un objet soup à partir de l'url d'une page et son numéro de page 
    ### Marche pour une unique page 

    def getDatas_bypage(self,nb_page):

        # Bordeaux
        # url = f'https://www.bellesdemeures.com/recherche?ci=330063&idtt=2&tri=Selection&page={nb_page}'
        # Gironde 
        url = f'https://www.bellesdemeures.com/recherche?cp=33&idtt=2&tri=Selection&page={nb_page}'
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
            self.getDatas_bypage(nb_page)
            j , datas = self.scrap_annonces()
            nb_annonces = nb_annonces + j
            list_datas.append(datas)
            time_total += time.time()-start_time
            print(f"Page {nb_page} / Temps d'execution {round(time.time()-start_time,2)} secondes pour {j} annonces")
            # self.pause_scrapper(nb_page,20)
        print(f"_________________________________________")
        print(f"Total annonces : {nb_annonces} annonces ")
        print(f"Temps total : {round((time_total/60),2)} minutes")

        #### Verifier qu'il existe ou non un fichier immos_gir_date.csv et en fonction de ca on choisit soit wb , soit ab 
        if os.path.exists(f'immos_gir_{datetime.date.today()}.csv'):
            self.write_csv('ab',list_datas)
        else:
            self.write_csv('wb',list_datas)


    ### Ecriture dans un fichier .csv
    ### Mode wb crée un fichier et ecrit dedans , ab ajoute a un fichier existant
    ### list_datas , donnés a inscrire dans le csv
  
    def write_csv(self,mode,list_datas):
        with open(f"immos_gir_{datetime.date.today()}.csv", mode) as csvfile:
            fieldnames = ['typeof','price','surface','field_surface','rooms','bedrooms','terrace','balcony','pool','parking','localisation','agency','link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if mode == 'wb':
                writer.writeheader()
            for datas in list_datas:
                for row in datas:
                    writer.writerow(row)


    # Fonction qui cherche une occurence dans le tableau moreinfos_split et récupere le nombre associé ( ex 2 , pour 2 parkings)
    # NA quand non renseigné comme  pour le terrain ( peut etre pas de terrain comme pour les apparts ) ou terrain pas assez grand pour etre mis en avant dans l'annonce
    # field_surface , bedrooms , balcony , parking 

    def search_nb_spec(self,specs,spec):
        nbspec = "NA"
        for info in specs :
            x = re.search(spec,info.strip())
            if(x): # cherche la spec dans les infos splités
                nbspec_str = re.findall("[0-9]+",info.strip())
                nbspec = nbspec_str[0]
        return nbspec

    # il n'est pas indiqué " 1 Piscine " mais "Piscine" quand il y'a une piscine 
    # pool , terrace
    def search_spec(self,specs,spec):
        spec_exist = "NON"
        for info in specs :
            x = re.search(spec,info.strip())
            if(x): # cherche la spec dans les infos splités
                spec_exist = "OUI"
        return spec_exist

    def scrap_annonces(self):

        j = 0
        properties_list = []

        listAnnonces = self.soup.find('section', {'class': 'annonces'})

        for annonce in listAnnonces.find_all('div', {'class': 'detailsWrap'}):
            link = annonce.find('a')['href']
            typeof = annonce.find('div', {'class': 'type'}).text

            # On supprime le symbole " € " du prix 
            price_str = annonce.find('div', {'class': 'price'}).text
            price = price_str.replace("€", "").strip()

            ### Certaines annonces ne sont pas sous le format classique Pieces - Surface , il n'y a que le nombre de Pieces ou que la Surface , ou meme parfois rien
            ### Cependant meme quand c'est vide la div class specs est présente 

            specs = annonce.find('div', {'class': 'specs'}).text

            if len(specs.strip()) == 0:
                rooms = "NA"
                surface = "NA"
            else:
                specs_split = specs.split("•")
                rooms = self.search_nb_spec(specs_split,"Pièces")
                surface = self.search_nb_spec(specs_split,"m²")

            ##############

            localisation = annonce.find('div', {'class': 'location'}).text
            agency = annonce.find('div', {'class': 'agency'}).text.strip()

            # Certaines annonces n'ont pas de div more avec des infos supplémentaires
            # Dans le cas ou le bloc n'existe pas on passe toutes les infos contenues habituellement en NA ou NON suivant le format 
            
            moreinfos = annonce.find('div', {'class': 'more'})
            if (moreinfos):
                moreinfos = annonce.find('div', {'class': 'more'}).text

                # Split du bloc moreinfos
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
                    'price' : price,
                    'surface' : surface,
                    'field_surface' : field_surface,
                    'rooms' : rooms,
                    'bedrooms' : bedrooms,
                    'terrace' : terrace,
                    'balcony' : balcony,
                    'pool' : pool,
                    'parking' : parking,
                    'localisation' : localisation,
                    'agency' : agency,
                    'link' : link}
            properties_list.append(data)
            j += 1
            
            ## DEBUG
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
            # print(f"Localisation : {localisation}")
            # print(f"Agence : {agency}")
            # print(f"Lien : {link}")
            # print(f"_________________________________________")


        return j,properties_list


    ## Fonction pour arreter le scrapper toutes les 5 pages et faire une pause de x secondes
    def pause_scrapper(self,nb_page,duration):
        if nb_page % 5 == 0 :
            print(f"*** Pause de {duration} secondes ***")
            time.sleep(duration)
            
     

bd = BellesDemeures()
### Scrappe de une ou plusieurs pages en partant d'une page donnée et ecriture dans un .csv
# bd.scrap_pages(1,25)
# bd.scrap_pages(26,25)
# bd.scrap_pages(51,25)
bd.scrap_pages(76,2)