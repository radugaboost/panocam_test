from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators import gzip
from werkzeug.utils import secure_filename
from panocam_app.models import DetectionModel
# from rknn.api import RKNN

from panocam_app.models import Camera
from panocam_app.scripts import THREADED_CAMERAS
import os


def video_list(request):
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


def get_available_cameras():
    return Camera.objects.all()


def generate(camera_id: int):
    capture = THREADED_CAMERAS[camera_id]
    while True:
        jpeg = capture.show_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')


@gzip.gzip_page
def camera(request, camera_id: int):
    if camera_id in THREADED_CAMERAS.keys():
        return StreamingHttpResponse(
            generate(camera_id),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    return HttpResponseNotFound()


def check_camera(request, camera_id: int):
    if camera_id in THREADED_CAMERAS.keys():
        return HttpResponse()
    return HttpResponseNotFound()


@gzip.gzip_page
def camera_stream(request):
    return render(request, 'camera.html', {'cameras': get_available_cameras()})


def upload_page(request):
    return render(request, "load_model.html")


UPLOAD_FOLDER = os.path.abspath('panocam_app/models')


def allowed_file(filename):
    return filename.split('.')[-1] in ['tflite', 'onnx']


def save_model_file(filename, saved_path, description, model_name=None):
    saved_model = os.path.join(UPLOAD_FOLDER, saved_path)
    file_prefix = os.path.splitext(filename)[0]
    model_name = file_prefix if model_name is None else model_name

    # rknn = RKNN()
    rknn.config(channel_mean_value='103.94 116.78 123.68 58.82', reorder_channel='0 1 2')

    if filename.endswith(".tflite"):
        # Load a TensorFlow Lite model
        model = rknn.load_tflite(model=saved_model)
    else:
        # Load an ONNX model
        model = rknn.load_onnx(model=saved_model)

    if model != 0:
        return HttpResponse('Failed to load model')

    rknn_model = os.path.join(UPLOAD_FOLDER, file_prefix)
    saved_rknn_model = rknn.export_rknn(''.join([rknn_model, '.rknn']))
    if saved_rknn_model != 0:
        return HttpResponse('Failed to save model')
    DetectionModel.objects.create(name=model_name, description=description, file_path=saved_model)
    os.remove(saved_model)
    return HttpResponse('File uploaded and processed successfully')


def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if allowed_file(uploaded_file.name):
            filename = secure_filename(uploaded_file.name)
            fs = FileSystemStorage(location=UPLOAD_FOLDER)
            path_to_save = f'pre-saved-{filename}'
            fs.save(path_to_save, uploaded_file)
            return save_model_file(filename, path_to_save, request.POST.get('description'), request.POST.get('name'))
        else:
            return HttpResponse('Invalid file format')
    return HttpResponse('Method is not allowed')
