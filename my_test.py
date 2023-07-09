import cv2

cap = cv2.VideoCapture(0)

# Определите кодек и создайте объект записи видео
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

while True:
    # Захватите кадр с веб-камеры
    ret, frame = cap.read()

    # Если захват прошел успешно, отобразите кадр и запишите его в видеофайл
    if ret:
        cv2.imshow('Frame', frame)
        out.write(frame)

    # Прервите цикл, если нажата клавиша 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освободите ресурсы
cap.release()
out.release()
cv2.destroyAllWindows()
