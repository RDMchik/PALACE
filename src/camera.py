from settings import *

import pygame as pg


class Camera:

    def __init__(self, x, y) -> None:

        self.offset = pg.Vector2(x, y)
        self.original_offset = pg.Vector2(x, y)

        self.velocity = pg.Vector2(0, 0)
        
        self.friction_active = False

    def update_offset(self, delta, width) -> None:
        
        if self.offset.x != self.original_offset.x:

            if self.offset.x < self.original_offset.x:

                self.offset.x += CAMERA_ACCELERATION * delta
                if self.offset.x > self.original_offset.x:
                    self.offset.x = self.original_offset.x

                if self.offset.x + width / 10  < self.original_offset.x:
                    self.offset.x = self.original_offset.x - width / 10

            elif self.offset.x > self.original_offset.x:

                self.offset.x -= CAMERA_ACCELERATION * delta
                if self.offset.x < self.original_offset.x:
                    self.offset.x = self.original_offset.x

                if self.offset.x - width / 10  > self.original_offset.x:
                    self.offset.x = self.original_offset.x + width / 10