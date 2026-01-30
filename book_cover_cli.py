#!/usr/bin/env python3
"""
Herramienta para detectar y recortar portadas de libros físicos
Usa detección de contornos para encontrar el rectángulo de la portada
"""

import cv2
import numpy as np
from PIL import Image
import argparse
import sys
from pathlib import Path


def order_points(pts):
    """Ordena puntos en: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left

    return rect


def detect_book_cover(image_path, min_area_ratio=0.1, debug=False):
    """
    Detecta el contorno rectangular de una portada de libro en una imagen

    Args:
        image_path: Ruta a la imagen
        min_area_ratio: Área mínima del contorno como ratio del área total (0.1 = 10%)
        debug: Si True, muestra imágenes intermedias para depuración

    Returns:
        Imagen PIL de la portada recortada, o None si no se detectó
    """

    # Leer imagen
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: No se pudo leer la imagen '{image_path}'")
        return None

    original = img.copy()
    height, width = img.shape[:2]
    total_area = height * width

    print(f"📐 Imagen: {width}x{height} px")

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar desenfoque para reducir ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detección de bordes con Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Dilatar para cerrar pequeños espacios
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)

    # Encontrar contornos
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"🔍 Contornos encontrados: {len(contours)}")

    # Ordenar contornos por área (mayor primero)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Modo debug: dibujar todos los contornos
    if debug:
        debug_img = original.copy()

    book_contour = None
    best_area = 0
    best_info = ""
    best_index = -1

    # Buscar el contorno rectangular más grande con proporciones de libro
    for i, contour in enumerate(contours[:15]):  # Revisar los 15 más grandes
        area = cv2.contourArea(contour)
        area_ratio = area / total_area

        # Aproximar el contorno a un polígono
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # Buscar contornos con 4 puntos (rectangulares) y área suficiente
        if len(approx) == 4 and area_ratio > min_area_ratio:
            # Calcular dimensiones aproximadas del contorno
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = h / w if w > 0 else 0

            print(f"  Contorno {i+1}: área={area_ratio:.2%}, aspecto={aspect_ratio:.2f} ({w}x{h}px)")

            # Priorizar contornos con:
            # 1. Mayor área
            # 2. Relación de aspecto típica de libros
            is_vertical = 1.2 <= aspect_ratio <= 1.8  # Libro vertical
            is_horizontal = 0.55 <= aspect_ratio <= 0.85  # Libro horizontal

            if (is_vertical or is_horizontal) and area > best_area:
                book_contour = approx
                best_area = area
                best_info = f"área={area_ratio:.1%}, aspecto={aspect_ratio:.2f}"
                best_index = i
                print(f"    ✅ Mejor candidato (proporciones de libro)")
            elif area > best_area * 1.5:  # Si es 50% más grande, considerar aunque no sea proporción ideal
                book_contour = approx
                best_area = area
                best_info = f"área={area_ratio:.1%}, aspecto={aspect_ratio:.2f}"
                best_index = i
                print(f"    ⚠️  Candidato por tamaño (proporciones atípicas)")

            # Modo debug: dibujar contornos
            if debug and len(approx) == 4:
                color = (0, 255, 0) if (is_vertical or is_horizontal) else (0, 165, 255)
                cv2.drawContours(debug_img, [approx], -1, color, 3)
                cv2.putText(debug_img, f"#{i+1}", tuple(approx[0][0]),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    if book_contour is not None:
        print(f"  ✅ Portada detectada: {best_info}")

        # Guardar imagen de debug
        if debug:
            cv2.drawContours(debug_img, [book_contour], -1, (0, 0, 255), 5)
            debug_path = str(Path(image_path).parent / 'debug_deteccion.jpg')
            cv2.imwrite(debug_path, debug_img)
            print(f"  📸 Imagen de debug guardada: {debug_path}")
            print(f"     Verde: proporciones de libro | Naranja: otras proporciones | Rojo: seleccionado")

    if book_contour is None:
        print("❌ No se detectó ninguna portada rectangular")
        print("💡 Sugerencias:")
        print("   - Asegúrate de que la portada tenga buen contraste con el fondo")
        print("   - La portada debe ocupar al menos 10% de la imagen")
        print("   - Evita sombras fuertes o reflejos")
        return None

    # Ordenar puntos del contorno
    pts = book_contour.reshape(4, 2)
    rect = order_points(pts)

    # Calcular dimensiones del rectángulo
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    print(f"📏 Portada detectada: {maxWidth}x{maxHeight} px")

    # Crear matriz de transformación de perspectiva
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(original, M, (maxWidth, maxHeight))

    # Convertir de BGR a RGB para PIL
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)

    return Image.fromarray(warped_rgb)


def process_cover(input_path, output_path, bg_color="#FFFFFF", canvas_size=(1920, 1080), min_area=0.1, debug=False):
    """
    Detecta portada, la recorta y la coloca en un lienzo
    """

    print(f"📖 Procesando: {Path(input_path).name}")

    # Validar archivo de entrada
    if not Path(input_path).exists():
        print(f"❌ Error: No se encuentra el archivo '{input_path}'")
        sys.exit(1)

    try:
        # Detectar y recortar portada
        print("🔍 Detectando portada...")
        cover_img = detect_book_cover(input_path, min_area_ratio=min_area, debug=debug)

        if cover_img is None:
            print("❌ No se pudo detectar la portada")
            sys.exit(1)

        # Convertir color de fondo
        try:
            if bg_color.startswith('#'):
                hex_color = bg_color.lstrip('#')
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                color_map = {
                    'white': (255, 255, 255),
                    'black': (0, 0, 0),
                    'red': (255, 87, 34),
                    'blue': (33, 150, 243),
                    'green': (76, 175, 80),
                    'yellow': (255, 193, 7),
                }
                rgb_color = color_map.get(bg_color.lower(), (255, 255, 255))
        except:
            print(f"⚠️  Color '{bg_color}' no válido, usando blanco")
            rgb_color = (255, 255, 255)

        # Crear lienzo
        print(f"🎨 Creando lienzo {canvas_size[0]}x{canvas_size[1]} con color {bg_color}...")
        canvas = Image.new('RGB', canvas_size, rgb_color)

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

        print(f"📐 Escalando portada de {cover_width}x{cover_height} a {new_width}x{new_height} ({int(scale_ratio*100)}%)")
        cover_img = cover_img.resize((new_width, new_height), Image.LANCZOS)

        # Calcular posición centrada
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2

        print(f"📍 Centrando portada escalada...")

        # Pegar portada
        canvas.paste(cover_img, (x, y))

        # Guardar resultado
        print(f"💾 Guardando resultado...")
        canvas.save(output_path, quality=95)

        print(f"✅ ¡Completado! Guardado en: {output_path}")
        print(f"   Lienzo: {canvas_size[0]}x{canvas_size[1]} px")
        print(f"   Portada escalada: {new_width}x{new_height} px (centrada y escalada al 80%)")

    except Exception as e:
        print(f"❌ Error al procesar: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Detecta y recorta portadas de libros físicos automáticamente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Detección básica con fondo blanco
  python3 book_cover_detector.py foto_portada.jpg resultado.png

  # Con fondo personalizado
  python3 book_cover_detector.py foto.jpg out.png --color "#2196F3"

  # Ajustar sensibilidad (área mínima 5%)
  python3 book_cover_detector.py foto.jpg out.png --min-area 0.05

Notas:
  - La portada debe tener buen contraste con el fondo
  - Funciona mejor con fondos uniformes
  - La portada debe ocupar al menos 10% de la imagen (ajustable con --min-area)
        """
    )

    parser.add_argument('input', help='Foto de la portada')
    parser.add_argument('output', help='Archivo de salida')

    parser.add_argument(
        '--color', '-c',
        default='#FFFFFF',
        help='Color de fondo del lienzo. Default: white'
    )

    parser.add_argument(
        '--size', '-s',
        nargs=2,
        type=int,
        metavar=('WIDTH', 'HEIGHT'),
        default=[1920, 1080],
        help='Tamaño del lienzo. Default: 1920 1080'
    )

    parser.add_argument(
        '--min-area',
        type=float,
        default=0.1,
        help='Área mínima de la portada como ratio (0.1 = 10%%). Default: 0.1'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Guarda imagen con todos los contornos detectados (debug_deteccion.jpg)'
    )

    args = parser.parse_args()

    process_cover(
        args.input,
        args.output,
        args.color,
        tuple(args.size),
        args.min_area,
        args.debug
    )


if __name__ == "__main__":
    main()
