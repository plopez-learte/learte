#!/usr/bin/env python3
"""
Herramienta SIMPLE para portadas digitales
Para imágenes que ya están listas, sin fondo a eliminar
Solo escala y centra en el lienzo
"""

from PIL import Image
import argparse
import sys
from pathlib import Path


def process_digital_cover(input_path, output_path, bg_color="#FFFFFF", canvas_size=(1920, 1080)):
    """
    Procesa portada digital: escala y centra sin detección
    """

    print(f"📖 Procesando portada digital: {Path(input_path).name}")

    if not Path(input_path).exists():
        print(f"❌ Error: No se encuentra el archivo '{input_path}'")
        sys.exit(1)

    try:
        # Cargar imagen
        cover_img = Image.open(input_path)

        # Convertir a RGB si es necesario
        if cover_img.mode != 'RGB':
            cover_img = cover_img.convert('RGB')

        cover_width, cover_height = cover_img.size
        print(f"📐 Imagen original: {cover_width}x{cover_height} px")

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
        print(f"🎨 Creando lienzo {canvas_size[0]}x{canvas_size[1]} con color {bg_color}...")
        canvas = Image.new('RGB', canvas_size, rgb_color)
        canvas_width, canvas_height = canvas.size

        # Escalar portada al 80% del alto del lienzo
        target_height = int(canvas_height * 0.8)
        scale_ratio = target_height / cover_height
        new_width = int(cover_width * scale_ratio)
        new_height = target_height

        # Si el ancho escalado es mayor que el 90% del lienzo, reajustar por ancho
        if new_width > canvas_width * 0.9:
            target_width = int(canvas_width * 0.9)
            scale_ratio = target_width / cover_width
            new_width = target_width
            new_height = int(cover_height * scale_ratio)

        print(f"📐 Escalando de {cover_width}x{cover_height} a {new_width}x{new_height} ({int(scale_ratio*100)}%)")
        cover_img_resized = cover_img.resize((new_width, new_height), Image.LANCZOS)

        # Centrar
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2

        print(f"📍 Centrando portada en el lienzo...")
        canvas.paste(cover_img_resized, (x, y))

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
        description='📚 Procesador SIMPLE de portadas digitales - Sin detección',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Portada digital con fondo blanco
  python3 book_cover_simple.py portada.jpg resultado.png

  # Con fondo de color
  python3 book_cover_simple.py portada.jpg resultado.png --color blue

  # Lienzo personalizado
  python3 book_cover_simple.py portada.jpg resultado.png --size 1280 720

Cuándo usar esta herramienta:
  ✓ Portadas digitales ya diseñadas (sin fondo a eliminar)
  ✓ Imágenes de Amazon, editoriales, etc.
  ✓ Archivos PNG/JPG que ya están listos

Cuándo usar book_cover_cli_v2.py:
  ✓ Fotos de portadas físicas sobre mesas/fondos
  ✓ Necesitas detectar y recortar el libro del fondo
        """
    )

    parser.add_argument('input', help='Imagen de portada digital')
    parser.add_argument('output', help='Archivo de salida')
    parser.add_argument('--color', '-c', default='#FFFFFF',
                       help='Color de fondo. Default: white')
    parser.add_argument('--size', '-s', nargs=2, type=int,
                       metavar=('WIDTH', 'HEIGHT'), default=[1920, 1080],
                       help='Tamaño del lienzo. Default: 1920 1080')

    args = parser.parse_args()

    process_digital_cover(args.input, args.output, args.color, tuple(args.size))


if __name__ == "__main__":
    main()
