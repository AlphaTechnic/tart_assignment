from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import response_msg
from startup_fundings_app.crawler.crawler import WadizCrawler, OhMyCompanyCrawler
import startup_fundings_app.crawler.selector as sel
# import ray

Platforms = ['wadiz', 'ohmycompany']
Status = ['scheduled', 'open', 'closed']
NumCPUs = 2


class ListView(APIView):
    def get_from_wadiz(self, status) -> list:
        uri = "https://www.wadiz.kr/web/winvest/startup"
        crawler = WadizCrawler(uri, sel.wadiz_card_selector, sel.wadiz_company_selector, sel.wadiz_identifier_selector)
        return crawler.crawl()

    def get_from_ohmycompany(self, status) -> list:
        uri = "https://www.ohmycompany.com/invest/list"
        crawler = OhMyCompanyCrawler(uri, sel.ohmycompany_card_selector)
        return crawler.crawl()

    #@ray.remote
    def get_info(self, platform, status) -> list:
        # platform에서 정보가져와서 가져옴
        if platform == 'wadiz':
            return self.get_from_wadiz(status)
        if platform == 'ohmycompany':
            return self.get_from_ohmycompany(status)
        raise Exception("Something Wrong!")

    def validate_request(self, platform, status):
        if platform is not None and platform not in Platforms:
            return False
        if status is not None and status not in Status:
            return False
        return True

    def get(self, request):
        platform = request.GET.get('platform')
        status = request.GET.get('status')

        # 요청의 유효성 검사
        if not self.validate_request(platform, status):
            return Response({"msg": response_msg.ERROR400}, status=status.HTTP_400_BAD_REQUEST)

        # platform 이 지정된 경우
        if platform is not None:
            info = self.get_info(platform, status)
            return Response(data=info)

        # platform 이 지정되지 않아서 모든 플랫폼을 불러오는 경우

        # multiprocessing으로 ray를 사용하려 했으나 라이브러리 호환성 문제 ㅜ
        # ray.init(num_cpus=NumCPUs)
        # merged_info = []
        # for platform in Platforms:
        #     merged_info.extend(self.get_info.remote(platform, status))
        # results = ray.get(merged_info)

        merged_info = []
        for platform in Platforms:
            merged_info.extend(self.get_info(platform, status))

        return Response(merged_info)


class InfoView(APIView):
    # 미완성 ㅜ
    def validate_request(self, platform):
        if platform is not None and platform not in Platforms:
            return False
        if status is not None and status not in Status:
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
