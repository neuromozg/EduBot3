IP='10.10.16.100'

gst-launch-1.0 rtspsrc location=rtsp://$IP:8554/front latency=100 drop-on-latency=true buffer-mode=0 ! \
rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false
