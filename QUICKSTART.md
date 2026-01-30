# 🚀 Inicio Rápido - BookEditor

## Instalación (Una sola vez)

```bash
cd bookeditor
pip3 install -r requirements.txt
```

## Uso Inmediato

### Opción 1: Script de inicio (Más fácil) ⭐

```bash
./start.sh
```

Selecciona una opción del menú interactivo.

### Opción 2: Interfaz Web

```bash
python3 book_cover_web.py
```

Luego abre: **http://localhost:5000**

### Opción 3: CLI

```bash
python3 book_cover_cli.py mi_foto.jpg resultado.png --color blue
```

## Ejemplos Rápidos

```bash
# Probar con imagen de ejemplo
python3 book_cover_cli.py ejemplos/foto_portada_test.jpg test.png --color red

# Fondo negro
python3 book_cover_cli.py mi_foto.jpg resultado.png --color black

# Color personalizado
python3 book_cover_cli.py mi_foto.jpg resultado.png --color "#FF5722"

# Más sensible (para portadas pequeñas)
python3 book_cover_cli.py mi_foto.jpg resultado.png --min-area 0.05
```

## Procesamiento por Lotes

```bash
# Procesar todas las JPG de una carpeta
for img in *.jpg; do
    python3 book_cover_cli.py "$img" "final_${img}" --color white
done
```

## Resultado

- ✅ Lienzo: 1920x1080 px
- ✅ Portada escalada al 80% del alto
- ✅ Centrada automáticamente
- ✅ Fondo de color personalizable

## ¿Problemas?

Ver **README.md** para solución de problemas completa.
