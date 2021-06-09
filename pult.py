#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import socket
import pickle
import crc16
import sys
import numpy as np
import cv2

SPEED = 150
IP_ROBOT = '10.10.16.164'
PORT = 8000
RTSP_PORT = 8554

FPS = 10  # количество кадров в секунду у окна Pygame
WIDTH = 640
HEIGHT = 360

#фунция вызываемая при получении кадра с камеры робота
def onFrameCallback(data, width, height):
    global frame
    #преобразуем массив байт в изображение Pygame
    frame = pygame.image.frombuffer(data, (width, height), 'RGB')

running = True
leftSpeed = 0
rightSpeed = 0
servoMove = 0
beep = 0
automat = False
frame = None

pygame.init() #инициализация Pygame
pygame.mixer.quit() #отключаем миксер иначе в Linux будет 100% загрузки CPU

screen = pygame.display.set_mode((WIDTH, HEIGHT))  #Создаем окно вывода программы
clock = pygame.time.Clock() #для формирования задержки
font = pygame.font.Font(None, 26) #создали шрифт

#создаем UDP клиента
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#основной цикл работы программы
while running:
    events = pygame.event.get() #получаем список событий
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        #обрабоотка нажатий клавиш    
        elif event.type == pygame.KEYDOWN:
            #print(event.key)
            if event.key == pygame.K_LEFT:
                leftSpeed = SPEED
                rightSpeed = SPEED
            elif event.key == pygame.K_RIGHT:
                leftSpeed = -SPEED
                rightSpeed = -SPEED
            elif event.key == pygame.K_UP:
                leftSpeed = SPEED
                rightSpeed = -SPEED
            elif event.key == pygame.K_DOWN:
                leftSpeed = -SPEED
                rightSpeed = SPEED
            elif event.key == pygame.K_PAGEUP:
                servoMove = -1
            elif event.key == pygame.K_PAGEDOWN:
                servoMove = 1
            elif event.key == pygame.K_SPACE:
                beep = True
                
        #обрабоотка отпускания клавиш        
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT,
                             pygame.K_UP, pygame.K_DOWN):
                leftSpeed = 0
                rightSpeed = 0
            elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                servoMove = 0
            elif event.key == pygame.K_SPACE:
                beep = False

                
    #сформировали управляющий пакет/кортеж
    packet = (leftSpeed, rightSpeed, servoMove, beep, automat)
    
    #упаковали в массив байт
    packetBytes = pickle.dumps(packet, protocol = 3)

    #рассчитываем контрольную сумму
    crc = crc16.crc16xmodem(packetBytes)

    #преобразуем сумму в байтовый массив
    crcBytes = int.to_bytes(crc, byteorder='big', length = 2, signed = False)

    #отправляем пакет + контр. сумма на робота
    client.sendto(packetBytes + crcBytes, (IP_ROBOT, PORT)) #отправили пакет на робота

    #Формируем картинку на экране
    #Очищаем экран
    screen.fill((255, 255, 255))

    if not frame is None:
        screen.blit(frame, (0,0)) #отрисовываем принятый кадр на экране

        #рисуем перекрестье
        pygame.draw.line(screen, (255, 0, 255), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)
        pygame.draw.line(screen, (255, 0, 255), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
    
    pygame.display.flip() #перерисовываем экран screen
    
    # задержка
    clock.tick(FPS)


#деинициализация Pygame
pygame.quit()
