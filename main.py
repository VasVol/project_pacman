from boards import boards
import pygame
from math import pi
from random import randint
from min_dist import min_dist
from copy import deepcopy
from pygame import mixer
from time import time


class Score:
    def __init__(self):
        self.score_for_eating_small_coin = 10
        self.score_for_eating_big_coin = 50
        self.score_for_eating_ghost = 200
        self.score = 0
        self.lives = 3


class Graphics:
    def __init__(self):
        pygame.init()
        self.board = deepcopy(boards[0])
        self.window_x_size = self.window_y_size = min(pygame.display.get_desktop_sizes()[0]) * 0.86
        self.stretch_factor = self.window_x_size / 900
        self.cell_x_size = self.window_x_size / len(self.board)
        self.cell_y_size = self.window_y_size / len(self.board[0])
        self.space = 50 * self.stretch_factor
        self.font_size = 20 * self.stretch_factor
        self.big_font_size = 30 * self.stretch_factor
        self.screen = pygame.display.set_mode([self.window_x_size, self.window_y_size + self.space])
        self.font = pygame.font.Font('freesansbold.ttf', round(self.font_size))
        self.big_font = pygame.font.Font('freesansbold.ttf', round(self.big_font_size))
        self.flicker_speed = (20, 3)
        self.pacman_images, self.ghosts_images, self.spooked_img, self.dead_img = self.get_images()
        self.change_pacman_image_counter = 0
        self.change_pacman_image_speed = 5
        self.pacman_image_number = 0
        self.flicker = False
        self.flicker_counter = 0

    def draw_maze_pacman_and_ghosts(self, pacman: 'Pacman', ghosts: list['Ghost']) -> None:
        self.draw_maze()
        self.draw_pacman(pacman)
        self.draw_ghosts(ghosts)

    def get_images(self) -> tuple:
        k = self.stretch_factor
        dimensions = ((self.cell_x_size + 16) * k, (self.cell_y_size + 16) * k)
        pacman_images = []
        for i in range(1, 5):
            pacman_images.append(pygame.transform.scale(pygame.image.load(f'pacman_images/{i}.png'), dimensions))
        red_img = pygame.transform.scale(pygame.image.load('ghost_images/red.png'), dimensions)
        pink_img = pygame.transform.scale(pygame.image.load('ghost_images/pink.png'), dimensions)
        blue_img = pygame.transform.scale(pygame.image.load('ghost_images/blue.png'), dimensions)
        orange_img = pygame.transform.scale(pygame.image.load('ghost_images/orange.png'), dimensions)
        spooked_img = pygame.transform.scale(pygame.image.load('ghost_images/spooked.png'), dimensions)
        dead_img = pygame.transform.scale(pygame.image.load('ghost_images/dead.png'), dimensions)
        ghosts_images = [red_img, pink_img, blue_img, orange_img]
        return pacman_images, ghosts_images, spooked_img, dead_img

    def stretch(self, array: list) -> list:
        return [elem * self.stretch_factor for elem in array]

    def draw_misc(self, score: int, powerup: bool, lives: int, game_over: bool, game_won: bool) -> None:
        k = self.stretch_factor
        score_text = self.font.render(f'Score: {score}', True, 'white')
        self.screen.blit(score_text, (10 * k, 920 * k))
        if powerup:
            pygame.draw.circle(self.screen, 'blue', (140 * k, 930 * k), 15 * k)
        for i in range(lives):
            self.screen.blit(pygame.transform.scale(self.pacman_images[0], (30 * k, 30 * k)),
                             ((650 + i * 40) * k, 915 * k))
        if game_over:
            text = self.font.render('Game over! Space bar to restart!', True, 'red')
        elif game_won:
            text = self.font.render('Victory! Space bar to restart!', True, 'green')
        if game_over or game_won:
            pygame.draw.rect(self.screen, 'white', ((50 * k, 200 * k), (800 * k, 300 * k)), 0, round(10 * k))
            pygame.draw.rect(self.screen, 'dark gray', ((70 * k, 220 * k), (760 * k, 260 * k)), 0, round(10 * k))
            self.screen.blit(text, [100 * k, 300 * k])

    def draw_ready_text(self) -> None:
        k = self.stretch_factor
        text = self.big_font.render('READY!', True, 'red')
        self.screen.blit(text, (390 * k, 490 * k))

    def draw_ghosts(self, ghosts: list['Ghost']) -> None:
        k = self.stretch_factor
        for i in range(len(ghosts)):
            coords = (ghosts[i].y - 5 * k, ghosts[i].x - 5 * k)
            if ghosts[i].dead:
                self.screen.blit(self.dead_img, coords)
            elif ghosts[i].powerup:
                self.screen.blit(self.spooked_img, coords)
            else:
                self.screen.blit(self.ghosts_images[i], coords)

    def draw_pacman(self, pacman: 'Pacman') -> None:
        k = self.stretch_factor
        self.change_pacman_image_counter += 1
        if self.change_pacman_image_counter % self.change_pacman_image_speed == 0:
            self.pacman_image_number = (self.pacman_image_number + 1) % 4
        coords = (pacman.y - 8 * k, pacman.x - 8 * k)
        if pacman.direction == (0, 1):
            self.screen.blit(self.pacman_images[self.pacman_image_number], coords)
        elif pacman.direction == (0, -1):
            self.screen.blit(pygame.transform.flip(self.pacman_images[self.pacman_image_number], True, False), coords)
        elif pacman.direction == (-1, 0):
            self.screen.blit(pygame.transform.rotate(self.pacman_images[self.pacman_image_number], 90), coords)
        elif pacman.direction == (1, 0):
            self.screen.blit(pygame.transform.rotate(self.pacman_images[self.pacman_image_number], 270), coords)

    def draw_maze(self) -> None:
        k = self.stretch_factor
        x = self.cell_x_size
        y = self.cell_y_size
        if self.flicker_counter < self.flicker_speed[0]:
            self.flicker_counter += 1
            if self.flicker_counter > self.flicker_speed[1]:
                self.flicker = False
        else:
            self.flicker_counter = 0
            self.flicker = True
        self.screen.fill('black')
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 1:
                    pygame.draw.circle(self.screen, 'white', ((j + 0.5) * y, (i + 0.5) * x), 4 * k)
                if self.board[i][j] == 2 and not self.flicker:
                    pygame.draw.circle(self.screen, 'white', ((j + 0.5) * y, (i + 0.5) * x), 10 * k)
                if self.board[i][j] == 3:
                    pygame.draw.line(self.screen, 'blue', ((j + 0.5) * y, i * x),
                                     ((j + 0.5) * y, (i + 1) * x), round(3 * k))
                if self.board[i][j] == 4:
                    pygame.draw.line(self.screen, 'blue', (j * y, (i + 0.5) * x),
                                     ((j + 1) * y, (i + 0.5) * x), round(3 * k))
                if self.board[i][j] == 5:
                    pygame.draw.arc(self.screen, 'blue', (((j - 0.4) * y - 2 * k, (i + 0.5) * x), (y, x)),
                                    0, pi / 2, round(3 * k))
                if self.board[i][j] == 6:
                    pygame.draw.arc(self.screen, 'blue',
                                    (((j + 0.5) * y, (i + 0.5) * x), (y, x)), pi / 2, pi, round(3 * k))
                if self.board[i][j] == 7:
                    pygame.draw.arc(self.screen, 'blue', (((j + 0.5) * y, (i - 0.4) * x), (y, x)),
                                    pi, 3 * pi / 2, round(3 * k))
                if self.board[i][j] == 8:
                    pygame.draw.arc(self.screen, 'blue', ((((j - 0.4) * y) - 2 * k, ((i - 0.4) * x)),
                                                          (y, x)), 3 * pi / 2, 2 * pi, round(3 * k))
                if self.board[i][j] == 9:
                    pygame.draw.line(self.screen, 'white', (j * y, (i + 0.5) * x),
                                     ((j + 1) * y, (i + 0.5) * x), round(3 * k))


def play_the_sound_stop_everything_else(sound: 'pygame.mixer.Sound') -> None:
    channel = sound.play()
    while channel.get_busy():
        pass


def play_sound_loop(sound: 'pygame.mixer.Sound') -> None:
    sound.play(-1)


def stop_playing_sound(sound: 'pygame.mixer.Sound') -> None:
    sound.stop()


class Sounds:
    def __init__(self):
        mixer.init()
        self.game_music = mixer.Sound('sounds/siren_2.wav')
        self.game_start_sound = mixer.Sound('sounds/game_start.wav')
        self.death_sound = mixer.Sound('sounds/death_1.wav')


class Creature:
    def __init__(self, direction: tuple, speed: float, x_start: float, y_start: float):
        self.speed = speed
        self.direction = direction
        self.next_direction = self.direction
        self.x_start = x_start
        self.y_start = y_start
        self.x = self.x_start
        self.y = self.y_start
        self.possible_directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]

    def is_collision(self, graphics: 'Graphics') -> bool:
        can_move_to = [0, 1, 2]
        if (self.__class__.__name__ == 'Ghost') and not (self.powerup and not self.dead):
            can_move_to.append(9)
        k = graphics.stretch_factor
        for x in range(len(graphics.board)):
            for y in range(len(graphics.board[x])):
                if (graphics.board[x][y] not in can_move_to) and \
                        (abs(self.x - x * graphics.cell_x_size) < graphics.cell_x_size - 1 * k) \
                        and (abs(self.y - y * graphics.cell_y_size) < graphics.cell_y_size - 1 * k):
                    return True
        return False

    def can_move_in_direction(self, direction: tuple, graphics: 'Graphics') -> bool:
        self.shift(direction)
        if self.is_collision(graphics):
            self.shift(tuple(-elem for elem in direction))
            return False
        self.shift(tuple(-elem for elem in direction))
        return True

    def shift(self, direction: tuple) -> None:
        self.x += direction[0] * self.speed
        self.y += direction[1] * self.speed

    def move(self, graphics: 'Graphics') -> None:
        if self.can_move_in_direction(self.next_direction, graphics):
            self.shift(self.next_direction)
            self.direction = self.next_direction
        elif self.can_move_in_direction(self.direction, graphics):
            self.shift(self.direction)

        if (self.y > graphics.window_y_size - 2 * graphics.cell_y_size) and (
                self.direction == (0, 1)) and (
                graphics.cell_x_size * 13 <= self.x <= graphics.cell_x_size * 17):
            self.y = 0
        if (self.y < 2 * graphics.cell_y_size) and (self.direction == (0, -1)) and \
                (graphics.cell_x_size * 13 <= self.x <= graphics.cell_x_size * 17):
            self.y = graphics.window_y_size - graphics.cell_y_size

    def rounded_coordinates(self, graphics: 'Graphics') -> tuple:
        return round(self.x / graphics.cell_x_size), round(self.y / graphics.cell_y_size)


class Pacman(Creature):
    def __init__(self, direction: tuple, speed: float, x_start: float, y_start: float):
        super().__init__(direction, speed, x_start, y_start)
        self.pacman_caught = False

    def check_keys(self, event: 'pygame.event.Event') -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                self.next_direction = (0, -1)
            elif event.key == pygame.K_UP:
                self.next_direction = (-1, 0)
            elif event.key == pygame.K_DOWN:
                self.next_direction = (1, 0)


def more(a: int, b: int) -> bool:
    return a > b


def less(a: int, b: int) -> bool:
    return a < b


class Ghost(Creature):
    def __init__(self, direction: tuple, speed: float, x_start: float, y_start: float):
        super().__init__(direction, speed, x_start, y_start)
        self.dead = False
        self.first_change_direction_after_powerup = False
        self.powerup = False

    def change_next_direction_if_dead(self, pacman: 'Pacman', graphics: 'Graphics') -> None:
        i, j = self.rounded_coordinates(graphics)
        possible_directions = self.possible_directions[:]
        possible_directions.remove((-self.direction[0], -self.direction[1]))
        self.change_next_direction_using_min_dist(possible_directions, True, True, pacman, graphics)
        if (i == 15) and (j == 15):
            self.dead = False
            self.powerup = False

    def change_next_direction_using_random(self, possible_directions: list, graphics: 'Graphics') -> None:
        best_direction = possible_directions[randint(0, 2)]
        for i in range(10):
            if not self.can_move_in_direction(best_direction, graphics):
                best_direction = possible_directions[randint(0, 2)]
        self.next_direction = best_direction

    def change_next_direction_using_min_dist(self, possible_directions: list, flag_powerup: bool, flag_dead: bool,
                                             pacman: 'Pacman', graphics: 'Graphics') -> None:
        best_direction = None
        i, j = self.rounded_coordinates(graphics)
        goal = pacman.rounded_coordinates(graphics)
        if flag_powerup:
            best_dist = 1000
            func = less
        else:
            best_dist = -1000
            func = more
        if flag_dead:
            goal = (15, 15)
        for direction in possible_directions:
            new_i = i + direction[0]
            new_j = j + direction[1]
            tmp = ((new_i, new_j), goal)
            if (tmp in min_dist) and (func(min_dist[tmp], best_dist)):
                best_dist = min_dist[tmp]
                best_direction = direction
        self.next_direction = best_direction

    def change_next_direction_if_powerup(self, pacman: 'Pacman', graphics: 'Graphics') -> None:
        possible_directions = self.possible_directions[:]
        if not self.first_change_direction_after_powerup:
            possible_directions.remove((-self.direction[0], -self.direction[1]))
        else:
            self.first_change_direction_after_powerup = False
        i, j = self.rounded_coordinates(graphics)
        if randint(1, 2) == 1:
            self.change_next_direction_using_random(possible_directions, graphics)
        else:
            self.change_next_direction_using_min_dist(possible_directions, False, False, pacman, graphics)
        if (i == 15) and (j == 15):
            self.dead = False
            self.powerup = False

    def change_next_direction_if_not_powerup_or_dead(self, pacman: 'Pacman', graphics: 'Graphics') -> None:
        possible_directions = self.possible_directions[:]
        possible_directions.remove((-self.direction[0], -self.direction[1]))
        if randint(1, 5) == 1:
            self.change_next_direction_using_random(possible_directions, graphics)
        else:
            self.change_next_direction_using_min_dist(possible_directions, True, False, pacman, graphics)

    def change_next_direction(self, pacman: 'Pacman', graphics: 'Graphics') -> None:
        if self.dead:
            self.change_next_direction_if_dead(pacman, graphics)
        elif self.powerup:
            self.change_next_direction_if_powerup(pacman, graphics)
        else:
            self.change_next_direction_if_not_powerup_or_dead(pacman, graphics)


class Mediator:
    def __init__(self):
        self.graphics = Graphics()
        self.sounds = Sounds()
        self.score = Score()
        k = self.graphics.stretch_factor
        self.pacman = Pacman((0, 1), 2 * k, 24 * self.graphics.cell_x_size, 15 * self.graphics.cell_y_size)
        self.red_ghost = Ghost((-1, 0), 2 * k, 15 * self.graphics.cell_x_size, 13 * self.graphics.cell_y_size)
        self.pink_ghost = Ghost((-1, 0), 2 * k, 15 * self.graphics.cell_x_size, 14 * self.graphics.cell_y_size)
        self.blue_ghost = Ghost((-1, 0), 2 * k, 15 * self.graphics.cell_x_size, 15 * self.graphics.cell_y_size)
        self.orange_ghost = Ghost((-1, 0), 2 * k, 15 * self.graphics.cell_x_size, 16 * self.graphics.cell_y_size)
        self.ghosts = [self.red_ghost, self.pink_ghost, self.blue_ghost, self.orange_ghost]
        self.fps = 60
        self.game_is_on = False
        self.powerup = False
        self.powerup_timer = 0
        self.game_over = False
        self.game_won = False

    def start_game(self) -> None:
        self.game_is_on = True
        while self.game_is_on:
            self.game_is_on = False
            self.__init__()
            self.game()

    def game(self) -> None:
        timer = pygame.time.Clock()
        self.graphics.draw_maze_pacman_and_ghosts(self.pacman, self.ghosts)
        self.graphics.draw_ready_text()
        pygame.display.flip()
        play_the_sound_stop_everything_else(self.sounds.game_start_sound)
        play_sound_loop(self.sounds.game_music)
        run = True
        while run:
            timer.tick(self.fps)
            self.graphics.draw_maze_pacman_and_ghosts(self.pacman, self.ghosts)
            self.graphics.draw_misc(self.score.score, self.powerup, self.score.lives, self.game_over, self.game_won)
            pygame.display.flip()
            if self.pacman.pacman_caught:
                self.graphics.draw_ready_text()
                pygame.display.flip()
                timer.tick(1)
                self.pacman.pacman_caught = False
                play_sound_loop(self.sounds.game_music)
            if self.powerup and (time() - self.powerup_timer > 7):
                self.powerup = False
                for ghost in self.ghosts:
                    ghost.powerup = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_SPACE) and (
                        self.game_over or self.game_won):
                    self.game_is_on = True
                    return
                self.pacman.check_keys(event)
            if (not self.game_over) and (not self.game_won):
                for ghost in self.ghosts:
                    ghost.change_next_direction(self.pacman, self.graphics)
                    ghost.move(self.graphics)
                self.pacman.move(self.graphics)
                self.touches_coin()
                self.touches_ghost()
                self.all_coins_collected()

    def touches_ghost(self) -> None:
        i, j = self.pacman.rounded_coordinates(self.graphics)
        for ghost in self.ghosts:
            ghost_i = round(ghost.x / self.graphics.cell_x_size)
            ghost_j = round(ghost.y / self.graphics.cell_y_size)
            if (i == ghost_i) and (j == ghost_j):
                if (not ghost.powerup) and (not ghost.dead):
                    stop_playing_sound(self.sounds.game_music)
                    self.score.lives -= 1
                    if self.score.lives < 0:
                        self.game_over = True
                    else:
                        self.powerup = False
                        self.pacman.pacman_caught = True
                        self.pacman.direction = (0, 1)
                        self.pacman.next_direction = (0, 1)
                        self.graphics.pacman_image_number = 0
                        self.pacman.x = self.pacman.x_start
                        self.pacman.y = self.pacman.y_start
                        for ghost1 in self.ghosts:
                            ghost1.x = ghost1.x_start
                            ghost1.y = ghost1.y_start
                            ghost1.powerup = False
                            ghost1.dead = False
                            ghost1.first_change_direction_after_powerup = True
                    play_the_sound_stop_everything_else(self.sounds.death_sound)
                    return
                else:
                    if not ghost.dead:
                        self.score.score += self.score.score_for_eating_ghost
                        pygame.display.flip()
                    ghost.dead = True

    def touches_coin(self) -> None:
        i, j = self.pacman.rounded_coordinates(self.graphics)
        if self.graphics.board[i][j] == 1:
            self.score.score += 10
            self.graphics.board[i][j] = 0
        elif self.graphics.board[i][j] == 2:
            self.score.score += 50
            self.graphics.board[i][j] = 0
            self.powerup = True
            self.powerup_timer = time()
            for ghost in self.ghosts:
                ghost.powerup = True

    def all_coins_collected(self) -> None:
        for i in range(len(self.graphics.board)):
            for j in range(len(self.graphics.board[i])):
                if self.graphics.board[i][j] in [1, 2]:
                    return
        self.game_won = True
        self.sounds.game_music.stop()


mediator = Mediator()
mediator.start_game()
