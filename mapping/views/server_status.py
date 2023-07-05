from time import time

from rest_framework import permissions, status, views, viewsets
from rest_framework.response import Response


class StatusReport(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request):
        print(f"[serverStatus/StatusReport list] requested @ {time.strftime('%c')}")
        for key, value in request.headers.items():
            print(f"[serverStatus/StatusReport list] {key} : {value}")
        print(f"[serverStatus/StatusReport list] {request.data}")
        return Response("All systems are go", status=418)
        # return Response('All systems are go', status=status.HTTP_200_OK)
