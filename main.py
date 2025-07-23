import pgzrun
import sys
import random

WIDTH = 800
HEIGHT = 600
TITLE = "Bunny Bee Bounce"
TILE_SIZE = 16
FONT_NAME = "pixel"

GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 4


STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


class Button:
    def __init__(self, text, pos):
        self.text = text
        self.pos = pos
        self.rect = Rect(0, 0, 250, 50)
        self.rect.center = self.pos

    def draw(self, screen, font_name):
        screen.draw.filled_rect(self.rect, '#2E4053')
        screen.draw.rect(self.rect, 'white')
        screen.draw.text(
            self.text,
            center=self.rect.center,
            fontname=font_name,
            fontsize=24,
            color='white'
        )

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Player(Actor):
    def __init__(self, pos):
        self.right_images = ['player_idle_1', 'player_idle_2']
        self.left_images = ['player_idle_1_left', 'player_idle_2_left']
        
        self.frame = 0
        self.timer = 0
        self.direction = 'right'
        
        super().__init__(self.right_images[0], pos)
        self.vy = 0
        self.on_ground = False

    def update(self, platforms):
        dx = 0
        if keyboard.left:
            dx = -PLAYER_SPEED
            self.direction = 'left'
        elif keyboard.right:
            dx = PLAYER_SPEED
            self.direction = 'right'
        
        self.vy += GRAVITY
        if keyboard.space and self.on_ground:
            self.vy = JUMP_STRENGTH
            game.play_sound('jump')

        self.x += dx
        self.y += self.vy

        if self.left < 0: self.left = 0
        if self.right > WIDTH: self.right = WIDTH
            
        self.timer += 1
        if self.timer > 15:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.right_images)
            if self.direction == 'right':
                self.image = self.right_images[self.frame]
            else:
                self.image = self.left_images[self.frame]
        
        self.on_ground = False
        for p in platforms:
            if self.colliderect(p):
                # **CORREÇÃO APLICADA AQUI**
                # Revertido para a lógica de colisão simples e funcional.
                if self.vy > 0:
                    self.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                # Colisão vertical (batendo a cabeça na plataforma)
                elif self.vy < 0:
                    self.top = p.bottom
                    self.vy = 0

class Enemy(Actor):
    def __init__(self, pos, patrol_range=100):
        self.fly_right_images = ['bee_fly_1', 'bee_fly_2']
        self.fly_left_images = ['bee_fly_1_left', 'bee_fly_2_left']
        
        self.frame = 0
        self.timer = 0
        super().__init__(self.fly_right_images[0], pos)
        
        self.start_x = pos[0]
        self.patrol_range = patrol_range
        self.speed = random.uniform(1.0, 2.0)

    def update(self):
        self.x += self.speed
        if abs(self.x - self.start_x) > self.patrol_range:
            self.speed *= -1
            if self.x > self.start_x:
                self.x = self.start_x + self.patrol_range
            else:
                self.x = self.start_x - self.patrol_range

        self.timer += 1
        if self.timer > 10:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.fly_right_images)
            if self.speed > 0:
                self.image = self.fly_right_images[self.frame]
            else:
                self.image = self.fly_left_images[self.frame]


class Game:
    def __init__(self):
        self.restart_game()

    def create_platform(self, x, y, length):
        left_grass, middle_grass, right_grass = 'tile_0001', 'tile_0002', 'tile_0003'
        single_block = 'tile_0000'

        if length == 1:
            self.platforms.append(Actor(single_block, (x, y)))
            return

        self.platforms.append(Actor(left_grass, (x, y)))
        for i in range(1, length - 1):
            tile_x = x + i * TILE_SIZE
            self.platforms.append(Actor(middle_grass, (tile_x, y)))
        last_tile_x = x + (length - 1) * TILE_SIZE
        self.platforms.append(Actor(right_grass, (last_tile_x, y)))


    def restart_game(self):
        self.game_state = STATE_MENU
        self.score = 0
        self.effects_on = True 
        self.music_on = True   
        
        self.buttons = {
            "start": Button("Start Game", (WIDTH / 2, 220)),
            "effects": Button("Effects: ON", (WIDTH / 2, 290)),
            "music": Button("Music: ON", (WIDTH / 2, 360)),
            "exit": Button("Exit", (WIDTH / 2, 430))
        }
        
        self.platforms = []
        
        self.create_platform(100, 500, length=14)
        self.create_platform(500, 400, length=10)
        self.create_platform(200, 300, length=8)
        self.create_platform(600, 200, length=5)
        self.create_platform(50, 150, length=10)
        
        self.create_platform(400, 450, length=1)
        self.create_platform(150, 400, length=1)
        self.create_platform(550, 300, length=1)
        self.create_platform(250, 200, length=1)

        floor_length = int(WIDTH / TILE_SIZE) + 2
        self.create_platform(0, HEIGHT - TILE_SIZE / 2, length=floor_length)

        self.player = Player((150, 450))
        
        self.enemies = [
            Enemy((250, 250), patrol_range=40), Enemy((650, 150), patrol_range=30),
            Enemy((100, 100), patrol_range=60), Enemy((400, 450), patrol_range=100),
            Enemy((700, 300), patrol_range=50), Enemy((200, 200), patrol_range=50)
        ]
        
        self.toggle_music()

    def draw(self):
        screen.clear()
        if self.game_state == STATE_MENU: self.draw_menu()
        elif self.game_state == STATE_PLAYING: self.draw_playing()
        elif self.game_state == STATE_GAME_OVER: self.draw_game_over()
        elif self.game_state == STATE_VICTORY: self.draw_victory()

    def update(self, dt):
        if self.game_state == STATE_PLAYING: self.update_playing(dt)

    def on_mouse_down(self, pos):
        if self.game_state == STATE_MENU:
            if self.buttons["start"].is_clicked(pos):
                self.game_state = STATE_PLAYING
            elif self.buttons["effects"].is_clicked(pos):
                self.effects_on = not self.effects_on
                self.buttons["effects"].text = f"Effects: {'ON' if self.effects_on else 'OFF'}"
            elif self.buttons["music"].is_clicked(pos):
                self.music_on = not self.music_on
                self.buttons["music"].text = f"Music: {'ON' if self.music_on else 'OFF'}"
                self.toggle_music()
            elif self.buttons["exit"].is_clicked(pos):
                sys.exit()

    def on_key_down(self, key):
        if self.game_state == STATE_GAME_OVER or self.game_state == STATE_VICTORY:
            self.restart_game()

    def draw_menu(self):
        screen.fill('#6495ED')
        screen.draw.text(
            TITLE,
            center=(WIDTH / 2, 120),
            fontname=FONT_NAME,
            fontsize=50,
            color='white',
            owidth=1.5, ocolor='black'
        )
        for button in self.buttons.values():
            button.draw(screen, FONT_NAME)

    def draw_playing(self):
        screen.fill('#6495ED')
        for p in self.platforms: p.draw()
        for e in self.enemies: e.draw()
        self.player.draw()
        screen.draw.text(f"Score: {self.score}", (20, 20), fontname=FONT_NAME, fontsize=24, color="white")

    def update_playing(self, dt):
        self.player.update(self.platforms)
        
        for e in self.enemies[:]:
            e.update()
            if self.player.colliderect(e):
                if self.player.vy > 0 and self.player.bottom < e.center[1]:
                    self.enemies.remove(e)
                    self.score += 1
                    self.player.vy = JUMP_STRENGTH * 0.5
                    self.play_sound('enemy_hit')
                else:
                    self.trigger_game_over()
        
        if not self.enemies and self.game_state == STATE_PLAYING:
            self.trigger_victory()
        
        if self.player.top > HEIGHT: self.trigger_game_over()

    def draw_game_over(self):
        screen.fill('black')
        screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2 - 50), fontname=FONT_NAME, fontsize=50, color="red")
        screen.draw.text("Press any key to restart", center=(WIDTH / 2, HEIGHT / 2 + 50), fontname=FONT_NAME, fontsize=24, color="white")

    def draw_victory(self):
        screen.fill('dark green')
        screen.draw.text("YOU WIN!", center=(WIDTH / 2, HEIGHT / 2 - 50), fontname=FONT_NAME, fontsize=60, color="yellow")
        screen.draw.text(f"Final Score: {self.score}", center=(WIDTH / 2, HEIGHT / 2 + 20), fontname=FONT_NAME, fontsize=30, color="white")
        screen.draw.text("Press any key to restart", center=(WIDTH / 2, HEIGHT / 2 + 80), fontname=FONT_NAME, fontsize=24, color="white")

    def trigger_game_over(self):
        if self.game_state == STATE_PLAYING:
            self.game_state = STATE_GAME_OVER
            self.play_sound('game_over')

    def trigger_victory(self):
        self.game_state = STATE_VICTORY
        self.play_sound('victory')

    def play_sound(self, name):
        if self.effects_on:
            sound = getattr(sounds, name)
            sound.play()

    def toggle_music(self):
        if self.music_on:
            music.play('background_music')
        else:
            music.stop()

game = Game()
def draw(): game.draw()
def update(dt): game.update(dt)
def on_key_down(key): game.on_key_down(key)
def on_mouse_down(pos): game.on_mouse_down(pos)

pgzrun.go()