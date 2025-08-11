import csv
from datetime import datetime, timedelta
from pathlib import Path

RECORDINGS_DIR = Path("recordings")

# Importar librerías de audio (opcionales)
try:
    import sounddevice as sd
    import soundfile as sf
    HAVE_AUDIO = True
except Exception:
    HAVE_AUDIO = False

CSV_FILE = 'canciones.csv'

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['nombre', 'link', 'ultima_practica', 'intervalo_dias', 'ease_factor'])

def leer_canciones():
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def guardar_canciones(canciones):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['nombre', 'link', 'ultima_practica', 'intervalo_dias', 'ease_factor']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for c in canciones:
            writer.writerow(c)

def proxima_fecha(ultima_practica, intervalo):
    return datetime.strptime(ultima_practica, "%Y-%m-%d") + timedelta(days=int(intervalo))

def repasar_hoy():
    hoy = datetime.today()
    canciones = leer_canciones()

    pendientes = [
        c for c in canciones
        if proxima_fecha(c['ultima_practica'], c['intervalo_dias']).date() <= hoy.date()
    ]

    if not pendientes:
        print("📭 No hay canciones pendientes para hoy.")
        return

    print(f"\n🎹 Hay {len(pendientes)} canciones para repasar hoy:")

    for i, c in enumerate(pendientes):
        print(f"\n🎵 {i+1}. {c['nombre']}")
        print(f"🔗 Link o referencia: {c['link']}")
        dificultad = input("¿Cómo te fue? (f = fácil, d = difícil): ").lower()

        if dificultad not in ['f', 'd']:
            print("❌ Entrada inválida. Se salta esta canción.")
            continue

        intervalo_actual = int(c['intervalo_dias'])
        ease_factor = float(c['ease_factor'])

        if dificultad == 'd':
            nuevo_intervalo = 1
            nuevo_ef = ease_factor * 0.9
        elif dificultad == 'f':
            nuevo_intervalo = int(intervalo_actual * ease_factor * 1.3)
            nuevo_ef = ease_factor * 1.1

        c['ultima_practica'] = hoy.strftime("%Y-%m-%d")
        c['intervalo_dias'] = str(max(1, nuevo_intervalo))
        c['ease_factor'] = str(round(max(1.3, min(nuevo_ef, 2.5)), 2))

    guardar_canciones(canciones)
    print("\n✅ Canciones actualizadas.")

def agregar_cancion():
    nombre = input("🎵 Nombre de la canción: ")
    link = input("🔗 Link o referencia: ")
    hoy = datetime.today().strftime("%Y-%m-%d")
    nueva = {
        'nombre': nombre,
        'link': link,
        'ultima_practica': hoy,
        'intervalo_dias': '1',
        'ease_factor': '2.5'
    }
    canciones = leer_canciones()
    canciones.append(nueva)
    guardar_canciones(canciones)
    print("✅ Canción agregada al sistema de repaso.")
def slugify(nombre):
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in nombre).strip("-")

def elegir_cancion(prompt="Elegí una canción (número): "):
    canciones = leer_canciones()
    if not canciones:
        print("🚫 No hay canciones.")
        return None, None
    listar_canciones(canciones)
    idx = input(prompt).strip()
    try:
        i = int(idx) - 1
        if i < 0 or i >= len(canciones):
            raise ValueError
    except Exception:
        print("❌ Índice inválido.")
        return None, None
    return canciones, i
def grabar_practica():
    canciones, i = elegir_cancion("N° de canción a grabar (Enter=cancelar): ")
    if canciones is None:
        return
    segundos = input("⏺️ ¿Cuántos segundos querés grabar? (por defecto 30): ").strip()
    segundos = int(segundos) if segundos.isdigit() else 30

    if not HAVE_AUDIO:
        print("❌ Función de audio no disponible. Instalá dependencias:\n"
              "   pip install sounddevice soundfile")
        return

    nombre = canciones[i]['nombre']
    carpeta = RECORDINGS_DIR / slugify(nombre)
    carpeta.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = carpeta / f"{ts}.wav"
def reproducir_practica():
    if not HAVE_AUDIO:
        print("❌ Reproducción no disponible. Instalá dependencias:\n"
              "   pip install sounddevice soundfile")
        return
    canciones, i = elegir_cancion("N° de canción para reproducir (Enter=cancelar): ")
    if canciones is None:
        return
    nombre = canciones[i]['nombre']
    carpeta = RECORDINGS_DIR / slugify(nombre)
    if not carpeta.exists():
        print("🚫 No hay grabaciones para esta canción.")
        return
    archivos = sorted([p for p in carpeta.glob("*.wav")])
    if not archivos:
        print("🚫 No hay grabaciones .wav.")
        return
    print("\n🎧 Grabaciones disponibles:")
    for idx, p in enumerate(archivos, 1):
        print(f"{idx}. {p.name}")
    sel = input("N° a reproducir (Enter=cancelar): ").strip()
    if not sel:
        print("↩️ Cancelado.")
        return
    try:
        j = int(sel) - 1
        if j < 0 or j >= len(archivos):
            raise ValueError
    except Exception:
        print("❌ Índice inválido.")
        return
    audio, fs = sf.read(str(archivos[j]))
    print(f"▶️ Reproduciendo {archivos[j].name} ...")
    sd.play(audio, fs)
    sd.wait()

    fs = 44100
    canales = 1
    print(f"🎙️ Grabando {segundos}s... (hablá/jugá) ")
    audio = sd.rec(int(segundos * fs), samplerate=fs, channels=canales)
    sd.wait()
    sf.write(str(archivo), audio, fs)
    print(f"✅ Guardado: {archivo}")

def menu():
    print("\n🎼 SISTEMA DE REPASO DE CANCIONES DE PIANO")
    print("1. Agregar nueva canción")
    print("2. Repasar hoy")
    print("3. Borrar canción")
    print("4. Grabar práctica (audio)")       # <-- NUEVO
    print("5. Reproducir práctica (audio)")   # <-- NUEVO
    opcion = input("Seleccioná una opción: ")
    if opcion == '1':
        agregar_cancion()
    elif opcion == '2':
        repasar_hoy()
    elif opcion == '3':
        eliminar_cancion()
    elif opcion == '4':
        grabar_practica()
    elif opcion == '5':
        reproducir_practica()
    else:
        print("❌ Opción inválida.")


menu()
