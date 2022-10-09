import scrapy
import os.path
from scrapy.crawler import CrawlerProcess

import regional_elo_calculator as regional_ec
import regions_weights_calculator as regions_wc
import MSI_elo_calculator as MSI_ec

# find the regions of the team at world
# use the elo that the team has domestically and multiply by the weight of the region to find that team's weighted elo

class Spider(scrapy.Spider):
    name = "elise"

    def start_requests(self):
        yield scrapy.Request("https://lol.fandom.com/wiki/2022_Season_World_Championship")

    def parse(self, response):
        teams = response.css("table.wikitable tr")
        region = ""

        for i in range(2,14):
            if type(teams[i].css("div.region-icon::text").get()) == str:
                region = teams[i].css("div.region-icon::text").get()
            if teams[i].css("a::text").get() == "Royal Never Give Up":
                result = {"team" : "RNG"}
            elif teams[i].css("a::text").get() == "DetonatioN FocusMe":
                result = {"team" : "DetonatioN FM"}
            else:
                result = {"team" : teams[i].css("a::text").get()}
            result["region"] = region
            yield result
        
        for i in range(20,31):
            if type(teams[i].css("div.region-icon::text").get()) == str:
                region = teams[i].css("div.region-icon::text").get()
            if teams[i].css("a::text").get() == "Royal Never Give Up":
                result = {"team" : "RNG"}
            elif teams[i].css("a::text").get() == "DetonatioN FocusMe":
                result = {"team" : "DetonatioN FM"}
            else:
                result = {"team" : teams[i].css("a::text").get()}
            result["region"] = region
            yield result

def scrape():
    if not os.path.exists("scraped_datas/world_teams.csv"):
        process = CrawlerProcess(settings = {
            "FEED_URI": "scraped_datas/world_teams.csv",
            "FEED_FORMAT": "csv"
        })
        process.crawl(Spider)

def calculate_elo():

    weights_dict = regions_wc.calculate_weights()
    elo_dict = regional_ec.calculate_elo()

    f = open("scraped_datas/world_teams.csv")
    lines = f.readlines()
    weighted_elo_dict = { "" : 0 }

    for line in lines:
        chunks = line.split(",")
        if chunks[0] in elo_dict:
            weighted_elo_dict[chunks[0]] = elo_dict[chunks[0]] * weights_dict[chunks[1]]
    return weighted_elo_dict

scrape()
MSI_ec.scrape()
regions_wc.scrape()
regional_ec.scrape()

elo_dict = calculate_elo()

elo_dict = sorted(elo_dict.items(), key=lambda item: item[1])

print(elo_dict)


    

    

    