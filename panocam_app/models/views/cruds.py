import shutil, os
from django.shortcuts import render
from django.http import (
    HttpResponse, HttpRequest
)
from django.core.files.storage import FileSystemStorage
from werkzeug.utils import secure_filename
from panocam_app.db.models import DetectionModel
# from rknn.api import RKNN

UPLOAD_FOLDER = os.path.abspath('panocam_app/storage/models')

def upload_page(request: HttpRequest) -> render:
    models = DetectionModel.objects.all()
    return render(request, 'load_model.html', {'models': models})


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
