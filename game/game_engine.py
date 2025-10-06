import pygame
import os
from .paddle import Paddle
from .ball import Ball

# Initialize pygame mixer for sound
pygame.mixer.init()

# Game Engine

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100
        self.winning_score = None  # Will be set to 3, 5, or 7
        self.game_state = "MENU"  # States: MENU, PLAYING, GAME_OVER

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.medium_font = pygame.font.SysFont("Arial", 35)
        
        # Load sound effects
        self.sounds = self.load_sounds()

    def load_sounds(self):
        """Load sound effects, use fallback if files don't exist"""
        sounds = {
            "paddle_hit": None,
            "wall_bounce": None,
            "score": None
        }
        
        # Define sound file paths
        sound_files = {
            "paddle_hit": "sounds/paddle_hit.wav",
            "wall_bounce": "sounds/wall_bounce.wav",
            "score": "sounds/score.wav"
        }
        
        # Try to load each sound file
        for sound_name, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    sounds[sound_name] = pygame.mixer.Sound(file_path)
                    sounds[sound_name].set_volume(0.7)  # Set volume to 70%
                    print(f"✓ Loaded {sound_name}: {file_path}")
                else:
                    # Create simple beep sound as fallback
                    sounds[sound_name] = self.create_beep_sound(sound_name)
                    print(f"⚠ Using fallback sound for {sound_name} (file not found: {file_path})")
            except Exception as e:
                print(f"✗ Error loading {sound_name}: {e}")
                sounds[sound_name] = self.create_beep_sound(sound_name)
        
        return sounds

    def create_beep_sound(self, sound_type):
        """Create a simple beep sound as fallback"""
        try:
            import numpy as np
            
            # Create different frequency beeps for different events
            sample_rate = 22050
            duration = 0.1  # 100ms
            
            if sound_type == "paddle_hit":
                frequency = 440  # A4 note
            elif sound_type == "wall_bounce":
                frequency = 330  # E4 note
            else:  # score
                frequency = 550  # C#5 note
                duration = 0.2
            
            # Generate simple sine wave
            samples = int(sample_rate * duration)
            wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
            
            # Apply fade out to avoid clicks
            fade_samples = int(samples * 0.1)
            wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit integer format
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo sound (duplicate mono to both channels)
            stereo_wave = np.column_stack((wave, wave))
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(0.5)  # Softer volume for beeps
            return sound
        except ImportError:
            print(f"⚠ numpy not installed - {sound_type} sound disabled")
            print("  Install with: pip install numpy")
            return None
        except Exception as e:
            print(f"✗ Error creating beep for {sound_type}: {e}")
            return None

    def play_sound(self, sound_name):
        """Play a sound effect if it exists"""
        if self.sounds.get(sound_name):
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing {sound_name}: {e}")

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.game_state == "MENU":
            # Menu selection
            if keys[pygame.K_3]:
                self.start_game(3)
            elif keys[pygame.K_5]:
                self.start_game(5)
            elif keys[pygame.K_7]:
                self.start_game(7)
            elif keys[pygame.K_ESCAPE]:
                pygame.quit()
                exit()
        
        elif self.game_state == "PLAYING":
            # Player controls during gameplay
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)
        
        elif self.game_state == "GAME_OVER":
            # Game over controls
            if keys[pygame.K_r]:
                self.return_to_menu()
            elif keys[pygame.K_ESCAPE]:
                pygame.quit()
                exit()

    def start_game(self, points):
        """Initialize a new game with specified winning score"""
        self.winning_score = points
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        self.game_state = "PLAYING"
        self.reset_positions()

    def return_to_menu(self):
        """Return to game selection menu"""
        self.game_state = "MENU"
        self.player_score = 0
        self.ai_score = 0
        self.winning_score = None
        self.winner = None
        self.reset_positions()

    def reset_positions(self):
        """Reset paddle and ball positions"""
        self.player.y = self.height // 2 - 50
        self.ai.y = self.height // 2 - 50
        self.ball.reset()

    def update(self):
        # Only update game logic if playing
        if self.game_state != "PLAYING":
            return
        
        self.ball.move()
        
        # Play wall bounce sound if ball hit a wall
        if self.ball.sound_event == "wall_bounce":
            self.play_sound("wall_bounce")
        
        self.ball.check_collision(self.player, self.ai)
        
        # Play paddle hit sound if ball hit a paddle
        if self.ball.sound_event == "paddle_hit":
            self.play_sound("paddle_hit")

        # Check scoring
        if self.ball.x <= 0:
            self.ai_score += 1
            self.play_sound("score")  # Play score sound
            self.check_game_over()
            if self.game_state == "PLAYING":
                self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.play_sound("score")  # Play score sound
            self.check_game_over()
            if self.game_state == "PLAYING":
                self.ball.reset()

        self.ai.auto_track(self.ball, self.height)

    def check_game_over(self):
        """Check if either player has reached the winning score"""
        if self.player_score >= self.winning_score:
            self.game_state = "GAME_OVER"
            self.winner = "Player"
        elif self.ai_score >= self.winning_score:
            self.game_state = "GAME_OVER"
            self.winner = "AI"

    def render(self, screen):
        if self.game_state == "MENU":
            self.render_menu(screen)
        else:
            # Draw game elements
            pygame.draw.rect(screen, WHITE, self.player.rect())
            pygame.draw.rect(screen, WHITE, self.ai.rect())
            pygame.draw.ellipse(screen, WHITE, self.ball.rect())
            pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

            # Draw score
            player_text = self.font.render(str(self.player_score), True, WHITE)
            ai_text = self.font.render(str(self.ai_score), True, WHITE)
            screen.blit(player_text, (self.width//4, 20))
            screen.blit(ai_text, (self.width * 3//4, 20))

            # Draw winning score indicator
            if self.winning_score:
                target_text = self.small_font.render(
                    f"First to {self.winning_score}",
                    True, CYAN
                )
                target_rect = target_text.get_rect(center=(self.width//2, 20))
                screen.blit(target_text, target_rect)

            # Draw game over overlay
            if self.game_state == "GAME_OVER":
                self.render_game_over(screen)

    def render_menu(self, screen):
        """Display game selection menu"""
        # Title
        title = self.large_font.render("PING PONG", True, YELLOW)
        title_rect = title.get_rect(center=(self.width//2, 100))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Select Winning Score", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(self.width//2, 180))
        screen.blit(subtitle, subtitle_rect)
        
        # Options
        options = [
            ("Press 3 - Play to 3 Points", 250),
            ("Press 5 - Play to 5 Points", 300),
            ("Press 7 - Play to 7 Points", 350),
        ]
        
        for text, y in options:
            option_text = self.medium_font.render(text, True, GREEN)
            option_rect = option_text.get_rect(center=(self.width//2, y))
            screen.blit(option_text, option_rect)
        
        # Exit option
        exit_text = self.small_font.render("Press ESC to Exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(self.width//2, 450))
        screen.blit(exit_text, exit_rect)
        
        # Controls info
        controls = self.small_font.render("Use W/S keys to move your paddle", True, CYAN)
        controls_rect = controls.get_rect(center=(self.width//2, 520))
        screen.blit(controls, controls_rect)

    def render_game_over(self, screen):
        """Display game over screen with winner and replay options"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Winner text
        winner_text = self.large_font.render(f"{self.winner} Wins!", True, YELLOW)
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 60))
        screen.blit(winner_text, winner_rect)
        
        # Final score
        score_text = self.font.render(
            f"Final Score: {self.player_score} - {self.ai_score}", 
            True, WHITE
        )
        score_rect = score_text.get_rect(center=(self.width//2, self.height//2))
        screen.blit(score_text, score_rect)
        
        # Winning target
        target_text = self.small_font.render(
            f"(First to {self.winning_score})",
            True, CYAN
        )
        target_rect = target_text.get_rect(center=(self.width//2, self.height//2 + 40))
        screen.blit(target_text, target_rect)
        
        # Options
        restart_text = self.small_font.render("Press R to Play Again", True, GREEN)
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 90))
        screen.blit(restart_text, restart_rect)
        
        quit_text = self.small_font.render("Press ESC to Exit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(self.width//2, self.height//2 + 120))
        screen.blit(quit_text, quit_rect)