# 📖 BookEditor - Detector Automático de Portadas

Herramienta profesional para automatizar el proceso de edición de portadas de libros físicos. Detecta automáticamente el contorno rectangular de portadas en fotografías y las centra en un lienzo de 1920x1080px con fondo personalizable.

**Ideal para editores gráficos** que necesitan procesar múltiples portadas de libros diariamente.

## ✨ Características Principales

- 🔍 **Detección automática de contornos** - Encuentra la portada rectangular en cualquier foto
- 📐 **Escalado inteligente al 80%** - La portada se escala automáticamente para ocupar el 80% del lienzo
- 🎨 **Fondos personalizables** - Elige entre colores predefinidos o usa cualquier color hexadecimal
- 🖼️ **Lienzo estándar 1920x1080** - Formato Full HD listo para usar
- 🌐 **Dos interfaces disponibles** - Aplicación web moderna o CLI para automatización
- ⚡ **Rápido y eficiente** - Procesamiento en segundos

## 🚀 Instalación Rápida

```bash
# Clonar o navegar al directorio
cd bookeditor

# Instalar dependencias
pip3 install -r requirements.txt

# ¡Listo para usar!
```

## 📱 Uso - Interfaz Web (Recomendado)

### Iniciar la aplicación:

```bash
python3 book_cover_web.py
```

Luego abre tu navegador en: **http://localhost:5000**

### Características de la interfaz web:

- ✅ Drag & Drop de imágenes
- ✅ 6 colores rápidos predefinidos + selector personalizado
- ✅ Control de sensibilidad de detección
- ✅ Vista previa de la imagen
- ✅ Descarga directa del resultado
- ✅ Mensajes de error claros

### Consejos para mejores resultados:

1. Coloca la portada sobre un **fondo uniforme** y contrastante
2. Asegúrate de que haya **buena iluminación** sin reflejos
3. La portada debe estar **completamente visible** en la foto
4. Evita **sombras fuertes** sobre la portada

## 💻 Uso - Línea de Comandos (CLI)

Perfecto para automatización y procesamiento por lotes.

### Sintaxis básica:

```bash
python3 book_cover_cli.py <entrada> <salida> [opciones]
```

### Ejemplos:

```bash
# Fondo blanco (por defecto)
python3 book_cover_cli.py foto_portada.jpg resultado.png

# Fondo azul
python3 book_cover_cli.py foto_portada.jpg resultado.png --color blue

# Color personalizado
python3 book_cover_cli.py foto_portada.jpg resultado.png --color "#FF5722"

# Ajustar sensibilidad (área mínima 5%)
python3 book_cover_cli.py foto_portada.jpg resultado.png --min-area 0.05
```

### Procesamiento por lotes:

```bash
# Procesar todas las imágenes de una carpeta
for img in *.jpg; do
    python3 book_cover_cli.py "$img" "procesado_${img%.jpg}.png" --color blue
done
```

## 🎨 Colores Disponibles

### Nombres rápidos:
- `white` - Blanco (por defecto)
- `black` - Negro
- `red` - Rojo
- `blue` - Azul
- `green` - Verde
- `yellow` - Amarillo

### Hexadecimales:
Cualquier color en formato `#RRGGBB`, por ejemplo:
- `#FF5722` - Rojo intenso
- `#2196F3` - Azul material
- `#4CAF50` - Verde material

## ⚙️ Opciones Avanzadas

### CLI:

```
Opciones:
  -h, --help              Muestra ayuda
  --color, -c COLOR       Color de fondo (nombre o hex). Default: white
  --size, -s W H          Tamaño del lienzo. Default: 1920 1080
  --min-area RATIO        Área mínima de detección (0.01-0.5). Default: 0.1
```

### Escalado automático:

La portada se escala automáticamente al **80% del alto del lienzo** (864px de 1080px), manteniendo las proporciones. Si el ancho resultante es mayor al 90% del lienzo, se reajusta por ancho.

**Ejemplo:**
- Portada original: 357x507 px
- Portada escalada: 608x864 px (170% más grande)

## 📁 Estructura del Proyecto

```
bookeditor/
├── book_cover_web.py          # Aplicación web principal ⭐
├── book_cover_cli.py          # Herramienta CLI principal ⭐
├── requirements.txt           # Dependencias
├── README.md                  # Este archivo
├── ejemplos/                  # Imágenes de ejemplo
│   ├── foto_portada_test.jpg
│   ├── portada_prueba.jpg
│   └── resultado_escalado.png
└── old_versions/              # Versiones anteriores (rembg)
    ├── book_cover_web_rembg.py
    ├── book_cover_cli_rembg.py
    └── book_cover_tool.py
```

## 🔧 Requisitos del Sistema

- **Python**: 3.8 o superior
- **Sistema operativo**: macOS, Linux, Windows
- **Dependencias**:
  - Pillow (procesamiento de imágenes)
  - OpenCV (detección de contornos)
  - NumPy (operaciones matriciales)
  - Flask (servidor web)

## 📊 Cómo Funciona

1. **Detección de bordes**: Usa el algoritmo Canny de OpenCV
2. **Búsqueda de contornos**: Encuentra formas cerradas en la imagen
3. **Filtrado rectangular**: Busca contornos con 4 puntos (rectangulares)
4. **Validación de área**: Verifica que ocupe al menos el 10% de la imagen
5. **Corrección de perspectiva**: Extrae y endereza la portada
6. **Escalado inteligente**: Ajusta al 80% del lienzo manteniendo proporciones
7. **Composición final**: Centra sobre fondo de color

## 🐛 Solución de Problemas

### No detecta la portada

**Soluciones:**
- Ajusta el slider de sensibilidad en la web (bájalo al 5-10%)
- En CLI, usa `--min-area 0.05` para mayor sensibilidad
- Asegúrate de que haya **buen contraste** con el fondo
- Verifica que la portada esté **bien iluminada**

### La detección toma mucho tiempo

- Es normal que tarde 5-15 segundos en la primera ejecución
- Las siguientes serán más rápidas

### Error: "No module named 'cv2'"

```bash
pip3 install opencv-python
```

### Error: "No module named 'flask'"

```bash
pip3 install flask
```

## 🎯 Casos de Uso

### Editoriales
Procesar cientos de portadas para catálogos digitales

### Bibliotecas
Digitalizar colecciones de libros físicos

### Tiendas de libros
Crear galerías web de productos

### Diseñadores gráficos
Automatizar tareas repetitivas de preparación de portadas

## 📝 Ejemplos Incluidos

En la carpeta `ejemplos/` encontrarás:

- **foto_portada_test.jpg** - Simulación de foto de portada física
- **portada_prueba.jpg** - Portada simple de ejemplo
- **resultado_escalado.png** - Ejemplo de resultado procesado

Pruébalos para familiarizarte con la herramienta:

```bash
python3 book_cover_cli.py ejemplos/foto_portada_test.jpg test_resultado.png --color blue
```

## 🔄 Versiones Anteriores

En la carpeta `old_versions/` se encuentran las versiones que usaban `rembg` (eliminación de fondo con IA) en lugar de detección de contornos. Estas versiones son útiles si tienes imágenes digitales con fondos a eliminar en lugar de fotos de portadas físicas.

## 📄 Licencia

Proyecto de código abierto - Uso libre

## 👨‍💻 Autor

Creado con Claude Code para automatizar el trabajo de editores gráficos.

## 🆘 Soporte

Para ver ayuda detallada:

```bash
# CLI
python3 book_cover_cli.py --help

# Web
Abre http://localhost:5000 y revisa los consejos en pantalla
```

---

**¿Listo para empezar?**

```bash
# Interfaz web (recomendado para comenzar)
python3 book_cover_web.py

# O usa CLI para automatización
python3 book_cover_cli.py ejemplos/foto_portada_test.jpg resultado.png --color blue
```

🎨 ¡Feliz edición de portadas!
