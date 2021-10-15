"""An implementation of Lindenmayer systems in Python with turtle graphics."""

from typing import List
import turtle
from defaults import *

IS_SETUP = False
IS_DONE = False

# todo have defaults up here as we can?


def get(value, default=None):
    return default if value is None else value


def setup(title="TurtLSystems", window_size=(0.75, 0.75), background_color=(0, 0, 0), background_image=None,
          canvas_size=(None, None), window_position=(None, None), delay=0, mode='standard'):
    turtle.colormode(255)
    turtle.title(str(get(title, "TurtLSystems")))
    turtle.mode(get(mode, "standard"))
    turtle.delay(get(delay, 0))
    window_w, window_h = get(window_size, (0.75, 0.75))
    window_x, window_y = get(window_position, (None, None))
    turtle.setup(window_w, window_h, window_x, window_y)
    canvas_w, canvas_h = get(canvas_size, (None, None))
    turtle.screensize(canvas_w, canvas_h)
    turtle.bgcolor(get(background_color, (0, 0, 0)))
    turtle.bgpic(background_image)
    global IS_SETUP
    IS_SETUP = True
# todo draws_per_frame, png_out/pad, gif_out/pad


def expand_lsystem(start, rules, n):
    for _ in range(n):
        start = ''.join(rules.get(c, c) for c in start)
    return start


def parse_rules(rules):
    if rules is None:
        rules = {}
    elif isinstance(rules, str):
        r = rules.split()
        rules = {inp: out for inp, out in zip(r[::2], r[1::2])}
    return rules


def make_color_list(color, fill_color, colors):
    if colors is None:
        colors = []
    if len(colors) < 10:
        defaults = [
            (255, 0, 0),
            (255, 128, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 255, 255),
            (0, 0, 255),
            (128, 0, 255),
            (255, 0, 255),
            (128, 128, 128),
            (255, 255, 255)
        ]
        colors = list(map(tuple, colors))
        colors.extend(defaults[len(colors):])
        if color is not None:
            colors[0] = tuple(color)
        if fill_color is not None:
            colors[1] = tuple(fill_color)
    return colors


def orient(t: turtle.Turtle, position, heading):
    speed = t.speed()
    down = t.isdown()
    t.penup()
    t.speed(0)
    t.setposition(position)
    t.setheading(heading)
    t.speed(speed)
    if down:
        t.pendown()


class State:
    def __init__(self, position, heading, angle, length, thickness, pen_color, fill_color,
                 swap_signs, change_fill):
        self.position = tuple(position)
        self.heading = heading
        self.angle = angle
        self.length = length
        self.thickness = thickness
        self.pen_color = pen_color
        self.fill_color = fill_color
        self.swap_signs = swap_signs
        self.change_fill = change_fill


def run(t: turtle.Turtle, string, colors, angle, length, thickness, angle_increment,
        length_increment, length_scalar, thickness_increment, color_increments, full_circle):
    initial_angle, initial_length = angle, length
    swap_signs, change_fill = False, False
    pen_color, fill_color = colors[0], colors[1]
    t.pencolor(pen_color)
    t.fillcolor(fill_color)
    stack: List[State] = []

    def set_color(color):
        nonlocal pen_color, fill_color, change_fill
        if change_fill:
            change_fill = False
            fill_color = color
            t.fillcolor(fill_color)
        else:
            pen_color = color
            t.pencolor(pen_color)

    def increment_color(channel, decrement=False):
        color = list(fill_color if change_fill else pen_color)
        amount = (1 if decrement else -1) * color_increments[channel]
        color[channel] = max(0, min(color[channel] + amount, 255))
        set_color(tuple(color))

    for c in string:
        # Length:
        if 'A' <= c <= 'Z':
            t.pendown()
            t.forward(length)
        elif 'a' <= c <= 'z':
            t.penup()
            t.forward(length)
        elif c == '_':
            length = initial_length
        elif c == '^':
            length += length_increment
        elif c == '%':
            length -= length_increment
        elif c == '*':
            length *= length_scalar
        elif c == '/':
            length /= length_scalar
        # Angle:
        elif c == '+':
            (t.right if swap_signs else t.left)(angle)
        elif c == '-':
            (t.left if swap_signs else t.right)(angle)
        elif c == '&':
            swap_signs = not swap_signs
        elif c == '|':
            t.right(full_circle/2.0)
        elif c == '~':
            angle = initial_angle
        elif c == ')':
            angle += angle_increment
        elif c == '(':
            angle -= angle_increment
        # Thickness:
        elif c == '=':
            t.pensize(thickness)
        elif c == '>':
            t.pensize(max(1, thickness + thickness_increment))
        elif c == '<':
            t.pensize(max(1, thickness - thickness_increment))
        # Color:
        elif '0' <= c <= '9':
            set_color(colors[int(c)])
        elif c == '#':
            change_fill = True
        elif c == ',':
            increment_color(0)
        elif c == '.':
            increment_color(0, True)
        elif c == ';':
            increment_color(1)
        elif c == ':':
            increment_color(1, True)
        elif c == '?':
            increment_color(2)
        elif c == '!':
            increment_color(2, True)
        # Other:
        elif c == '{':
            t.begin_fill()
        elif c == '}':
            t.end_fill()
        elif c == '@':
            t.dot(None, fill_color)
        elif c == '`':
            stack.clear()
        elif c == '[':
            stack.append(State(t.position(), t.heading(), angle, length, thickness,
                         pen_color, fill_color, swap_signs, change_fill))
        elif c == ']':
            if stack:
                s = stack.pop()
                orient(t, s.position, s.heading)
                angle, length = s.angle, s.length
                swap_signs, change_fill = s.swap_signs, s.change_fill
                pen_color, fill_color = s.pen_color, s.fill_color
        elif c == '$':
            break


# todo? get-ify all these? probably, watch out for colors and rules
def draw(start='F', rules='F ,F+F-F-F+F', n=4, angle=90, length=10, thickness=1, color=(255, 0, 0),
         fill_color=(255, 128, 0), background_color=(0, 0, 0), *, colors=None,
         angle_increment=15, length_increment=5, length_scalar=2, thickness_increment=1,
         red_increment=4, green_increment=4, blue_increment=4, position=(0, 0), heading=0,
         speed=0, asap=False, show_turtle=False, turtle_shape='classic', full_circle=360.0, last=True):
    if not IS_SETUP:
        setup()

    turtle.colormode(255)
    turtle.bgcolor(background_color)
    if asap:
        saved_tracer, saved_delay = turtle.tracer(), turtle.delay()
        turtle.tracer(0, 0)

    t = turtle.Turtle()
    t.speed(speed)
    t.degrees(full_circle)
    t.shape(turtle_shape)
    if show_turtle:
        t.showturtle()
    else:
        t.hideturtle()
    orient(t, position, heading)

    string = expand_lsystem(start, parse_rules(rules), n)
    colors = make_color_list(color, fill_color, colors)
    run(t, string, colors, angle, length, thickness, angle_increment, length_increment, length_scalar,
        thickness_increment, (red_increment, green_increment, blue_increment), full_circle)

    if asap:
        turtle.tracer(saved_tracer, saved_delay)
        turtle.update()
    if last and not IS_DONE:
        turtle.done()

    return string, tuple(t.position()), t.heading()


def finish():
    global IS_DONE
    if not IS_DONE:
        IS_DONE = True
        turtle.done()


# print(draw("F", {'F': 'F+F-F-F+F'}, angle=90, instant=True, last=False))


draw(red_increment=1, n=4, asap=True, speed=1)
