# 🚀 Desplegar BookEditor en Railway

## Paso 1: Subir a GitHub

1. **Crea un nuevo repositorio en GitHub**:
   - Ve a https://github.com/new
   - Nombre: `bookeditor`
   - Visibilidad: Público o Privado (ambos funcionan)
   - NO marques "Initialize with README" (ya tenemos archivos)

2. **Conecta tu proyecto local con GitHub**:
   ```bash
   cd /Users/plopez/bookeditor
   git remote add origin https://github.com/TU_USUARIO/bookeditor.git
   git branch -M main
   git push -u origin main
   ```

   Reemplaza `TU_USUARIO` con tu username de GitHub.

## Paso 2: Desplegar en Railway

1. **Ve a Railway**:
   - Abre https://railway.app
   - Haz clic en "Start a New Project"
   - Selecciona "Deploy from GitHub repo"

2. **Conecta GitHub** (primera vez):
   - Autoriza Railway a acceder a tus repos
   - Puedes dar acceso solo al repo `bookeditor`

3. **Selecciona el repositorio**:
   - Busca y selecciona `bookeditor`
   - Railway detectará automáticamente:
     - ✅ `Procfile` (para saber cómo ejecutar)
     - ✅ `requirements.txt` (para instalar dependencias)
     - ✅ `runtime.txt` (versión de Python)

4. **Configura variables de entorno** (opcional):
   - En el dashboard de Railway, ve a "Variables"
   - Agrega si es necesario:
     - `PORT` (automático, Railway lo configura)
     - `DEBUG` = `False` (ya está por defecto)

5. **Despliega**:
   - Railway comenzará el deploy automáticamente
   - Verás los logs en tiempo real
   - El proceso tarda ~3-5 minutos

6. **Obtén tu URL**:
   - Una vez completado, Railway te dará una URL tipo:
   - `https://bookeditor-production.up.railway.app`

## Paso 3: Probar

Abre la URL y verás tu aplicación funcionando:
- Interfaz web completa
- Subida de imágenes
- Procesamiento en la nube

## 📊 Archivo esenciales (ya incluidos):

```
bookeditor/
├── Procfile                 ✅ Indica cómo ejecutar la app
├── requirements.txt         ✅ Dependencias Python
├── runtime.txt             ✅ Versión de Python
├── book_cover_web.py       ✅ Aplicación principal
└── .gitignore              ✅ Ignora archivos innecesarios
```

## 🔄 Actualizar la app:

Cada vez que hagas cambios y los subas a GitHub, Railway redesplegará automáticamente:

```bash
# Hacer cambios en el código
git add .
git commit -m "Descripción de cambios"
git push
```

Railway detecta el push y actualiza automáticamente.

## 💰 Costos:

- Railway ofrece **$5 USD de crédito gratis** al mes
- Esta app consume muy poco
- Plan gratuito es suficiente para pruebas

## 🐛 Solución de problemas:

### Error: "No module named 'cv2'"
- Railway instala `opencv-python-headless` automáticamente
- Si falla, verifica `requirements.txt`

### Error: "Application failed to respond"
- Verifica que `book_cover_web.py` use `PORT` de env
- Ya está configurado en la línea:
  ```python
  port = int(os.environ.get('PORT', 5000))
  ```

### Deploy tarda mucho
- Primera vez tarda ~5 min (instala dependencias)
- Siguientes deploys: ~2 min

## 📱 Compartir:

Una vez desplegado, comparte tu URL:
```
https://tu-app.up.railway.app
```

Cualquiera puede acceder y procesar portadas en la nube!

---

**¿Listo para desplegar?** Sigue el Paso 1 para subir a GitHub 🚀
