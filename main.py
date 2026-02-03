# ==============================================================================
#   /$$      /$$  /$$$$$$  /$$$$$$$  /$$   /$$ /$$$$$$ /$$   /$$  /$$$$$$ 
#  | $$  /$ | $$ /$$__  $$| $$__  $$| $$$ | $$|_  $$_/| $$$ | $$ /$$__  $$
#  | $$ /$$$| $$| $$  \ $$| $$  \ $$| $$$$| $$  | $$  | $$$$| $$| $$  \__/
#  | $$/$$ $$ $$| $$$$$$$$| $$$$$$$/| $$ $$ $$  | $$  | $$ $$ $$| $$ /$$$$
#  | $$$$_  $$$$| $$__  $$| $$__  $$| $$  $$$$  | $$  | $$  $$$$| $$|_  $$
#  | $$$/ \  $$$| $$  | $$| $$  \ $$| $$ \  $$  | $$  | $$\  $$$| $$  \ $$
#  | $$/   \  $$| $$  | $$| $$  | $$| $$  \ $$ /$$$$$$| $$ \  $$|  $$$$$$/
#  |__/     \__/|__/  |__/|__/  |__/|__/  \__/|______/|__/  \__/ \______/ 
#                                                                           
#   [!] CRITICAL: IF YOU CAN READ THIS, PLEASE FORK FIRST!
# ==============================================================================

import sys, cv2, numpy as np, pyvirtualcam
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSlider, QLineEdit, QPushButton, 
                             QColorDialog, QLabel, QComboBox, QGroupBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class SuperAscii(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Cam - Dual Mode")
        
        # --- Default Settings ---
        self.cap = cv2.VideoCapture(0) # Mengambil webcam asli
        self.chars = "MWB&@#$kdbpxoq0unvrtclij!=-~_:. " 
        self.color = (0, 255, 0)
        self.bright = 0
        self.contrast = 1.0
        self.inverted = False
        self.vcam = None
        
        # --- BARU: Mode Switch Variable ---
        self.ascii_mode = True # True = ASCII, False = Normal Camera
        
        # --- Setting Resolusi ---
        self.res_options = [
            (640, 480, "640x480 (OmeTV Safe)"),
            (800, 600, "800x600 (Medium)"),
            (1280, 720, "1280x720 (HD)"),
            (320, 240, "320x240 (Low Res)")
        ]
        self.target_w = 640
        self.target_h = 480

        # --- UI SETUP ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # === KIRI: PREVIEW ===
        video_layout = QVBoxLayout()
        self.preview_label = QLabel("Camera Preview Loading...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("border: 2px solid #444; background-color: black;")
        video_layout.addWidget(self.preview_label)
        video_layout.addStretch()
        main_layout.addLayout(video_layout, 3)

        # === KANAN: KONTROL ===
        controls_group = QGroupBox("Control Panel")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        # 1. Resolusi
        controls_layout.addWidget(QLabel("Resolution:"))
        self.combo_res = QComboBox()
        for r in self.res_options:
            self.combo_res.addItem(r[2])
        self.combo_res.currentIndexChanged.connect(self.change_resolution)
        controls_layout.addWidget(self.combo_res)

        # --- BARU: TOMBOL MODE (NORMAL vs ASCII) ---
        self.btn_mode = QPushButton("MODE: ASCII ART")
        self.btn_mode.setMinimumHeight(40)
        self.btn_mode.setStyleSheet("background-color: #007acc; color: white; font-weight: bold;")
        self.btn_mode.clicked.connect(self.toggle_mode)
        controls_layout.addWidget(self.btn_mode)
        
        # 2. Karakter
        controls_layout.addWidget(QLabel("Character Set:"))
        self.char_input = QLineEdit(self.chars)
        self.char_input.textChanged.connect(lambda t: setattr(self, 'chars', t if t else " "))
        controls_layout.addWidget(self.char_input)

        # 3. Brightness
        controls_layout.addWidget(QLabel("Brightness:"))
        self.b_slider = QSlider(Qt.Horizontal)
        self.b_slider.setRange(-100, 100)
        self.b_slider.setValue(0)
        self.b_slider.valueChanged.connect(lambda v: setattr(self, 'bright', v))
        controls_layout.addWidget(self.b_slider)

        # 4. Contrast
        controls_layout.addWidget(QLabel("Contrast:"))
        self.c_slider = QSlider(Qt.Horizontal)
        self.c_slider.setRange(5, 40) 
        self.c_slider.setValue(10)
        self.c_slider.valueChanged.connect(lambda v: setattr(self, 'contrast', v / 10.0))
        controls_layout.addWidget(self.c_slider)

        # 5. Buttons
        self.inv_btn = QPushButton("INVERT COLORS")
        self.inv_btn.setCheckable(True)
        self.inv_btn.clicked.connect(lambda: setattr(self, 'inverted', self.inv_btn.isChecked()))
        controls_layout.addWidget(self.inv_btn)

        btn_color = QPushButton("CHANGE TEXT COLOR")
        btn_color.clicked.connect(self.set_color)
        controls_layout.addWidget(btn_color)

        controls_layout.addStretch()

        # 6. Start VCam
        self.btn_start = QPushButton("TOGGLE VCAM")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.btn_start.clicked.connect(self.toggle_vcam)
        controls_layout.addWidget(self.btn_start)

        main_layout.addWidget(controls_group, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.process)
        self.timer.start(30)

    # --- BARU: FUNGSI GANTI MODE ---
    def toggle_mode(self):
        self.ascii_mode = not self.ascii_mode
        if self.ascii_mode:
            self.btn_mode.setText("MODE: ASCII ART")
            self.btn_mode.setStyleSheet("background-color: #007acc; color: white; font-weight: bold;")
        else:
            self.btn_mode.setText("MODE: NORMAL CAMERA")
            self.btn_mode.setStyleSheet("background-color: #gray; color: black; font-weight: bold;")

    def change_resolution(self, index):
        w, h, label = self.res_options[index]
        self.target_w = w
        self.target_h = h
        self.preview_label.setMinimumSize(w, h)
        self.resize(w + 300, h + 50) 
        if self.vcam:
            self.toggle_vcam()
            self.toggle_vcam()

    def set_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.color = (c.blue(), c.green(), c.red())

    def toggle_vcam(self):
        if self.vcam: 
            self.vcam.close()
            self.vcam = None
            self.btn_start.setText("TOGGLE VCAM")
            self.btn_start.setStyleSheet("background-color: none; font-weight: bold; font-size: 14px;")
        else:
            try:
                # Update device='/dev/video2' sesuai hasil diagnosa Anda tadi
                self.vcam = pyvirtualcam.Camera(width=self.target_w, height=self.target_h, fps=30, 
                                                fmt=pyvirtualcam.PixelFormat.BGR, 
                                                device='/dev/video2')
                self.btn_start.setText(f"VCAM ACTIVE")
                self.btn_start.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 14px;")
            except Exception as e:
                self.btn_start.setText("ERROR (See Terminal)")
                print(e)

    def process(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        t_w, t_h = self.target_w, self.target_h
        
        # --- LOGIKA CABANG (NORMAL vs ASCII) ---
        if self.ascii_mode:
            # === PROSES ASCII (Jika Mode ASCII Nyala) ===
            cols = t_w // 6  
            rows = t_h // 12
            if cols < 1: cols=1
            if rows < 1: rows=1
            
            cw, ch = t_w // cols, t_h // rows
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            small = cv2.resize(gray, (cols, rows))

            # Math
            small_float = small.astype(float)
            processed = (small_float - 128) * self.contrast + 128 + self.bright
            val_matrix = np.clip(processed / 255, 0, 1)

            if self.inverted:
                val_matrix = 1.0 - val_matrix
            
            num_chars = len(self.chars)
            idx_matrix = (val_matrix * (num_chars - 1)).astype(int)

            canvas = np.zeros((t_h, t_w, 3), dtype=np.uint8)

            for y in range(rows):
                for x in range(cols):
                    char = self.chars[idx_matrix[y, x]]
                    cv2.putText(canvas, char, (x * cw, y * ch + ch), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.color, 1)
        else:
            # === PROSES NORMAL (Jika Mode Normal) ===
            # Cukup resize gambar asli agar pas dengan resolusi Virtual Cam
            canvas = cv2.resize(frame, (t_w, t_h))

        # --- PENGIRIMAN ---
        # Kirim canvas (baik itu hasil ASCII atau hasil Resize Normal) ke Virtual Cam
        if self.vcam: 
            self.vcam.send(canvas)

        # Update Preview GUI
        rgb_image = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.preview_label.setPixmap(QPixmap.fromImage(qt_image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SuperAscii()
    win.show()
    sys.exit(app.exec_())
