from random import randint
from time import time as timer

from pygame import *
init()
mixer.init()
font.init()

class InterfaceImage:
    def __init__(self, sprite_image, x, y, width, height):
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))

class HpImage(InterfaceImage):
    def __init__(self, x):
        super().__init__("images/heart.png", x, 20, 50, 50)


class ClipImage(InterfaceImage):
    def __init__(self, x):
        super().__init__("images/bullet.png", x, 670, 15, 30)


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.resistance = False
        self.resistance_time = 0
        self.shield_image = transform.scale(image.load("images/shield_bonus.png"), (width, width))

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))
        if self.resistance:
            virtual_surface.blit(self.shield_image, (self.rect.x, self.rect.y))

    def get_shield(self, duration):
        self.resistance_time = duration
        self.resistance = True

    def buff_time_reduce(self):
        if self.resistance:
            self.resistance_time -= 1
            if self.resistance_time <= 0:
                self.resistance = False


class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/rocket.png", x, y, 100, 150, 10)
        self.kd_shoot = 6
        self.wait = 0
        self.hp = 3
        self.clip = 10
        self.start_reload = 0

        self.reload = False
        self.alive = True

        self.health_list = []
        self.interface_clip = []
        self.full_interface_clip = []

        heart_x = 1210
        for i in range(self.hp):
            heart = HpImage(heart_x)
            self.health_list.append(heart)
            heart_x -= 60

        ammo_x = 20
        for i in range(self.clip):
            cartridge = ClipImage(ammo_x)
            self.full_interface_clip.append(cartridge)
            ammo_x += 15

        self.interface_clip = self.full_interface_clip

    def update(self):
        self.buff_time_reduce()
        keys_pressed = key.get_pressed()
        if keys_pressed[K_a] and self.rect.x >= 10:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x <= WIDTH - self.rect.width - 10:
            self.rect.x += self.speed
        if keys_pressed[K_SPACE] and self.wait <= 0 and not self.reload:
            if self.clip > 0:
                self.wait = self.kd_shoot
                self.fire()
            else:
                self.reload = True
                self.start_reload = timer()

        else:
            self.wait -= 1

        if self.reload:
            current_time = timer()
            if current_time - self.start_reload >= 1:
                self.reload = False
                self.clip = 10
                self.interface_clip = self.full_interface_clip

    def fire(self):
        bullet = Bullet(self.rect.centerx - 7, self.rect.top)
        bullets_group.add(bullet)
        self.clip -= 1
        self.interface_clip = self.interface_clip[:-1]

    def get_dmg(self):
        if not self.resistance:
            self.hp -= 1
            self.health_list = self.health_list[:-1]
            if self.hp <= 0:
                self.alive = False

    def heal(self, amount):
        self.hp += amount
        for i in range(amount):
            heart = HpImage(self.health_list[-1].rect.x)
            self.health_list.append(heart)


class Enemy(GameSprite):
    def __init__(self, width, height, speed, damage_lost):
        self.width = width
        self.height = height
        self.damage_lost = damage_lost
        self.hp = 1
        self.shield_bonus_chance = 5
        super().__init__("images/ufo.png",
                         randint(0, WIDTH - self.width), randint(-HEIGHT, -self.width), self.width, self.height, speed)

    def update(self):
        global lost, text_lost
        self.buff_time_reduce()
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            lost += self.damage_lost
        text_lost = font_interface.render("lponyueHo: " + str(lost), True, (255, 255, 255))
        self.respawn(2)

    def respawn(self, hp):
        self.rect.x = randint(0, WIDTH - self.width)
        self.rect.y = randint(-HEIGHT, -self.width)
        self.hp = hp

    def get_dmg(self):
        if not self.resistance:
            if randint(1, 100) < 10:
                self.death()
                print("yes")
            else:
                self.hp -= 1
                print(self.hp)

                if self.hp <= 0:
                    self.death()

    def death(self):
        pass

    def spawn_bonus(self):
        chance = randint(1, 100)
        if chance <= self.shield_bonus_chance:
            bonus = Bonus("shield", "images/shield_bonus.png", self.rect.centerx - 25, self.rect.top)
            bonuses_group.add(bonus)


class CommonUfo(Enemy):
    def __init__(self):
        super().__init__(180, 95, 2, 1)
        self.hp = 2
        self.shield_bonus_chance = 5

    def death(self):
        global text_score, score
        self.spawn_bonus()
        self.respawn(2)
        score += 1
        text_score = font_interface.render("PaxyHOK:" + str(score), True, (255, 255, 255))

class FastUfo(Enemy):
    def __init__(self):
        super().__init__(120, 70, 3, 2)
        self.hp = 3
        self.shield_bonus_chance = 10

    def death(self):
        global text_score, score
        self.spawn_bonus()
        self.respawn(3)
        score += 2
        text_score = font_interface.render("PaxyHok: " + str(score), True, (255, 255, 255))


class BossUfo(Enemy):
    def init(self):
        super().__init__(320, 170, 1, 3)
        self.rect.y = -200
        self.hp = 5
        self.shield_bonus_chance = 80

    def death(self):
        global text_score, score, boss_access
        self.spawn_bonus()
        self.kill()
        score += 5
        player.heal(1)
        boss_access = True
        text_score = font_interface.render("PaxyHOk: " + str(score), True, (255, 255, 255))


class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/bullet.png", x, y, 15, 30, 25)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= - self.rect.height:
            self.kill()


class Bonus(GameSprite):
    def  __init__(self, effect, sprite_image, x, y):
        self.effect = effect
        super().__init__(sprite_image, x, y, 50, 50, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.kill()

        def catch(self, sprite, duration):
            if self.effect == "shield":
                sprite.get_shield(duration)
            self.kill()


class Asteroid(GameSprite):
    def __init__(self):
        self.width = randint(20, 80)
        super().__init__("images/asteroid.png", randint(0, WIDTH - self.width), randint(-HEIGHT, -self.width),
                         self.width, self.width, randint(1, 4))

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.respawn()

    def respawn(self):
        self.width = randint(20, 80)
        self.image = transform.scale(image.load("images/asteroid.png"), (self.width, self.width))
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, WIDTH - self.width)
        self.rect.y = randint(-HEIGHT, -self.width)
        self.speed = randint(1, 4)


WIDTH = 1280
HEIGHT = 720
ASPECT_RATIO = WIDTH / HEIGHT

FPS = 60

window = display.set_mode((WIDTH, HEIGHT), RESIZABLE)
background = transform.scale(image.load("images/galaxy.jpg"), (WIDTH, HEIGHT))
clock = time.Clock()

virtual_surface = Surface((WIDTH, HEIGHT))
current_size = window.get_size()

mixer.music.load("sounds/space.ogg")
mixer.music.play(-1)
mixer.music.set_volume(0.1)

player = Player(WIDTH // 2 - 50, HEIGHT - 170)

ufo_group = sprite.Group()
for i in range(6):
    ufo = CommonUfo()
    ufo_group.add(ufo)

fast_ufo = FastUfo()
ufo_group.add(fast_ufo)

boss_group = sprite.Group()
boss_access = True

bullets_group = sprite.Group()
bonuses_group = sprite.Group()

bonus = Bonus("shield", "images/shield_bonus.png", 100, 200)
bonuses_group.add(bonus)

asteroids_group = sprite.Group()
for i in range(5):
    asteroid = Asteroid()
    asteroids_group.add(asteroid)

lost = 0
score = 0

font_interface = font.Font(None, 40)
font_finish = font.Font(None, 200)

text_lost = font_interface.render ("Mponyueho: " + str(lost), True, (255, 255, 255))
text_score = font_interface.render("PaxyHoK: " + str(score), True, (255, 255, 255))
text_win = font_finish.render("lepemora!", True, (50, 200, 55))
text_lose = font_finish.render("Iporpab!", True, (200, 55, 55))


game = True
finish = False
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False
        if e.type == VIDEORESIZE:
            new_width = e.w
            new_height = int(new_width / ASPECT_RATIO)
            window = display.set_mode((new_width, new_height), RESIZABLE)
            current_size = window.get_size()

    if not finish:
        virtual_surface.blit(background, (0, 0))
        if boss_access and 0 <= score % 30 <= 5 and score >= 20:
            boss_ufo = BossUfo()
            boss_group.add(boss_ufo)
            boss_access = False

        player.update()
        player.reset()

        ufo_group.update()
        ufo_group.draw(virtual_surface)

        boss_group.update()
        boss_group.draw(virtual_surface)

        bullets_group.update()
        bullets_group.draw(virtual_surface)

        bonuses_group.update()
        bonuses_group.draw(virtual_surface)

        asteroids_group.update()
        asteroids_group.draw(virtual_surface)

        crash_list_asteroids = sprite.spritecollide(player, asteroids_group, False)
        for asteroid in crash_list_asteroids:
            asteroid.respawn()
            player.get_dmg()

        crash_list = sprite.spritecollide(player, ufo_group, False)
        for monster in crash_list:
            monster.death()
            player.get_dmg()

        bonus_catch_list = sprite.spritecollide(player, bonuses_group, True)
        for bonus in bonus_catch_list:
            bonus.catch(player, 300)

        hit_list = sprite.groupcollide(ufo_group, bullets_group, False, True)
        for monster in hit_list:
            monster.get_dmg()

        hit_list_asteroids = sprite.groupcollide(asteroids_group, bullets_group, False, True)

        if not player.alive or lost >= 20:
            finish = True
            virtual_surface.blit(text_lose, (360, 300))

        if score >= 100:
            finish = True
            virtual_surface.blit(text_win, (320, 300))

        virtual_surface.blit(text_lost, (30, 30))
        virtual_surface.blit(text_score, (30, 60))

        for heart in player.health_list:
            heart.reset()

        for cartridge in player.interface_clip:
            cartridge.reset()

    scaled_surface = transform.scale(virtual_surface, current_size)
    window.blit(scaled_surface, (0, 0))
    display.update()
    clock.tick(FPS)
