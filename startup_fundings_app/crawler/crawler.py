import asyncio

import pyppeteer
from requests_html import HTMLSession, AsyncHTMLSession
from bs4 import BeautifulSoup


class Investment:
    def __init__(self, platform):
        self.platform = platform
        self.identifier = None
        self.status = None
        self.title = None

        # investment info
        self.company = None
        self.amount = None
        self.category = None

    def __repr__(self):
        return f"{self.platform};{self.identifier};{self.status};{self.title[:5]};{self.company};{self.amount};{self.category}"


class Crawler(object):
    def __init__(self):
        self.obj_list = []


class WadizCrawler(Crawler):
    to_status = {
        "종료": "closed",
        "진행": "open",
    }
    uri = None
    cards_selector = None
    company_selector = None
    identifier_selector = None

    def __init__(self, uri, cards_selector, company_selector, identifier_selector):
        super().__init__()
        self.uri = uri
        self.cards_selector = cards_selector
        self.company_selector = company_selector
        self.identifier_selector = identifier_selector

    def create_objs(self, raw_data):
        """
        company, status 뽑아냄
        """
        for data in raw_data:
            obj = Investment('wadiz')

            soup = BeautifulSoup(data.html, 'html.parser')
            info = soup.text.split('·')[0]
            obj.company, obj.status = info[:-3], self.to_status[info[-3:-1]]
            if obj.status == "회사":
                print(soup)
                print(soup.text)

            self.obj_list.append(obj)

    def add_info_to_objs(self, raw_data):
        """
        identifier, category, amount, title 뽑아냄
        """
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')

            # id
            link = soup.find('a')
            self.obj_list[i].identifier = link.attrs["href"].split('/')[-1]

            elem = soup.find_all('span')
            self.obj_list[i].category, self.obj_list[i].amount = elem[1].text, elem[2].text
            elem = soup.find_all('strong')
            self.obj_list[i].title = elem[0].text

    def print_obj_list(self):
        """
        for debug
        """
        for obj in self.obj_list:
            print(obj)

    def crawl(self, uri):
        async def load_page_helper(uri):
            session = AsyncHTMLSession()
            browser = await pyppeteer.launch({
                'ignoreHTTPSErrors': True,
                'headless': True,
                'handleSIGINT': False,
                'handleSIGTERM': False,
                'handleSIGHUP': False
            })
            session._browser = browser

            resp = await session.get(uri)
            await resp.html.arender()
            await session.close()
            return resp

        resp = asyncio.run(load_page_helper(uri))
        # session open and 동적페이지 생성
        resp.html.arender(timeout=15)

        cards = resp.html.find(self.cards_selector)[0]

        raw_data1 = cards.find("p.ProjectCardInfo_maker__2EK-a")
        self.create_objs(raw_data1)

        raw_data2 = cards.find("a.CardLink_link__1k83H")[1::2]
        self.add_info_to_objs(raw_data2)

        # session.close()

        # make return data
        ret = []
        for obj in self.obj_list:
            data = {
                "platform": obj.platform,
                "identifier": obj.identifier,
                "status": obj.status,
                "title": obj.title,
                "investmentInfo": {
                    "company": obj.company,
                    "amount": obj.amount,
                    "category": obj.category,
                }
            }
            ret.append(data)
        return ret


class OhMyCompanyCrawler(Crawler):
    to_status = {
        "종료": "closed",
        "진행": "open",
    }
    uri = None
    cards_selector = None
    company_selector = None
    identifier_selector = None

    def __init__(self, uri, cards_selector, company_selector, identifier_selector):
        super().__init__()
        self.uri = uri
        self.cards_selector = cards_selector
        self.company_selector = company_selector
        self.identifier_selector = identifier_selector

    def create_objs(self, raw_data):
        """
        company, status 뽑아냄
        """
        for data in raw_data:
            obj = Investment('wadiz')

            soup = BeautifulSoup(data.html, 'html.parser')
            info = soup.text.split('·')[0]
            obj.company, obj.status = info[:-3], self.to_status[info[-3:-1]]
            if obj.status == "회사":
                print(soup)
                print(soup.text)

            self.obj_list.append(obj)

    def add_info_to_objs(self, raw_data):
        """
        identifier, category, amount, title 뽑아냄
        """
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')

            # id
            link = soup.find('a')
            self.obj_list[i].identifier = link.attrs["href"].split('/')[-1]

            elem = soup.find_all('span')
            self.obj_list[i].category, self.obj_list[i].amount = elem[1].text, elem[2].text
            elem = soup.find_all('strong')
            self.obj_list[i].title = elem[0].text

    def print_obj_list(self):
        """
        for debug
        """
        for obj in self.obj_list:
            print(obj)

    def crawl(self, uri):
        async def load_page_helper(uri):
            session = AsyncHTMLSession()
            browser = await pyppeteer.launch({
                'ignoreHTTPSErrors': True,
                'headless': True,
                'handleSIGINT': False,
                'handleSIGTERM': False,
                'handleSIGHUP': False
            })
            session._browser = browser

            resp = await session.get(uri)
            await resp.html.arender()
            await session.close()
            return resp

        resp = asyncio.run(load_page_helper(uri))
        # session open and 동적페이지 생성
        resp.html.arender(timeout=15)

        cards = resp.html.find(self.cards_selector)[0]

        raw_data1 = cards.find("p.ProjectCardInfo_maker__2EK-a")
        self.create_objs(raw_data1)

        raw_data2 = cards.find("a.CardLink_link__1k83H")[1::2]
        self.add_info_to_objs(raw_data2)

        # session.close()

        # make return data
        ret = []
        for obj in self.obj_list:
            data = {
                "platform": obj.platform,
                "identifier": obj.identifier,
                "status": obj.status,
                "title": obj.title,
                "investmentInfo": {
                    "company": obj.company,
                    "amount": obj.amount,
                    "category": obj.category,
                }
            }
            ret.append(data)
        return ret



if __name__ == "__main__":
    print("크롤링 시작")
    uri = "https://www.wadiz.kr/web/winvest/startup"
    card_selector = "#main-app > div.MainWrapper_content__GZkTa > div > div.EquityMainStartup_container__34N-z.EquityMainCommon_container__2fyRJ > div.EquityMainProjectList_container__2jo41 > div > div.ProjectCardList_container__3Y14k > div.ProjectCardList_list__1YBa2"
    company_selector = "p.ProjectCardInfo_maker__2EK-a"
    identifier_selector = "a.CardLink_link__1k83H"

    crawler = WadizCrawler(uri, card_selector, company_selector, identifier_selector)
    print(crawler.crawl(uri))
