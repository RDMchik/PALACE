from settings import *

import pygame as pg


class FontEngine:

    def __init__(self, font_size: int) -> None:
        
        self.font = pg.font.Font('static/ZZYZX.TTF', font_size)

    def render(self, text: str, color: WHITE) -> None:
        return self.font.render(text, True, color)

    def render_p(self, text: str, color: WHITE) -> None:
        
        parts = text.split('\n')
        
        rendered_parts = []
        for part in parts:
            rendered_parts.append(self.render(part, color))
        
        return rendered_parts