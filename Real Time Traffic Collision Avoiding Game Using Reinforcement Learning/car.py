import pygame
import random
import numpy

pygame.init()

clock = pygame.time.Clock()

fps = 60

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
point = 0

car_height = 100
car_width = 60
speed = 25

lane = 3
lane_width = SCREEN_WIDTH//lane

road_line_height = 50
road_line_width = 8
road_line_gap = 100
road_line_speed = 2

font_size = 36

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont("Arial", font_size)
user_car = pygame.Rect((SCREEN_WIDTH - car_width)//2, 500, car_width , car_height)

maximum_npc_cars = 10
npc_cars = []
road_lines = []
alive = True

spawn_prob_list = [0.7 , 0.1 , 0.1, 0.05 ,0.05]

def spawn_npc_car():
    if len(npc_cars) < maximum_npc_cars:
        num = numpy.random.choice([0,1,2,3,4], p=spawn_prob_list)
        if num != 0:
            num = num - 1
            npc_cars.append((pygame.Rect(num * lane_width + car_width // 2 - road_line_width, - car_height , car_width, car_height), num))

def distroy_old_npc():
    i = 0
    global point
    while i < len(npc_cars):
        if npc_cars[i][0].y > SCREEN_HEIGHT:
            npc_cars.pop(i)
            point +=1 
        else:
            i+=1

def move_npc():
    for car , lane_index in npc_cars:
        car.y += road_line_speed + lane_index

def draw_npc_car():
    for car , speed in npc_cars:
        pygame.draw.rect(screen , (0,255,255) , car)

def collision_detect():
    global alive
    for npc_rect, lane in npc_cars:
        collide = pygame.Rect.colliderect(user_car, npc_rect)
        if collide:
            alive = False
            pygame.time.delay(500)
            break

def draw_road():
    if len(road_lines) == 0:
        i = 0
        while i < SCREEN_HEIGHT // (road_line_gap + road_line_height) + 1:
            j = 0
            while j < lane - 1:
                road_lines.append(pygame.Rect(lane_width * (j+1) - road_line_width//2 , i * (road_line_gap + road_line_height), road_line_width, road_line_height))
                j += 1
            i += 1
    
    if road_lines[-1].y > SCREEN_HEIGHT:
        for i in range(lane-1):
            road_lines.pop(-1)
            road_lines.insert(0 , pygame.Rect(lane_width * (i+1) - road_line_width//2 , -(road_line_gap + road_line_height), road_line_width, road_line_height))

    for line in road_lines:
        line.y += road_line_speed
        pygame.draw.rect(screen, (255,255,255), line)

def display():
    screen.fill((75,75,75))
    draw_road()
    draw_npc_car()
    pygame.draw.rect(screen , (255,0,0) , user_car)
    str1 = str(point)
    text = font.render(str1, True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH // 2 - (len(str1) * font_size / 2), 0))
    pygame.display.update()

num = 0
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if user_car.y < SCREEN_HEIGHT - car_height:
                    user_car.y = speed + user_car.y
            if event.key == pygame.K_UP:
                if user_car.y >= 0:
                    user_car.y = -speed + user_car.y
            if event.key == pygame.K_RIGHT:
                if user_car.x < SCREEN_WIDTH - car_width:
                    user_car.x = speed + user_car.x
            if event.key == pygame.K_LEFT:
                if user_car.x >= 0:
                    user_car.x = -speed + user_car.x

    if alive == True:
        distroy_old_npc()
        if num == 20:
            spawn_npc_car()
            num = 0
        move_npc()
        collision_detect()
    else:
        run = False

    display()
    num += 1
    clock.tick(fps)

pygame.quit()