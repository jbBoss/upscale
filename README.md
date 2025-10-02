# SimSwap Super-Resolution Demo

<<<<<<< HEAD
A minimal tool that upsamples images 4× using the Real-ESRGAN model. You can run it from the CLI **or** via the included Flask web UI with drag & drop uploading.
=======
A minimal script that upsamples `source.png` using the Real-ESRGAN model (x4 scale) through the `py_real_esrgan` wrapper.
>>>>>>> 3c57f4522786e0671a18d30f5778165443c6f258

## Quick start

```powershell
# inside the project root
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
<<<<<<< HEAD

# Option 1: Upscale from the CLI (defaults to source.png -> output.png)
python .\main.py [input_image] [output_image]

# Option 2: Launch the web UI and open http://127.0.0.1:5000
python .\app.py
```

The model weights download automatically on first use. Web uploads are capped at 20&nbsp;MB and accept png, jpg, jpeg, webp, or bmp.
=======
python .\main.py
```

The script will download Real-ESRGAN weights on the first run and write the super-resolved image to `output.png`.
>>>>>>> 3c57f4522786e0671a18d30f5778165443c6f258
