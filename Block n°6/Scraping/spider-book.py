import scrapy
from scrapy import signals
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import os
import logging
import pandas as pd
from scrapy.crawler import CrawlerProcess
import config

'''Ce spider permet de prendre en input la list-book-user avec quelques infos sur les livres et de sortir '''

def scrapping_book_runner(output_file, log_level = logging.INFO):
  logging.info(f"SCRAPING BEGIN")

  process = CrawlerProcess({
      "FEEDS":{rf"{output_file}" : { "format" : "jsonlines", "overwrite" : False }},
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

  process.crawl(BabelioBookSpider)
  process.start()

class BabelioBookSpider(scrapy.Spider):
    name = 'babelio-book'
    df_list_books = None
    
    # on charge la liste des livres obtenus dans le 1er spider : spider-list-book
    def load_list_books(self, input_file):
        return pd.read_json(input_file, lines=True)

    # on a crée un STATUS_FILE qui garde en mémoire les livres déja scraper (ce qui permet de ne pas tout faire en une fois et de ne pas scraper un même livre une seconde fois)

    # va mettre à jour le STATUS_FILE en rajoutant chaque 'book_id' du livre qu'on va scraper
    def update_status_file(self, book_id):
        # on ouvre le fichier STATUS_FILE et on ecrit le 'book_id' du livre
        with open(config.STATUS_FILE.format(config.NAME_USER), "a+") as f:
            f.write(f"{book_id}\n")

    # permet de charger le STATUS_FILE : ouvre le fichier, pour chaque ligne du STATUS_FILE, on retire les espaces en fin de lignes et on stocke le resultat dans une liste
    def load_list_status(self):
        try:
            with open(config.STATUS_FILE.format(config.NAME_USER), "r") as file:
                lines = [line.rstrip() for line in file]
                return lines
        except:
            return []

    # on redéfinit la methode 'from_crawler' de la classe mere de BabelioBookSpider(qui est scrapy.Spider)
    # elle permet dedéclencher une méthode dans une classe Spider juste avant qu'elle ne se termine
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BabelioBookSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.engine_stopped, signal=signals.engine_stopped)
        signals.engine_stopped
        return spider

    # cette fonction va s'execute à la fin de tous les crawling
    # affiche des stats pour savoir le % total de livres à scraper
    def engine_stopped(self): 
        if self.df_list_books is not None:
            # nombre total de livres
            total_books = self.df_list_books.shape[0]
            # liste de livres déja scrapé
            list_status = self.load_list_status()
            # nombre de livres déja scrapé
            current_books_parsed = len(list_status)
            print('')
            print(f"##### {current_books_parsed} livres parsés sur {total_books} #####")
            # pourcentage du nombre de livres déja scrapé / total de livres 
            print(f"##### {round((current_books_parsed / total_books)*100, 2)}% d'avancement #####")
            print('')
            if current_books_parsed < total_books:
                print(f'Courage {config.NAME_USER} !')
            else: print(f'Bravo {config.NAME_USER} !!! C\'est fini !')
            print('')

    # on commence le scraping par cette fonction : elle permet de boucler sur chaque livre de la liste des livres scraper dans le 1er Spider(spider-list-books)
    #
    def start_requests(self):
        # on charge la liste des livres scraper dans spider-list-books
        self.df_list_books = self.load_list_books(config.LIST_BOOKS_FILE)
        # on charge egalement la liste des livres déja scraper avec ce spider (spider-books)
        list_status = self.load_list_status()

        i = 0
        # pour chaque livre 
        for _, book in self.df_list_books.iterrows():
            # on check si un livre (avec son id) est déja dans la liste de STATUS_FILE, on ne le scrape pas et on continue
            if str(book['book_id']) in list_status: # pour reprendre où le scrapper s'était arrêté
                continue
            # si i est inférieur au nombre maximum de livre à scraper, on incrémente i de 1 et on retourne l'url du livre, ainsi que son id et son nombre de commentaires(infos qui sont dans STATUS_FILE ou dans la liste déja scraper)
            if i < config.BOOKS_BY_PARSING:
                i += 1
                # on avait déja recuperer l'url des livres ce qui va nous permettre de commencer à scraper à partir de cet url (l'url de la page du livre)
                yield scrapy.Request(book['book_url'], callback=self.parse, meta={'data' : {'book_id': book['book_id'], 'book_nb_comm':book['book_nb_comm']}})

    # cette fonction permet de scraper le nom, prenom de l'auteur, titre, l'image et les tags (sous thème du livre)
    # on commence à partir de la page du livre
    def parse(self, response):
        # data va contenir toutes les infos précédemments récupérées (url, book_id, book_nb_comm')
        data = response.request.meta["data"]
        
        # on update le STATUS_FILE avec le book_id pour ajouter le livre scrapé à ce fichier (pour eviter de le rescraper)
        self.update_status_file(str(data['book_id']))

        # on scrape toutes les infos qu'on a besoin
        name = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/text()').get(default="").strip()
        # name = response.path('//div[@class='livre_con']/div[2]//a/span/b).get(default="").strip()[1])
        surname = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/b/text()').get(default="").strip()
        # surnamme = response.xpath('//div[@class='livre_con']/div[2]//a/span/text()').get(default="").strip()
        title = response.xpath('//*[@class="livre_header_con"]/h1/a/text()').get(default="").strip()
        img_url = response.xpath('//div[@class="livre_con"]/div/img/@src').get(default="").strip()
        tags = ",".join([t.strip() for t in response.xpath('//*[@id="page_corps"]//p[@class="tags"]/a/text()').getall()])

        # on crée une url pour les critiques qui utilise l'url de la page du livre + '/critiques' pour accéder à cette page
        url = response.url + "/critiques"
        
        # on retourne l'url des critiques que l'on va suivre dans la prochaine fonction + toutes les infos récupérées
        yield response.follow(url=url, callback=self.parse_critiques,meta={"data" : {**data, "title":title,"name":name,"surname":surname,"tags":tags,"img_url":img_url}, "nb_comm_fornow":0})

    # dans cette fonction, on va récupérer toutes les critiques ainsi que les infos du profil utilisateur
    def parse_critiques(self,response):
        # on stocke toutes les infos que l'on vient de récupérer dans une variable 'data'
        data = response.request.meta["data"]
        # 'nb_comm_fornow' est initialisé à 0 et va être incrémenter pour connaitre le nombre de commentaires que l'on à scraper
        nb_comm_fornow = response.request.meta["nb_comm_fornow"]
        # comments correspond à la vignette de tous les commentaires (chaque commentaire est dans une sous vignettes que l'on va parcourir grace à la boucle 'for com in comments')
        comments = response.xpath('//span[@itemprop="itemReviewed"]')

        # pour chaque commentaire, on va récupérer les infos concernant l'autheur du commentaire, son identifiant
        for com in comments:  
            # sur la page de critiques d'un livre (ex:'https://www.babelio.com' + '/livres/Da-Costa-La-doublure/1433127/critiques')     
            url_profile = "https://www.babelio.com"+com.xpath('.//a[@class="author"]').attrib["href"]
            try:
                user_id = url_profile.split('=')[1].strip()
            except:
                user_id = 0

            if nb_comm_fornow >= config.NB_COMM_MAX: #nb max de comm à parser atteint, on arrête
                break

            nb_comm_fornow += 1

            yield {
                **data,
                "comm_id" : com.xpath('.//div[@class="post_con"]/@id').get(default="").replace("B_CRI",""),
                "user_id" : user_id,
                "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(default=""),
                "date" : com.xpath('.//span[@class="gris"]/text()').get(default=""),
                "appreciations" : com.xpath('.//span[@class="post_items_like "]/span[2]/text()').get(default="").strip(),
                "commentaire" : com.xpath("string(.//div[@class='text row']/div)").get(default="").strip()
                }
            
            # yield scrapy.Request(url=url_profile,callback=self.parse_profile,meta={"data" : {
            #                                                                         **data,
            #                                                                         "comm_id" : com.xpath('.//div[@class="post_con"]/@id').get(default="").replace("B_CRI",""),
            #                                                                         "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(default=""),
            #                                                                         "date" : com.xpath('.//span[@class="gris"]/text()').get(default=""),
            #                                                                         "appreciations" : com.xpath('.//span[@class="post_items_like "]/span[2]/text()').get(default="").strip(),
            #                                                                         "commentaire" : com.xpath("string(.//div[@class='text row']/div)").get(default="").strip() #[c.strip() for c in com.xpath('.//div/div/text()').getall()]
            #                                                                         }})

        if nb_comm_fornow < config.NB_COMM_MAX: # on ne continue pas si on a assez de commentaires
            try:
                next_page = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[14]/a[@class="fleche icon-next"]').attrib["href"]
            except KeyError:
                logging.info('No next page. Terminating crawling process.')
            else:
                yield response.follow(next_page, callback=self.parse_critiques,meta={"data" : {**data}, "nb_comm_fornow":nb_comm_fornow})

    def parse_profile(self,response):
        data = response.request.meta["data"]

        sex = response.xpath('//*[@id="page_corps"]/div/div[4]/div[1]/div[2]/div[2]/text()').get(default="")
        if sex.split(",")[0].strip()=="Femme" or sex.split(",")[0].strip()=="Homme":
            sexe = sex.split(",")[0].strip()
        else:
            sexe = "Inconnu"

        yield {
                **data,
                "sexe_redacteur":sexe
                }


if __name__ == "__main__":
    scrapping_book_runner(config.FINAL_FILE.format(config.NAME_USER))
