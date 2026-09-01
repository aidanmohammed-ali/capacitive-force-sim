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
MAX_DELTA_C = 5.0e-14

def get_thermal_color(norm_val: float) -> tuple:
    """
    @brief Maps a normalised float (0.0 to 1.0) to a Black->Blue->Cyan->Yellow->Red color scale.
    @param norm_val The normalized delta capacitance value as a float (clamped between 0.0 and 1.0).
    @return An (R, G, B) tuple of integers representing the thermal color.
    """
    norm_val = max(0.0, min(1.0, norm_val))
    if norm_val < 0.25:
        t = norm_val / 0.25
        return (0, 0, int(255 * t))
    elif norm_val < 0.5:
        t = (norm_val - 0.25) / 0.25
        return (0, int(255 * t), 255)
    elif norm_val < 0.75:
        t = (norm_val - 0.5) / 0.25
        return (int(255 * (1 - t)), 255, int(255 * (1 - t)))
    else:
        t = (norm_val - 0.75) / 0.25
        return (255, int(255 * (1 - t)), 0)

def get_raw_color(norm_val: float) -> tuple:
    """
    @brief Soft, low-contrast color scale (Dark Blue -> Muted Cyan) for the RAW baseline.
    @param norm_val The normalized baseline capacitance value as a float (clamped between 0.0 and 1.0).
    @return An (R, G, B) tuple of integers representing the cool/raw structural color.
    """
    norm_val = max(0.0, min(1.0, norm_val))
    r = int(30 + 20 * norm_val)
    g = int(40 + 100 * norm_val)
    b = int(80 + 120 * norm_val)
    return (r, g, b)

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
    font = pygame.font.SysFont(None, 20)
    
    # Load physics
    cal_data = matrix_sim.load_calibration("constants.json")
    forces = np.zeros((ROWS, COLS))
    baseline = matrix_sim.simulate_matrix_readout(np.zeros((ROWS, COLS)), cal_data)
    
    # Dynamic Auto-Scaling
    MIN_RAW_C = np.nanmin(baseline)
    MAX_RAW_C = np.nanmax(baseline) + MAX_DELTA_C
    
    display_mode = 1
    running = True
    
    while running:
        # Get the actual window size the OS provided
        actual_width, actual_height = screen.get_size()
        
        # Calculate dynamic cell widths and heights (as floats)
        cell_w = actual_width / COLS
        cell_h = actual_height / ROWS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    display_mode = (display_mode + 1) % 3
        
        # Handle mouse input
        mouse_buttons = pygame.mouse.get_pressed()
        x, y = pygame.mouse.get_pos()
        c = int(x // cell_w)
        r = int(y // cell_h)
        
        if 0 <= r < ROWS and 0 <= c < COLS:
            if mouse_buttons[0]:
                forces[r, c] = min(forces[r, c] + 0.1, MAX_FORCE)
            elif mouse_buttons[2]:
                forces[r, c] = 0.0
        
        # Calculate physics superposition
        active_matrix = matrix_sim.simulate_matrix_readout(forces, cal_data)
        delta_matrix = active_matrix - baseline
        
        # Update window title to show current mode
        if display_mode == 0:
            mode_text = "RAW Mode (fF)"
        elif display_mode == 1:
            mode_text = "DELTA Mode (pF)"
        else:
            mode_text = "FORCE Mode (N)"
        pygame.display.set_caption(f"Tactile Skin ({ROWS}x{COLS}) | {mode_text} | Press SPACE to toggle")
        
        # Render the heatmap
        screen.fill((20, 20, 20))
        
        for row in range(ROWS):
            for col in range(COLS):
                is_saturated = False
                
                if display_mode == 1: # DELTA MODE
                    val = delta_matrix[row, col]
                    if np.isnan(val):
                        is_saturated = True
                    else:
                        norm = val / MAX_DELTA_C
                        display_val = val * 1e15
                        threshold = 0.01
                elif display_mode == 2: # FORCE MODE
                    val = forces[row, col]
                    is_saturated = False
                    norm = val / MAX_FORCE
                    display_val = val
                    threshold = 0.01
                else: # RAW MODE
                    val = active_matrix[row, col]
                    if np.isnan(val):
                        is_saturated = True
                    else:
                        norm = (val - MIN_RAW_C) / (MAX_RAW_C - MIN_RAW_C)
                        intensity = int(min(max(norm, 0), 1) * 255)
                        display_val = val * 1e12
                        threshold = 0.0
                
                # Check hardware saturation
                if is_saturated:
                    color = (255, 255, 255)
                    text_surface = font.render("SAT", True, (0, 0, 0))
                    draw_text = True
                else:                
                    if display_mode == 0:
                        color = get_raw_color(norm)
                    else:
                        color = get_thermal_color(norm)
                    
                    luminance = (0.2126 * color[0]) + (0.7152 * color[1]) + (0.0722 * color[2])
                    if luminance > 140:
                        text_color = (0, 0, 0)
                    else:
                        text_color = (255, 255, 255)
                    text_surface = font.render(f"{display_val:.3f}", True, text_color)
                    draw_text = (display_val > threshold) or (display_mode == 0)
                
                rect = (col * cell_w, row * cell_h, cell_w, cell_h)
                
                # Draw the coloured taxel and a subtle grid outline
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (30, 30, 30), rect, 1)
                
                if draw_text:
                    text_rect = text_surface.get_rect(center=(col * cell_w + cell_w // 2, row * cell_h + cell_h // 2))
                    screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(30)
        
    pygame.quit()
    print("GUI closed.")
    
if __name__ == "__main__":
    run_gui()
