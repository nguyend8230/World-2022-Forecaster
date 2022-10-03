import scrapy
from scrapy.crawler import CrawlerProcess

class WorldSpider(scrapy.Spider):
    name = "elise"
    priority = 0

    def start_requests(self):
        url = "https://lol.fandom.com/wiki/" + self.region + "/2022_Season"
        yield scrapy.Request(url)

    def parse(self, response):
        tournaments = response.css("div.tabheader-top").css("div.tabheader-tab").css("div.tabheader-content a")
        for tournament in tournaments:
            next_page = "https://lol.fandom.com" + tournament.attrib["href"] + "/Scoreboards"
            yield scrapy.Request(next_page, callback=self.scrape_tournaments, priority=self.priority)
            self.priority-=1
    
    def scrape_tournaments(self, response):
        # print("______________________________________________",response)
        stages = response.css("div.tabheader-top")[2].css("div.tabheader-tab").css("div.tabheader-content a")
        start = str(response)[5:-1]
        yield scrapy.Request(start, callback=self.scrape_stages, dont_filter=True, priority=self.priority)
        self.priority-=1
        for stage in stages:
            next_page = "https://lol.fandom.com" + stage.attrib["href"]
            yield scrapy.Request(next_page, callback=self.scrape_stages, priority=self.priority)
            self.priority-=1
       
    def scrape_stages(self, response):
        # print("                                              ",response)
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

regions = ["LCS","LEC","LCK","LPL","CBLOL","LCL","LJL","LLA","LCO","PCS","TCL","VCS"]

for region in regions:
    print(region + ".csv")
    process = CrawlerProcess(settings = {
        "FEED_URI": "regions results/" + region + ".csv",
        "FEED_FORMAT": "csv",
        "CONCURRENT_REQUESTS": 1
    })
    process.crawl(WorldSpider, region=region)
process.start()