from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

import base64


class Permission_Validation_access(permissions.BasePermission):
    """
    Global permission check - rights to the translation validation module
    """
    def has_permission(self, request, view):
        if 'validation | access' in request.user.groups.values_list('name', flat=True):
            return True

class ingestAuditEvent(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]
    def create(self, request):
        print(f"#### NTS #### POST request received\n#### NTS #### {request.body}")
        
        try:
        

            message_bytes = base64.b64decode(request.body)
            message = message_bytes.decode('utf-8')
            print(f"{message}")
        except Exception as e:
            print(e)

        return Response({
            'success' : True
        })
        
    def retrieve(self, request, pk=None):
        print(f"#### NTS #### RETRIEVE request received\n#### NTS #### {pk} / {request.body}")

        try:
            message_bytes = base64.b64decode(request.body)
            message = message_bytes.decode('utf-8')
            print(f"{message}")
        except Exception as e:
            print(e)

        return Response({
            'success' : True
        })

    def put(self, request):
        print(f"#### NTS #### PUT request received\n#### NTS #### {request.body}")

        try:
            message_bytes = base64.b64decode(request.body)
            message = message_bytes.decode('utf-8')
            print(f"{message}")
        except Exception as e:
            print(e)

        return Response({
            'success' : True
        })

    def list(self, request):
        print(f"#### NTS #### LIST request received\n#### NTS #### {request.body}")
        
        try:
            message_bytes = base64.b64decode(request.body)
            message = message_bytes.decode('utf-8')
            print(f"{message}")
        except Exception as e:
            print(e)
            
        return Response({
            'success' : True
        })
