import epd2in7b
import Image
import ImageFont
import ImageDraw
import datetime

COLORED = 1
UNCOLORED = 0

def refreshDisplay():
    epd = epd2in7b.EPD()
    epd.init()
    frame_black = epd.get_frame_buffer(Image.open('./contours.png'))
    frame_red = epd.get_frame_buffer(Image.open('./out.png'))
    epd.draw_filled_circle(frame_black, 121, 112, 2, COLORED);
    epd.draw_filled_circle(frame_red, 121, 112, 2, UNCOLORED);

    now = datetime.datetime.now()
    message = "Last update: {0:02d}:{1:02d}".format(now.hour + 2, now.minute)
    font = ImageFont.truetype('/usr/share/fonts/truetype/freemono/FreeMonoBold.ttf', 12)
    epd.draw_string_at(frame_black, 4, 250, message, font, COLORED)
    epd.draw_string_at(frame_red, 4, 250, message, font, UNCOLORED)

    epd.display_frame(frame_black, frame_red)
