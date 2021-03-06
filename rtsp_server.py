#!/usr/bin/env python
# -*- coding:utf-8 vi:ts=4:noexpandtab
# Simple RTSP server. Run as-is or with a command-line to replace the default pipeline

""" Для получения доступа к трансляции необходимо ввести ссылку "rtsp://..." (выводится при запуске сервера) в проигрыватель rtsp потоков, например плеер vlc"""


import sys
import gi
import os

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

loop = GLib.MainLoop()
Gst.init(None)


# Функция для получения IP робота
def getIP():
    res = os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','') #получаем IP, удаляем \n
    return res

# функция для формирования пайплайна
class CamFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        pipeline_str = "( v4l2src device=/dev/video0 ! video/x-raw, width=640, height=480 ! v4l2h264enc ! rtph264pay name=pay0 pt=96 )"
        print(pipeline_str)
        return Gst.parse_launch(pipeline_str)



# класс сервера
class Server():
    def __init__(self):
        self.Server = GstRtspServer.RTSPServer.new()
        Cam = CamFactory()
        Cam.set_shared(True)

        m = self.Server.get_mount_points()
        m.add_factory("/edubot", Cam)

        self.Server.attach(None)

        portServer = self.Server.get_bound_port()
        print('RTSP server started: rtsp://%s:%d/front' % (getIP(), portServer)) # Вывод ссылки для подключения к серверу

		
if __name__ == '__main__':
    server = Server() # инициализация сервера
    loop.run()
