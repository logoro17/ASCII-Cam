readme: |
  # SuperAscii 📸
  > **Turn your reality into code.**
  > A real-time webcam-to-ASCII converter with Virtual Camera support. Stream yourself as raw text to Zoom, Discord, OBS, or Teams.

  <br />
  <div align="center">
    <img src="https://via.placeholder.com/800x400.png?text=SuperAscii+Demo+Screenshot" alt="SuperAscii Screenshot" width="800">
    <p><em>(Replace this link with a real screenshot of your app!)</em></p>
  </div>
  <br />

  ## ⚡ Features

  * **Real-Time Conversion:** High-performance mapping of webcam frames to ASCII characters using OpenCV.
  * **Virtual Camera Support:** Pipe your ASCII video directly into other apps (Zoom, Discord, etc.) using `pyvirtualcam`.
  * **Full Customization:**
      * 🎛 **Brightness & Contrast:** Sliders to tweak the image logic on the fly.
      * 🔡 **Custom Charset:** Type your own characters to change the texture of the video.
      * 🎨 **Color Picker:** Choose any hex color for your ASCII output.
      * 🔄 **Invert Mode:** Toggle for "Matrix" style (dark background) or paper style (light background).
  * **GUI Control:** Built with **PyQt5** for a responsive and clean interface.

  ## 🛠️ Built With

  * [Python](https://www.python.org/) - The core language.
  * [OpenCV](https://opencv.org/) - For image processing and capture.
  * [PyQt5](https://pypi.org/project/PyQt5/) - For the graphical user interface.
  * [PyVirtualCam](https://github.com/letmaik/pyvirtualcam) - To simulate a hardware webcam.
  * [NumPy](https://numpy.org/) - For high-speed matrix operations.

  ## 🚀 Getting Started

  To get a local copy up and running, follow these simple steps.

  ### Prerequisites

  You need Python installed. You also need a virtual camera driver if you want to use the "Toggle VCam" feature:
  * **Windows:** Install [OBS Studio](https://obsproject.com/) (includes Virtual Cam) or [Unity Capture](https://github.com/schellingb/UnityCapture).
  * **macOS:** Install [OBS Studio](https://obsproject.com/).
  * **Linux:** Ensure `v4l2loopback` is installed.

  ### Installation

  1. **Clone the repo**
      ```sh
      git clone [https://github.com/logoro17/ASCII-Cam.git](https://github.com/logoro17/ASCII-Cam.git)
      cd SuperAscii
      ```

  2. **Install dependencies**
      ```sh
      pip install opencv-python numpy pyvirtualcam PyQt5
      ```

  3. **Run the App**
      ```sh
      python main.py
      ```

  ## 🎮 Usage

  1. **Launch the App:** The GUI will open and your default webcam will start.
  2. **Adjust the Look:**
      * Use the **Brightness** slider to filter out background noise.
      * Use the **Contrast** slider to sharpen the edges.
  3. **Go Virtual:**
      * Click **TOGGLE VCAM**.
      * Open your meeting app (e.g., Zoom).
      * Select the virtual camera (e.g., "OBS Virtual Camera" or "Unity Video") as your video source.
  4. **Have Fun:** Try changing the "Character Set" to just binary `01` or `Matrix` style characters!

  ## 🧩 Code Overview

  The magic happens in the `process` loop inside `main.py`:

  ```python
  # Downscale the image to 'pixelate' it
  small = cv2.resize(frame, (cols, rows))

  # Map pixel brightness to character index
  val = np.clip(pixel / 255, 0, 1)
  idx = int(val * (len(chars) - 1))
