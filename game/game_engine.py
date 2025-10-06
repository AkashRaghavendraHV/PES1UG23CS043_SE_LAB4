import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100
        self.winning_score = 5
        self.game_state = "PLAYING"  # States: PLAYING, GAME_OVER

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.game_state == "PLAYING":
            # Player controls during gameplay
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)
        
        elif self.game_state == "GAME_OVER":
            # Game over controls
            if keys[pygame.K_r]:
                self.restart_game()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                exit()

    def update(self):
        # Only update game logic if playing
        if self.game_state != "PLAYING":
            return
        
        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        # Check scoring
        if self.ball.x <= 0:
            self.ai_score += 1
            self.check_game_over()
            if self.game_state == "PLAYING":
                self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
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

    def restart_game(self):
        """Reset the game to initial state"""
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        self.game_state = "PLAYING"
        
        # Reset positions
        self.player.y = self.height // 2 - 50
        self.ai.y = self.height // 2 - 50
        self.ball.reset()

    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw score
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

        # Draw game over screen
        if self.game_state == "GAME_OVER":
            self.render_game_over(screen)

    def render_game_over(self, screen):
        """Display game over screen with winner and instructions"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Winner text
        winner_text = self.large_font.render(f"{self.winner} Wins!", True, YELLOW)
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 50))
        screen.blit(winner_text, winner_rect)
        
        # Final score
        score_text = self.font.render(
            f"Final Score: {self.player_score} - {self.ai_score}", 
            True, WHITE
        )
        score_rect = score_text.get_rect(center=(self.width//2, self.height//2 + 20))
        screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.small_font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 80))
        screen.blit(restart_text, restart_rect)
        
        quit_text = self.small_font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(self.width//2, self.height//2 + 110))
        screen.blit(quit_text, quit_rect)