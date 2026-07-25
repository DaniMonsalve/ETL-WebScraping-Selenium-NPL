# LinkedIn Job Scraper 2026

Scraper automatizado con Selenium que autentica en LinkedIn, busca ofertas de trabajo por palabra clave, recorre múltiples páginas de resultados y extrae datos estructurados (título, empresa, ubicación, modalidad, fecha y descripción completa) a un archivo CSV listo para análisis.

> Desarrollado y probado en julio de 2026 como actualización completa de un scraper original de 2023, adaptado a los cambios del DOM y la arquitectura de LinkedIn.

---

## Tabla de contenidos

- [Características](#características)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Prerrequisitos](#prerrequisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Seguridad](#seguridad)
- [Uso](#uso)
- [Salida](#salida)
- [Cómo funciona](#cómo-funciona)
- [Referencia de constantes](#referencia-de-constantes)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Hoja de ruta](#hoja-de-ruta)
- [Aviso legal](#aviso-legal)

---

## Características

- **Login automático** con detección dinámica de campos (sin depender de atributos `name` que LinkedIn cambia con frecuencia).
- **Recolección de links** mediante paginación por URL (`&start=N`), más robusta que hacer clic en botones.
- **Scroll inteligente** del panel lateral: detecta el contenedor scrollable real mediante el sentinel `[data-results-list-top-scroll-sentinel]`, sin depender de clases CSS hasheadas.
- **Extracción por oferta** con selectores estables resistentes a redespliegues del frontend:
  - `document.title` para título y empresa.
  - `a[href*="/company/"]` para confirmar empresa.
  - Párrafo con separador `·` para ubicación y fecha.
  - `[data-testid="expandable-text-box"]` para la descripción completa (sin necesidad de hacer clic en "ver más").
  - Links de badge para modalidad (Remote, Hybrid, Contract…).
- **Exportación a CSV** con `pandas`, codificación `utf-8-sig` (compatible con Excel).
- **Modo test** configurable: limita páginas y ofertas a extraer para iteraciones rápidas de desarrollo.
- **Gestión de credenciales** mediante `.env` (con fallback a archivos de texto por compatibilidad).

---

## Stack tecnológico

| Componente | Versión | Notas |
|---|---|---|
| Python | 3.12.4 AMD64 | `C:\Python312\python.exe` |
| Selenium | 4.46.0 | Incluye Selenium Manager (gestiona chromedriver automáticamente) |
| pandas | 3.0.5 | Construcción del DataFrame y exportación CSV |
| python-dotenv | ≥ 1.0.0 | Carga de variables de entorno desde `.env` |
| Chrome | 150.0.7871.125 | Navegador de automatización |
| Chromedriver | Auto | Descargado y gestionado por Selenium Manager, sin instalación manual |

---

## Estructura del proyecto

```
scrap/
├── scraping_2026.py          # Script principal
├── .env                      # Credenciales (NO subir al repositorio)
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Exclusiones de git
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Este archivo
│
├── linkedin_jobs_*.csv       # Salidas generadas (excluidas de git)
├── stdout.log                # Log de salida estándar (excluido de git)
├── stderr.log                # Log de errores (excluido de git)
└── debug.log                 # Log detallado de diagnóstico (excluido de git)
```

---

## Prerrequisitos

- **Python 3.10+** instalado y accesible desde la terminal.
- **Google Chrome** instalado (cualquier versión reciente; Selenium Manager descarga el chromedriver compatible automáticamente).
- Cuenta activa de **LinkedIn**.
- Acceso a internet sin restricciones de firewall para `chrome.exe` y `chromedriver.exe`.

> **Windows:** Si las reglas de firewall de Windows bloquean Chrome, es necesario permitir el acceso en Configuración → Firewall → Aplicaciones permitidas.

---

## Instalación

```bash
# 1. Clonar o descargar el repositorio
git clone <url-del-repo>
cd scrap

# 2. (Opcional pero recomendado) Crear un entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración

### Credenciales (método recomendado)

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` con tus credenciales:
   ```env
   LINKEDIN_EMAIL=tu_email@ejemplo.com
   LINKEDIN_PASSWORD=tu_contraseña
   ```

3. Asegúrate de que `.env` está incluido en `.gitignore` (ya lo está por defecto).

### Constantes del script

Edita las siguientes constantes al inicio de `scraping_2026.py` según tus necesidades:

```python
SEARCH_ITEM = 'data engineer'   # Término de búsqueda
NUM_PAGES   = 3                 # Páginas a recorrer (25 ofertas/página)
TEST_LIMIT  = 2                 # Ofertas a extraer; None = todas
WAIT_TIMEOUT = 15               # Segundos máx. de espera por elemento
```

Para **producción**, usar:
```python
NUM_PAGES  = 10    # ~250 ofertas
TEST_LIMIT = None  # Extraer todas
```

---

## Seguridad

### Gestión de credenciales

El script utiliza `python-dotenv` para leer las credenciales desde un archivo `.env` local que **nunca debe subirse al repositorio**. El flujo de carga es:

1. **Prioridad 1 — Variables de entorno (`.env`):** método recomendado. El archivo `.env` está excluido por `.gitignore`.
2. **Prioridad 2 — Archivos de texto (`email.txt` / `password.txt`):** compatibilidad con la versión original. Se muestra una advertencia al usarlos. También excluidos por `.gitignore`.
3. Si no se encuentran credenciales por ningún método, el script termina con un mensaje de error claro.

### Archivos excluidos del repositorio

El `.gitignore` del proyecto excluye explícitamente:

| Archivo / Patrón | Motivo |
|---|---|
| `.env` | Credenciales de acceso |
| `email.txt`, `password.txt` | Credenciales (método legacy) |
| `linkedin_jobs_*.csv` | Datos personales de terceros extraídos |
| `*.log` | Logs que podrían contener información sensible |
| `chromedriver*/`, `*.zip` | Binarios descargados, innecesarios en el repo |

### Recomendaciones adicionales

- **No reutilices** la contraseña de LinkedIn en ningún otro servicio.
- **Usa una cuenta secundaria** o de prueba para el scraping si el volumen de extracciones es alto, para reducir el riesgo de restricción de la cuenta principal.
- **No compartas** los CSV generados sin anonimizar los datos, ya que pueden contener información personal de ofertas y empresas sujeta a RGPD.
- El script incluye pausas (`time.sleep`) entre peticiones para **no sobrecargar los servidores de LinkedIn** y reducir la detección como bot.

---

## Uso

```bash
# Modo test (2 ofertas, 3 páginas)
python scraping_2026.py

# Los logs se redirigen a archivos para facilitar la depuración:
python scraping_2026.py > stdout.log 2> stderr.log
```

El navegador Chrome se abre en modo visible. No lo cierres durante la ejecución. Al finalizar queda abierto para inspección.

### Ejecución silenciosa (headless)

Para ejecutar sin ventana visible, añade en `setup_driver()`:

```python
options.add_argument("--headless=new")
```

> Nota: LinkedIn puede detectar con mayor facilidad las sesiones headless. Se recomienda el modo con ventana para producción.

---

## Salida

El script genera un CSV con el nombre `linkedin_jobs_YYYYMMDD_HHMMSS.csv` en el directorio de trabajo, con las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---|---|---|
| `url` | URL canónica de la oferta | `https://www.linkedin.com/jobs/view/4435101094/` |
| `titulo` | Título del puesto | `Data Engineer` |
| `empresa` | Nombre de la empresa | `Tech Mahindra` |
| `ubicacion` | Ciudad / región / país | `Barcelona, Catalonia, Spain` |
| `modalidad` | Tipo de trabajo y contrato | `Remote, Full-time` |
| `fecha` | Tiempo desde publicación | `3 weeks ago` |
| `descripcion` | Texto completo de la oferta | `We are seeking...` |
| `scrape_date` | Fecha de extracción | `2026-07-24` |

El archivo se codifica en `utf-8-sig` para compatibilidad directa con Microsoft Excel.

### Ejemplo de salida en consola

```
[FASE 5] CSV guardado: linkedin_jobs_20260724_203738.csv  (75 filas, 8 columnas)

titulo                    empresa        ubicacion                    modalidad         fecha
Data Engineer             Tech Mahindra  Barcelona, Catalonia, Spain  Remote, Full-time 3 weeks ago
Data Engineer I (Remote)  Hire Feed      European Union               Remote, Contract  13 hours ago
```

---

## Cómo funciona

El script está organizado en seis fases secuenciales:

### Fase 0 — Entorno
Inicia Chrome mediante `webdriver.Chrome()` con Selenium Manager gestionando el chromedriver. Verifica conectividad cargando Google.

### Fase 1 — Login
Navega a `https://www.linkedin.com/login`, localiza los campos de email y contraseña con XPath robustos (`autocomplete='username webauthn'` y `type='password'` filtrando por visibilidad) y hace clic en el botón de inicio de sesión con match exacto de texto para evitar los botones SSO (Microsoft/Apple). Verifica el éxito comprobando que la URL resultante es `/feed/`.

### Fase 2 — Navegación a búsqueda
Navega directamente a la URL de búsqueda por keyword:
```
https://www.linkedin.com/jobs/search/?keywords=data%20engineer
```
Evita interactuar con la UI de navegación, más frágil ante cambios de diseño.

### Fase 3 — Recolección de links
Para cada página (`&start=0`, `&start=25`, `&start=50`...):
1. Carga la URL de paginación.
2. Detecta el contenedor scrollable real buscando el ancestro con `overflow-y: auto/scroll` del sentinel `[data-results-list-top-scroll-sentinel]`.
3. Hace scroll gradual (20 pasos de 300 px) para revelar las tarjetas ocultas por el mecanismo de oclusión de LinkedIn (`occludable-update`).
4. Extrae todos los `href` que contienen `linkedin.com/jobs/view/`, limpiando query params para deduplicar.

### Fase 4 — Extracción por oferta
Para cada URL recolectada:
1. Navega a la URL y hace un scroll breve de `main#workspace` para asegurar el render.
2. Extrae campos mediante JavaScript ejecutado en el contexto de la página:
   - **Título y empresa**: `document.title.split(' | ')` → formato estable `"Título | Empresa | LinkedIn"`.
   - **Empresa**: confirmada con `a[href*="/company/"][href*="life/"]`.
   - **Ubicación y fecha**: párrafo `p` con separadores ` · ` que sigue el patrón `"Lugar · fecha · candidatos"`.
   - **Modalidad**: `<a>` de badges que enlazan a la propia oferta con texto en lista de tipos conocidos.
   - **Descripción completa**: `[data-testid="expandable-text-box"]` — el DOM contiene el texto completo aunque visualmente aparezca truncado; no es necesario hacer clic en "ver más".

### Fase 5 — Persistencia
Construye un `pd.DataFrame` con las ofertas extraídas, añade la columna `scrape_date` con la fecha actual y exporta a CSV con `utf-8-sig`.

---

## Referencia de constantes

```python
# scraping_2026.py

WAIT_TIMEOUT = 15      # Timeout máximo (segundos) para WebDriverWait
SEARCH_ITEM  = 'data engineer'  # Término de búsqueda en LinkedIn Jobs
NUM_PAGES    = 3       # Número de páginas a recorrer (25 ofertas/página)
TEST_LIMIT   = 2       # Máx. ofertas a extraer; None para extraer todas
```

---

## Limitaciones conocidas

| Limitación | Descripción |
|---|---|
| **Clases CSS hasheadas** | LinkedIn usa CSS Modules con hashes que cambian en cada despliegue. Los selectores del script usan `data-testid`, `href`, `document.title` y texto plano para evitar esta dependencia. |
| **Detección de bots** | LinkedIn puede bloquear temporalmente cuentas que realizan muchas peticiones automatizadas. Se recomiendan pausas generosas y usar una cuenta secundaria en producción. |
| **Login con 2FA** | El script no soporta autenticación de dos factores. Si tu cuenta tiene 2FA activado, deberás desactivarlo o gestionarlo manualmente. |
| **Variación por idioma** | Los selectores de texto ("About the job", "Remote", etc.) están en inglés, que es el idioma que LinkedIn sirve por defecto en el contexto de Selenium. Si la cuenta tiene el idioma configurado en español, algunos extractores de texto podrían fallar. |
| **CAPTCHAs** | En caso de detección de automatización, LinkedIn puede mostrar un CAPTCHA que detiene la ejecución. El script quedará pausado hasta que se resuelva manualmente. |
| **Sesiones headless** | El modo sin ventana (`--headless`) incrementa la detección. No recomendado para sesiones largas. |

---

## Hoja de ruta

- [ ] **Fase 6 — Modularización**: separar el código en módulos (`auth.py`, `collector.py`, `extractor.py`, `exporter.py`).
- [ ] **Multi-keyword**: soporte para lista de búsquedas en una sola ejecución.
- [ ] **Deduplicación persistente**: base de datos SQLite para no reextraer ofertas ya procesadas.
- [ ] **Notificaciones**: envío de resumen por email o Telegram al finalizar.
- [ ] **Análisis integrado**: notebook de análisis de las ofertas extraídas (skills más demandados, distribución salarial, etc.).
- [ ] **CI/CD**: ejecución programada con GitHub Actions + almacenamiento en Google Sheets.

---

## Aviso legal

Este proyecto es de uso **personal y educativo**. El scraping de LinkedIn puede ir en contra de sus [Términos de Servicio](https://www.linkedin.com/legal/user-agreement). El autor no se hace responsable del uso que terceros puedan hacer de este código. Úsalo de forma responsable:

- No extraigas datos personales de usuarios sin su consentimiento.
- No sobrecargues los servidores con peticiones masivas.
- Consulta siempre el archivo `robots.txt` del sitio objetivo.
- En la Unión Europea, el tratamiento de datos personales está sujeto al **RGPD** (Reglamento General de Protección de Datos).
