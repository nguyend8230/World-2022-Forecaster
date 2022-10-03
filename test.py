import scrapy
from scrapy.crawler import CrawlerProcess

class WorldSpider(scrapy.Spider):
    name = "elise"
    priority = 0

    def start_requests(self):
        yield scrapy.Request("https://lol.fandom.com/wiki/2022_Season_World_Championship")

    def parse(self, response):
        for i in range(2,14):
            next_page = "https://lol.fandom.com" + response.css("div.hlist ul")[i].css("li a").attrib["href"]
            yield scrapy.Request(next_page, callback=self.scrape_regions, priority=self.priority)
            self.priority-=1

    def scrape_regions(self, response):
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

process = CrawlerProcess(settings = {
    "FEED_URI": "results.csv",
    "FEED_FORMAT": "csv",
    "CONCURRENT_REQUESTS": 1
})
process.crawl(WorldSpider)
process.start()