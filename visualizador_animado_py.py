import py5
import pandas as pd
import numpy as np

# --- Variáveis Globais ---
df = None
glitch_end_frame = 90
r_node = 150  
n_jato = 4000
n_residual = 2500
dir_jato = []
v_jato = []
dir_res = []
v_res = []

def map_value(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

def settings():
    # Definimos o tamanho inicial, mas permitimos redimensionamento
    py5.size(1200, 1000, py5.P3D)

def setup():
    global df, dir_jato, v_jato, dir_res, v_res
    
    # --- Comandos para Maximizar e Redimensionar ---
    py5.window_resizable(True)  # Ativa o botão de maximizar/redimensionar
    # py5.window_maximized(True) # Opcional: descomente para iniciar já maximizado
    
    py5.background(0)
    
    try:
        df = pd.read_parquet("supernova_signed_data.parquet")
        print(f"✅ Dados carregados: {len(df)} frames")
    except Exception as e:
        print(f"❌ Erro ao carregar Parquet: {e}")
        py5.exit_sketch()

    np.random.seed(42)
    v_jato = np.random.uniform(2, 8, n_jato)
    for i in range(n_jato):
        side = 1 if i < n_jato // 2 else -1
        spread = np.random.exponential(0.05)
        angle = np.random.uniform(0, 2 * np.pi)
        vx, vy = np.cos(angle) * spread, np.sin(angle) * spread
        vz = side * (1.0 - spread)
        dir_jato.append(np.array([vx, vy, vz]))
    
    v_res = np.random.uniform(0.5, 2.0, n_residual)
    for i in range(n_residual):
        vec = np.random.normal(0, 1, 3)
        vec /= np.linalg.norm(vec)
        dir_res.append(vec)

def draw():
    global df
    if df is None: return
    
    py5.background(0)
    frame = py5.frame_count % len(df)
    row = df.iloc[frame]
    
    scale_z = row['scale_z']
    scale_r = row['scale_r']
    
    # --- Câmera Adaptativa ao Tamanho da Janela ---
    if frame < glitch_end_frame:
        zoom = 400
    elif frame < 300:
        zoom = 400 + (frame - glitch_end_frame) * 5
    else:
        zoom = max(500, 400 + (300 - glitch_end_frame) * 5 - (frame - 300) * 3)
        
    # Usamos py5.width/2 e py5.height/2 para manter o centro sempre correto
    py5.translate(py5.width/2, py5.height/2, -zoom)
    py5.rotate_y(py5.frame_count * 0.01)
    py5.rotate_x(0.3)

    # --- Estrela ---
    py5.no_fill()
    py5.stroke(0, 255, 255, 100) 
    py5.stroke_weight(1)
    draw_deformed_sphere(r_node * scale_r, r_node * scale_z)

    # --- Partículas de Superfície ---
    py5.stroke(255, 215, 0, 150)
    py5.stroke_weight(2)
    py5.begin_shape(py5.POINTS)
    for _ in range(300):
        phi = np.random.uniform(0, 2*np.pi)
        theta = np.arccos(np.random.uniform(-1, 1))
        x = (r_node * scale_r) * np.sin(theta) * np.cos(phi)
        y = (r_node * scale_r) * np.sin(theta) * np.sin(phi)
        z = (r_node * scale_z) * np.cos(theta)
        py5.vertex(x, y, z)
    py5.end_shape()

    # --- Jatos e Resíduos ---
    if frame > glitch_end_frame:
        t_j = (frame - glitch_end_frame) * 5
        py5.stroke_weight(1)
        
        # Jatos
        py5.stroke(255, 255, 255) if frame % 2 == 0 else py5.stroke(255, 215, 0)
        py5.begin_shape(py5.POINTS)
        for i in range(n_jato):
            pos = dir_jato[i] * (v_jato[i] * t_j)
            py5.vertex(pos[0], pos[1], pos[2])
        py5.end_shape()

        # Resíduos
        py5.stroke(255, 215, 0, 80)
        t_r = (frame - glitch_end_frame) * 2
        py5.begin_shape(py5.POINTS)
        for i in range(n_residual):
            pos = dir_res[i] * (v_res[i] * t_r)
            if np.linalg.norm(pos) > r_node:
                py5.vertex(pos[0], pos[1], pos[2])
        py5.end_shape()

    draw_hud(frame, scale_z, len(df))

def draw_deformed_sphere(r_base, r_height):
    detail = 24
    for i in range(detail):
        lat0 = map_value(i, 0, detail, 0, np.pi)
        lat1 = map_value(i + 1, 0, detail, 0, np.pi)
        py5.begin_shape(py5.QUAD_STRIP)
        for j in range(detail + 1):
            lon = map_value(j, 0, detail, 0, 2 * np.pi)
            x0 = r_base * np.sin(lat0) * np.cos(lon)
            y0 = r_base * np.sin(lat0) * np.sin(lon)
            z0 = r_height * np.cos(lat0)
            x1 = r_base * np.sin(lat1) * np.cos(lon)
            y1 = r_base * np.sin(lat1) * np.sin(lon)
            z1 = r_height * np.cos(lat1)
            py5.vertex(x0, y0, z0)
            py5.vertex(x1, y1, z1)
        py5.end_shape()

def draw_hud(f, sz, total):
    py5.hint(py5.DISABLE_DEPTH_TEST)
    py5.camera() 
    py5.no_lights()
    py5.fill(255, 215, 0)
    status = 'REBOUND' if f > 300 else 'TENSOR DISCHARGE'
    txt = f"HARPIA V29 - PY5\nFRAME: {f}/{total-1}\nSTRETCH: {sz:.2f}x\nSTATUS: {status}"
    py5.text(txt, 30, 50)
    py5.hint(py5.ENABLE_DEPTH_TEST)

if __name__ == "__main__":
    py5.run_sketch()
