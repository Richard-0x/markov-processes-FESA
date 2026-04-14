import pygame
import numpy as np
import sys

# desactiva .venv -> deactivate
# pip install -r requirements.txt
# python Explo.py

# INICIALIZACIÓN
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CTMC - Explosión (q_n = n vs n²)")

font = pygame.font.SysFont("Arial", 20)
large_font = pygame.font.SysFont("Arial", 30, bold=True)
clock = pygame.time.Clock()

# SONIDO
sample_rate = 44100
duration = 0.05
t = np.linspace(0, duration, int(sample_rate * duration), False)
onda = np.sin(440 * 2 * np.pi * t)
audio = np.int16(onda * 32767)
audio_stereo = np.column_stack((audio, audio))
beep_sound = pygame.sndarray.make_sound(audio_stereo)
beep_sound.set_volume(0.4)

# PARÁMETROS

modo_explosivo = True
usar_semilla = True
estado = 1
tiempo_actual = 0.0
tiempo_inicio_estado = 0.0
historial_tiempos = []

max_nodes = 12  

if usar_semilla:
    np.random.seed(42)

# FUNCIONES
def tasa_estado(n):
    return n**2 if modo_explosivo else n

def generar_tiempo(n):
    return np.random.exponential(1 / tasa_estado(n))

def reiniciar():
    global estado, tiempo_actual, tiempo_inicio_estado, historial_tiempos
    estado = 1
    tiempo_actual = 0.0
    tiempo_inicio_estado = 0.0
    historial_tiempos.clear()
    return generar_tiempo(estado)

def get_pos(n):
    x = 80 + (n - 1) * 70
    y = HEIGHT // 2
    return x, y

tiempo_espera = generar_tiempo(estado)


# LOOP PRINCIPAL
running = True

while running:
    dt = clock.tick(60) / 1000.0
    tiempo_actual += dt

    # Fondo dinámico
    if estado >= max_nodes and modo_explosivo:
        screen.fill((60, 20, 20))
    else:
        screen.fill((30, 30, 30))

  
    # EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                modo_explosivo = not modo_explosivo
                tiempo_espera = reiniciar()

            if event.key == pygame.K_r:
                tiempo_espera = reiniciar()

            if event.key == pygame.K_s:
                usar_semilla = not usar_semilla
                if usar_semilla:
                    np.random.seed(42)
                tiempo_espera = reiniciar()

    
    # DIBUJAR CONEXIONES
    
    for n in range(1, max_nodes):
        pygame.draw.line(screen, (100, 100, 100), get_pos(n), get_pos(n + 1), 2)

    
    # DIBUJAR NODOS
    
    for n in range(1, max_nodes + 1):
        x, y = get_pos(n)
        color = (100, 200, 100) if n == estado else (70, 70, 150)
        pygame.draw.circle(screen, color, (x, y), 20)

        text = font.render(str(n), True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(x, y)))

    
    # LÓGICA CTMC
    
    tiempo_en_estado = tiempo_actual - tiempo_inicio_estado
    tiempo_restante = tiempo_espera - tiempo_en_estado

    if tiempo_restante <= 0 and estado < max_nodes:
        beep_sound.play()
        historial_tiempos.append(tiempo_espera)

        estado += 1
        tiempo_inicio_estado = tiempo_actual
        tiempo_espera = generar_tiempo(estado)

    
    #reloj exponencial
    if estado < max_nodes:
        x, y = get_pos(estado)
        progreso = max(0, tiempo_restante / tiempo_espera)

        rect = pygame.Rect(x - 30, y - 30, 60, 60)
        pygame.draw.arc(screen, (255, 80, 80), rect, 0, progreso * 2 * np.pi, 4)

    
    # INFORMACIÓN
    tasa = tasa_estado(estado)
    suma_total = sum(historial_tiempos)

    modo_txt = "EXPLOSIVO (q_n = n²)" if modo_explosivo else "REGULAR (q_n = n)"

    info = [
        f"Modo: {modo_txt}",
        f"Estado: {estado}",
        f"Tiempo total: {tiempo_actual:.4f}",
        f"Tasa actual: {tasa}",
        f"Suma acumulada ΣT_n: {suma_total:.4f}"
    ]

    for i, txt in enumerate(info):
        render = font.render(txt, True, (200, 200, 255))
        screen.blit(render, (20, 20 + i * 25))

    
    # MENSAJE DE EXPLOSIÓN
    
    if estado >= max_nodes:
        msg = "Explosión (aprox): muchos saltos en poco tiempo"
        text = large_font.render(msg, True, (255, 120, 120))
        screen.blit(text, (WIDTH // 2 - 300, 50))

    
    # GRÁFICA DE TIEMPOS 
    base_x = WIDTH - 300
    base_y = HEIGHT - 40

    pygame.draw.line(screen, (255, 255, 255), (base_x, base_y), (base_x + 250, base_y), 2)

    for i, t_val in enumerate(historial_tiempos):
        altura = min(t_val * 60, 120)
        pygame.draw.rect(
            screen,
            (150, 200, 255),
            (base_x + 10 + i * 18, base_y - altura, 12, altura)
        )

    titulo = font.render("Tiempos T_n", True, (200, 200, 200))
    screen.blit(titulo, (base_x, base_y + 5))

    
    # CONTROLES
    controles = "[M] Modo | [R] Reset"
    ctrl_txt = font.render(controles, True, (120, 120, 120))
    screen.blit(ctrl_txt, (20, HEIGHT - 30))

    pygame.display.flip()


pygame.quit()
sys.exit()