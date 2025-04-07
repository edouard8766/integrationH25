import pygame
import os
import time


current_dir = os.path.dirname(os.path.abspath(__file__))

class TrafficLight(pygame.sprite.Sprite):
    def __init__(self, direction, state=2):
        pygame.sprite.Sprite.__init__(self)
        self.__state = state # state -> 0=green, 1=yellow, 2=red, 3=green blink
        self.direction = direction # direction -> 0 to 3 for which direction it controls
        filename = os.path.join(current_dir, "assets", "traffic_light_bar_" + str(self.__state) + ".png")
        if os.path.exists(filename):
            self.image = pygame.image.load(filename)
        else:
            self.image = pygame.image.load(
                os.path.join(current_dir, "assets", "traffic_light_bar_off.png"))
        self.size = (64, 6) #in pixels
        self.relative_size = (0.064, 0.006)  # originally 64x6 for 1000x1000
        self.relative_pos = {
            0: (0.433, 0.503),
            1: (0.560, 0.434),
            2: (0.503, 0.560),
            3: (0.434, 0.433)
        }[self.direction]
        # Placeholders until we know screen size
        self.size = (0, 0)
        self.pos = (0, 0)

        self.blink_counter_reset = 100
        self.blink_counter = self.blink_counter_reset
        self.blink_speed = 90
        self.blink_bool = False

    def update_position(self, screen_width, screen_height):
        self.pos = (int(self.relative_pos[0] * screen_width), int(self.relative_pos[1] * screen_height))

    def update_geometry(self, screen_width, screen_height):
        # Update size
        width = int(self.relative_size[0] * screen_width)
        height = int(self.relative_size[1] * screen_height)
        self.size = (width, height)

        # Reload and rescale image
        self.set_color(self.__state)

        # Update position
        x = int(self.relative_pos[0] * screen_width)
        y = int(self.relative_pos[1] * screen_height)
        self.pos = (x, y)

    def draw(self, screen):
        screen_width, screen_height = screen.get_size()
        self.update_geometry(screen_width, screen_height)

        if self.__state == 3:
            # Use current time in seconds (floating point)
            t = time.time()
            # Pulse every 1 second (0.5 on, 0.5 off)
            if (t % 1) < 0.5:
                self.set_color(0)  # green
            else:
                self.set_color(404)  # off

        screen.blit(self.image, self.pos)

    def set_color(self, state):
        if state == 3:
            # Use green as base for blinking state
            filename = os.path.join(current_dir, "assets", "traffic_light_bar_0.png")
        elif state != 404:
            filename = os.path.join(current_dir, "assets", "traffic_light_bar_" + str(state) + ".png")
        else:
            filename = os.path.join(current_dir, "assets", "traffic_light_bar_off.png")

        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, self.size)

        if self.direction in [0, 1]:
            self.image = pygame.transform.rotate(self.image, 90)

    def set_state(self, state):
        if self.__state != state:
            self.blink_counter = self.blink_counter_reset
            if state == 3:
                self.set_color(0)
            else:
                self.set_color(state)
        self.__state = state
