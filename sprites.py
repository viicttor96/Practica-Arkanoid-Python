import pygame
from settings import *
from pygame import Vector2
import random


class Brick(pygame.sprite.Sprite):
    def __init__(self, game, x, y, drop):
        self.groups = game.bricks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.drop = drop
        if drop:
            self.image = random.choice(game.glossy_brick_images)
            self.rect = self.image.get_rect()
        else:
            self.image = random.choice(game.brick_images)
            self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        
    def destroy(self):
        self.game.break_fx.play()
        self.kill()
    
    def drop_powerup(self):
        if self.drop:
            Item(self.game, self.rect.centerx, self.rect.centery)

    
class Item(pygame.sprite.Sprite):
    def __init__(self,game, x, y):
        self.groups = game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.powerup_img
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x,y)
        self.velocity = Vector2(0, 100)
    
    def update(self):
        self.rect.centerx += self.velocity.x 
        self.rect.centery += 1
        self.check_hits()

    def check_hits(self):
        hits = pygame.sprite.spritecollide(self, self.game.players, False)
        if len(hits) > 0:
            self.picked_by()
            self.kill()
            self.game.powerup_fx.play()

    def picked_by(self):
        self.game.powerup_multiball()


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x , y):
        self.game = game
        self.groups = game.players
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.pad_img
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = 0

    def update(self):
        self.keyboard_input()
        self.move()

    def move(self):
        self.velocity.x += self.acceleration * self.game.dt
        if self.velocity.magnitude() > PAD_MAX_SPEED:
            self.velocity.scale_to_length(PAD_MAX_SPEED)
        self.rect.centerx += self.velocity.x * self.game.dt
        self.velocity -= Vector2(self.velocity.x * DRAG * self.game.dt, 0)
        if self.velocity.magnitude() < 20:
            self.velocity.x = 0
        if self.rect.left < TILE_SIZE:
            self.rect.left = TILE_SIZE
            self.velocity.x = 0
        if self.rect.right > WIDTH - TILE_SIZE:
            self.rect.right = WIDTH - TILE_SIZE
            self.velocity.x = 0

    def hit(self, ball):
        offset = (ball.rect.centerx - self.rect.centerx) / (self.rect.width//2)
        ball.velocity.x = offset
        ball.rect.bottom = self.rect.top
    
    def keyboard_input(self):
        keystate = pygame.key.get_pressed()
        self.acceleration = 0
        if keystate[pygame.K_LEFT]:
            self.acceleration = -PAD_MAX_ACCEL
        if keystate[pygame.K_RIGHT]:
            self.acceleration = PAD_MAX_ACCEL


class Ball(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.balls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.ball_img
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.is_asleep = True
        self.push = 0

    def bounce(self, thing):
        if self.velocity.magnitude() == 0:
            return
        velocity = self.velocity.normalize()
        is_vertical_bounce = velocity.x == 0
        if velocity.x != 0:
            v_slope = -velocity.y / velocity.x
            corner = thing.rect.center
            if v_slope > 0 and velocity.x > 0:  # Q1 bottom left
                corner = thing.rect.bottomleft
            if v_slope < 0 and velocity.x < 0:  # Q2 bottom right
                corner = thing.rect.bottomright
            if v_slope > 0 and velocity.x < 0:  # Q3 top right
                corner = thing.rect.topright
            if v_slope < 0 and velocity.x > 0:  # Q4 top left
                corner = thing.rect.topleft
            towards_thing = (Vector2(corner) -
                             Vector2(self.rect.center))
            if towards_thing.magnitude() == 0:
                return
            towards_thing = towards_thing.normalize()
            if towards_thing.x == 0:
                is_vertical_bounce = True
            else:
                t_slope = towards_thing.y / towards_thing.x
                is_vertical_bounce = abs(v_slope) > abs(t_slope)
        if is_vertical_bounce:
            self.velocity.y *= -1
        else:
            self.velocity.x *= -1
        self.game.bounce_fx.play()
        self.push = 500
 
    def update(self):
        if self.is_asleep:
            if self.game.player.acceleration != 0 and self.game.player.velocity.magnitude() != 0:
                self.velocity = self.game.player.velocity.normalize() + Vector2(0, -1)
                self.is_asleep = False
            return

        if self.velocity.magnitude() != 0:
            self.rect.center += self.velocity.normalize() * (BALL_SPEED + self.push) * self.game.dt
        self.push *= 0.9

        if self.rect.right > WIDTH - TILE_SIZE:
            self.rect.right = WIDTH - TILE_SIZE
            self.velocity.x *= -1

        if self.rect.left < 0 + TILE_SIZE:
            self.rect.left = 0 + TILE_SIZE
            self.velocity.x *= -1

        if self.rect.top < 0 + TILE_SIZE:
            self.rect.top = 0 + TILE_SIZE
            self.velocity.y *= -1

        if self.rect.centery > HEIGHT:
            self.kill()
            self.game.any_ball_alive()


class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y, stage):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        if stage == 1:
            self.image = game.stage1_border
            self.rect = self.image.get_rect()
        elif stage == 2:
            self.image = game.stage2_border
            self.rect = self.image.get_rect()
        elif stage == 3:
            self.image = game.stage3_border
            self.rect = self.image.get_rect()
        else:
            self.image = game.stage4_border
            self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE


class BackGround(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        if game.stage == 0:
            self.image = game.wallpaper_img
            self.rect = self.image.get_rect()
        if game.stage == 1:
            self.image = game.bg_1_img
            self.rect = self.image.get_rect()
        if game.stage == 2:
            self.image = game.bg_2_img
            self.rect = self.image.get_rect()
        if game.stage == 3:
            self.image = game.bg_3_img
            self.rect = self.image.get_rect()
        if game.stage == 4:
            self.image = game.bg_4_img
            self.rect = self.image.get_rect()
        if game.stage == 5:
            self.image = game.victory_img
            self.rect = self.image.get_rect()