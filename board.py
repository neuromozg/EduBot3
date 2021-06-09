#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import os
import pickle
import sys
import crc16
import smbus

#библиотеки для работы с изображениями Python Image Library
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#sys.path.append('EduBot/EduBotLibrary')
import edubot

#IP = '127.0.0.1'
IP = str(os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','')) #получаем IP, удаляем \n
PORT = 8000
TIMEOUT = 60
SERVO_MIN_POS = 42
SERVO_MED_POS = 62
SERVO_MAX_POS = 90

#настройки видеопотока
WIDTH, HEIGHT = 320, 240
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30
RTP_PORT = 8554 #порт отправки RTP видео

oldText = '' #переменная для отрисовки текста на дисплее

def SetSpeed(leftSpeed, rightSpeed):
    robot.setPwm0(leftSpeed)
    robot.setPwm1(rightSpeed)

def SetCameraServoPos(position):
    #нормализация значения
    if position > SERVO_MAX_POS:
        position = SERVO_MAX_POS
    elif position < SERVO_MIN_POS:
        position = SERVO_MIN_POS
    
    robot.setServo0(position)

def TextDisplay(text):
    global oldText
    if oldText != text:
        # Отрисовываем на картинке черный прямоугольник, тем самым её очищая
        draw.rectangle((0, 0, robot.displaySize[0], robot.displaySize[1]), outline=0, fill=0)
        widthText, heightText = draw.textsize(text)
        widthDisp, heightDisp = robot.displaySize
        #Отрисовываем текс в центре картинки
        draw.text(((widthDisp - widthText)/2, (heightDisp - heightText)/2), text, font=font, fill=255)
        robot.DrawDisplay(image) #отрисовываем сформированную картинку на дисплее
        oldText = text
    

bus = smbus.SMBus(1)
robot = edubot.EduBot(bus)
assert robot.check(), 'EduBot not found!!!'
print('EduBot shield found')

#проверка наличия камеры в системе  
#assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
#print('Raspberry Pi camera found')

robot.start() #обязательная процедура, запуск потока отправляющего на контроллер EduBot онлайн сообщений
print ('EduBot started!!!')

robot.setMotorMode(edubot.MotorMode.MOTOR_MODE_PWM)

#image = Image.new('1', robot.displaySize) #создаем ч/б картинку для отрисовки на дисплее
#draw = ImageDraw.Draw(image) #создаем объект для рисования на картинке
#font = ImageFont.load_default() #создаем шрифт для отрисовки текста на картинке
#fontFile = 'DejaVuSerif.ttf'
#font = ImageFont.truetype(fontFile, 15) #создаем шрифт для отрисовки текста на картинке

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем UDP server
server.bind((IP, PORT)) #запускаем сервер
server.settimeout(TIMEOUT)
print("Listening %s on port %d..." % (IP, PORT))

countPacket = 0
userIP = ''

TextDisplay('EduBot')

servoPos = SERVO_MED_POS

while True:
    try:
        packet = server.recvfrom(1024) # получаем UDP пакет
    except socket.timeout:
        print('Time is out...')
        break

    countPacket += 1
    if userIP == '':
        userIP = packet[1][0]
        print('Робот зохвачен: %s. Мва-ха-ха!!!!' % userIP)

    else:
        if packet[1][0] == userIP:
        
            data = packet[0] #полученный массив байт
    
            crcBytes = data[-2:] #берем последние 2 байта из пакета данных
            crc = int.from_bytes(crcBytes, byteorder='big', signed = False)

            stateMoveBytes = data[:-2] #берем байты пакета
            newCrc = crc16.crc16xmodem(stateMoveBytes) #вычисляем CRC16

            if crc == newCrc:
                leftSpeed, rightSpeed, servoMove, beep, automat = pickle.loads(stateMoveBytes)
 
                servoPos += servoMove
                servoPos = min(max(SERVO_MIN_POS, servoPos), SERVO_MAX_POS)  # нормализуем значение
                
                SetSpeed(leftSpeed, rightSpeed) #задаем скорости
                SetCameraServoPos(servoPos) #задаем положение серво

                #TextDisplay(text) #отрисовываем текcт на дисплее

            else:
                print('%d Error CRC packet' % countPacket)
        else:
            print('Левый пакет от %s' % packet[1][0])

server.close()

SetSpeed(0, 0)
SetCameraServoPos(SERVO_MED_POS)

#останавливаем поток отправки онлайн сообщений в контроллер EduBot
robot.exit()
print('End program')
