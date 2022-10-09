import scrapy
import os.path
from scrapy.crawler import CrawlerProcess

# calculate the elo of the teams from each region to get their unweighted elo

class Spider(scrapy.Spider):
    name = "elise"

    regions_links = []
    tournaments_links = []
    stages_links = []

    def start_requests(self):
        yield scrapy.Request("https://lol.fandom.com/wiki/2022_Season_World_Championship")

    def parse(self, response):
        for i in range(2,14):
            next_page = "https://lol.fandom.com" + response.css("div.hlist ul")[i].css("li a").attrib["href"]
            self.regions_links.append(next_page)
        yield scrapy.Request(self.regions_links[0], callback=self.scrape_regions, dont_filter=True)

    def scrape_regions(self, response):
        tournaments = response.css("div.tabheader-top").css("div.tabheader-tab").css("div.tabheader-content a")

        for tournament in tournaments:
            next_page = "https://lol.fandom.com" + tournament.attrib["href"] + "/Scoreboards"
            self.tournaments_links.append(next_page)
        self.regions_links.pop(0)
        if self.regions_links:
            yield scrapy.Request(self.regions_links[0], callback=self.scrape_regions, dont_filter=True)
        else:
            yield scrapy.Request(self.tournaments_links[0], callback=self.scrape_tournaments, dont_filter=True)
    
    def scrape_tournaments(self, response):
        if response.status != 404:
            start = str(response)[5:-1]
            self.stages_links.append(start)
            if len(response.css("div.tabheader-top")) >= 3:
                stages = response.css("div.tabheader-top")[2].css("div.tabheader-tab").css("div.tabheader-content a")
                for stage in stages:
                    next_page = "https://lol.fandom.com" + stage.attrib["href"]
                    self.stages_links.append(next_page)
        self.tournaments_links.pop(0)
        if self.tournaments_links:
            yield scrapy.Request(self.tournaments_links[0], callback=self.scrape_tournaments, dont_filter=True)
        else:
            yield scrapy.Request(self.stages_links[0], callback=self.scrape_stages, dont_filter=True)
       
    def scrape_stages(self, response):
        for i in range(len(response.css("table.sb"))):
            blue_team = response.css("table.sb")[i].css("tbody tr th.sb-teamname")[0].css("span.team span.teamname").css("::text").get()
            red_team = response.css("table.sb")[i].css("tbody tr th.sb-teamname")[1].css("span.team span.teamname").css("::text").get()
            result = response.css("table.sb")[i].css("div.sb-header-vertict").css("::text").get()
            if type(result) is not str:
                continue
            game_time = response.css("table.sb")[i].css("tbody tr")[2].css("th")[1].css("::text").get()
            blue_gold = response.css("table.sb")[i].css("tbody th div.sb-header div.sb-header-Gold").css("::text").get().replace("k","").replace(" ","")
            red_gold = response.css("table.sb")[i].css("tbody th.side-red div.sb-header-Gold").css("::text").get().replace("k","").replace(" ","")    
            matches_dict = {"blue team" : blue_team}
            matches_dict["red team"] = red_team
            matches_dict["result"] = result
            matches_dict["game time"] = game_time
            matches_dict["blue gold"] = blue_gold
            matches_dict["red gold"] = red_gold
            yield matches_dict
        self.stages_links.pop(0)
        if self.stages_links:
            yield scrapy.Request(self.stages_links[0], callback=self.scrape_stages, dont_filter=True)

def scrape():
    if not os.path.exists("scraped_datas/regional_results.csv"):
        process = CrawlerProcess(settings = {
            "FEED_URI": "scraped_datas/regional_results.csv",
            "FEED_FORMAT": "csv",
            "HTTPERROR_ALLOWED_CODES": [404]
        })
        process.crawl(Spider)
        
        process.start()

def calculate_elo():

    f = open("scraped_datas/regional_results.csv")
    lines = f.readlines()

    elo_dict = { "" : 0 }

    # this uses the same elo algorithm as when calculating the teams elo at MSI
    # however, k is 50 because I think that the teams' strength relative to the region 
    # is only half as impactful as the region that it's played on in the calculation of the team's true power

    k = 50
    for line in lines:
        chunks = line.split(",")
        if chunks[0] not in elo_dict:
            elo_dict[chunks[0]] = 1000
        if chunks[1] not in elo_dict:
            elo_dict[chunks[1]] = 1000
        p1 = (1.0 / (1.0 + pow(10, ((elo_dict[chunks[1]] - elo_dict[chunks[0]]) / 400))))
        p2 = (1.0 / (1.0 + pow(10, ((elo_dict[chunks[0]] - elo_dict[chunks[1]]) / 400))))
        elo_dict[chunks[0]] = elo_dict[chunks[0]] + k*((chunks[2] == "Victory") - p1)
        elo_dict[chunks[1]] = elo_dict[chunks[1]] + k*((chunks[2] == "Defeat") - p2)
    f.close()
    return elo_dict
