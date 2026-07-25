"""
LinkedIn Job Scraper 2026
Fase 0-1: Verificacion de entorno + Login
"""
import os
import sys
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

WAIT_TIMEOUT = 15


def setup_driver():
    print("[FASE 0] Iniciando Chrome (Selenium Manager gestionara el driver)...")
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    print("[FASE 0] Chrome iniciado OK")
    return driver


def accept_cookies(driver):
    print("[FASE 1] Buscando banner de cookies...")
    try:
        btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[@id='artdeco-global-alert-container']/div/section/div/div[2]/button[1]"
            ))
        )
        btn.click()
        print("[FASE 1] Banner de cookies aceptado OK")
        time.sleep(1)
    except TimeoutException:
        print("[FASE 1] Banner de cookies no encontrado (puede que no aparezca).")
        print("         >> Continua el script. Revisar si el navegador parece bloqueado > 15 segundos.")


def diagnostico_inputs(driver, log):
    """Registra todos los inputs visibles en la pagina actual."""
    inputs = driver.find_elements(By.TAG_NAME, "input")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    titulo = driver.title
    url = driver.current_url
    msg = (
        f"  URL: {url}\n"
        f"  Titulo: {titulo}\n"
        f"  Iframes encontrados: {len(iframes)}\n"
        f"  Inputs encontrados: {len(inputs)}\n"
    )
    for inp in inputs:
        msg += (
            f"    - name='{inp.get_attribute('name')}'"
            f"  id='{inp.get_attribute('id')}'"
            f"  type='{inp.get_attribute('type')}'"
            f"  visible={inp.is_displayed()}\n"
        )
    print(msg)
    log.write(msg + "\n")


def login(driver, log):
    print("[FASE 1] Leyendo credenciales...")
    load_dotenv()
    username = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    if not username or not password:
        # Fallback a archivos .txt (metodo legacy, no recomendado en repos publicos)
        try:
            with open("email.txt") as f:
                username = f.read().strip()
            with open("password.txt") as f:
                password = f.read().strip()
            print("[FASE 1] AVISO: usando credenciales de archivos .txt (metodo legacy).")
            print("         Migra a .env para evitar exponer credenciales en el repositorio.")
        except FileNotFoundError:
            print("[ERROR] No se encontraron credenciales.")
            print("        Crea un archivo .env con LINKEDIN_EMAIL y LINKEDIN_PASSWORD.")
            print("        Consulta .env.example como referencia.")
            sys.exit(1)

    print("[FASE 1] Esperando que cargue la pagina de login (hasta 15 s)...")
    time.sleep(3)

    print("[DIAG] Inspeccionando inputs en la pagina...")
    diagnostico_inputs(driver, log)

    # LinkedIn ya no usa name='session_key': buscamos por autocomplete (estable)
    try:
        email_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@autocomplete='username webauthn']")
            )
        )
    except TimeoutException:
        print("[ERROR] No se encontro el campo de email en 15 segundos.")
        log.write("[ERROR] email input no encontrado\n")
        sys.exit(1)

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: any(
                i.is_displayed()
                for i in d.find_elements(By.XPATH, "//input[@type='password']")
            )
        )
        password_field = next(
            i for i in driver.find_elements(By.XPATH, "//input[@type='password']")
            if i.is_displayed()
        )
    except (TimeoutException, StopIteration):
        print("[ERROR] No se encontro un input de password visible en 15 segundos.")
        sys.exit(1)

    email_field.clear()
    email_field.send_keys(username)
    time.sleep(0.5)
    password_field.clear()
    password_field.send_keys(password)
    time.sleep(0.5)

    # Diagnostico: listar todos los botones visibles antes de hacer click
    buttons = driver.find_elements(By.TAG_NAME, "button")
    log.write(f"[DIAG] Botones en la pagina ({len(buttons)}):\n")
    for b in buttons:
        log.write(
            f"  type='{b.get_attribute('type')}'  "
            f"visible={b.is_displayed()}  "
            f"texto='{b.text[:60]}'\n"
        )

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: any(
                b.text.strip() == 'Iniciar sesión' and b.is_displayed()
                for b in d.find_elements(By.TAG_NAME, "button")
            )
        )
        submit_btn = next(
            b for b in driver.find_elements(By.TAG_NAME, "button")
            if b.text.strip() == 'Iniciar sesión' and b.is_displayed()
        )
        submit_btn.click()
        print("[FASE 1] Credenciales enviadas. Esperando respuesta de LinkedIn (5 s)...")
    except (TimeoutException, StopIteration):
        print("[ERROR] Boton de login no encontrado en 15 s.")
        log.write("[ERROR] submit button no encontrado\n")
        sys.exit(1)

    time.sleep(5)

    url_actual = driver.current_url
    log.write(f"[LOGIN] URL tras submit: {url_actual}\n")
    print(f"\n[FASE 1] URL actual tras el intento de login: {url_actual}")
    print("-" * 60)
    print("El navegador queda abierto. Revisalo y dime que ves.")
    print("-" * 60)


SEARCH_ITEM = 'data engineer'


def search_and_go_to_jobs(driver, log):
    url = f"https://www.linkedin.com/jobs/search/?keywords={SEARCH_ITEM.replace(' ', '%20')}"
    print(f"\n[FASE 2] Navegando a busqueda de empleos: {url}")
    driver.get(url)
    time.sleep(5)
    url_actual = driver.current_url
    log.write(f"[FASE 2] URL resultante: {url_actual}\n")
    print(f"[FASE 2] URL resultante: {url_actual}")


NUM_PAGES = 10   # paginas a recolectar (25 ofertas/pagina aprox.)
TEST_LIMIT = None  # ofertas a extraer en pruebas; None para produccion


def scroll_page(driver):
    """Scroll gradual sobre el panel de lista para revelar cards ocultas (occlude).
    Usa el sentinel [data-results-list-top-scroll-sentinel] para encontrar
    el ancestro scrollable real, evitando depender de clases aleatorias."""
    panel = driver.execute_script("""
        var sentinel = document.querySelector('[data-results-list-top-scroll-sentinel]');
        if (sentinel) {
            var el = sentinel.parentElement;
            while (el && el !== document.body) {
                var s = window.getComputedStyle(el);
                if (s.overflowY === 'auto' || s.overflowY === 'scroll') return el;
                el = el.parentElement;
            }
        }
        return null;
    """)

    if panel:
        for _ in range(20):
            driver.execute_script("arguments[0].scrollTop += 300;", panel)
            time.sleep(0.3)
        time.sleep(0.5)
        driver.execute_script("arguments[0].scrollTop = 0;", panel)
        time.sleep(0.5)
    else:
        # Fallback: scroll de ventana completa
        print("[WARN] Panel scrollable no encontrado, usando window.scrollBy como fallback.")
        for _ in range(12):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.4)
        driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)


def diagnostico_scroll_containers(driver, log):
    """Detecta via JS los elementos desplazables reales de la pagina."""
    containers = driver.execute_script("""
        var result = [];
        var all = document.querySelectorAll('*');
        for (var el of all) {
            var s = window.getComputedStyle(el);
            var oy = s.overflowY;
            if ((oy === 'auto' || oy === 'scroll') &&
                 el.scrollHeight > el.clientHeight + 20) {
                result.push({
                    tag: el.tagName,
                    cls: el.className.toString().substring(0, 100),
                    scrollH: el.scrollHeight,
                    clientH: el.clientHeight
                });
            }
        }
        return result.slice(0, 10);
    """)
    log.write(f"[DIAG] Contenedores desplazables ({len(containers)}):\n")
    for c in containers:
        log.write(f"  <{c['tag']}> scrollH={c['scrollH']} clientH={c['clientH']}\n")
        log.write(f"    class='{c['cls']}'\n")
    print(f"[DIAG] Contenedores desplazables encontrados: {len(containers)} (ver debug.log)")


def collect_links(driver, log):
    print(f"\n[FASE 3] Recolectando links en {NUM_PAGES} paginas...")
    all_job_links = []

    for page in range(NUM_PAGES):
        start = page * 25
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={SEARCH_ITEM.replace(' ', '%20')}&start={start}"
        )
        print(f"[FASE 3] Pagina {page + 1} (start={start})...")
        driver.get(url)
        time.sleep(4)

        if page == 0:
            diagnostico_scroll_containers(driver, log)

        scroll_page(driver)

        all_anchors = driver.find_elements(By.TAG_NAME, 'a')
        page_links = list(dict.fromkeys(
            href.split('?')[0]  # limpiar query params para deduplicar
            for a in all_anchors
            if (href := a.get_attribute('href')) and
               'linkedin.com/jobs/view' in href
        ))

        new_links = [l for l in page_links if l not in all_job_links]
        all_job_links.extend(new_links)
        log.write(f"[FASE 3] Pagina {page + 1}: {len(page_links)} encontrados, {len(new_links)} nuevos. Total: {len(all_job_links)}\n")
        print(f"         {len(page_links)} encontrados, {len(new_links)} nuevos. Total acumulado: {len(all_job_links)}")

    print(f"\n[FASE 3] Recoleccion completada: {len(all_job_links)} links unicos")
    log.write(f"[FASE 3] TOTAL links unicos: {len(all_job_links)}\n")
    return all_job_links


def diagnostico_job_page(driver, log):
    """Vuelca h1/h2, elementos con 'job'/'company'/'description' en su clase,
    para identificar los selectores correctos de la pagina de oferta."""
    info = driver.execute_script("""
        var out = {};
        // Todos los h1 y h2
        out.headings = [];
        document.querySelectorAll('h1,h2').forEach(function(el) {
            if (el.innerText.trim()) {
                out.headings.push({tag: el.tagName, cls: el.className.substring(0,120), txt: el.innerText.trim().substring(0,100)});
            }
        });
        // Elementos cuya clase incluye palabras clave relevantes
        var keywords = ['job-title','company-name','top-card','location','posted','description','bullet','detail'];
        out.candidates = [];
        document.querySelectorAll('*').forEach(function(el) {
            var cls = el.className;
            if (typeof cls !== 'string') return;
            for (var i=0; i<keywords.length; i++) {
                if (cls.indexOf(keywords[i]) !== -1 && el.innerText.trim().length > 0) {
                    out.candidates.push({cls: cls.substring(0,150), txt: el.innerText.trim().substring(0,120)});
                    break;
                }
            }
        });
        // Primeros 20 candidatos
        out.candidates = out.candidates.slice(0, 20);
        return out;
    """)
    log.write("[DIAG JOB PAGE] Headings:\n")
    for h in info.get('headings', []):
        log.write(f"  <{h['tag']}> cls='{h['cls']}'\n    txt='{h['txt']}'\n")
    log.write("[DIAG JOB PAGE] Candidatos con clase relevante:\n")
    for c in info.get('candidates', []):
        log.write(f"  cls='{c['cls']}'\n    txt='{c['txt']}'\n")
    print(f"[DIAG] {len(info.get('headings',[]))} headings y {len(info.get('candidates',[]))} candidatos volcados en debug.log")


def extract_job_details(driver, url, log):
    """Extrae campos de una oferta con selectores estables:
    data-testid, href con /company/, y el parrafo con separadores ·"""
    driver.get(url)
    time.sleep(4)

    # Scroll breve del panel de detalle para asegurar render completo
    driver.execute_script("""
        var main = document.getElementById('workspace');
        if (main) { main.scrollTo(0, 600); }
    """)
    time.sleep(0.8)
    driver.execute_script("""
        var main = document.getElementById('workspace');
        if (main) { main.scrollTo(0, 0); }
    """)
    time.sleep(0.5)

    result = {'url': url}

    data = driver.execute_script("""
        var out = {};

        // --- Titulo y empresa desde document.title ---
        // Formato: "Job Title | Company | LinkedIn"
        var titleParts = (document.title || '').split(' | ');
        out.titulo  = titleParts[0] ? titleParts[0].trim() : null;
        out.empresa = titleParts[1] ? titleParts[1].trim() : null;

        // --- Empresa: confirmar con link /company/ (mas preciso) ---
        var companyLink = document.querySelector('a[href*="/company/"][href*="life/"]');
        if (!companyLink) companyLink = document.querySelector('a[href*="/company/"]');
        if (companyLink && companyLink.innerText.trim()) {
            out.empresa = companyLink.innerText.trim();
        }

        // --- Ubicacion y fecha desde el parrafo "Lugar · fecha · candidatos" ---
        out.ubicacion = null;
        out.fecha = null;
        var allPs = document.querySelectorAll('p');
        for (var i = 0; i < allPs.length; i++) {
            var ptxt = allPs[i].innerText.trim();
            if (ptxt.indexOf(' · ') !== -1 && ptxt.length < 300 &&
                (ptxt.indexOf('ago') !== -1 || ptxt.indexOf('hour') !== -1 ||
                 ptxt.indexOf('day') !== -1 || ptxt.indexOf('week') !== -1 ||
                 ptxt.indexOf('month') !== -1)) {
                var segs = ptxt.split(' · ');
                if (segs.length >= 2) {
                    out.ubicacion = segs[0].trim();
                    out.fecha = segs[1].trim();
                    break;
                }
            }
        }

        // --- Modalidad: badges Remote/Hybrid/Contract/Full-time etc. ---
        out.modalidad = null;
        var jobPath = window.location.pathname;
        var badgeLinks = document.querySelectorAll('a[href*="' + jobPath + '"]');
        var knownTypes = ['Remote','Hybrid','On-site','Contract','Full-time','Part-time','Internship','Temporary'];
        var modalities = [];
        for (var j = 0; j < badgeLinks.length; j++) {
            var btxt = badgeLinks[j].innerText.trim();
            if (knownTypes.indexOf(btxt) !== -1 && modalities.indexOf(btxt) === -1) {
                modalities.push(btxt);
            }
        }
        if (modalities.length > 0) out.modalidad = modalities.join(', ');

        // --- Descripcion: data-testid="expandable-text-box" (selector estable) ---
        // El texto completo ya esta en el DOM aunque visualmente aparezca truncado
        out.descripcion = null;
        var descBox = document.querySelector('[data-testid="expandable-text-box"]');
        if (descBox) out.descripcion = descBox.innerText.trim();

        return out;
    """)

    result.update(data)

    log.write(f"[FASE 4] {url}\n")
    for k, v in result.items():
        if k != 'url':
            log.write(f"  {k}: {str(v)[:400]}\n")
    log.write("\n")

    print(f"  titulo    : {result.get('titulo')}")
    print(f"  empresa   : {result.get('empresa')}")
    print(f"  ubicacion : {result.get('ubicacion')}")
    print(f"  modalidad : {result.get('modalidad')}")
    print(f"  fecha     : {result.get('fecha')}")
    desc_txt = result.get('descripcion') or ''
    print(f"  descripcion: {desc_txt[:150]}{'...' if len(desc_txt) > 150 else ''}")

    return result


def extract_all_jobs(driver, links, log):
    sample = links[:TEST_LIMIT] if TEST_LIMIT else links
    print(f"\n[FASE 4] Extrayendo {len(sample)} oferta(s) (TEST_LIMIT={TEST_LIMIT})...")
    jobs = []
    for i, url in enumerate(sample, 1):
        print(f"\n[FASE 4] Oferta {i}/{len(sample)}: {url}")
        data = extract_job_details(driver, url, log)
        jobs.append(data)
        time.sleep(2)
    print(f"\n[FASE 4] Extraccion completada: {len(jobs)} oferta(s)")
    return jobs


def save_to_csv(jobs):
    if not jobs:
        print("[FASE 5] Sin datos que guardar.")
        return None

    cols = ['url', 'titulo', 'empresa', 'ubicacion', 'modalidad', 'fecha', 'descripcion']
    df = pd.DataFrame(jobs)[cols]
    df['scrape_date'] = datetime.today().strftime('%Y-%m-%d')

    filename = f"linkedin_jobs_{datetime.today().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"\n[FASE 5] CSV guardado: {filename}  ({len(df)} filas, {len(df.columns)} columnas)")
    print(df[['titulo', 'empresa', 'ubicacion', 'modalidad', 'fecha']].to_string(index=False))
    return filename


def main():
    print("=" * 60)
    print("LinkedIn Scraper 2026 - Fase 0-1: Entorno + Login")
    print("=" * 60)

    with open("debug.log", "w", encoding="utf-8") as log:
        driver = setup_driver()

        print("\n[FASE 0] Prueba de conexion con Google...")
        driver.get("https://www.google.com/")
        time.sleep(2)
        print("[FASE 0] Google cargado OK")

        print("\n[FASE 1] Abriendo pagina de login de LinkedIn...")
        driver.get("https://www.linkedin.com/login")

        accept_cookies(driver)
        login(driver, log)
        search_and_go_to_jobs(driver, log)
        links = collect_links(driver, log)
        log.write(f"\n[LINKS]\n" + "\n".join(links) + "\n")
        jobs = extract_all_jobs(driver, links, log)
        save_to_csv(jobs)

    print("\n[SCRIPT] Fases 0-5 completadas. Navegador abierto.")


if __name__ == "__main__":
    main()
