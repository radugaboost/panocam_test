from django.http import (
    JsonResponse, HttpRequest
)
from django.shortcuts import render


def area_detection_view(request: HttpRequest) -> JsonResponse:
    return render(request, 'area_detection.html')
