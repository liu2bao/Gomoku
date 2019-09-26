import pygame
import pygame.freetype
from pygame.sprite import Sprite
import numpy as np
from enum import Enum, unique
from GomokuConst import HEIGHT, WIDTH, COLORS_ALL, BLUE, WHITE, BLACK, cns_default


def create_surface_with_text(text, font_size, text_rgb, bg_rgb=None):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


def blit_images(surface, center_pos, text, font_size, text_rgb, bg_rgb=None):
    text_img = create_surface_with_text(text, font_size, text_rgb, bg_rgb)
    text_rect = text_img.get_rect(center=center_pos)
    surface.blit(text_img, text_rect)


@unique
class SwitchState(Enum):
    On = 1
    Off = 0


class Text(Sprite):
    def __init__(self, center_pos, text, font_size, text_rgb, bg_rgb=None):
        self._text_img = create_surface_with_text(text, font_size, text_rgb, bg_rgb)
        self._text_rect = self._text_img.get_rect(center=center_pos)
        super().__init__()

    def draw(self, surface):
        surface.blit(self._text_img, self._text_rect)


class Button(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, width, height, font_size, bg_rgb=BLUE, text_rgb=WHITE, switch=False):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element
        self._switch = switch  # indicates if the button is a switch
        self._switch_state = SwitchState.Off
        # create the text image

        colors_text = {SwitchState.On: bg_rgb, SwitchState.Off: text_rgb}
        self._colors_rect = {SwitchState.On: text_rgb, SwitchState.Off: bg_rgb}
        self._texts = {k: Text(center_pos=center_position, text=text, font_size=font_size, text_rgb=v)
                       for k, v in colors_text.items()}
        self.Rect = pygame.Rect(((center_position[0] - width / 2, center_position[1] - height / 2),
                                 (width, height)))

        # calls the init method of the parent sprite class
        super().__init__()

    @property
    def text(self):
        return self._texts[self._switch_state]

    @property
    def rect_color(self):
        return self._colors_rect[self._switch_state]

    @property
    def switch_state(self):
        return self._switch_state

    @switch_state.setter
    def switch_state(self, ss):
        if isinstance(ss, SwitchState):
            self._switch_state = ss

    def alter_switch(self):
        self._switch_state = SwitchState((self._switch_state.value + 1) % len(SwitchState))

    def update(self, mouse_pos, mouse_down):
        """ Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked.
        """
        flag_press = False
        if self.Rect.collidepoint(*mouse_pos):
            self.mouse_over = True
            if mouse_down:
                if self._switch:
                    self.alter_switch()
                flag_press = True
        else:
            self.mouse_over = False
        return flag_press

    def draw(self, surface):
        pygame.draw.rect(surface, self.rect_color, self.Rect)
        """ Draws element onto a surface """
        self.text.draw(surface)


class RadioButton(Sprite):
    def __init__(self, center_position, array_texts, width, height, font_size,
                 bg_rgb=BLUE, text_rgb=WHITE, margin=0, disable=True, default_choice=None):
        att = array_texts
        if isinstance(array_texts, tuple) or isinstance(array_texts, list):
            att = np.array(array_texts)
        shape_t = att.shape
        if len(shape_t) == 1:
            att_r = att.reshape((1, -1))
        else:
            att_r = att
        self._shape = att_r.shape[-1::-1]
        self._sides = [width, height]
        self._center_pos = {}
        self._intervals = {}
        self._current_choice = None
        for i in range(len(self._shape)):
            c = center_position[i]
            d = self._shape[i]
            lens = self._sides[i]
            size_t = (lens - (d + 1) * margin) / d
            self._intervals[i] = size_t
            interval_t = size_t + margin
            ini_pos_t = c - lens / 2 + size_t / 2 + margin
            self._center_pos[i] = np.arange(d) * interval_t + ini_pos_t
        self._buttons = {(i, j): Button([self._center_pos[0][i], self._center_pos[1][j]],
                                        att_r[j, i], self._intervals[0], self._intervals[1],
                                        font_size=font_size, bg_rgb=bg_rgb, text_rgb=text_rgb,
                                        switch=False)
                         for i in range(self._shape[0]) for j in range(self._shape[1])}
        if default_choice is not None:
            if isinstance(default_choice, int):
                default_choice = (0, default_choice)
            self._buttons[default_choice].switch_state = SwitchState.On
            self._current_choice = default_choice
        self._disable = disable
        super().__init__()

    @property
    def current_choice(self):
        return self._current_choice

    def update(self, mouse_pos, mouse_down):
        for k in self._buttons.keys():
            flag_press = self._buttons[k].update(mouse_pos, mouse_down)
            if flag_press:
                if self._buttons[k].switch_state == SwitchState.Off:
                    self._current_choice = k
                    self._buttons[k].switch_state = SwitchState.On
                elif self._disable:
                    self._current_choice = None
                    self._buttons[k].switch_state = SwitchState.Off
                for kk, vv in self._buttons.items():
                    if kk != k:
                        self._buttons[kk].switch_state = SwitchState.Off
                break

    def draw(self, surface):
        for v in self._buttons.values():
            v.draw(surface)


AMP = 3


class GomokuChainChooser(Sprite):
    def __init__(self, center_pos, interval, left=False, color=BLACK, chain_nums_setting=cns_default):
        cn_temp = list(chain_nums_setting)
        cn_temp.sort()
        self._chain_num_min, self._chain_num, self._chain_num_max = cn_temp
        self._interval = interval
        self._width = self._chain_num_max / 2 * self._interval
        if left:
            start_pos_x = center_pos[0]
        else:
            start_pos_x = center_pos[0] - self._width
        self._circle_centers_x = start_pos_x + (np.arange(self._chain_num_max) + 0.5) * self._interval
        self._circle_center_y = center_pos[1]
        self._color = color
        self._radius_full = interval / AMP
        self._radius_thumb = self._radius_full / AMP
        super().__init__()

    @property
    def chain_num(self):
        return self._chain_num

    @property
    def width(self):
        return self._width

    def update(self, mouse_pos, mouse_down):
        if mouse_down:
            mpx, mpy = mouse_pos
            c = int((mpx - self._circle_centers_x[0] + self._interval / 2) / self._interval)
            if 0<=c<self._chain_num_max:
                dists = (mpx - self._circle_centers_x[c], mpy - self._circle_center_y)
                if all([np.abs(k) <= self._radius_full for k in dists]):
                    cn = c + 1
                    if cn >= self._chain_num_min:
                        self._chain_num = cn

    def draw(self, surface):
        for i in range(self._chain_num_max):
            circle_center_t = [int(self._circle_centers_x[i]), int(self._circle_center_y)]
            if i >= self._chain_num:
                r = self._radius_thumb
            else:
                r = self._radius_full
            pygame.draw.circle(surface, self._color, circle_center_t, int(r))


class GomokuStarter:
    def __init__(self, type_texts, font_size, rgb_bg=BLUE, rgb_text=WHITE, colors=COLORS_ALL,
                 width=WIDTH, height=HEIGHT, default_choices=None):
        self._screen = pygame.display.set_mode((width, height))
        self._player_colors = colors
        self._width = width
        self._height = height
        self._rgb_bg = rgb_bg
        num_players = len(colors)
        num_choices = len(type_texts)
        interval_w_t = width / (num_choices + 1.5)
        interval_h_t = height / (num_players + 5)
        self._interval_w_t = interval_w_t
        self._radius = self._interval_w_t / 16
        self._circle_center_x = interval_w_t * 0.25
        player_text_center_x = interval_w_t
        radio_button_center_x = interval_w_t * (1.5 + num_choices / 2)
        self._radio_button_centers_y = (np.arange(num_players) + 2.5) * interval_h_t
        self._title_text = Text(center_pos=(width / 2, interval_h_t),
                                text='Please choose player types',
                                font_size=font_size*1.5, text_rgb=rgb_text, bg_rgb=rgb_bg)
        chain_y = interval_h_t * (num_players + 2.5)
        self._chain_num_text = Text(center_pos=(player_text_center_x, chain_y),
                                    text='Winning chain :', font_size=font_size, text_rgb=rgb_text,
                                    bg_rgb=rgb_bg)
        self._chain_num_chooser = GomokuChainChooser(center_pos=(radio_button_center_x, chain_y),
                                                     interval=self._radius * AMP)
        self._button_confirm = Button(center_position=(width / 2, interval_h_t * (num_players + 4)),
                                      text='Confirm', width=interval_w_t, height=interval_h_t,
                                      font_size=font_size, bg_rgb=rgb_text, text_rgb=rgb_bg,
                                      switch=False)
        if default_choices is None:
            default_choices = {}
        self._radio_buttons = []
        self._player_aliases = ['Player #' + str(i) for i in range(num_players)]
        self._player_texts = []
        for i in range(num_players):
            color_t = colors[i]
            if i in default_choices.keys():
                default_choice = default_choices[i]
                disable = False
            else:
                default_choice = None
                disable = True
            y_t = self._radio_button_centers_y[i]
            radio_button_t = \
                RadioButton(center_position=(radio_button_center_x, y_t),
                            array_texts=type_texts, width=interval_w_t * num_choices, margin=1,
                            height=interval_h_t, font_size=font_size, bg_rgb=rgb_bg, text_rgb=rgb_text,
                            disable=disable, default_choice=default_choice)
            player_text_t = Text(center_pos=(player_text_center_x, y_t),
                                 text=self._player_aliases[i] + ' :',
                                 font_size=font_size, text_rgb=color_t, bg_rgb=rgb_bg)
            self._radio_buttons.append(radio_button_t)
            self._player_texts.append(player_text_t)

    @property
    def choices(self):
        return tuple([k.current_choice[0] if k.current_choice else None for k in self._radio_buttons])

    @property
    def player_colors(self):
        return self._player_colors

    @property
    def player_aliases(self):
        return self._player_aliases

    @property
    def chain_num(self):
        return self._chain_num_chooser.chain_num

    def draw(self, surface=None):
        if surface is None:
            surface = self._screen
        surface.fill(self._rgb_bg)
        self._title_text.draw(surface)
        self._button_confirm.draw(surface)
        self._chain_num_text.draw(surface)
        self._chain_num_chooser.draw(surface)
        for pt in self._player_texts:
            pt.draw(surface)
        for rb in self._radio_buttons:
            rb.draw(surface)
        for i in range(len(self._player_colors)):
            cc = (int(self._circle_center_x), int(self._radio_button_centers_y[i]))
            pygame.draw.circle(surface, self._player_colors[i], cc, int(self._radius))
        pygame.display.flip()

    def start(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(3000)
            self.draw()
            mouse_down = False
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button ==1:
                    mouse_down = True
                elif event.type == pygame.QUIT:
                    running = False

            mouse_pos = pygame.mouse.get_pos()
            for i in range(len(self._radio_buttons)):
                self._radio_buttons[i].update(mouse_pos=mouse_pos, mouse_down=mouse_down)

            self._chain_num_chooser.update(mouse_pos=mouse_pos, mouse_down=mouse_down)
            flag_confirm = self._button_confirm.update(mouse_pos=mouse_pos, mouse_down=mouse_down)
            if flag_confirm:
                return flag_confirm


# call main when the script is run
if __name__ == "__main__":
    type_texts_s = ('Human', 'GoofyAI', 'NormalAI', 'SmartAI')
    pygame.init()
    GS = GomokuStarter(type_texts_s, 15, default_choices={0: 0, 1: 0})
    flag_confirm = GS.start()
    if flag_confirm:
        choices = GS.choices
        print(choices)
