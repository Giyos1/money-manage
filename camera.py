import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from PIL import Image


class CameraApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(CameraApp, self).__init__()
        self.setWindowTitle("Camera App")
        self.setFixedSize(640, 480)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setGeometry(QtCore.QRect(0, 0, 640, 480))
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.capture_button = QtWidgets.QPushButton("Capture Image", self)
        self.capture_button.setGeometry(QtCore.QRect(270, 400, 100, 30))
        self.capture_button.clicked.connect(self.capture_image)

        self.video_capture = cv2.VideoCapture(0)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30ms

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert frame from BGR to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert frame to QImage
            qimage = QtGui.QImage(
                frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QtGui.QImage.Format_RGB888
            )
            # Convert QImage to QPixmap
            pixmap = QtGui.QPixmap.fromImage(qimage)
            # Scale pixmap to fit the label size
            pixmap = pixmap.scaled(
                self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio
            )
            # Set the pixmap as the label's image
            self.image_label.setPixmap(pixmap)

    def capture_image(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert frame from BGR to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert frame to PIL Image
            image = Image.fromarray(frame_rgb)
            # Save the image to disk
            image.save("captured_image.jpg")

    def closeEvent(self, event):
        self.video_capture.release()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
