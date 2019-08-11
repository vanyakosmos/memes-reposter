from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request


@api_view()
@permission_classes([IsAdminUser])
def index(request: Request):
    return render(request, 'reddit/index.html')
