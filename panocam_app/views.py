import shutil
import cv2
from json import loads
from django.http import HttpRequest
import numpy as np

from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators import gzip
from werkzeug.utils import secure_filename
from panocam_app.models import DetectionModel
from panocam_app.streaming.camera import ThreadedCamera
# from rknn.api import RKNN

from panocam_app.models import Camera
from panocam_app.scripts import THREADED_CAMERAS
import os


def video_list(request: HttpRequest) -> render:
    video_dir = './panocam_app/static/videos'
    video_files = os.listdir(video_dir)
    video_list = []

    for filename in video_files:
        if filename.endswith('.mp4'):
            video_path = os.path.join('/static/videos/', filename)
            video_list.append(video_path)

    context = {
        'video_list': video_list
    }

    return render(request, 'video.html', context)


def get_available_cameras() -> list:
    return Camera.objects.all()

def add_area(request: HttpRequest, camera_id: int) -> JsonResponse:
    camera = THREADED_CAMERAS.get(camera_id)
    if camera:
        areas = camera.areas
        data = request.body.decode('utf-8')
        json_data = loads(data)
        frame = camera.show_frame()
        points = json_data['points']
        height, width = json_data['shape']
        init_height, init_width = frame.shape[:2]
        x_modifier, y_modifier = init_width / width, init_height / height

        top, height, left, width = 0, 0, 0, 0
        modified_points = list()
        for point in points:
            x, y = int(point['x'] * x_modifier), int(point['y'] * y_modifier)
            modified_points.append((x, y))
            if not top:
                top, height = y, y
                left, width = x, x
                continue
            top, height = min(top, y), max(height, y)
            left, width = min(left, x), max(width, x)

        area_id = len(areas) + 1
        areas[area_id] = [(top, left, width, height), modified_points]
        return JsonResponse(data={'area_id': area_id}, status=201)

    return JsonResponse(data='Not found',status=404)

def generate(camera: ThreadedCamera, area: list):
    while True:
        frame = camera.show_frame()
        if area:
            borders = area[0]
            points = area[1]

            mask = np.zeros(frame.shape, dtype=np.uint8)
            roi_corners = np.array(points, dtype=np.int32)
            channel_count = frame.shape[2]
            ignore_mask_color = (255,) * channel_count
            cv2.fillPoly(mask, [roi_corners], ignore_mask_color)
            masked_image = cv2.bitwise_and(frame, mask)

            top, left = borders[0], borders[1]
            width = borders[2] - left
            height = borders[3] - top

            frame = masked_image[top:top + height, left:left + width]

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@gzip.gzip_page
def camera(
    request: HttpRequest, camera_id: int, area_id: int = None
) -> StreamingHttpResponse or HttpResponseNotFound:
    camera = THREADED_CAMERAS.get(camera_id)

    if camera:
        area = camera.areas.get(area_id)
        return StreamingHttpResponse(
            generate(camera, area),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    return HttpResponseNotFound()


def check_camera(
    request: HttpRequest, camera_id: int
) -> HttpResponse or HttpResponseNotFound:
    if camera_id in THREADED_CAMERAS.keys():
        return HttpResponse()
    return HttpResponseNotFound()


@gzip.gzip_page
def camera_stream(request: HttpRequest) -> render:
    return render(request, 'camera.html', {'cameras': get_available_cameras()})


def upload_page(request: HttpRequest) -> render:
    models = DetectionModel.objects.all()
    return render(request, 'load_model.html', {'models': models})


UPLOAD_FOLDER = os.path.abspath('panocam_app/storage/models')


def change_model_status(request: HttpRequest, model_id: int) -> HttpResponse:
    model = DetectionModel.objects.filter(id=model_id).first()
    if model is not None:
        model.active = not model.active
        model.save()
        return HttpResponse({'message': 'Model status changed'})
    else:
        return HttpResponse({'message': 'Model not found'}, status=404)


def allowed_file(filename: str) -> bool:
    return filename.split('.')[-1] in ['tflite', 'onnx']


def save_model_file(model_path, image_path, description, model_name=None):
    model_file_name = os.path.basename(model_path)
    model_file_prefix = os.path.splitext(model_file_name)[0]
    model_dir = os.path.dirname(model_path)

    with open(os.path.join(model_dir, 'dataset.txt'), 'w') as dataset:
        dataset.write(image_path)

    rknn = RKNN()
    rknn.config(channel_mean_value='103.94 116.78 123.68 58.82', reorder_channel='0 1 2')

    if model_file_name.endswith('.tflite'):
        # Load a TensorFlow Lite model
        model = rknn.load_tflite(model=model_file_prefix)
    else:
        # Load an ONNX model
        model = rknn.load_onnx(model=model_file_prefix)

    if model != 0:
        shutil.rmtree(model_dir, ignore_errors=True)
        return HttpResponse('Failed to load model')

    ret = rknn.build(do_quantization=True, dataset=os.path.join(model_dir, 'dataset.txt'))
    if ret != 0:
        shutil.rmtree(model_dir, ignore_errors=True)
        return HttpResponse('Failed to build model')

    rknn_model = os.path.join(os.path.dirname(model_path), f'{model_file_prefix}.rknn')
    saved_rknn_model = rknn.export_rknn(rknn_model)

    if saved_rknn_model != 0:
        shutil.rmtree(model_dir, ignore_errors=True)
        return HttpResponse('Failed to save model')

    DetectionModel.objects.create(name=model_name, description=description, file_path=rknn_model)
    os.remove(model_path)
    return HttpResponse('File uploaded and processed successfully')


def upload_file(request: HttpRequest):
    if request.method == 'POST':
        model_file = request.FILES.get('file')
        image_file = request.FILES.get('image')
        description = request.POST.get('description')
        model_name = request.POST.get('name')

        if allowed_file(model_file.name) and image_file:
            folder_to_save = os.path.join(UPLOAD_FOLDER, request.POST.get('name'))
            os.mkdir(folder_to_save)
            fs = FileSystemStorage(location=folder_to_save)

            model_to_save = os.path.join(folder_to_save, f'temp_{secure_filename(model_file.name)}')
            image_to_save = os.path.join(folder_to_save, secure_filename(image_file.name))

            fs.save(model_to_save, model_file)
            fs.save(image_to_save, image_file)
            return save_model_file(model_to_save, image_to_save, description, model_name)
        else:
            return HttpResponse('Invalid file format')
    return HttpResponse('Method is not allowed')


def delete_model(request: HttpRequest, model_id: int) -> HttpResponse:
    model = DetectionModel.objects.filter(id=model_id).first()
    if model:
        model_dir = os.path.dirname(model.file_path)
        shutil.rmtree(model_dir, ignore_errors=True)
        model.delete()
        return HttpResponse({"message": "Модель успешно удалена"})
    else:
        return HttpResponse({"error": "Модель не найдена"})
