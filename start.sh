#!/bin/bash

# Script de inicio rápido para BookEditor

echo "╔════════════════════════════════════════════╗"
echo "║   📖 BookEditor - Detector de Portadas    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✓ Python 3 detectado: $(python3 --version)"

# Verificar dependencias
echo ""
echo "Verificando dependencias..."

if python3 -c "import cv2, PIL, flask, numpy" 2>/dev/null; then
    echo "✓ Todas las dependencias instaladas"
else
    echo "⚠️  Instalando dependencias..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Selecciona una opción:"
echo ""
echo "  1) 🌐 Iniciar interfaz web (recomendado)"
echo "  2) 💻 Ver ayuda de CLI"
echo "  3) 🧪 Ejecutar ejemplo de prueba"
echo "  4) 📖 Ver README"
echo "  5) ❌ Salir"
echo ""
read -p "Opción [1-5]: " opcion

case $opcion in
    1)
        echo ""
        echo "🚀 Iniciando interfaz web..."
        echo "📱 Abre tu navegador en: http://localhost:5000"
        echo "⏹️  Presiona Ctrl+C para detener"
        echo ""
        python3 book_cover_web.py
        ;;
    2)
        echo ""
        python3 book_cover_cli.py --help
        ;;
    3)
        echo ""
        echo "🧪 Ejecutando ejemplo de prueba..."
        python3 book_cover_cli.py ejemplos/foto_portada_test.jpg test_resultado.png --color blue
        echo ""
        if [ -f "test_resultado.png" ]; then
            echo "✅ Resultado guardado en: test_resultado.png"
            echo "Abriendo imagen..."
            open test_resultado.png 2>/dev/null || xdg-open test_resultado.png 2>/dev/null || echo "Imagen guardada como test_resultado.png"
        fi
        ;;
    4)
        echo ""
        cat README.md | head -50
        echo ""
        echo "... (ver README.md completo para más información)"
        ;;
    5)
        echo "👋 ¡Hasta pronto!"
        exit 0
        ;;
    *)
        echo "❌ Opción no válida"
        exit 1
        ;;
esac
