import scrapy
import os.path
from scrapy.crawler import CrawlerProcess

import MSI_elo_calculator as ec

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

    # temp = weights_dict
    # temp = sorted(temp.items(), key=lambda item: item[1])
    # print(temp)
    return weights_dict

