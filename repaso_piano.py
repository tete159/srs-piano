import csv
from datetime import datetime, timedelta
import os

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
        dificultad = input("¿Cómo te fue? (f=fácil, m=medio, d=difícil): ").lower()


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
        elif dificultad == 'm':
            # Intermedio: crece menos que fácil, no resetea como difícil
            nuevo_intervalo = max(1, int(round(intervalo_actual * ease_factor * 1.15)))
            nuevo_ef = ease_factor * 1.02


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

def menu():
    print("\n🎼 SISTEMA DE REPASO DE CANCIONES DE PIANO")
    print("1. Agregar nueva canción")
    print("2. Repasar hoy")
    opcion = input("Seleccioná una opción: ")
    if opcion == '1':
        agregar_cancion()
    elif opcion == '2':
        repasar_hoy()
    else:
        print("❌ Opción inválida.")

menu()
