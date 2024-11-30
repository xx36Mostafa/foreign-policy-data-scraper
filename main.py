import requests
import json
import datetime
import sqlite3 

class data_base:
    def __init__(self):
        self.db = sqlite3.connect('articles.db')
        self.cr = self.db.cursor()
        self.db.execute("CREATE TABLE if not exists articles (id integer,date TEXT, tittle TEXT, content TEXT, link TEXT)")

    def insert_data(self,data):
        self.cr.execute("SELECT IFNULL(MAX(id), 0) FROM articles")
        max_id = self.cr.fetchone()[0]
        for index , value in enumerate(data, start=max_id + 1):
            tittle, article_date, content, link = value
            self.cr.execute("SELECT 1 FROM articles WHERE link = ?", (link,))
            if self.cr.fetchone():
                print(f"[!] Link already exists, skipping: {link}")
                continue  
            self.cr.execute(
            "INSERT INTO articles (id, date, tittle, content, link) VALUES (?, ?, ?, ?, ?)",
            (index, article_date, tittle, content, link))
        print('[+] Success Insert Articles In DataBase..')
        self.db.commit()
    
class scrape_data(data_base):
    def __init__(self,s_year=False,e_year=False,s_month=False,e_month=False,articles=80):
        super().__init__()
        now = datetime.datetime.now()
        self.session = requests.Session()
        self.num_of_articles = articles
        if not s_year:
            self.start_year = now.year
            self.end_year = now.year
        else:
            self.start_year = s_year 
            self.end_year = e_year
        self.start_month , self.end_month =  s_month , e_month

    def scrap_data(self,key,topic):
        URL = 'https://search.foreignpolicy.com/multi-search'
        headers = {
            'accept':'*/*',
            'accept-language':'en-US,en;q=0.5',
            'authorization':f'Bearer {key}',
            'content-type':'application/json',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-meilisearch-client':'Meilisearch instant-meilisearch (v0.22.0) ; Meilisearch JavaScript (v0.45.0)'
        }
        payload = {
        "queries": [
            {
            "indexUid": "production",
            "facets": [
                "is_newsletter",
                "post_authors.name",
                "post_categories.name",
                "post_date",
                "post_regions.name",
                "post_topics.name"
            ],
            "hitsPerPage": 40,
            "page": 1}]}
        response = requests.post(URL,headers=headers,json=payload)
        if response.status_code == 200:
            start , end = self.get_time()
            payload = {
                    "queries": [
                        {
                        "indexUid": "production",
                        "q": f"{topic}",
                        "facets": [
                            "is_newsletter",
                            "post_authors.name",
                            "post_categories.name",
                            "post_date",
                            "post_regions.name",
                            "post_topics.name"
                        ],
                        "attributesToCrop": [
                            "post_content:40"
                        ],
                        "filter": [
                            f"\"post_date\">={end}",
                            f"\"post_date\"<={start}",
                            [
                            "\"is_newsletter\"=\"false\""
                            ]
                        ],
                        "attributesToHighlight": [
                            "*"
                        ],
                        "highlightPreTag": "__ais-highlight__",
                        "highlightPostTag": "__/ais-highlight__",
                        "hitsPerPage": self.num_of_articles,
                        "page": 1
                        },
                        {
                        "indexUid": "production",
                        "q": f"{topic}",
                        "facets": [
                            "is_newsletter"
                        ],
                        "attributesToCrop": [
                            "post_content:40"
                        ],
                        "filter": [
                            f"\"post_date\">={end}",
                            f"\"post_date\"<={start}"
                        ],
                        "attributesToHighlight": [
                            "*"
                        ],
                        "highlightPreTag": "__ais-highlight__",
                        "highlightPostTag": "__/ais-highlight__",
                        "hitsPerPage": 0,
                        "page": 1
                        },
                        {
                        "indexUid": "production",
                        "q": f"{topic}",
                        "facets": [
                            "post_date"
                        ],
                        "attributesToCrop": [
                            "post_content:40"
                        ],
                        "filter": [
                            [
                            "\"is_newsletter\"=\"false\""
                            ]
                        ],
                        "attributesToHighlight": [
                            "*"
                        ],
                        "highlightPreTag": "__ais-highlight__",
                        "highlightPostTag": "__/ais-highlight__",
                        "hitsPerPage": 0,
                        "page": 1
                        }
                    ]
                    }
            response = requests.post(URL,headers=headers,json=payload)
            data = response.json()
            with open("response.json", "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4)
            self.save_data(data)

    def get_auth(self,topic):
        URL = f'https://foreignpolicy.com/?s={topic}'
        headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.5",
        "priority": "u=0, i",
        "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        response = self.session.get(URL,headers=headers)
        if 'key":"' in str(response.text):
            key = str(response.text).split('key":"')[1].split('"')[0]
            print('[+] Key Found',key)    
            return self.scrap_data(key,topic)
        return '[!] Failed To Get AUTH To Scrape Data...'
    
    def get_time(self):
        now = datetime.datetime.now()
        # start_of_day = datetime.datetime(now.year-3, now.month, now.day, 0, 0, 0) # Last 3 year

        start_of_day = datetime.datetime(self.start_year, self.start_month, now.day, 0, 0, 0)
        start_of_day_timestamp = int(start_of_day.timestamp())

        # end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        end_of_day = datetime.datetime(self.end_year, self.end_month, now.day, 23, 59, 59)
        end_of_day_timestamp = int(end_of_day.timestamp())

        return end_of_day_timestamp , start_of_day_timestamp

    def save_data(self,data):
        data_ = []
        for index in range(len(data['results'][0]['hits'])):
            tittle = data['results'][0]['hits'][index]['post_title']
            link = data['results'][0]['hits'][index]['post_permalink']
            content = data['results'][0]['hits'][index]['post_content']
            date_stamp = int(data['results'][0]['hits'][index]['post_date'])
            converted_time = datetime.datetime.fromtimestamp(date_stamp)
            article_date = converted_time.strftime("%Y-%m-%d %H:%M:%S")
            # print(f'Tittle: {tittle} | Date For Article: {article_date} | Article Link: {link}')
            data_.append([tittle,article_date,content,link])
        self.insert_data(data_)

if __name__ == '__main__':
    scraper = scrape_data(s_month=1,e_month=11,articles=80)
    scraper.get_auth('Gaza')