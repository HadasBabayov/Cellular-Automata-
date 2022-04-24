# Roni Gotlib 322805029
# Hadas Babayov 322807629
import numpy as np
import pygame
import sys
import matplotlib.pyplot as plt
from random import randint
import random

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([700, 450])
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)
text_color = pygame.Color('#61A4BC')
title_color = pygame.Color('black')
num_of_iterations = 100
slot_size = 2
EMPTY, RECOVERING, HEALTHY, SICK = 'empty', 'recovering', 'healthy', 'sick'


class textField:
    def __init__(self, location, value=''):
        self.location = pygame.Rect(location)
        self.value = value
        self.activeColor = pygame.Color('#A9A9A9')
        self.passiveColor = pygame.Color('#5B7DB1')
        self.color = self.passiveColor
        self.isActive = False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.location.collidepoint(event.pos):
                self.isActive = True
            else:
                self.isActive = False

        if event.type == pygame.KEYDOWN:
            if self.isActive:
                if event.key == pygame.K_BACKSPACE:
                    self.value = self.value[:-1]
                else:
                    self.value += event.unicode

        if self.isActive:
            self.color = self.activeColor
        else:
            self.color = self.passiveColor

    def update_width(self):
        width = max(100, font.render(self.value, True, self.color).get_width() + 10)
        self.location.w = width

    def write_value(self):
        pygame.draw.rect(screen, self.color, self.location)
        screen.blit(font.render(self.value, True, 'black'), (self.location.x + 5, self.location.y + 5))


# This class forms one slot from the board.
class Square:
    def __init__(self, state, count_iterations):
        self.state = state
        self.count_iterations = count_iterations

    # Sick --> count_iterations++
    def addToCounter(self, x):
        self.count_iterations += 1
        if self.count_iterations >= x:
            self.state = RECOVERING


# This function receives data and displays it in a graph.
def graph(graph_title, x_title, y_title, x_values, y_values):
    plt.title(graph_title)
    plt.plot(x_values, y_values)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.show()


def is_exit_event(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


def get_input():
    # Background.
    screen.fill('#F7E2E2')
    # Titles.
    screen.blit(font.render("Enter the following details : ", True, title_color), (30, 20))
    screen.blit(font.render("Number of creatures : ", True, text_color), (50, 60))
    screen.blit(font.render("Initial percentage of patients : ", True, text_color), (50, 110))
    screen.blit(font.render("Percentage of fast-moving creatures : ", True, text_color), (50, 160))
    screen.blit(font.render("Number of generations until recovery : ", True, text_color), (50, 210))
    screen.blit(font.render("Chance of infection : ", True, text_color), (50, 260))
    screen.blit(font.render("Threshold value of the chance of infection : ", True, text_color), (50, 310))
    screen.blit(font.render("-- Press ENTER to start the graphic display --", True, title_color), (100, 380))

    # Text fields.
    N = textField((500, 60, 150, 30), str(2000))
    D = textField((500, 110, 150, 30), str(0.01))
    R = textField((500, 160, 150, 30), str(0.3))
    X = textField((500, 210, 150, 30), str(6))
    P = textField((500, 260, 150, 30), str(0.3))
    T = textField((500, 310, 150, 30), str(0.5))
    all_text_fields = [N, D, R, X, P, T]
    finish = False

    global n, d, r, x, p, t
    while not finish:
        for event in pygame.event.get():
            is_exit_event(event)

            for field in all_text_fields:
                field.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    n = int(N.value)
                    d = float(D.value)
                    r = float(R.value)
                    x = int(X.value)
                    p = float(P.value)
                    t = float(T.value)
                    finish = True

        for field in all_text_fields:
            field.update_width()

        for field in all_text_fields:
            field.write_value()

        pygame.display.flip()
        clock.tick(30)


# The function gets a location and a board, and checks if there is a sick neighbor.
def has_sick_neighbor(board, i, j):
    for k in range(-1, 2):
        for l in range(-1, 2):
            if board[(i + k) % 200][(j + l) % 200].state == SICK:
                return True
    return False


# This function performs a step to free neighbor by to the logic that prevents collisions that we explained in PDF.
def make_move(board, next_board, i, j, moves):
    for times in range(10):
        moveOnRow = random.randint(0, 2)
        moveOnCol = random.randint(0, 2)
        row = (i + moves[moveOnRow]) % 200
        col = (j + moves[moveOnCol]) % 200

        if next_board[row][col].state == EMPTY and board[row][col].state == EMPTY:
            next_board[row][col] = board[i][j]
            board[i][j] = Square(EMPTY, 0)
            return board, next_board

    if next_board[i][j].state == EMPTY:
        next_board[i][j] = board[i][j]
        board[i][j] = Square(EMPTY, 0)
        return board, next_board

    return board, next_board


# This function returns n random places on the board.
def random_tuples(n):
    seen = set()
    a, b = randint(0, 199), randint(0, 199)

    for i in range(n):
        seen.add((a, b))
        yield a, b
        a, b = randint(0, 199), randint(0, 199)
        while (a, b) in seen:
            a, b = randint(0, 199), randint(0, 199)
    return seen


# This function returns a board where all the squares are empty.
def init_empty_board():
    board = []
    for i in range(int(200)):
        row = []
        for j in range(int(200)):
            row.append(Square(EMPTY, 0))
        board.append(row)
    return board


# This function initializes a board with n creatures at random locations.
def initialization(n, d):
    # Simulation first values
    board = init_empty_board()

    n_locations = random_tuples(n)
    for (i, j) in n_locations:
        healthy = Square(HEALTHY, 0)
        sick = Square(SICK, 0)
        # In probability D the creature will be sick.
        label = np.random.choice([sick, healthy], p=[d, 1 - d])
        board[i][j] = label
    return board


def simulation(n, d, r, x, p, t):
    # Background.
    screen.fill('#F7E2E2')
    pygame.draw.rect(screen, 'grey', (0, 0, 200, 450))
    pygame.draw.rect(screen, 'black', (180, 0, 20, 450))
    # Title.
    screen.blit(font.render("SIMULATION ", True, title_color), (20, 30))
    screen.blit(small_font.render("-- Press SPACE to export graph -- ", True, title_color), (350, 10))
    pygame.display.update()

    # Number of sicks - to show in graph.
    num_of_sicks = []
    # First board.
    board = initialization(n, d)
    iteration = 0
    while iteration < num_of_iterations:
        for event in pygame.event.get():
            is_exit_event(event)

            # If the user export SPACE - export graph.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    title = 'Number of sicks over the generations'
                    x_title = 'Number of iterations'
                    y_title = 'Number of sicks'
                    x_values = list(range(iteration))
                    y_values = num_of_sicks
                    graph(title, x_title, y_title, x_values, y_values)

        count_sick, count_healthy, count_recovering = 0, 0, 0
        for i in range(int(200)):
            for j in range(int(200)):
                # Draw creatures on the screen.
                offset_x = 250
                offset_y = 30
                a = i * slot_size + offset_x
                b = j * slot_size + offset_y
                if board[i][j].state == SICK:
                    pygame.draw.rect(screen, 'white', (a, b, slot_size, slot_size))
                    count_sick += 1
                elif board[i][j].state == HEALTHY:
                    pygame.draw.rect(screen, 'steelblue4', (a, b, slot_size, slot_size))
                    count_healthy += 1
                elif board[i][j].state == RECOVERING:
                    pygame.draw.rect(screen, 'red', (a, b, slot_size, slot_size))
                    count_recovering += 1
                elif board[i][j].state == EMPTY:
                    pygame.draw.rect(screen, 'black', (a, b, slot_size, slot_size))
                pygame.draw.line(screen, (20, 20, 20), (a, b), (a, 270))
                pygame.draw.line(screen, (20, 20, 20), (a, b), (270, b))

        for i in range(int(200)):
            for j in range(int(200)):
                # Infection.
                if board[i][j].state == HEALTHY and has_sick_neighbor(board, i, j):
                    healthy = Square(HEALTHY, 0)
                    sick = Square(SICK, 0)
                    new_label = np.random.choice([healthy, sick], p=[1 - p, p])
                    board[i][j] = new_label

                # Add 1 to counters of sicks.
                if board[i][j].state == SICK:
                    board[i][j].addToCounter(x)

        num_of_sicks.append(count_sick)

        # Make move (In probability R -- jump 10 steps).
        next_board = init_empty_board()
        for i in range(int(200)):
            for j in range(int(200)):
                # In probability R the step is size 10.
                is_r = np.random.choice(np.arange(0, 2), p=[1 - r, r])
                if is_r == 0:
                    board, next_board = make_move(board, next_board, i, j, [-1, 0, 1])
                else:
                    board, next_board = make_move(board, next_board, i, j, [-10, 0, 10])

        # Update P according to the threshold ratio.
        if (count_sick / n) > t:
            p = max(p - 0.2, 0.1)
        else:
            p = min(p + 0.2, 0.9)

        board = next_board
        iteration += 1
        # Write the iteration results on the screen.
        pygame.draw.rect(screen, 'grey', (0, 60, 200, 450))
        pygame.draw.rect(screen, 'black', (180, 0, 20, 450))
        screen.blit(small_font.render("Iteration: " + str(iteration), True, title_color), (20, 70))
        screen.blit(small_font.render("Sick: " + str(count_sick), True, title_color), (20, 120))
        screen.blit(small_font.render("Healthy: " + str(count_healthy), True, title_color), (20, 170))
        screen.blit(small_font.render("Recovering: " + str(count_recovering), True, title_color), (20, 220))
        pygame.display.update()

    # Show graph for all simulation.
    x_values = list(range(num_of_iterations))
    y_values = num_of_sicks
    graph('Number of sicks over the generations', 'Number of iterations', 'Number of sicks', x_values, y_values)


if __name__ == '__main__':
    get_input()
    simulation(n, d, r, x, p, t)
