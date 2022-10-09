import scrapy
import os.path
from scrapy.crawler import CrawlerProcess

import MSI_elo_calculator as ec

# the region's weight is calculated using the team that represented the region at MSI
# that team's elo at MSI will be divided by 1000 (the starting elo) to find the region's weight
# the region's weight will be multiplied to the elo of the teams from that region to find the weighted elo of those teams 

class Spider(scrapy.Spider):
    name = "elise"
    
    def start_requests(self):
        yield scrapy.Request("https://lol.fandom.com/wiki/2022_Mid-Season_Invitational")
    
    def parse(self, response):
        teams = response.css("div.pools.maxteams-3 div.inline-content")
        for team in teams:
            result = {"team" : team.css("tbody a::text").get()}
            result["region"] = team.css("div.region-icon::text").get()
            yield result

def scrape():
    if not os.path.exists("scraped_datas/MSI_regions_mapping.csv"):
        process = CrawlerProcess(settings = {
            "FEED_URI": "scraped_datas/MSI_regions_mapping.csv",
            "FEED_FORMAT": "csv"
        })
        process.crawl(Spider)

def calculate_weights():

    f = open("scraped_datas/MSI_regions_mapping.csv")
    lines = f.readlines()
    
    elo_dict = ec.calculate_elo()

    weights_dict = { "" : 0 }

    for line in lines:
        chunks = line.split(",")
        if chunks[0] in elo_dict:
            chunks = line.split(",") 
            weights_dict[chunks[1]] = elo_dict[chunks[0]]/1000

    return weights_dict

