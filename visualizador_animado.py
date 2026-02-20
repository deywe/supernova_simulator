import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

def replay_supernova_from_parquet(filename="supernova_signed_data.parquet"):
    print(f"🐦 HARPIA V29 - Carregando dados para reprodução visual...")
    
    # 1. Carregamento do Data-Set
    try:
        df = pd.read_parquet(filename)
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo Parquet: {e}")
        print("Por favor, execute o script V27 (generate_signed_dataset) primeiro para criar o arquivo.")
        return

    print(f"✅ Arquivo {filename} carregado com sucesso para reprodução.")
    print(f"✅ Total de frames disponíveis: {len(df)}")
    
    # Parâmetros fixos da simulação original (precisam ser os mesmos usados na geração)
    R_NODE = 5.0
    N_JATO = 4000
    N_RESIDUAL = 2500
    GLITCH_END_FRAME = 90 # Precisamos do glitch_end_frame para timing de partículas
    FRAMES = len(df) # O número de frames é o tamanho do DataFrame

    fig = plt.figure(figsize=(12, 10), facecolor='#000000')
    ax = fig.add_subplot(111, projection='3d', facecolor='#000000')
    ax.axis('off')

    # Geometria Base (para a malha da esfera)
    u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:40j]

    # Qubits de Saída (Funil e Resíduo) - Estes foram gerados deterministicamente
    # Recriar os vetores de direção da geração original (importante para consistência visual)
    np.random.seed(42) # Usar a mesma semente da geração
    v_jato_orig = np.random.uniform(10, 25, N_JATO)
    dir_jato_orig = []
    for i in range(N_JATO):
        side = 1 if i < N_JATO // 2 else -1
        spread = np.random.exponential(0.05)
        angle = np.random.uniform(0, 2*np.pi)
        vx, vy = np.cos(angle) * spread, np.sin(angle) * spread
        vz = side * (1.0 - spread)
        dir_jato_orig.append([vx, vy, vz])
    dir_jato_orig = np.array(dir_jato_orig)

    v_res_orig = np.random.uniform(1, 4, N_RESIDUAL)
    dir_res_orig = np.random.normal(0, 1, (N_RESIDUAL, 3))
    dir_res_orig /= np.linalg.norm(dir_res_orig, axis=1)[:, np.newaxis]
    
    # Artistas para a Animação
    particles_jato, = ax.plot([], [], [], 'o', color='#FFFFFF', markersize=0.4, alpha=0.5)
    particles_res, = ax.plot([], [], [], 'o', color='#FFD700', markersize=0.6, alpha=0.3)
    surface_dots, = ax.plot([], [], [], 'o', color='#FFD700', markersize=1.2, alpha=0.9)
    node_collection = [None]
    
    info_text = ax.text2D(0.02, 0.95, '', transform=ax.transAxes, color='#FFD700', fontfamily='monospace')

    def update(frame):
        # Remove o wireframe anterior
        if node_collection[0] is not None:
            node_collection[0].remove()
        
        # Leitura dos dados do frame atual do DataFrame
        row = df.iloc[frame]
        scale_z = row['scale_z']
        scale_r = row['scale_r']
        
        # --- Lógica de Câmera (Reproduzir o zoom out/in) ---
        if frame < GLITCH_END_FRAME:
            limit = 12
        elif frame < 300: 
            limit = 12 + (frame - GLITCH_END_FRAME) * 0.25
        else: 
            limit = max(15, 12 + (300 - GLITCH_END_FRAME) * 0.25 - (frame - 300) * 0.15)
        
        ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)

        # --- Reconstrução da Estrela (com deformação lida do Parquet) ---
        x_node = R_NODE * scale_r * np.cos(u) * np.sin(v)
        y_node = R_NODE * scale_r * np.sin(u) * np.sin(v)
        z_node = R_NODE * scale_z * np.cos(v)
        node_collection[0] = ax.plot_wireframe(x_node, y_node, z_node, color='#00FFFF', alpha=0.1, lw=0.4)

        # Partículas Douradas (também seguem a deformação)
        phi_s, theta_s = np.random.uniform(0, 2*np.pi, 1000), np.arccos(np.random.uniform(-1, 1, 1000))
        xs = (R_NODE * scale_r) * np.cos(phi_s) * np.sin(theta_s)
        ys = (R_NODE * scale_r) * np.sin(phi_s) * np.sin(theta_s)
        zs = (R_NODE * scale_z) * np.cos(theta_s)
        surface_dots.set_data(xs, ys); surface_dots.set_3d_properties(zs)

        # --- Reconstrução dos Jatos e Resíduo ---
        if frame > GLITCH_END_FRAME:
            # Jatos
            t_j = (frame - GLITCH_END_FRAME) * 1.5
            p_j = dir_jato_orig * (v_jato_orig[:, np.newaxis] * t_j)
            particles_jato.set_data(p_j[:, 0], p_j[:, 1]); particles_jato.set_3d_properties(p_j[:, 2])
            particles_jato.set_color('#FFD700' if frame % 2 == 0 else '#FFFFFF')

            # Resíduo
            t_r = (frame - GLITCH_END_FRAME) * 0.4
            p_r = dir_res_orig * (v_res_orig[:, np.newaxis] * t_r)
            mask_res = np.linalg.norm(p_r, axis=1) > R_NODE
            active_p_r = p_r[mask_res]
            particles_res.set_data(active_p_r[:, 0], active_p_r[:, 1])
            particles_res.set_3d_properties(active_p_r[:, 2])

        # HUD
        status_text = "REBOUND & RESIDUAL HARMONY" if frame > 300 else "TENSOR DISCHARGE"
        info_text.set_text(f"HARPIA V29 - PARQUET REPLAY\nFRAME: {frame}/{FRAMES-1}\nSTRETCH: {scale_z:.2f}x\nSTATUS: {status_text}")
        
        ax.view_init(elev=20, azim=frame * 0.5)
        return [particles_jato, particles_res, surface_dots, info_text]

    print("[*] Iniciando reprodução visual dos tensores...")
    ani = FuncAnimation(fig, update, frames=FRAMES, interval=20, blit=False)
    plt.show()

if __name__ == "__main__":
    replay_supernova_from_parquet()
