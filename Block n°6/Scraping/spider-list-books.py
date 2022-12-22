import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import os
import logging
from scrapy.crawler import CrawlerProcess
import config

'''le but de ce Spider est de créer une liste de livres avec plusieurs paramètres :
theme_id
theme_name
book_id
book_url
book_nb_comms'''


def scrapping_runner(output_file, log_level = logging.INFO):
  logging.info(f"SCRAPING BEGIN")

  # on determine les paramètres du CrawlerProcess
  process = CrawlerProcess({
      "FEEDS":{rf"{output_file}" : { "format" : "jsonlines", "overwrite" : True }},
      'USER_AGENT' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
      'ROBOTSTXT_OBEY' : False,
      'AUTOTHROTTLE_ENABLED' : True,
      'AUTOTHROTTLE_START_DELAY' : 5,
      'AUTOTHROTTLE_MAX_DELAY' : 10,
      'DOWNLOAD_DELAY' : config.DOWNLOAD_DELAY,
      'CONCURRENT_REQUESTS' : 1,
      'CONCURRENT_REQUESTS_PER_DOMAIN' : 1,
      'LOG_LEVEL': log_level,
      'LOG_FORMAT':'%(asctime)s %(levelname)s: %(message)s',
      'REQUEST_FINGERPRINTER_IMPLEMENTATION':'2.7'
  })

  # lancement du CrawlerProcess
  process.crawl(BabelioSpider)
  process.start()

class BabelioSpider(scrapy.Spider):
    name = 'babelio-list-books'
    url_theme_ = 'https://www.babelio.com/livres-' # url de depart : on rajoute '/theme/numero-du-theme' à l'url pour arriver sur la page web contenant la liste de livre associé au thème recherché
    url_ = 'https://www.babelio.com'               # exemple : https://www.babelio.com/livres-/roman/1
 
    # fonction qui va recréer les urls pour le scraping
    def start_requests(self):
        for theme_name,theme_id in config.THEMES.items():
            end_url = f'/{theme_name}/{theme_id}'  # '/roman/1' car theme_name = 'roman' / theme_id = 1
            new_url = self.url_theme_ + end_url    # 'https://www.babelio.com/livres-' + '/roman/1' = 'https://www.babelio.com/livres-/roman/1'
            yield scrapy.Request(new_url, callback=self.parse_list_books, meta={'data' : {'theme_id': theme_id, 'theme_name': theme_name}}) # on retourne la nouvelle url avec comme meta : 'data' = theme_id, theme_name

    
    def parse_list_books(self, response):
        data = response.request.meta["data"]

        livres = response.xpath('//div[contains(@class, " list_livre")]') # on veut trouver <div class="list_livre_con"> qui est la div contenant tous les livres de la page(chaque vignette de cette div correspond à un livre)
                                                                          # //div[@class="list_livre_con"]/div[i] pour livre i (i allant de 1 à 100 par pages)      
        # on boucle sur toutes les vignettes 
        for livre in livres:
            url = livre.xpath('./a[1]/@href').get(default='') # url de la page du livre : on utilise la 2e balise <a> qui contient l'url de la page du livre sous forme href : //div[@class="list_livre_con"]/div[1]/a[1]/@href pour le livre 1
                                                              # <a href="/livres/Dolce-De-verre-et-de-cendre/1405958">  donne https://www.babelio.com/livres/Dolce-De-verre-et-de-cendre/1405958 
                                                              # on passe de l'url : "https://www.babelio.com/livres-/roman/1" à "https://www.babelio.com/livres/Dolce-De-verre-et-de-cendre/1405958"
            try:
                # on essai de recupérer le nombre de commentaires grace à la balise <h3 style="margin:5px 0 0 0"> qui contient la balise a[1]/strong ou est stocké le nombre de commentaires
                # // : sélectionne les nodes du document à partir du current node qui correspondent à la sélection, peu importe où ils se trouvent (car la balise <a[1]> n'est pas directement sous la balise <h3>)
                nb_comm = int(livre.xpath('./h3//a[1]/strong/text()').get(default='').strip())
            except:
                # sinon il n'y a pas de commentaires
                nb_comm = 0

            # on trouve bien 'livres/' dans l'url du livre à scraper (car il se peut que certains livres est une url éronée ou une mauvaise redirection) et que le nombre de commentaires est supérieur au 30 commentaires (NB_COMM_MIN = 30)
            if ('livres/' in url and nb_comm >= config.NB_COMM_MIN): 
                # on retourne l'identifiant du livre, son url et son nombre de commentaire
                yield {
                    'book_id': url.split('/')[-1], # identifiant du livre (est compris dans l'url mais est séparable à droite par '/', ex: https://www.babelio.com/livres/Da-Costa-La-doublure/1433127 (id = 1433127))
                    'book_url': self.url_ + url,   # url du livre comme decrit plus haut : concatenation entre l'url de base et l'url de la vignette du livre (ex: 'https://www.babelio.com' + 'livres/nom_du_livre/id_livre')
                    'book_nb_comm': nb_comm,       # nombre de commentaires
                    **data,
                }
        
        try:
            # après avoir scraper tous les livres de la page, on essai de passer à la page suivante : la balise <div id='id_pagination" class="pagination"> contient toutes les numéros des pages ainsi que le bouton page suivante
            # il suffit d'utiliser la balise <a href="/livres-/roman/1?page=i" class="fleche icon-next" onclick="Npage=Npage+1;get();return false;"> (avec i=numero de page) pour avoir le href de la page suivante
            next_page = response.xpath('//div[@id="id_pagination"]//a[@class="fleche icon-next"]').attrib["href"]
        except KeyError:
            # on ne peut plus continuer, il n'y a plus de pages donc on arrête le crawling (arrêt du spider)
            logging.info('No next page. Terminating crawling process.')
        else:
            # on continu de scraper de page en page, en recoltant les infos 'data' (theme_id, theme_name), 'book_id', 'book_url', 'book_nb_comm') jusqu'a arriver au KeyError qui stoppera le process
            yield response.follow(next_page, callback=self.parse_list_books,meta={"data" : {**data}})


if __name__ == "__main__":
    # on lance le scraping 
    scrapping_runner(config.LIST_BOOKS_FILE)
