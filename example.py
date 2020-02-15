import theglobe.database as db
import theglobe.logging as log
import theglobe.scraper as scr
import logging

# This has to be on top level!
log.InitLogging()
logger = logging.getLogger(__name__)

# Init Database
URL = ("mongodb://b.lnru.de:27017/")
DB = "tg"
COLLECTION = "articles"
insert = db.Insert(URL, DB, COLLECTION)

# Get scraped data
scraper = scr.Scrape()
articles_json_list = scraper._get_articles_([
            'http://feeds.bbci.co.uk/news/england/london/rss.xml', 
            'https://www.spiegel.de/international/index.rss', 
            'https://elpais.com/rss/elpais/inenglish.xml', 
            'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', 
            'http://rss.cnn.com/rss/edition.rss', 
            'http://rss.cnn.com/rss/cnn_topstories.rss', 
            'http://rssfeeds.usatoday.com/usatoday-NewsTopStories', 
            'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms', 
            'https://feeds.a.dj.com/rss/RSSWorldNews.xml', 
            'https://www.rt.com/rss/news/', 
            'https://www.latimes.com/world/rss2.0.xml', 
            'http://www.aljazeera.com/xml/rss/all.xml', 
            'https://www.cbc.ca/cmlink/rss-world', 
            'http://www.independent.co.uk/news/world/rss', 
            'http://feeds.reuters.com/Reuters/worldNews'])


# Insert Data
insert._insert_many_articles_(articles_json_list)

