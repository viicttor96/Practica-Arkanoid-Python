import pygame
from settings import *
from sprites import *
from map import Map
from os import path


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.load_data()
        self.stage = 0
        self.score = 0
        self.small_font = pygame.font.SysFont('purisa', 32)
        self.large_font = pygame.font.SysFont('purisa', 100)

    def load_data(self):
        root_folder = path.dirname(__file__)
        fx_folder = path.join(root_folder, "sound")
        img_folder = path.join(root_folder, "img")
        
        self.load_fx_and_music(fx_folder)
        self.load_img(img_folder)

    def load_fx_and_music(self, fx_folder):
        self.bounce_fx = pygame.mixer.Sound(path.join(fx_folder, "bounce.wav"))
        pygame.mixer.Sound.set_volume(self.bounce_fx, 0.2)
        self.break_fx = pygame.mixer.Sound(path.join(fx_folder, "break.wav"))
        pygame.mixer.Sound.set_volume(self.break_fx, 0.15)
        self.victory_fx = pygame.mixer.Sound(path.join(fx_folder, "victory.wav"))
        pygame.mixer.Sound.set_volume(self.victory_fx, 0.2)
        self.powerup_fx = pygame.mixer.Sound(path.join(fx_folder, "powerup.wav"))
        pygame.mixer.Sound.set_volume(self.powerup_fx, 0.15)
        self.game_over_fx = pygame.mixer.Sound(path.join(fx_folder, "gameover.wav"))
        pygame.mixer.Sound.set_volume(self.game_over_fx, 0.2)
        self.menu_fx = pygame.mixer.Sound(path.join(fx_folder, "menu.wav"))
        pygame.mixer.Sound.set_volume(self.menu_fx, 0.1)
        self.stage1_fx = pygame.mixer.Sound(path.join(fx_folder, "stage1.wav"))
        pygame.mixer.Sound.set_volume(self.stage1_fx, 0.07)
        self.stage2_fx = pygame.mixer.Sound(path.join(fx_folder, "stage2.wav"))
        pygame.mixer.Sound.set_volume(self.stage2_fx, 0.07)
        self.stage3_fx = pygame.mixer.Sound(path.join(fx_folder, "stage3.wav"))
        pygame.mixer.Sound.set_volume(self.stage3_fx, 0.07)
        self.stage4_fx = pygame.mixer.Sound(path.join(fx_folder, "stage4.wav"))
        pygame.mixer.Sound.set_volume(self.stage4_fx, 0.07)

    def load_img(self, img_folder):
        self.wallpaper_img = pygame.image.load(path.join(img_folder, "wallpaper.png"))
        self.pad_img = pygame.image.load(
                            path.join(img_folder, "paddleRed.png"))
        self.ball_img = pygame.image.load(
                            path.join(img_folder, "ballGrey.png"))
        self.stage1_border = pygame.image.load(
                            path.join(img_folder, "element_grey_square_glossy.png"))
        self.stage2_border = pygame.image.load(
                            path.join(img_folder, "element_yellow_square_glossy.png"))
        self.stage3_border = pygame.image.load(
                            path.join(img_folder, "element_blue_square_glossy.png"))
        self.stage4_border = pygame.image.load(
                            path.join(img_folder, "element_purple_cube_glossy.png"))
        self.powerup_img = pygame.image.load(path.join(img_folder, "powerup.png"))
        self.bg_1_img = pygame.image.load(path.join(img_folder, "bg_1.png"))
        self.bg_2_img = pygame.image.load(path.join(img_folder, "bg_2.png"))
        self.bg_3_img = pygame.image.load(path.join(img_folder, "bg_3.png"))
        self.bg_4_img = pygame.image.load(path.join(img_folder, "bg_4.png"))
        self.victory_img = pygame.image.load(path.join(img_folder, "victory_img.png"))
        self.gameover_img = pygame.image.load(path.join(img_folder, "game_over_img.png"))

        brick_colors = ["blue", "purple", "green", "grey", "yellow", "red"]
        self.brick_images = []
        self.glossy_brick_images = []
        for color in brick_colors:
            filename = f"element_{color}_rectangle.png"
            filename_glossy = f"element_{color}_rectangle_glossy.png"
            img = pygame.image.load(path.join(img_folder, filename))
            self.brick_images.append(img)
            img = pygame.image.load(path.join(img_folder, filename_glossy))
            self.glossy_brick_images.append(img)
        
    def start(self):
        self.bricks = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.create_stage()
        self.player = Player(self, WIDTH//2, HEIGHT-PAD_HEIGHT*2)
        self.ball = Ball(self, WIDTH//2, HEIGHT-PAD_HEIGHT*4)
        self.run()

    def create_stage(self):
            self.current_map = Map()
            self.current_map.load_map_from_file(self.stage)
            self.current_map.create_sprites_from_data(self, self.stage)
            self.change_music_playing()

    def run(self):
        self.playing = True
        while (self.playing):
            self.dt = self.clock.tick(FPS)/1000
            self.event()
            self.update()
            self.draw()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    def update(self):
        self.update_collisions()
        self.bricks.update()
        self.balls.update()
        self.items.update()
        self.players.update()   

    def change_music_playing(self):
            if self.stage == 1:
                self.menu_fx.stop()
                self.stage1_fx.play(-1)
            if self.stage == 2:
                self.stage1_fx.stop()
                self.stage2_fx.play(-1)
            if self.stage == 3:
                self.stage2_fx.stop()
                self.stage3_fx.play(-1)
            if self.stage == 4:
                self.stage3_fx.stop()
                self.stage4_fx.play(-1)

    def update_collisions(self):
        hits = pygame.sprite.spritecollide(self.player, self.balls, False)
        for ball in hits:
            ball.bounce(self.player)
            self.player.hit(ball)

        hits = pygame.sprite.groupcollide(
            self.balls, self.bricks, False, False)
        for ball, bricks in hits.items():
            the_brick = bricks[0]
            ball.bounce(the_brick)
            the_brick.destroy()
            the_brick.drop_powerup()
            self.current_map.counter -= 1
            self.score += 1
            if self.current_map.counter == 0:
                if self.stage < 4:
                    self.stage += 1
                    self.start()
                else: 
                    self.victory_screen()
            break
  
    def victory_screen(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.victory_img, (0, 0))
        won_text = self.large_font.render(f'YOU WON!', True, (255, 255, 255))
        score_text = self.small_font.render(
                             f'Your score is: {self.score}', True, (210,210,210))
        esc_text = self.small_font.render(
            "Press ESC to QUIT", True, (190,190,190))
        self.screen.blit(
            won_text,
            (WIDTH//2 - won_text.get_rect().centerx,
             HEIGHT//2 - won_text.get_rect().centery))
        self.screen.blit(
            score_text,
            (WIDTH//2 - score_text.get_rect().centerx,
             HEIGHT//2 - score_text.get_rect().centery + 64))
        self.screen.blit(
            esc_text,
            (WIDTH//2 - esc_text.get_rect().centerx,
             HEIGHT//2 - esc_text.get_rect().centery + 100))
        pygame.display.flip()
        self.stage1_fx.stop()
        self.stage2_fx.stop()
        self.stage3_fx.stop()
        self.stage4_fx.stop()
        self.victory_fx.play()
        pygame.time.delay(1000)
        in_victory = True
        while in_victory:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    in_victory = False
        self.main_menu()

    def any_ball_alive(self):
        balls_alive = pygame.sprite.Group.sprites(self.balls)
        if not balls_alive:
            self.game_over()

    def powerup_multiball(self):
        for _ in range(random.randint(MIN_POWERUP_NUM, MAX_POWERUP_NUM)):
            reference = self.balls.sprites()[0]
            ball = Ball(self, reference.rect.centerx, reference.rect.centery)
            ball.velocity = Vector2(
                    reference.velocity.x + random.uniform(-0.5, 0.5), 
                    reference.velocity.y)
            ball.is_asleep=False
        self.score += 5

    def game_over(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.gameover_img, (0, 0))
        pygame.display.flip()
        self.stage1_fx.stop()
        self.stage2_fx.stop()
        self.stage3_fx.stop()
        self.stage4_fx.stop()
        self.game_over_fx.play()
        esc_text = self.small_font.render(
            "Press ESC to QUIT", True, (190,190,190))
        self.screen.blit(
            esc_text,
            (WIDTH//2 - esc_text.get_rect().centerx,
             HEIGHT//2 - esc_text.get_rect().centery + 130))
        pygame.display.flip()
        pygame.time.delay(1000)
        in_game_over = True
        while in_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    in_game_over = False
        self.main_menu()

    def draw(self):
        self.background = BackGround(self)
        self.screen.blit(self.background.image, (0, 0))
        self.walls.draw(self.screen)
        self.bricks.draw(self.screen)
        self.balls.draw(self.screen)
        self.players.draw(self.screen)
        self.items.draw(self.screen)
        self.draw_score()
        pygame.display.flip()

    def draw_score(self):
        score_text = self.small_font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (TILE_SIZE, TILE_SIZE * 0.6))

    def main_menu(self):
        self.score = 0
        self.stage = 0
        title_text = self.large_font.render("ARKANOID", True, (255, 255, 255))
        instructions_text = self.small_font.render(
            "Press any key to PLAY", True, (190,190,190))
        esc_text = self.small_font.render(
            "Press ESC to QUIT", True, (190,190,190))
        background = BackGround(self)
        self.menu_fx.play(-1)
        self.screen.blit(background.image, (0, 0))
        self.screen.blit(
            title_text,
            (WIDTH//2 - title_text.get_rect().centerx,
             HEIGHT//2 - title_text.get_rect().centery))
        self.screen.blit(
            instructions_text,
            (WIDTH//2 - instructions_text.get_rect().centerx,
             HEIGHT//2 - instructions_text.get_rect().centery + 64))
        self.screen.blit(
            esc_text,
            (WIDTH//2 - esc_text.get_rect().centerx,
             HEIGHT//2 - esc_text.get_rect().centery + 100))
        pygame.display.flip()

        pygame.time.delay(3000)

        in_main_menu = True
        while in_main_menu:
            pressed = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if (event.type == pygame.KEYDOWN):
                    if pressed[pygame.K_ESCAPE]:
                        quit()
                    in_main_menu = False
        self.stage = 1
        self.start()


game = Game()
game.main_menu()