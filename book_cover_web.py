#!/usr/bin/env python3
"""
Herramienta web para detectar y recortar portadas de libros físicos
Versión 2: Usa detección de contornos en lugar de eliminación de fondo
"""

from flask import Flask, render_template_string, request, send_file, jsonify
from PIL import Image
import cv2
import numpy as np
import io
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detector de Portadas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 1.1em;
        }

        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }

        .info-box h4 {
            color: #1976d2;
            margin-bottom: 8px;
        }

        .info-box ul {
            margin-left: 20px;
            color: #555;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 30px;
        }

        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }

        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
            transform: scale(1.02);
        }

        #fileInput {
            display: none;
        }

        .upload-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }

        .settings-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .setting-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }

        .setting-box h4 {
            color: #333;
            margin-bottom: 15px;
        }

        .color-picker-wrapper {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        #colorPicker {
            width: 60px;
            height: 50px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }

        #colorValue {
            font-family: monospace;
            font-size: 1.1em;
            color: #333;
            font-weight: bold;
        }

        .color-presets {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }

        .color-btn {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.85em;
            background: white;
        }

        .color-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .color-btn.selected {
            border-color: #667eea;
            border-width: 3px;
        }

        .slider-container {
            margin: 15px 0;
        }

        .slider-container label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
        }

        .slider-value {
            text-align: center;
            color: #667eea;
            font-weight: bold;
            margin-top: 5px;
        }

        .process-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }

        .process-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .process-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .status {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-weight: 500;
            display: none;
        }

        .status.loading {
            background: #fff3cd;
            color: #856404;
            display: block;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }

        .result-area {
            display: none;
            margin-top: 30px;
            text-align: center;
        }

        .result-area h3 {
            margin-bottom: 20px;
            color: #28a745;
        }

        .result-area img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }

        .download-btn {
            padding: 15px 40px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }

        .download-btn:hover {
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
        }

        .preview-image {
            max-width: 250px;
            margin: 20px auto;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .settings-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 Detector de Portadas</h1>
        <p class="subtitle">Detecta automáticamente portadas de libros físicos y las centra en un lienzo</p>

        <div class="info-box">
            <h4>💡 Consejos para mejores resultados:</h4>
            <ul>
                <li>Coloca la portada sobre un fondo uniforme y contrastante</li>
                <li>Asegúrate de que la portada esté bien iluminada sin reflejos</li>
                <li>La portada debe estar completamente visible en la foto</li>
                <li>Evita sombras fuertes sobre la portada</li>
            </ul>
        </div>

        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">📸</div>
            <h3>Sube una foto de la portada</h3>
            <p style="color: #666; margin-top: 10px;">JPG, PNG, BMP (máx. 16MB)</p>
            <input type="file" id="fileInput" accept="image/*">
            <div id="preview"></div>
        </div>

        <div class="settings-grid">
            <div class="setting-box">
                <h4>🎨 Color de fondo</h4>

                <div class="color-picker-wrapper">
                    <input type="color" id="colorPicker" value="#FFFFFF">
                    <span id="colorValue">#FFFFFF</span>
                </div>

                <div class="color-presets">
                    <button class="color-btn selected" data-color="#FFFFFF" style="background: #FFFFFF; color: #333;">
                        Blanco
                    </button>
                    <button class="color-btn" data-color="#000000" style="background: #000000; color: white;">
                        Negro
                    </button>
                    <button class="color-btn" data-color="#FF5722" style="background: #FF5722; color: white;">
                        Rojo
                    </button>
                    <button class="color-btn" data-color="#2196F3" style="background: #2196F3; color: white;">
                        Azul
                    </button>
                    <button class="color-btn" data-color="#4CAF50" style="background: #4CAF50; color: white;">
                        Verde
                    </button>
                    <button class="color-btn" data-color="#FFC107" style="background: #FFC107; color: #333;">
                        Amarillo
                    </button>
                </div>
            </div>

            <div class="setting-box">
                <h4>⚙️ Detección</h4>

                <div class="slider-container">
                    <label>Sensibilidad (área mínima)</label>
                    <input type="range" id="minArea" min="0.01" max="0.5" step="0.01" value="0.1">
                    <div class="slider-value" id="minAreaValue">10%</div>
                </div>

                <p style="font-size: 0.85em; color: #666; margin-top: 10px;">
                    Ajusta si no detecta la portada. Menor = más sensible
                </p>
            </div>
        </div>

        <button class="process-btn" id="processBtn" disabled>🔍 Detectar y Procesar</button>

        <div class="status" id="status"></div>

        <div class="result-area" id="resultArea">
            <h3>✅ ¡Portada procesada!</h3>
            <img id="resultImage" src="" alt="Resultado">
            <br>
            <a href="#" class="download-btn" id="downloadBtn" download="portada_procesada.png">⬇️ Descargar Imagen</a>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let selectedColor = '#FFFFFF';
        let minAreaValue = 0.1;

        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const preview = document.getElementById('preview');
        const colorPicker = document.getElementById('colorPicker');
        const colorValue = document.getElementById('colorValue');
        const minArea = document.getElementById('minArea');
        const minAreaValueDisplay = document.getElementById('minAreaValue');
        const processBtn = document.getElementById('processBtn');
        const status = document.getElementById('status');
        const resultArea = document.getElementById('resultArea');
        const resultImage = document.getElementById('resultImage');
        const downloadBtn = document.getElementById('downloadBtn');

        // Drag & Drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        // File selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.type.startsWith('image/')) {
                showStatus('error', 'Por favor selecciona un archivo de imagen');
                return;
            }

            selectedFile = file;

            const reader = new FileReader();
            reader.onload = (e) => {
                preview.innerHTML = `<img src="${e.target.result}" class="preview-image" alt="Preview">`;
            };
            reader.readAsDataURL(file);

            processBtn.disabled = false;
            resultArea.style.display = 'none';
        }

        // Color picker
        colorPicker.addEventListener('input', (e) => {
            selectedColor = e.target.value;
            colorValue.textContent = selectedColor;
            document.querySelectorAll('.color-btn').forEach(btn => btn.classList.remove('selected'));
        });

        // Color presets
        document.querySelectorAll('.color-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedColor = btn.dataset.color;
                colorPicker.value = selectedColor;
                colorValue.textContent = selectedColor;

                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });

        // Min area slider
        minArea.addEventListener('input', (e) => {
            minAreaValue = parseFloat(e.target.value);
            minAreaValueDisplay.textContent = Math.round(minAreaValue * 100) + '%';
        });

        // Process button
        processBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            processBtn.disabled = true;
            showStatus('loading', '🔍 Detectando portada... (puede tardar 5-15 segundos)');
            resultArea.style.display = 'none';

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('color', selectedColor);
            formData.append('min_area', minAreaValue);

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Error al procesar la imagen');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                resultImage.src = url;
                downloadBtn.href = url;

                showStatus('success', '✅ ¡Portada detectada y procesada exitosamente!');
                resultArea.style.display = 'block';

            } catch (error) {
                showStatus('error', '❌ ' + error.message + ' - Prueba ajustando la sensibilidad');
            } finally {
                processBtn.disabled = false;
            }
        });

        function showStatus(type, message) {
            status.className = 'status ' + type;
            status.textContent = message;

            if (type === 'loading') {
                status.innerHTML = message + '<div class="spinner"></div>';
            }
        }
    </script>
</body>
</html>
"""


def order_points(pts):
    """Ordena puntos del contorno"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def score_contour_web(contour, total_area, img_width, img_height):
    """Calcula score para determinar la mejor portada"""
    area = cv2.contourArea(contour)
    area_ratio = area / total_area
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = h / w if w > 0 else 0

    center_x, center_y = x + w/2, y + h/2
    center_dist = np.sqrt((center_x - img_width/2)**2 + (center_y - img_height/2)**2)
    max_dist = np.sqrt((img_width/2)**2 + (img_height/2)**2)
    center_score = 1 - (center_dist / max_dist)

    if area_ratio > 0.95:
        area_score = 0.3
    elif area_ratio > 0.85:
        area_score = 0.6
    else:
        area_score = min(area_ratio / 0.5, 1.0)

    if 1.2 <= aspect_ratio <= 1.8:
        aspect_score = 1.0
    elif 0.55 <= aspect_ratio <= 0.85:
        aspect_score = 0.9
    elif 1.0 <= aspect_ratio <= 2.0:
        aspect_score = 0.7
    else:
        aspect_score = 0.3

    peri = cv2.arcLength(contour, True)
    complexity = peri / (2 * (w + h)) if (w + h) > 0 else 999
    complexity_score = 1.0 if complexity < 1.1 else (0.5 if complexity < 1.3 else 0.2)

    total_score = (area_score * 0.35 + aspect_score * 0.30 +
                   center_score * 0.20 + complexity_score * 0.15)

    return total_score


def detect_book_cover(image_data, min_area_ratio=0.1):
    """Detecta portada usando múltiples estrategias"""

    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo leer la imagen")

    original = img.copy()
    height, width = img.shape[:2]
    total_area = height * width

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((5, 5), np.uint8)

    candidates = []

    # Estrategia 1: Canny estándar
    edges1 = cv2.Canny(blurred, 30, 100)
    dilated1 = cv2.dilate(edges1, kernel, iterations=2)
    contours1, _ = cv2.findContours(dilated1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours1, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(contour) / total_area > min_area_ratio:
            candidates.append(approx)

    # Estrategia 2: Canny sensible
    edges2 = cv2.Canny(blurred, 50, 150)
    dilated2 = cv2.dilate(edges2, kernel, iterations=3)
    contours2, _ = cv2.findContours(dilated2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours2, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(contour) / total_area > min_area_ratio:
            candidates.append(approx)

    # Estrategia 3: Umbralización adaptativa
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    dilated3 = cv2.dilate(thresh, kernel, iterations=2)
    contours3, _ = cv2.findContours(dilated3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours3, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(contour) / total_area > min_area_ratio:
            candidates.append(approx)

    # Estrategia 4: Otsu
    _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    dilated4 = cv2.dilate(thresh_otsu, kernel, iterations=2)
    contours4, _ = cv2.findContours(dilated4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours4, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(contour) / total_area > min_area_ratio:
            candidates.append(approx)

    if not candidates:
        # No se encontraron contornos rectangulares - asumir portada digital
        # Devolver la imagen completa sin transformación de perspectiva
        img_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    # Evaluar candidatos con scoring
    best_score = 0
    book_contour = None

    for approx in candidates:
        contour_full = approx.reshape(-1, 1, 2)
        score = score_contour_web(contour_full, total_area, width, height)
        if score > best_score:
            best_score = score
            book_contour = approx

    if book_contour is None:
        # No se encontró un contorno con score adecuado - asumir portada digital
        img_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    # Ordenar puntos y extraer portada
    pts = book_contour.reshape(4, 2)
    rect = order_points(pts)

    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(original, M, (maxWidth, maxHeight))

    # Convertir de BGR a RGB
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)

    return Image.fromarray(warped_rgb)


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/process', methods=['POST'])
def process():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400

        file = request.files['file']
        color = request.form.get('color', '#FFFFFF')
        min_area = float(request.form.get('min_area', 0.1))

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

        # Leer imagen
        input_data = file.read()

        # Detectar y recortar portada
        cover_img = detect_book_cover(input_data, min_area_ratio=min_area)

        # Convertir color
        hex_color = color.lstrip('#')
        rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Crear lienzo 1920x1080
        canvas = Image.new('RGB', (1920, 1080), rgb_color)

        # Escalar portada al 80% del alto del lienzo
        canvas_width, canvas_height = canvas.size
        cover_width, cover_height = cover_img.size

        target_height = int(canvas_height * 0.8)
        scale_ratio = target_height / cover_height
        new_width = int(cover_width * scale_ratio)
        new_height = target_height

        # Si el ancho escalado es mayor que el lienzo, reajustar por ancho
        if new_width > canvas_width * 0.9:
            target_width = int(canvas_width * 0.9)
            scale_ratio = target_width / cover_width
            new_width = target_width
            new_height = int(cover_height * scale_ratio)

        cover_img = cover_img.resize((new_width, new_height), Image.LANCZOS)

        # Centrar portada escalada
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2

        canvas.paste(cover_img, (x, y))

        # Guardar
        output = io.BytesIO()
        canvas.save(output, format='PNG', quality=95)
        output.seek(0)

        return send_file(
            output,
            mimetype='image/png',
            as_attachment=True,
            download_name='portada_procesada.png'
        )

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    print("🚀 Iniciando Detector de Portadas Web...")
    if port == 5000:
        print("📱 Abre tu navegador en: http://localhost:5000")
    print("⏹️  Presiona Ctrl+C para detener")
    print("")
    print("💡 Soporta fotos de libros físicos Y portadas digitales")
    print("📖 Detección automática: física (con bordes) o digital (imagen completa)")

    app.run(debug=debug, host='0.0.0.0', port=port)
