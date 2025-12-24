import pygame
import sys
import random
import math
from enum import Enum

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Adventure")

# Colors
BACKGROUND = (25, 25, 40)
WHITE = (255, 255, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 150)
BLUE = (100, 200, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 180, 50)
PINK = (255, 150, 200)
COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK]

# Bubble types
class BubbleType(Enum):
    NORMAL = 1
    BOMB = 2
    COIN = 3
    HEART = 4

# Sound effects (simple pygame tones)
def play_pop_sound():
    # Simple beep for popping
    pygame.mixer.Sound(buffer=bytes([128] * 8000)).play()

def play_collect_sound():
    # Higher pitch for collecting special bubbles
    pygame.mixer.Sound(buffer=bytes([200] * 4000)).play()

# Bubble class
class Bubble:
    def __init__(self, x=None, y=None):
        self.radius = random.randint(20, 40)
        self.x = x if x is not None else random.randint(self.radius, WIDTH - self.radius)
        self.y = y if y is not None else HEIGHT + self.radius
        self.speed = random.uniform(1.0, 3.0)
        self.color = random.choice(COLORS)
        
        # Random bubble type (mostly normal bubbles)
        rand_type = random.random()
        if rand_type < 0.05:  # 5% bomb bubbles
            self.type = BubbleType.BOMB
            self.color = (100, 100, 100)  # Gray
        elif rand_type < 0.1:  # 5% coin bubbles
            self.type = BubbleType.COIN
            self.color = (255, 215, 0)  # Gold
        elif rand_type < 0.12:  # 2% heart bubbles
            self.type = BubbleType.HEART
            self.color = (255, 100, 150)  # Pink-red
        else:  # 88% normal bubbles
            self.type = BubbleType.NORMAL
            
        self.pulse = 0
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.wobble = 0
        self.wobble_speed = random.uniform(0.03, 0.07)
        self.wobble_amount = random.uniform(0.5, 2.0)
        
    def update(self):
        self.y -= self.speed
        self.pulse += self.pulse_speed
        self.wobble += self.wobble_speed
        
        # Slight horizontal wobble
        self.x += math.sin(self.wobble) * self.wobble_amount
        
        # Keep bubble on screen horizontally
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        
    def draw(self, surface):
        # Pulsing effect
        current_radius = self.radius + math.sin(self.pulse) * 3
        
        # Draw bubble with highlight
        pygame.draw.circle(surface, self.color, 
                          (int(self.x), int(self.y)), int(current_radius))
        
        # Bubble highlight
        highlight_radius = current_radius * 0.4
        highlight_x = self.x - current_radius * 0.3
        highlight_y = self.y - current_radius * 0.3
        highlight_color = (255, 255, 255, 150)
        
        # Create surface for highlight with alpha
        highlight = pygame.Surface((highlight_radius * 2, highlight_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(highlight, highlight_color, 
                          (int(highlight_radius), int(highlight_radius)), int(highlight_radius))
        surface.blit(highlight, (highlight_x - highlight_radius, highlight_y - highlight_radius))
        
        # Draw symbols for special bubbles
        if self.type == BubbleType.BOMB:
            # Draw "X" for bomb
            line_length = current_radius * 0.7
            pygame.draw.line(surface, WHITE, 
                            (self.x - line_length, self.y - line_length),
                            (self.x + line_length, self.y + line_length), 3)
            pygame.draw.line(surface, WHITE,
                            (self.x + line_length, self.y - line_length),
                            (self.x - line_length, self.y + line_length), 3)
                            
        elif self.type == BubbleType.COIN:
            # Draw "$" for coin
            font = pygame.font.Font(None, int(current_radius))
            text = font.render("$", True, WHITE)
            surface.blit(text, (self.x - text.get_width()//2, self.y - text.get_height()//2))
            
        elif self.type == BubbleType.HEART:
            # Draw heart symbol
            font = pygame.font.Font(None, int(current_radius))
            text = font.render("♥", True, WHITE)
            surface.blit(text, (self.x - text.get_width()//2, self.y - text.get_height()//2))
    
    def is_off_screen(self):
        return self.y < -self.radius
    
    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
        return distance <= self.radius
    
    def get_points(self):
        if self.type == BubbleType.NORMAL:
            return 10
        elif self.type == BubbleType.COIN:
            return 50
        elif self.type == BubbleType.HEART:
            return 25
        return 0  # Bomb gives 0 points

# Particle effect for popping bubbles
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-4, 4)
        self.speed_y = random.uniform(-4, 4)
        self.life = random.randint(20, 40)
        self.gravity = 0.1
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, 
                          (int(self.x), int(self.y)), int(self.size))
        
    def is_dead(self):
        return self.life <= 0

# Game class
class BubbleGame:
    def __init__(self):
        self.bubbles = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0
        self.combo_timer = 0
        self.bubble_timer = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.game_over = False
        self.game_started = False
        self.spawn_rate = 60  # Frames between bubble spawns
        self.bubbles_popped = 0
        
        # Load background image (simple gradient)
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.create_gradient_background()
        
    def create_gradient_background(self):
        # Create a simple gradient background
        for y in range(HEIGHT):
            # Blue-purple gradient
            r = 25 + int(y / HEIGHT * 30)
            g = 25 + int(y / HEIGHT * 30)
            b = 40 + int(y / HEIGHT * 60)
            pygame.draw.line(self.background, (r, g, b), (0, y), (WIDTH, y))
        
        # Add some stars
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.uniform(0.5, 2)
            brightness = random.randint(150, 255)
            pygame.draw.circle(self.background, (brightness, brightness, brightness), 
                             (int(x), int(y)), int(size))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                if self.game_over and event.key == pygame.K_r:
                    self.__init__()  # Restart game
                    
                if not self.game_started and event.key == pygame.K_SPACE:
                    self.game_started = True
                    
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_started and not self.game_over:
                if event.button == 1:  # Left mouse button
                    self.check_bubble_click(event.pos)
    
    def check_bubble_click(self, pos):
        for bubble in self.bubbles[:]:
            if bubble.is_clicked(pos):
                # Handle different bubble types
                if bubble.type == BubbleType.BOMB:
                    self.lives -= 1
                    play_pop_sound()
                    if self.lives <= 0:
                        self.game_over = True
                else:
                    self.score += bubble.get_points()
                    self.combo += 1
                    self.combo_timer = 60  # 1 second combo timer
                    self.bubbles_popped += 1
                    
                    if bubble.type == BubbleType.HEART:
                        self.lives = min(5, self.lives + 1)
                        play_collect_sound()
                    elif bubble.type == BubbleType.COIN:
                        play_collect_sound()
                    else:
                        play_pop_sound()
                
                # Create particles
                for _ in range(15):
                    self.particles.append(Particle(bubble.x, bubble.y, bubble.color))
                
                # Remove the bubble
                self.bubbles.remove(bubble)
                
                # Check level progression
                if self.bubbles_popped % 20 == 0:
                    self.level += 1
                    self.spawn_rate = max(20, 60 - self.level * 3)  # Faster spawning as level increases
                
                break  # Only pop one bubble per click
    
    def update(self):
        if not self.game_started or self.game_over:
            return
            
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
            
        # Spawn bubbles
        self.bubble_timer += 1
        if self.bubble_timer > self.spawn_rate:
            self.bubble_timer = 0
            self.bubbles.append(Bubble())
            
            # Occasionally spawn multiple bubbles
            if random.random() < 0.1:
                for _ in range(random.randint(2, 4)):
                    self.bubbles.append(Bubble())
        
        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble.update()
            if bubble.is_off_screen():
                self.bubbles.remove(bubble)
                if bubble.type != BubbleType.BOMB:  # Only lose life for missing normal bubbles
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
    
    def draw(self):
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw bubbles
        for bubble in self.bubbles:
            bubble.draw(screen)
            
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (20, 20))
        
        # Draw lives
        hearts = "♥" * self.lives
        lives_text = self.font.render(f"Lives: {hearts}", True, (255, 100, 150))
        screen.blit(lives_text, (20, 60))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, BLUE)
        screen.blit(level_text, (20, 100))
        
        # Draw combo if active
        if self.combo > 1:
            combo_text = self.font.render(f"Combo: x{self.combo}!", True, GREEN)
            screen.blit(combo_text, (WIDTH - combo_text.get_width() - 20, 20))
        
        # Draw instructions
        if self.game_started:
            instructions = [
                "Click bubbles to pop them!",
                "Gray bubbles (X) are bombs - avoid them!",
                "Gold bubbles ($) give 50 points",
                "Heart bubbles (♥) give extra life",
                "Don't let bubbles reach the top!",
                "ESC: Quit  |  R: Restart"
            ]
            
            for i, text in enumerate(instructions):
                instr = self.small_font.render(text, True, WHITE)
                screen.blit(instr, (WIDTH - instr.get_width() - 20, 80 + i * 25))
        else:
            # Draw start screen
            title_font = pygame.font.Font(None, 72)
            title = title_font.render("Bubble Pop Adventure", True, (100, 200, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            
            start_text = self.font.render("Press SPACE to Start", True, GREEN)
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
            
            instr = self.small_font.render("Click on bubbles to pop them and score points!", True, YELLOW)
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT//2 + 50))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2))
            
            restart_text = self.font.render("Press R to Restart", True, GREEN)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

# Start the game
if __name__ == "__main__":
    game = BubbleGame()
    game.run()