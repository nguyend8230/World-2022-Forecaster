import scrapy
import os.path
from scrapy.crawler import CrawlerProcess

class Spider(scrapy.Spider):
    name = "elise"
    links = []

    def start_requests(self):
        yield scrapy.Request("https://lol.fandom.com/wiki/2022_Mid-Season_Invitational/Scoreboards")

    def parse(self, response):
        # print("______________________________________________",response)
        start = str(response)[5:-1]
        self.links.append(start)
        stages = response.css("div.tabheader-top")[1].css("div.tabheader-tab").css("div.tabheader-content a")
        for stage in stages:
            next_page = "https://lol.fandom.com" + stage.attrib["href"]
            self.links.append(next_page)
        
        yield scrapy.Request(self.links[0], callback=self.scrape_stages, dont_filter=True)

    def scrape_stages(self, response):
        for i in range(len(response.css("table.sb"))):
            blue_team = response.css("table.sb")[i].css("tbody tr th.sb-teamname")[0].css("span.team span.teamname").css("::text").get()
            red_team = response.css("table.sb")[i].css("tbody tr th.sb-teamname")[1].css("span.team span.teamname").css("::text").get()
            result = response.css("table.sb")[i].css("div.sb-header-vertict").css("::text").get()
            game_time = response.css("table.sb")[i].css("tbody tr")[2].css("th")[1].css("::text").get()
            blue_gold = response.css("table.sb")[i].css("tbody th div.sb-header div.sb-header-Gold").css("::text").get().replace("k","").replace(" ","")
            red_gold = response.css("table.sb")[i].css("tbody th.side-red div.sb-header-Gold").css("::text").get().replace("k","").replace(" ","")    
            # print(blue_team, " ", red_team, " ", result, " ", game_time, " ", blue_gold, " ", red_gold)
            matches_dict = {"blue team" : blue_team}
            matches_dict["red team"] = red_team
            matches_dict["result"] = result
            matches_dict["game time"] = game_time
            matches_dict["blue gold"] = blue_gold
            matches_dict["red gold"] = red_gold
            yield matches_dict
        self.links.pop(0)
        if self.links:
            yield scrapy.Request(self.links[0], callback=self.scrape_stages, dont_filter=True)


def scrape():    
    if not os.path.exists("scraped_datas/MSI_results.csv"):
        process = CrawlerProcess(settings = {
            "FEED_URI": "scraped_datas/MSI_results.csv",
            "FEED_FORMAT": "csv"
        })
        process.crawl(Spider)

def calculate_elo():

    f = open("scraped_datas/MSI_results.csv")
    lines = f.readlines()

    elo_dict = { "" : 0 }
    k = 100
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





