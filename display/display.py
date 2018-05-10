import epd2in7b
import Image
import ImageFont
import ImageDraw

COLORED = 1
UNCOLORED = 0

def refreshDisplay():
    epd = epd2in7b.EPD()
    epd.init()
    frame_black = epd.get_frame_buffer(Image.open('../map.png'))
    frame_red = epd.get_frame_buffer(Image.open('../out.png'))
    epd.display_frame(frame_black, frame_red)
