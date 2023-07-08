import fcntl
import os
import subprocess


# Функция для получения информации о доступных устройствах видеозахвата
def get_video_devices():
    video_devices = []

    cmd = 'v4l2-ctl --list-devices'
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
    for i in output.decode().split('\t')[1:]:
        if 'video' in i:
            video_devices.append(i.rstrip())

    return video_devices


# Получение информации о доступных устройствах видеозахвата
print(get_video_devices())

# Вывод списка устройств
# for device in devices:
#     print(device)
#