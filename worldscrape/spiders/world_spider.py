import scrapy
 
class PostsSpider(scrapy.Spider):
    name = "elise"
    custom_settings = {"CONCURRENT_REQUESTS": 1}
    start_urls = ["https://lol.fandom.com/wiki/LCS/2022_Season"]
    regions = ["LCS","LEC,","LCK","LPL","CBLOL","LCL","LJL","LLA","LCO","PCS","TCL","VCS"]
    
   
    def parse(self, response):
        # look at all the tournaments in the year
        tournaments = response.css("div.tabheader-top").css("div.tabheader-tab").css("div.tabheader-content a")
        matches_dict = {"blue team" : "blue_team"}
        for tournament in tournaments:
            next_page = "https://lol.fandom.com" + tournament.attrib["href"] + "/Scoreboards"
            yield scrapy.Request(next_page, callback=self.scrape_tournaments)
 
    def scrape_tournaments(self, response):
        stages = response.css("div.tabheader-top")[2].css("div.tabheader-tab").css("div.tabheader-content a")
        start = str(response)[5:-1]
        yield scrapy.Request(start, callback=self.scrape_stages, dont_filter=True)
        for stage in stages:
            next_page = "https://lol.fandom.com" + stage.attrib["href"]
            yield scrapy.Request(next_page, callback=self.scrape_stages)
       
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
 
    # response.css("div.mw-parser-output div.inline-content table.sb tbody tr th.sb-teamname")[1].css("span.team span.teamname").css("::text").get()
    # len(response.css("div.mw-parser-output div.inline-content"))  
 
 
 
 

