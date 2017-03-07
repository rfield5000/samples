
# manage things like CSS and color schemes

import colorsys
import os.path

base_color = (1, 1, 0) # yellow

def run_rgb_to_hsv(rgb):
    return colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])

def rgb_to_color(rgb):
    return "#" + (''.join([("%02x" % int(255*color)) for color in rgb]))

def rotate_color(rgb, fraction):
     hsv = run_rgb_to_hsv(rgb)
     new_value = (hsv[0] + fraction) % 1
     return colorsys.hsv_to_rgb(new_value, hsv[1], hsv[2])

def change_saturation(rgb, new_sat):
     hsv = run_rgb_to_hsv(rgb)
     return colorsys.hsv_to_rgb(hsv[0], new_sat, hsv[2])

base_color = (1, 1, 0) # yellow
base_color_string = rgb_to_color(base_color)

complementary_color = change_saturation(rotate_color(base_color, 1.0/3.0), 0.25)
complementary_color_string = rgb_to_color(complementary_color)

minor_color = change_saturation(rotate_color(base_color, 2.0/3.0), 0.25)
minor_color_string = rgb_to_color(minor_color)

# Relating to templating
template_directory = "displays"
schedule_template_name = "schedule_include.html"
schedule_template_path = os.path.join(template_directory, schedule_template_name)

if __name__ == "__main__":
    print base_color_string, complementary_color_string, minor_color_string
    print run_rgb_to_hsv(base_color)
    print rotate_color(base_color, 0.5)

