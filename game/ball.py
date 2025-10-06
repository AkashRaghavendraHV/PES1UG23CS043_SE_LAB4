import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        self.last_hit = None  # Track which paddle was hit last

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Wall collision (top/bottom)
        if self.y <= 0 or self.y + self.height >= self.screen_height:
            self.velocity_y *= -1
            # Position correction to prevent sticking
            if self.y <= 0:
                self.y = 0
            else:
                self.y = self.screen_height - self.height

    def check_collision(self, player, ai):
        ball_rect = self.rect()
        player_rect = player.rect()
        ai_rect = ai.rect()
        
        # Check collision with player paddle (left side)
        if ball_rect.colliderect(player_rect) and self.last_hit != 'player':
            # Verify ball is actually moving toward the paddle
            if self.velocity_x < 0:
                # Reverse horizontal velocity
                self.velocity_x *= -1
                
                # Position correction: place ball right next to paddle
                self.x = player_rect.right
                
                # Add slight random variation to y-velocity for variety
                self.velocity_y += random.uniform(-0.5, 0.5)
                
                # Mark this paddle as last hit to prevent double-bounce
                self.last_hit = 'player'
        
        # Check collision with AI paddle (right side)
        elif ball_rect.colliderect(ai_rect) and self.last_hit != 'ai':
            # Verify ball is actually moving toward the paddle
            if self.velocity_x > 0:
                # Reverse horizontal velocity
                self.velocity_x *= -1
                
                # Position correction: place ball right next to paddle
                self.x = ai_rect.left - self.width
                
                # Add slight random variation to y-velocity for variety
                self.velocity_y += random.uniform(-0.5, 0.5)
                
                # Mark this paddle as last hit to prevent double-bounce
                self.last_hit = 'ai'
        
        # Reset last_hit when ball is away from both paddles
        if not ball_rect.colliderect(player_rect) and not ball_rect.colliderect(ai_rect):
            self.last_hit = None

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        self.last_hit = None  # Reset collision tracking

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)