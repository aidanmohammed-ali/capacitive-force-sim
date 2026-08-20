"""
@file gui_sim.py
@author Aidan Mohammed-Ali
@brief Real-time interactive GUI for the tactile matrix simulation.
@date 2026-08-20
"""

# =============================
# Frameworks
# =============================
import pygame
import numpy as np

# =============================
# Custom Modules
# =============================
import matrix_sim

# --- Configuration ---
ROWS, COLS = 16, 32
CELL_SIZE = 75 # Pixels per taxel
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Max force (N) to cap the input at, and approximate max delta Farads for the color scale
MAX_FORCE = 5.0
MAX_DELTA_C = 1.6e-17
MIN_RAW_C = 2.4e-13
MAX_RAW_C = 2.7e-13

def run_gui():
    """
    @brief Intitialises and runs the main Pygame loop for the tactile matrix GUI.
    @details Includes a spacebar toggle to switch between raw and delta capacitance.
    """
    print("Starting Tactile Matrix GUI...")
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Tactile Skin Simulator ({ROWS}x{COLS})")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    
    # Load physics
    cal_data = matrix_sim.load_calibration("constants.json")
    forces = np.zeros((ROWS, COLS))
    baseline = matrix_sim.simulate_matrix_readout(np.zeros((ROWS, COLS)), cal_data)
    
    show_delta = True
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_delta = not show_delta
        
        # Handle mouse input
        mouse_buttons = pygame.mouse.get_pressed()
        x, y = pygame.mouse.get_pos()
        c = x // CELL_SIZE
        r = y // CELL_SIZE
        
        if 0 <= r < ROWS and 0 <= c < COLS:
            if mouse_buttons[0]:
                forces[r, c] = min(forces[r, c] + 0.1, MAX_FORCE)
            elif mouse_buttons[2]:
                forces[r, c] = 0.0
        
        # Calculate physics superposition
        active_matrix = matrix_sim.simulate_matrix_readout(forces, cal_data)
        delta_matrix = active_matrix - baseline
        
        # Update window title to show current mode
        if show_delta:
            mode_text = "DELTA Mode (aF)"
        else:
            mode_text = "RAW Mode (fF)"
        pygame.display.set_caption(f"Tactile Skin ({ROWS}x{COLS}) | {mode_text} | Press SPACE to toggle")
        
        # Render the heatmap
        screen.fill((20, 20, 20))
        
        for row in range(ROWS):
            for col in range(COLS):
                if show_delta:
                    val = delta_matrix[row, col]
                    intensity = int(min(max(val / MAX_DELTA_C, 0), 1) * 255)
                    display_val = val * 1e18
                    threshold = 0.1
                else:
                    val = active_matrix[row, col]
                    norm = (val - MIN_RAW_C) / (MAX_RAW_C - MIN_RAW_C)
                    intensity = int(min(max(norm, 0), 1) * 255)
                    display_val = val * 1e15
                    threshold = 0.0
                
                color = (intensity, 0, 255 - intensity)
                rect = (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Draw the coloured taxel and a subtle grid outline
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (40, 40, 40), rect, 1)
                
                if display_val > threshold or not show_delta:
                    text_surface = font.render(f"{display_val:.3f}", True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))
                    screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(30)
        
    pygame.quit()
    print("GUI closed.")
    
if __name__ == "__main__":
    run_gui()
