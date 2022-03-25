from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import response_msg
from startup_fundings_app.crawler.crawler import WadizCrawler, OhMyCompanyCrawler
import startup_fundings_app.crawler.selector as sel
import ray
import time


@ray.remote
def get_info_async(obj, platform, status=None) -> list:
    if platform == 'wadiz':
        return obj.get_from_wadiz(status)
    if platform == 'ohmycompany':
        return obj.get_from_ohmycompany(status)
    raise Exception("Something Wrong!")


class StartupFundings(object):
    Platforms = ['wadiz', 'ohmycompany']
    Status = ['scheduled', 'open', 'closed']


class ListView(APIView, StartupFundings):
    def get_from_wadiz(self, status) -> list:
        uri = "https://www.wadiz.kr/web/winvest/startup"
        crawler = WadizCrawler(uri, sel.wadiz_card_selector, sel.wadiz_company_selector, sel.wadiz_identifier_selector)
        return crawler.crawl()

    def get_from_ohmycompany(self, status) -> list:
        uri = "https://www.ohmycompany.com/invest/list"
        crawler = OhMyCompanyCrawler(uri, sel.ohmycompany_card_selector)
        return crawler.crawl()

    def get_info_directly(self, platform, status) -> list:
        if platform == 'wadiz':
            return self.get_from_wadiz(status)
        if platform == 'ohmycompany':
            return self.get_from_ohmycompany(status)
        raise Exception("Something Wrong!")

    def validate_request(self, platform, status):
        if platform is not None and platform not in self.Platforms:
            return False
        if status is not None and status not in self.Status:
            return False
        return True

    def mk_result_using_multiprocessing(self):
        start = time.time()
        merged_info = [
            get_info_async.remote(ListView(), platform=platform, status=status) for platform in self.Platforms
        ]
        objs = ray.get(merged_info)
        end = time.time()
        print(f"{end - start:.5f} sec", "!!!!!!!!!!!!!!!!!!!")

        return sum(objs, [])

    def mk_result_iteratively(self):
        start = time.time()
        merged_info = []
        for platform in self.Platforms:
            merged_info.extend(self.get_info_directly(platform, status))
        end = time.time()
        print(f"{end - start:.5f} sec", "!!!!!!!!!!!!!!!!!!!")

        return merged_info

    def get(self, request):
        platform = request.GET.get('platform')
        status = request.GET.get('status')

        # 요청의 유효성 검사
        if not self.validate_request(platform, status):
            return Response({"msg": response_msg.ERROR400}, status=status.HTTP_400_BAD_REQUEST)

        # platform 이 지정된 경우
        if platform is not None:
            info = self.get_info_directly(platform, status)
            return Response(data=info)

        # platform 이 지정되지 않아서 모든 플랫폼을 불러오는 경우
        # multiprocessing
        # return Response(self.mk_result_using_multiprocessing())

        # NO multiprocessing
        return Response(self.mk_result_iteratively())


class InfoView(APIView, StartupFundings):
    # make a skeleton code...
    # not finished yet

    def validate_request(self, platform):
        if platform is not None and platform not in self.Platforms:
            return False
        if status is not None and status not in self.Status:
            return False
        return True

    def get_from_wadiz(self, identifier) -> dict:
        pass

    def get_from_ohmycompany(self, identifier) -> dict:
        pass

    def get_info(self, platform, identifier) -> dict:
        if platform == 'wadiz':
            return self.get_from_wadiz(identifier)
        if platform == 'ohmycompany':
            return self.get_from_ohmycompany(identifier)
        raise Exception("Something Wrong!")

    def get(self, request, platform, identifier):
        if not self.validate_request(platform):
            return Response({"msg": response_msg.ERROR400}, status=status.HTTP_400_BAD_REQUEST)

        info = self.get_info(platform, identifier)
        return Response(info, status=status.HTTP_200_OK)
