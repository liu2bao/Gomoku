import pygame
import pygame.freetype
from pygame.sprite import Sprite
import numpy as np
from enum import Enum, unique
from GomokuConst import HEIGHT, WIDTH, COLORS_ALL, BLUE, WHITE, BLACK, cns_default, rse_default, cse_default

AMP = 3


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
        self._text = self._text_img = self._text_rect = None
        self._center_pos = center_pos
        self._text_img_gen = lambda t: create_surface_with_text(t, font_size, text_rgb, bg_rgb)
        self.text = text
        super().__init__()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._text_img = self._text_img_gen(text)
        self._text_rect = self._text_img.get_rect(center=self._center_pos)

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


class ChainChooser(Sprite):
    def __init__(self, center_pos, interval, max_width=None, left=False, color=BLACK,
                 chain_nums_setting=cns_default, slide=False, cut_front=False, font_size=None):
        cn_temp = np.array(chain_nums_setting)
        cn_temp.sort()
        if cut_front:
            self._offset = cn_temp[0]-1
            cn_temp -= cn_temp[0]-1
        else:
            self._offset = 0
        self._chain_num_min, self._chain_num, self._chain_num_max = cn_temp
        self._interval = interval
        if max_width:
            self._interval = min(self._interval,max_width/(self._chain_num_max+4))
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
        self._slide = slide
        self._mouse_down = False
        if font_size is None:
            self._Text = None
        else:
            self._Text = Text(center_pos=[self._circle_centers_x[-1] + self._interval, self._circle_center_y],
                              text=str(self.chain_num), font_size=font_size, text_rgb=self._color)
        super().__init__()

    @property
    def chain_num(self):
        return self._chain_num+self._offset

    @property
    def width(self):
        return self._width

    def update(self, mouse_pos, mouse_down, mouse_up=False):
        mpx, mpy = mouse_pos
        flag_y = np.abs(mpy - self._circle_center_y) <= self._interval
        if (not self._mouse_down) and mouse_down and flag_y:
            self._mouse_down = True
        if mouse_up:
            self._mouse_down = False

        flag_enter = ((not self._slide) and mouse_down and flag_y) or (self._slide and self._mouse_down)
        if flag_enter:
            c = int((mpx - self._circle_centers_x[0] + self._interval / 2) / self._interval)+1
            if self._chain_num_min <= c <= self._chain_num_max:
                if c >= self._chain_num_min:
                    self._chain_num = c
                    if self._Text:
                        self._Text.text = str(self.chain_num)

    def draw(self, surface):
        if self._slide:
            I = [self._chain_num - 1]
            start_pos, end_pos = [[self._circle_centers_x[k], self._circle_center_y] for k in [0, -1]]
            pygame.draw.line(surface, self._color, start_pos, end_pos)
        else:
            I = np.arange(self._chain_num_max)

        for i in I:
            circle_center_t = [int(self._circle_centers_x[i]), int(self._circle_center_y)]
            if i >= self._chain_num:
                r = self._radius_thumb
            else:
                r = self._radius_full
            pygame.draw.circle(surface, self._color, circle_center_t, int(r))

        if self._Text:
            self._Text.draw(surface)


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
        interval_h_t = height / (num_players + 7)
        self._interval_w_t = interval_w_t
        self._radius = self._interval_w_t / 16
        self._circle_center_x = interval_w_t * 0.25
        player_text_center_x = interval_w_t
        radio_button_center_x = interval_w_t * (1.5 + num_choices / 2)
        self._radio_button_centers_y = (np.arange(num_players) + 2.5) * interval_h_t
        self._title_text = Text(center_pos=(width / 2, interval_h_t),
                                text='Please choose player types',
                                font_size=font_size * 1.5, text_rgb=rgb_text, bg_rgb=rgb_bg)
        chain_y = interval_h_t * (num_players + 2.5)
        itexts = ['Winning chain','Rows','Columns']
        self._instruction_texts = [Text(center_pos=(player_text_center_x, chain_y+t*interval_h_t),
                                    text=itexts[t]+' :', font_size=font_size, text_rgb=rgb_text,
                                    bg_rgb=rgb_bg) for t in range(len(itexts))]
        MW = interval_w_t*num_choices
        self._chain_num_chooser = ChainChooser(center_pos=(radio_button_center_x, chain_y), max_width=MW,
                                               interval=self._radius * AMP, font_size=font_size)
        sbs_default = [rse_default,cse_default]
        self._slide_bars_size = [ChainChooser(center_pos=(radio_button_center_x, chain_y+(k+1)*interval_h_t),
                                              interval=self._radius * AMP, font_size=font_size, max_width=MW,
                                              slide=True,cut_front=True,chain_nums_setting=sbs_default[k])
                                 for k in range(2)]
        self._button_confirm = Button(center_position=(width / 2, chain_y+interval_h_t * 3.5),
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

    @property
    def rows(self):
        return self._slide_bars_size[0].chain_num

    @property
    def cols(self):
        return self._slide_bars_size[1].chain_num

    def draw(self, surface=None):
        if surface is None:
            surface = self._screen
        surface.fill(self._rgb_bg)
        self._title_text.draw(surface)
        self._button_confirm.draw(surface)
        self._chain_num_chooser.draw(surface)
        for it in self._instruction_texts:
            it.draw(surface)
        for pt in self._player_texts:
            pt.draw(surface)
        for rb in self._radio_buttons:
            rb.draw(surface)
        for sb in self._slide_bars_size:
            sb.draw(surface)
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
            mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_down = True
                elif event.type == pygame.QUIT:
                    running = False

            mouse_pos = pygame.mouse.get_pos()
            for i in range(len(self._radio_buttons)):
                self._radio_buttons[i].update(mouse_pos=mouse_pos, mouse_down=mouse_down)
            for i in range(len(self._slide_bars_size)):
                self._slide_bars_size[i].update(mouse_pos=mouse_pos, mouse_down=mouse_down, mouse_up=mouse_up)

            self._chain_num_chooser.update(mouse_pos=mouse_pos, mouse_down=mouse_down)
            flag_confirm = self._button_confirm.update(mouse_pos=mouse_pos, mouse_down=mouse_down)
            if flag_confirm:
                return flag_confirm


# call main when the script is run
if __name__ == "__main__":
    type_texts_s = ('Human', 'GoofyAI', 'NormalAI', 'SmartAI')
    pygame.init()
    GS = GomokuStarter(type_texts_s, 15, default_choices={0: 0, 1: 0})
    flag_confirm_t = GS.start()
    if flag_confirm_t:
        choices = GS.choices
        print(choices)
