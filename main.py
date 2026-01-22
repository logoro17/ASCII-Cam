import sys, cv2, numpy as np, pyvirtualcam
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSlider, QLineEdit, QPushButton, QColorDialog, QLabel
from PyQt5.QtCore import QTimer, Qt

class SuperAscii(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Controller")
        
        # --- Default Settings ---
        self.cap = cv2.VideoCapture(0)
        self.chars = "MWB&@#$kdbpxoq0unvrtclij!=-~_:. " 
        self.color = (0, 255, 0)
        self.bright = 0
        self.contrast = 1.0
        self.inverted = False
        self.vcam = None

        # --- UI Setup ---
        layout = QVBoxLayout()
        
        # Characters
        self.char_input = QLineEdit(self.chars)
        self.char_input.textChanged.connect(lambda t: setattr(self, 'chars', t if t else " "))
        layout.addWidget(QLabel("Character Set:"))
        layout.addWidget(self.char_input)

        # Brightness
        self.b_slider = QSlider(Qt.Horizontal)
        self.b_slider.setRange(-100, 100)
        self.b_slider.setValue(0)
        self.b_slider.valueChanged.connect(lambda v: setattr(self, 'bright', v))
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.b_slider)

        # Contrast
        self.c_slider = QSlider(Qt.Horizontal)
        self.c_slider.setRange(5, 40) 
        self.c_slider.setValue(10)
        self.c_slider.valueChanged.connect(lambda v: setattr(self, 'contrast', v / 10.0))
        layout.addWidget(QLabel("Contrast:"))
        layout.addWidget(self.c_slider)

        # Invert Button
        self.inv_btn = QPushButton("INVERT SYMBOLS")
        self.inv_btn.setCheckable(True)
        self.inv_btn.clicked.connect(lambda: setattr(self, 'inverted', self.inv_btn.isChecked()))
        layout.addWidget(self.inv_btn)

        # Color & VCam
        btn_color = QPushButton("Set Color")
        btn_color.clicked.connect(self.set_color)
        layout.addWidget(btn_color)

        self.btn_start = QPushButton("TOGGLE VCAM")
        self.btn_start.clicked.connect(self.toggle_vcam)
        layout.addWidget(self.btn_start)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.process)
        self.timer.start(30)

    def set_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.color = (c.blue(), c.green(), c.red())

    def toggle_vcam(self):
        if self.vcam: 
            self.vcam.close(); self.vcam = None
            self.btn_start.setText("TOGGLE VCAM")
        else:
            w, h = int(self.cap.get(3)), int(self.cap.get(4))
            self.vcam = pyvirtualcam.Camera(width=w, height=h, fps=30)
            self.btn_start.setText("VCAM ACTIVE")

    def process(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        h, w = frame.shape[:2]
        cols, rows = 120, 45
        small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (cols, rows))
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        
        cw, ch = w // cols, h // rows
        num_chars = len(self.chars)

        for y in range(rows):
            for x in range(cols):
                pixel = small[y, x]
                
                # Math: Contrast -> Brightness
                pixel = (pixel - 128) * self.contrast + 128 + self.bright
                
                # Mapping
                val = np.clip(pixel / 255, 0, 1)
                
                # Inversion logic
                if self.inverted:
                    val = 1.0 - val
                
                idx = int(val * (num_chars - 1))
                cv2.putText(canvas, self.chars[idx], (x * cw, y * ch + ch), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.color, 1)

        if self.vcam: self.vcam.send(canvas)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SuperAscii()
    win.show()
    sys.exit(app.exec_())