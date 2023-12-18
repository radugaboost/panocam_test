import os
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect

from panocam_app.db.models import VideoRecord


def video_list(request):
    return render(request, 'video_list.html')


def video_page(request, video_id):
    if not VideoRecord.objects.filter(id=video_id):
        return redirect('/videos')
    return render(request, 'video_page.html')


def get_video_records(request):
    records = [{'id': record.id, 'name': record.name} for record in VideoRecord.objects.all()[::-1]]
    return JsonResponse(records, status=200, safe=False)


def get_video_data(request, video_id):
    record = VideoRecord.objects.filter(id=video_id).first()
    if not record:
        return JsonResponse('Not found', safe=404)
    response = {
        'name': record.name,
        'start': record.start,
        'end': record.end,
        'saving_path': record.saving_path,
    }
    return JsonResponse(response, status=200, safe=False)


def get_video_file(request, video_id):
    record = VideoRecord.objects.filter(id=video_id).first()
    if not record:
        return JsonResponse({'message', "Not found"}, status=404)

    video_path = record.saving_path

    if not os.path.exists(video_path):
        return JsonResponse({'message', "Not found"}, status=404)

    try:
        return FileResponse(open(video_path, 'rb'), content_type='video/mp4', status=200)
    except FileNotFoundError:
        return JsonResponse({'message', "Not found"}, status=404)


def drop_video_record(request, video_id):
    video_record = VideoRecord.objects.filter(id=video_id)
    if not video_record:
        return JsonResponse({'message', "Not found"}, status=404)
    video = video_record.first()
    video_path = video.saving_path
    try:
        video_record.delete()
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Not found'}, status=404)
    os.remove(video_path)
    return JsonResponse({'message': 'No content'}, status=204, safe=False)


def drop_video_records(request):
    video_record = VideoRecord.objects.all()
    paths = [record.saving_path for record in video_record]
    for record in video_record:
        try:
            record.delete()
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'Not found'}, status=404)

    for path in paths:
        if os.path.exists(path):
            os.remove(path)
    return JsonResponse({'message': 'No content'}, status=204)
