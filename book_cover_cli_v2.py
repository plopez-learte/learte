#!/usr/bin/env python3
"""
Herramienta MEJORADA para detectar y recortar portadas de libros físicos
Versión 2: Múltiples estrategias de detección para máxima precisión
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
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def score_contour(contour, total_area, img_width, img_height):
    """
    Calcula un score para determinar qué tan probable es que sea una portada
    Mayor score = más probable que sea la portada
    """
    area = cv2.contourArea(contour)
    area_ratio = area / total_area

    # Calcular bounding rect
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = h / w if w > 0 else 0

    # Calcular posición relativa (centrado es mejor)
    center_x = x + w/2
    center_y = y + h/2
    img_center_x = img_width / 2
    img_center_y = img_height / 2

    # Distancia al centro (normalizada)
    center_dist = np.sqrt((center_x - img_center_x)**2 + (center_y - img_center_y)**2)
    max_dist = np.sqrt(img_center_x**2 + img_center_y**2)
    center_score = 1 - (center_dist / max_dist)

    # Score por área (más grande es mejor, pero con límite)
    # Penalizar contornos muy grandes (>95%) que probablemente sean el fondo
    if area_ratio > 0.95:
        area_score = 0.3  # Penalización fuerte para fondos
    elif area_ratio > 0.85:
        area_score = 0.6  # Penalización media
    else:
        area_score = min(area_ratio / 0.5, 1.0)  # Óptimo: 50% de la imagen

    # Score por aspecto (libros típicos: 1.3-1.6)
    aspect_score = 0
    if 1.2 <= aspect_ratio <= 1.8:  # Libro vertical
        aspect_score = 1.0
    elif 0.55 <= aspect_ratio <= 0.85:  # Libro horizontal
        aspect_score = 0.9
    elif 1.0 <= aspect_ratio <= 2.0:  # Cerca de libro
        aspect_score = 0.7
    else:
        aspect_score = 0.3

    # Score por complejidad del contorno (más simple = mejor para libros)
    peri = cv2.arcLength(contour, True)
    complexity = peri / (2 * (w + h)) if (w + h) > 0 else 999
    complexity_score = 1.0 if complexity < 1.1 else (0.5 if complexity < 1.3 else 0.2)

    # Score total ponderado
    total_score = (
        area_score * 0.35 +           # 35% área
        aspect_score * 0.30 +         # 30% aspecto
        center_score * 0.20 +         # 20% posición
        complexity_score * 0.15       # 15% complejidad
    )

    return total_score, {
        'area_ratio': area_ratio,
        'aspect_ratio': aspect_ratio,
        'area_score': area_score,
        'aspect_score': aspect_score,
        'center_score': center_score,
        'complexity_score': complexity_score,
        'total_score': total_score
    }


def detect_book_cover_multi_strategy(image_path, min_area_ratio=0.1, debug=False):
    """
    Detecta portada usando múltiples estrategias y elige la mejor
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: No se pudo leer la imagen '{image_path}'")
        return None

    original = img.copy()
    height, width = img.shape[:2]
    total_area = height * width

    print(f"📐 Imagen: {width}x{height} px")

    if debug:
        debug_img = original.copy()

    # ESTRATEGIA 1: Detección de bordes estándar con Canny
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    candidates = []

    print("🔍 Estrategia 1: Detección de bordes Canny...")
    edges1 = cv2.Canny(blurred, 30, 100)
    kernel = np.ones((5, 5), np.uint8)
    dilated1 = cv2.dilate(edges1, kernel, iterations=2)
    contours1, _ = cv2.findContours(dilated1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours1, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area / total_area > min_area_ratio:
                candidates.append(('Canny_standard', approx, contour))

    # ESTRATEGIA 2: Detección con Canny más sensible
    print("🔍 Estrategia 2: Canny sensible...")
    edges2 = cv2.Canny(blurred, 50, 150)
    dilated2 = cv2.dilate(edges2, kernel, iterations=3)
    contours2, _ = cv2.findContours(dilated2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours2, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area / total_area > min_area_ratio:
                candidates.append(('Canny_sensitive', approx, contour))

    # ESTRATEGIA 3: Umbralización adaptativa
    print("🔍 Estrategia 3: Umbralización adaptativa...")
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    dilated3 = cv2.dilate(thresh, kernel, iterations=2)
    contours3, _ = cv2.findContours(dilated3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours3, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area / total_area > min_area_ratio:
                candidates.append(('Adaptive_thresh', approx, contour))

    # ESTRATEGIA 4: Umbralización de Otsu
    print("🔍 Estrategia 4: Umbralización Otsu...")
    _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    dilated4 = cv2.dilate(thresh_otsu, kernel, iterations=2)
    contours4, _ = cv2.findContours(dilated4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in sorted(contours4, key=cv2.contourArea, reverse=True)[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area / total_area > min_area_ratio:
                candidates.append(('Otsu_thresh', approx, contour))

    print(f"📋 Total de candidatos encontrados: {len(candidates)}")

    if not candidates:
        print("❌ No se encontraron contornos rectangulares")
        return None

    # Evaluar todos los candidatos con el sistema de scoring
    best_score = 0
    best_contour = None
    best_method = ""
    best_details = {}

    print("\n🎯 Evaluando candidatos:")
    for i, (method, approx, contour) in enumerate(candidates):
        score, details = score_contour(contour, total_area, width, height)

        print(f"  Candidato {i+1} ({method}):")
        print(f"    Área: {details['area_ratio']:.1%}, Aspecto: {details['aspect_ratio']:.2f}")
        print(f"    Score total: {score:.3f} (área:{details['area_score']:.2f}, "
              f"aspecto:{details['aspect_score']:.2f}, pos:{details['center_score']:.2f}, "
              f"complejidad:{details['complexity_score']:.2f})")

        if score > best_score:
            best_score = score
            best_contour = approx
            best_method = method
            best_details = details
            print(f"    ✅ NUEVO MEJOR CANDIDATO")

        # Dibujar en debug
        if debug:
            color = (0, 255, 0) if score == best_score else (255, 165, 0)
            cv2.drawContours(debug_img, [approx], -1, color, 2)
            x, y, w, h = cv2.boundingRect(approx)
            cv2.putText(debug_img, f"#{i+1} {score:.2f}", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    if best_contour is None:
        print("❌ No se encontró un candidato adecuado")
        return None

    print(f"\n✅ Portada detectada con método: {best_method}")
    print(f"   Score: {best_score:.3f}")
    print(f"   Área: {best_details['area_ratio']:.1%}")
    print(f"   Aspecto: {best_details['aspect_ratio']:.2f}")

    # Guardar debug
    if debug:
        cv2.drawContours(debug_img, [best_contour], -1, (0, 0, 255), 5)
        debug_path = str(Path(image_path).parent / 'debug_deteccion_v2.jpg')
        cv2.imwrite(debug_path, debug_img)
        print(f"\n📸 Debug guardado: {debug_path}")
        print(f"   Verde: Mejor candidato | Naranja: Otros | Rojo grueso: Seleccionado")

    # Extraer y enderezar la portada
    pts = best_contour.reshape(4, 2)
    rect = order_points(pts)

    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    print(f"📏 Dimensiones detectadas: {maxWidth}x{maxHeight} px")

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(original, M, (maxWidth, maxHeight))

    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
    return Image.fromarray(warped_rgb)


def process_cover(input_path, output_path, bg_color="#FFFFFF", canvas_size=(1920, 1080), min_area=0.1, debug=False):
    """Detecta portada, la recorta y la coloca en un lienzo"""

    print(f"📖 Procesando: {Path(input_path).name}\n")

    if not Path(input_path).exists():
        print(f"❌ Error: No se encuentra el archivo '{input_path}'")
        sys.exit(1)

    try:
        cover_img = detect_book_cover_multi_strategy(input_path, min_area_ratio=min_area, debug=debug)

        if cover_img is None:
            print("\n❌ No se pudo detectar la portada")
            print("\n💡 Sugerencias:")
            print("   • Prueba con --min-area 0.05 para mayor sensibilidad")
            print("   • Asegúrate de que la portada tenga buen contraste con el fondo")
            print("   • Usa --debug para ver qué está detectando")
            sys.exit(1)

        # Convertir color de fondo
        try:
            if bg_color.startswith('#'):
                hex_color = bg_color.lstrip('#')
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                color_map = {
                    'white': (255, 255, 255), 'black': (0, 0, 0),
                    'red': (255, 87, 34), 'blue': (33, 150, 243),
                    'green': (76, 175, 80), 'yellow': (255, 193, 7),
                }
                rgb_color = color_map.get(bg_color.lower(), (255, 255, 255))
        except:
            rgb_color = (255, 255, 255)

        # Crear lienzo
        print(f"\n🎨 Creando lienzo {canvas_size[0]}x{canvas_size[1]} con color {bg_color}...")
        canvas = Image.new('RGB', canvas_size, rgb_color)

        # Escalar portada al 80% del alto del lienzo
        canvas_width, canvas_height = canvas.size
        cover_width, cover_height = cover_img.size

        target_height = int(canvas_height * 0.8)
        scale_ratio = target_height / cover_height
        new_width = int(cover_width * scale_ratio)
        new_height = target_height

        if new_width > canvas_width * 0.9:
            target_width = int(canvas_width * 0.9)
            scale_ratio = target_width / cover_width
            new_width = target_width
            new_height = int(cover_height * scale_ratio)

        print(f"📐 Escalando de {cover_width}x{cover_height} a {new_width}x{new_height} ({int(scale_ratio*100)}%)")
        cover_img = cover_img.resize((new_width, new_height), Image.LANCZOS)

        # Centrar
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.paste(cover_img, (x, y))

        # Guardar
        canvas.save(output_path, quality=95)

        print(f"\n✅ ¡Completado! Guardado en: {output_path}")
        print(f"   Lienzo: {canvas_size[0]}x{canvas_size[1]} px")
        print(f"   Portada: {new_width}x{new_height} px (escalada al 80%)")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='🚀 DETECTOR MEJORADO de portadas - Múltiples estrategias de detección',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Detección con modo debug para diagnóstico
  python3 book_cover_cli_v2.py foto.jpg resultado.png --debug

  # Con fondo personalizado y mayor sensibilidad
  python3 book_cover_cli_v2.py foto.jpg out.png --color blue --min-area 0.05

  # Ver todos los candidatos y sus scores
  python3 book_cover_cli_v2.py foto.jpg out.png --debug

Mejoras en V2:
  ✓ 4 estrategias de detección diferentes
  ✓ Sistema de scoring inteligente
  ✓ Evalúa área, aspecto, posición y complejidad
  ✓ Elige automáticamente el mejor candidato
        """
    )

    parser.add_argument('input', help='Foto de la portada')
    parser.add_argument('output', help='Archivo de salida')
    parser.add_argument('--color', '-c', default='#FFFFFF', help='Color de fondo. Default: white')
    parser.add_argument('--size', '-s', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                       default=[1920, 1080], help='Tamaño del lienzo. Default: 1920 1080')
    parser.add_argument('--min-area', type=float, default=0.1,
                       help='Área mínima (0.1 = 10%%). Default: 0.1')
    parser.add_argument('--debug', action='store_true',
                       help='Modo debug: muestra todos los candidatos y scores')

    args = parser.parse_args()

    process_cover(args.input, args.output, args.color, tuple(args.size), args.min_area, args.debug)


if __name__ == "__main__":
    main()
