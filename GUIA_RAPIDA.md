# 🎯 Guía Rápida - ¿Qué herramienta usar?

## 📚 Dos tipos de portadas, dos herramientas:

### 1️⃣ Portadas DIGITALES (ya diseñadas)
**Usa: `book_cover_simple.py`** ⭐

Portadas que **YA ESTÁN LISTAS**, sin fondo a eliminar:
- ✅ Imágenes de Amazon, editoriales
- ✅ Archivos PNG/JPG completos
- ✅ Diseños finalizados con texto y gráficos

```bash
python3 book_cover_simple.py portada_digital.jpg resultado.png --color white
```

**Ejemplo**: `813tSdzdgGL._AC_UF1000,1000_QL80_.jpg` (Almudena Grandes)
- Imagen digital completa con texto, imagen y logo
- Solo necesita escalarse y centrarse

---

### 2️⃣ Portadas FÍSICAS (fotos con fondo)
**Usa: `book_cover_cli_v2.py`** 🔍

Fotos de libros físicos que necesitan **DETECCIÓN Y RECORTE**:
- ✅ Fotos de portadas sobre mesas
- ✅ Imágenes con fondos a eliminar
- ✅ Libros fotografiados en cualquier superficie

```bash
python3 book_cover_cli_v2.py foto_libro.jpg resultado.png --debug --color blue
```

**Ejemplo**: Foto de un libro sobre una mesa de madera
- Necesita detectar el contorno del libro
- Recortar y eliminar el fondo

---

## 🌐 Interfaz Web

La web actualmente usa **detección automática**. Para portadas digitales, usa mejor el CLI simple:

```bash
python3 book_cover_simple.py TU_PORTADA.jpg resultado.png
```

---

## 📊 Tabla de decisión rápida:

| Tipo de imagen | Herramienta | Comando |
|---|---|---|
| Portada de Amazon/editorial | `simple.py` | `python3 book_cover_simple.py input.jpg out.png` |
| Imagen digital completa | `simple.py` | `python3 book_cover_simple.py input.jpg out.png` |
| Foto de libro sobre mesa | `cli_v2.py` | `python3 book_cover_cli_v2.py input.jpg out.png --debug` |
| Portada con fondo a eliminar | `cli_v2.py` | `python3 book_cover_cli_v2.py input.jpg out.png --debug` |

---

## 🚀 Ejemplos completos:

### Caso 1: Amazon / Editorial
```bash
# Imagen: 813tSdzdgGL._AC_UF1000,1000_QL80_.jpg
# Es una portada digital completa
python3 book_cover_simple.py 813tSdzdgGL._AC_UF1000,1000_QL80_.jpg resultado.png --color white
```

### Caso 2: Foto de libro físico
```bash
# Imagen: foto_libro_mesa.jpg
# Foto de un libro sobre una superficie
python3 book_cover_cli_v2.py foto_libro_mesa.jpg resultado.png --debug --color blue
```

---

## 💡 ¿Dudas?

- **¿Es una foto con fondo?** → `cli_v2.py` (con detección)
- **¿Es una imagen digital lista?** → `simple.py` (sin detección)

---

## 📁 Archivos disponibles:

- `book_cover_simple.py` ⭐ - Para portadas digitales
- `book_cover_cli_v2.py` 🔍 - Para fotos de portadas físicas
- `book_cover_web.py` 🌐 - Interfaz web (usa detección)

---

**Prueba con tus imágenes y elige la herramienta adecuada** 🎯
