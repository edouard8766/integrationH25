import pygame
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

class TrafficLight(pygame.sprite.Sprite):
    def __init__(self, direction, state=2):
        pygame.sprite.Sprite.__init__(self)
        self.__state = state # state -> 0=green, 1=yellow, 2=red, 3=green blink
        self.direction = direction # direction -> 0 to 3 for which direction it controls
        filename = os.path.join(current_dir, "items", "traffic_light_bar_" + str(self.__state) + ".png")
        if os.path.exists(filename):
            self.image = pygame.image.load(filename)
        else:
            self.image = pygame.image.load(
                os.path.join(current_dir, "items", "traffic_light_bar_off.png"))
        self.size = (64, 6) #in pixels
        self.image = pygame.transform.scale(self.image, self.size)
        if self.direction == 0:
            self.pos = (433, 503)
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.direction == 1:
            self.pos = (560, 434)
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.direction == 2:
            self.pos = (503, 560)
        else:
            self.pos = (434, 433)

        self.blink_counter_reset = 100
        self.blink_counter = self.blink_counter_reset
        self.blink_speed = 95
        self.blink_bool = False


    def draw(self, screen):
        if self.__state == 3:
            self.blink_counter -= 1
            if self.blink_counter < self.blink_speed:
                self.blink_bool = not self.blink_bool
                self.blink_counter = self.blink_counter_reset
                if self.blink_bool:
                    self.set_color(404)
                else:
                    self.set_color(0)
        screen.blit(self.image, self.pos)

    def set_color(self, state):
        if state != 404:
            filename = os.path.join(current_dir, "items", "traffic_light_bar_" + str(state) + ".png")
        else:
            filename = os.path.join(current_dir, "items", "traffic_light_bar_off.png")
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, self.size)
        if self.direction == 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.direction == 1:
            self.image = pygame.transform.rotate(self.image, 90)

    def set_state(self, state):
        if self.__state != state:
            self.blink_counter = self.blink_counter_reset
            if state == 3:
                self.set_color(0)
            else:
                self.set_color(state)
        self.__state = state
