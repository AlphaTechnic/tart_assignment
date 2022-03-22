from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import response_msg

Platforms = ['wadiz', 'ohmycompany']
Status = ['scheduled', 'open', 'closed']


class ListView(APIView):
    # 공통정보 : 기업명, title, 투자액, 카테고리,

    def get_from_wadiz(self, status) -> list:
        pass

    def get_from_ohmycompany(self, status) -> list:
        pass

    def get_info(self, platform, status) -> list:
        # platform에서 정보가져와서 가져옴
        if platform == 'wadiz':
            return self.get_from_wadiz(status)
        if platform == 'ohmycompany':
            return self.get_from_ohmycompany(status)
        raise Exception("Something Wrong!")

    def merge_info(self, info_list) -> list:
        # platform1에서 온 list of dict, platform2에서 온 list of dict 합침
        pass

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
            return Response(info, status=status.HTTP_200_OK)

        # platform 이 지정되지 않아서 모든 플랫폼을 불러오는 경우
        infos = []
        for p in range(Platforms):
            info = self.get_info(p, status)
            infos.append(info)
        merged_info = self.merge_info(infos)

        return Response(merged_info, status=status.HTTP_200_OK)


class InfoView(APIView):
    def validate_request(self, platform):
        if platform is not None and platform not in Platforms:
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
