# Deploy en Render - Sistema de Gestión de Biblioteca

## Pasos para Deploy Automático

### 1. Preparar Repositorio
```bash
git add .
git commit -m "Configuración para deploy en Render"
git push origin main
```

### 2. Crear Servicio en Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Conecta tu repositorio de GitHub
3. Selecciona "Blueprint" y usa el archivo `render.yaml`

### 3. Variables de Entorno (Automáticas)

Render configurará automáticamente:
- `DATABASE_URL` - URL de conexión PostgreSQL
- `SECRET_KEY` - Clave secreta generada automáticamente
- `DEBUG=False` - Modo producción

### 4. Acceso Post-Deploy

- **API Base**: `https://tu-app.onrender.com/api/`
- **Swagger**: `https://tu-app.onrender.com/swagger/`
- **Django Admin**: `https://tu-app.onrender.com/admin/`

## Deploy Manual (Alternativo)

### 1. Crear Base de Datos PostgreSQL
- Crear servicio PostgreSQL en Render
- Copiar `DATABASE_URL` de la configuración

### 2. Crear Web Service
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn config.wsgi:application`
- **Environment**: Python 3

### 3. Variables de Entorno Manuales
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
SECRET_KEY=tu-clave-secreta-segura-aqui
DEBUG=False
WEB_CONCURRENCY=4
```

## Verificación Post-Deploy

### 1. Probar Endpoints
```bash
# Obtener token
curl -X POST https://tu-app.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Password!!"}'

# Listar libros
curl -X GET https://tu-app.onrender.com/api/books/ \
  -H "Authorization: Bearer TOKEN_JWT"
```

### 2. Verificar Usuarios Predeterminados
Los usuarios se crean automáticamente al ejecutar las migraciones:
- `admin` / `Password!!` (Bibliotecario)
- `estudiante1` / `PasswordE1!!` (Estudiante)
- `estudiante2` / `PasswordE2!!` (Estudiante)

## Configuración de Producción

### Archivos Modificados para Deploy:
- ✅ `render.yaml` - Configuración de servicios
- ✅ `build.sh` - Script de construcción
- ✅ `requirements.txt` - Dependencias actualizadas
- ✅ `config/settings.py` - Variables de entorno
- ✅ `staticfiles/` - Directorio para archivos estáticos

### Dependencias Añadidas:
- `gunicorn` - Servidor WSGI para producción
- `whitenoise` - Servir archivos estáticos
- `dj-database-url` - Configuración de BD por URL

## Monitoreo

### Logs en Render:
- Ve a tu servicio en Render Dashboard
- Pestaña "Logs" para ver errores
- Pestaña "Events" para historial de deployments

### Comandos Útiles:
```bash
# Ver logs en tiempo real (desde Render dashboard)
# Reiniciar servicio (botón en dashboard)
# Configurar dominios personalizados (Settings → Custom Domains)
```

## Troubleshooting

### Error 500:
- Revisar logs en Render Dashboard
- Verificar variables de entorno
- Confirmar que `DEBUG=False`

### Error de Base de Datos:
- Verificar `DATABASE_URL`
- Confirmar que las migraciones se ejecutaron
- Revisar conexión PostgreSQL

### Archivos Estáticos:
- Confirmar que `collectstatic` se ejecutó
- Verificar configuración de WhiteNoise