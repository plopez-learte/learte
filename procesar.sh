#!/bin/bash

# Script interactivo para elegir la herramienta correcta

echo "╔════════════════════════════════════════════╗"
echo "║   📚 BookEditor - Procesador de Portadas  ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "¿Qué tipo de imagen tienes?"
echo ""
echo "  1) 📱 Portada DIGITAL (Amazon, editorial, imagen completa)"
echo "     → Sin fondo a eliminar, ya está diseñada"
echo ""
echo "  2) 📸 Foto de portada FÍSICA (libro sobre mesa/fondo)"
echo "     → Necesita detectar y recortar del fondo"
echo ""
echo "  3) ❓ No estoy seguro"
echo ""
read -p "Opción [1-3]: " tipo

if [ "$tipo" = "3" ]; then
    echo ""
    echo "💡 Ayuda para decidir:"
    echo ""
    echo "   Portada DIGITAL (opción 1):"
    echo "   • Descargaste la imagen de Amazon/editorial"
    echo "   • Es un archivo con el diseño completo (texto + imagen)"
    echo "   • No hay fondo alrededor del libro"
    echo ""
    echo "   Portada FÍSICA (opción 2):"
    echo "   • Tomaste una foto del libro"
    echo "   • El libro está sobre una mesa/superficie"
    echo "   • Necesitas recortar el fondo"
    echo ""
    read -p "¿Cuál es tu caso? [1-2]: " tipo
fi

echo ""
read -p "Ruta de la imagen: " input_path

if [ ! -f "$input_path" ]; then
    echo "❌ Error: No se encuentra el archivo '$input_path'"
    exit 1
fi

# Nombre de salida basado en el input
filename=$(basename "$input_path")
name="${filename%.*}"
output_path="resultado_${name}.png"

echo ""
echo "Colores disponibles: white, black, red, blue, green, yellow"
echo "O usa formato hexadecimal: #FF5722"
read -p "Color de fondo [white]: " color
color=${color:-white}

if [ "$tipo" = "1" ]; then
    echo ""
    echo "🚀 Procesando portada DIGITAL (sin detección)..."
    python3 book_cover_simple.py "$input_path" "$output_path" --color "$color"

elif [ "$tipo" = "2" ]; then
    echo ""
    echo "🔍 Procesando portada FÍSICA (con detección)..."
    echo ""
    read -p "¿Activar modo debug? (ver contornos detectados) [s/N]: " debug

    if [[ "$debug" =~ ^[Ss]$ ]]; then
        python3 book_cover_cli_v2.py "$input_path" "$output_path" --color "$color" --debug
    else
        python3 book_cover_cli_v2.py "$input_path" "$output_path" --color "$color"
    fi
else
    echo "❌ Opción no válida"
    exit 1
fi

echo ""
if [ -f "$output_path" ]; then
    echo "✅ Resultado guardado en: $output_path"
    read -p "¿Abrir imagen? [S/n]: " abrir
    if [[ ! "$abrir" =~ ^[Nn]$ ]]; then
        open "$output_path" 2>/dev/null || xdg-open "$output_path" 2>/dev/null
    fi
fi
