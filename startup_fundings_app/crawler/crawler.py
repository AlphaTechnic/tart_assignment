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

    def print_obj_list(self):
        """
        for debug
        """
        for obj in self.obj_list:
            print(obj)

    def mk_return_data(self):
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

    async def load_page_helper(self, uri):
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
        await resp.html.arender(timeout=30)
        await session.close()
        return resp


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
        company, status 를 정의하면서 investment instance 생성
        """
        for data in raw_data:
            obj = Investment('wadiz')

            soup = BeautifulSoup(data.html, 'html.parser')
            info = soup.text.split('·')[0]
            obj.company, obj.status = info[:-3], self.to_status[info[-3:-1]]
            self.obj_list.append(obj)

    def add_info_to_objs(self, raw_data):
        """
        identifier, category, amount, title 의 정보를 더함
        """
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')

            link = soup.find('a')
            self.obj_list[i].identifier = link.attrs["href"].split('/')[-1]
            elem = soup.find_all('span')
            self.obj_list[i].category, self.obj_list[i].amount = elem[1].text, elem[2].text
            elem = soup.find_all('strong')
            self.obj_list[i].title = elem[0].text

    def crawl(self, debug=False):
        if not debug:
            resp = asyncio.run(self.load_page_helper(self.uri))
            resp.html.arender(timeout=15)
        else:
            # debug mode
            session = HTMLSession()
            resp = session.get(self.uri)
            resp.html.render(timeout=15)

        cards = resp.html.find(self.cards_selector)[0]
        raw_data1 = cards.find(self.company_selector)
        self.create_objs(raw_data1)
        raw_data2 = cards.find(self.identifier_selector)[1::2]
        self.add_info_to_objs(raw_data2)

        return self.mk_return_data()


class OhMyCompanyCrawler(Crawler):
    uri = None
    cards_selector = None

    def __init__(self, uri, cards_selector):
        super().__init__()
        self.uri = uri
        self.cards_selector = cards_selector

    def create_objs(self, cards):
        """
        title을 정의하면서 investment instance 생성
        """
        titles = []
        raw_data = cards.find(".project_name")
        for data in raw_data:
            soup = BeautifulSoup(data.html, 'html.parser')
            title = soup.text.split('\n')[2].rstrip().lstrip()
            titles.append(title)

        for title in titles:
            obj = Investment("ohmycompany")
            obj.title = title
            self.obj_list.append(obj)

    def add_identifier_info(self, cards):
        raw_data = cards.find(".project_detail_link")
        for i, data in enumerate(raw_data[1::2]):
            soup = BeautifulSoup(data.html, 'html.parser')
            self.obj_list[i].identifier = soup.find('a').attrs["data-project-seq"]

    def add_status_info(self, cards):
        raw_data = cards.find(".project_state")
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')
            status = soup.text.split('\n')[2]
            if status == '현재 참여금액':  # 펀딩 진행중
                self.obj_list[i].status = "open"
            else:
                self.obj_list[i].status = "closed"

    def add_company_info(self, cards):
        raw_data = cards.find(".txt_name")
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')
            self.obj_list[i].company = soup.text.split('\n')[0]

    def add_amount_info(self, cards):
        raw_data = cards.find(".project_state")
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')
            state = soup.text.split('\n')[2]
            if state == "현재 참여금액":  # 펀딩 진행중
                self.obj_list[i].amount = soup.text.split('\n')[3].rstrip().lstrip()
            else:
                raw = soup.text.split('\n')[3]
                amount = raw.rstrip().lstrip().split()[1]
                self.obj_list[i].amount = amount

    def add_category_info(self, cards):
        raw_data = cards.find(".project_category")
        for i, data in enumerate(raw_data):
            soup = BeautifulSoup(data.html, 'html.parser')
            self.obj_list[i].category = soup.text.split('\n')[0][4:]

    def add_info_to_objs(self, cards):
        """
        identifier, status, company, amount, category 뽑아냄
        """
        self.add_identifier_info(cards)
        self.add_status_info(cards)
        self.add_company_info(cards)
        self.add_amount_info(cards)
        self.add_category_info(cards)

    def crawl(self, debug=False):
        if not debug:
            resp = asyncio.run(self.load_page_helper(self.uri))
            resp.html.arender(timeout=15)
        else:
            # debug mode
            session = HTMLSession()
            resp = session.get(self.uri)
            resp.html.render(timeout=15)

        cards = resp.html.find(self.cards_selector)[0]
        self.create_objs(cards)
        self.add_info_to_objs(cards)

        return self.mk_return_data()


if __name__ == "__main__":
    print("크롤링 시작")
    uri = "https://www.ohmycompany.com/invest/list"
    cards_selector = "#listPrj > div"

    print(OhMyCompanyCrawler(uri, cards_selector).crawl(debug=True))
