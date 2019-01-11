import os
import sys
from PIL import Image, ImageFont, ImageDraw
import zxcvbn

from .emoji_directory import INITIAL_UNICODE, UNICODE_TO_PATH

RGB = 'RGB'
RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)
RGBA = 'RGBA'
RGBA_WHITE = (255, 255, 255, 1)
RGBA_BLACK = (0, 0, 0, 255)
RGBA_TRANSPARENT = (0, 0, 0, 0)
DEFAULT_FONT_SIZE = 72
DEFAULT_WIDTH = 1080
ZERO = 0
NEGATIVE = -1
MARGIN_LEFT = DEFAULT_FONT_SIZE * 1
MARGIN_RIGHT = DEFAULT_FONT_SIZE * 1
MARGIN_TOP = DEFAULT_FONT_SIZE * 1
MARGIN_BOTTOM = DEFAULT_FONT_SIZE * 1
LINE_SPACE = DEFAULT_FONT_SIZE * 1

EMOJI = 4
FULL_WIDTH = 3
HALF_WIDTH = 1


class Text2Pic(object):
    """将带有emoji的文本绘制到图片上，返回class 'PIL.Image.Image'。
       Text with emoji draw to the picture.return class 'PIL.Image.Image'

    :param text: 文本内容
    :param font: 字体
    :param ascii_font: ASCII字体
    :param emoji_folder: emoji图片和编码文件夹
    :param width: 图片宽度
    :param font_size: 文字大小
    :param color_mode: 图片底色模式
    :param font_color: 文字颜色
    :param background_color: 图片底色
    :param line_space: 行间距
    :param left: 左边距    left margins
    :param right: 右边距
    :param top: 上边距
    :param bottom: 下边距
    :param ascii_up: ASCII字符向上移动的像素
                     The pixel that the ASCII character moves up
    :param ascii_width: ASCII字符宽度
                        ASCII Character width

    :return:class 'PIL.Image.Image'
    """

    def __init__(self, text, font, emoji_folder,
                 ascii_font=None,
                 width=DEFAULT_WIDTH,
                 font_size=DEFAULT_FONT_SIZE,
                 color_mode=RGB,
                 font_color=RGB_BLACK,
                 background_color=RGB_WHITE,
                 line_space=LINE_SPACE,
                 left=MARGIN_LEFT,
                 right=MARGIN_RIGHT,
                 top=MARGIN_TOP,
                 bottom=MARGIN_BOTTOM,
                 ascii_width=ZERO,
                 ascii_up=ZERO,
                 ):
        self.text = text
        self.chs_font = font
        self.emoji_folder = emoji_folder
        self.ascii_font = ascii_font
        self.pic_width = int(width)
        self.font_size = int(font_size)
        self.background_color_mode = color_mode
        self.font_color = font_color
        self.background_color = background_color
        self.line_space = int(line_space)
        self.margin_left = int(left)
        self.margin_right = int(right)
        self.margin_top = int(top)
        self.margin_bottom = int(bottom)
        self.ascii_width = int(ascii_width)
        self.ascii_up_pixels = int(ascii_up)

        self.ZERO = 0
        self.coordinate_x = self.ZERO
        self.coordinate_y = self.ZERO
        self.progressbar_num = self.ZERO
        self.text_length = self.ZERO
        self.paragraph_list = []
        self.img_list = []
        self.img = None
        self.img_top = None
        self.img_bottom = None
        self.flag_code = None
        self.paragraph = None
        self.character = None
        self.emoji_char = None
        self.pass_num = None
        self.char_num = None
        self.emoji_codes = None
        self.character_class = None

    def split_paragraph(self):
        """
        分割段落
        Split paragraph
        """
        if isinstance(self.text, str) is not True:
            raise ValueError('text must be string.')
        self.paragraph_list = self.text.replace('\n\n', '\n \n').split('\n')
        # ---*--- 进度条 ---*--- #  progress bar
        for paragraph in self.paragraph_list:
            self.text_length += len(paragraph)
        # ---*---*---*---*---*--- #
        return self.paragraph_list

    def img_margin_top(self):
        """
        创建上边距图片
        Create top margin picture
        """
        self.img_top = Image.new(mode=self.background_color_mode,
                                 size=(self.pic_width, self.margin_top),
                                 color=self.background_color)
        self.img_list.append(self.img_top)
        return self.img_list

    def new_line_img(self):
        """
        创建一行的空白图片
        Create a blank picture
        """
        img = Image.new(mode=self.background_color_mode,
                        size=(self.pic_width, self.font_size + self.line_space),
                        color=self.background_color)
        return img

    def text_draw(self):
        """
        每个字符按坐标绘制
        Each character is plotted by coordinates
        """
        for paragraph in self.paragraph_list:
            self.paragraph = paragraph
            self.img = self.new_line_img()
            self.coordinate_x = self.margin_left
            self.coordinate_y = self.ZERO
            self.pass_num = self.NEGATIVE
            for num in range(len(paragraph)):
                # ---*--- 进度条 ---*--- #  progress bar
                self.progressbar_num += 1
                display_length = 50
                percent_num = int(self.progressbar_num / self.text_length * 100)
                percent_length = int(self.progressbar_num / self.text_length * display_length)
                sys.stdout.write('\r')
                sys.stdout.write(
                    'Drawing| '"[%s>%s] %s" % ('=' * percent_length, ' ' * (display_length - percent_length),
                                               str(percent_num) + '%'))
                sys.stdout.flush()
                # ---*---*---*---*---*--- #
                self.char_num = num
                if num <= self.pass_num:
                    pass  # 跳过
                else:
                    self.character = paragraph[num]
                    self.character_class = self.character_classification()
                    if self.character_class == -1:  # 跳过
                        pass
                    elif self.character_class == 1:  # ASCII字符
                        self.draw_ascii_chars()
                        if self.ascii_width == self.ZERO:
                            self.ascii_width = int(self.font_size / 2)
                        self.coordinate_x += self.ascii_width
                    elif self.character_class == 0:  # 全角字符
                        self.draw_full_width_chars()
                        self.coordinate_x += self.font_size
                    elif self.character_class in [2, 3, 4, 5]:  # emoji
                        self.draw_emoji()
                        self.coordinate_x += self.font_size
                # 换行
                if self.coordinate_x > self.pic_width - (
                        self.margin_right + self.font_size) or num >= len(paragraph) - 1:
                    self.img_list.append(self.img)
                    self.img = self.new_line_img()
                    self.coordinate_x = self.margin_left
                    self.coordinate_y = self.ZERO
        return self.img_list

    def character_classification(self):
        """字符分类
        Character classification

        分类方法：
        -1、跳过  pass
        0、全角字符                       Full-width characters
        1、ASCII字符                      ASCII characters
        2、*，#，数字emoji，三个字符      *,#,Digital emoji, three characters emoji
        3、单字符emoji                    Single character emoji
        4、多字符emoji                    Multiple characters emoji
        5、国旗emoji，两个字符            Flag emoji, double characters emoji
        """
        if not self.emoji_codes:
            with open(os.path.join(self.emoji_folder, 'emoji_codes.txt'), 'rb') as file:
                self.emoji_codes = pickle.load(file)
        emoji_connect = self.emoji_codes['emoji_connect']  # emoji肤色性别连接符
        emoji_utf8 = self.emoji_codes['emoji_utf8']  # utf8编码的emoji
        emoji_flag = self.emoji_codes['emoji_flag']  # 国旗emoji
        if u'\x20' <= self.character <= u'\x7e':
            if u'\x30' <= self.character <= u'\x39' or self.character in [u'\x23', u'\x2a']:
                try:
                    if self.paragraph[self.char_num + 1] in emoji_connect:
                        return 2  # 数字emoji
                except IndexError:
                    pass
            return 1  # ASCII字符
        elif self.character in emoji_flag:
            return 5  # 国旗emoji
        elif self.character >= u'\U0001f000' or self.character in emoji_utf8:
            try:
                if self.paragraph[self.char_num + 1] in emoji_connect:
                    return 4  # 多字符emoji
            except IndexError:
                pass
            return 3  # 单字符emoji
        else:
            return 0  # 全角字符

    def draw_ascii_chars(self):
        """
        绘制ASCII字符文本
        Draw ASCII character
        """
        if not self.ascii_font:
            self.ascii_font = self.chs_font
        font_type = ImageFont.truetype(self.ascii_font, size=self.font_size)
        ImageDraw.Draw(self.img).text(xy=(self.coordinate_x, self.coordinate_y - self.ascii_up_pixels),
                                      text=self.character, fill=self.font_color, font=font_type)
        return self.img

    def draw_full_width_chars(self):
        """
        绘制全角字符文本
        Draw full-width character
        """
        font_type = ImageFont.truetype(self.chs_font, size=self.font_size)
        ImageDraw.Draw(self.img).text(xy=(self.coordinate_x, self.coordinate_y),
                                      text=self.character, fill=self.font_color, font=font_type)
        return self.img

    def draw_emoji(self):
        """
        绘制emoji.png
        """
        emoji_file_name = self.emoji_name()
        try:
            emoji_pic = Image.open(os.path.join(self.emoji_folder, emoji_file_name + '.png'))
            if self.font_size == 72:
                pass
            else:
                emoji_pic = emoji_pic.resize((self.font_size, self.font_size), Image.ANTIALIAS)
            if emoji_pic.mode == 'RGBA':
                r, g, b, a = emoji_pic.split()  # 分离alpha通道  split alpha channel
            elif emoji_pic.mode == 'LA':
                l, a = emoji_pic.split()
            else:  # image.mode == 'P'
                emoji_pic = emoji_pic.convert('RGBA')
                r, g, b, a = emoji_pic.split()
            self.img.paste(emoji_pic, (self.coordinate_x, self.coordinate_y), mask=a)
        except (ValueError, FileNotFoundError, UnboundLocalError, AttributeError):
            self.coordinate_x -= self.font_size
        return self.img

    def emoji_name(self):
        """
        emoji文件名
        emoji file name
        """
        emoji_file_name = self.character.encode('unicode_escape')[1:].decode()
        # 多字符emoji
        if self.character_class == 4:
            file_name = emoji_file_name
            try:
                for i in range(7):
                    file_name = file_name + '-' + self.paragraph[self.char_num + i + 1].encode(
                        'unicode_escape')[1:].decode()
                    if file_name + '.png' in self.emoji_codes['emoji_files_name']:
                        self.pass_num = self.char_num + i + 1
                        emoji_file_name = file_name
            except IndexError:
                pass
        # 国旗emoji
        if self.character_class == 5:
            try:
                file_name = emoji_file_name + '-' + self.paragraph[self.char_num + 1].encode(
                    'unicode_escape')[1:].decode()
                if file_name + '.png' in self.emoji_codes['emoji_files_name']:
                    self.pass_num = self.char_num + 1
                    emoji_file_name = file_name
            except IndexError:
                pass
        # 数字emoji，三个字符
        if self.character_class == 2:
            if self.character == '*':
                file_name = 'x2a'
            elif self.character == '#':
                file_name = 'x23'
            else:
                file_name = 'x3' + self.character
            try:
                file_name_positive = file_name + '-' + self.paragraph[self.char_num + 1].encode(
                    'unicode_escape')[1:].decode() + '-' + self.paragraph[self.char_num + 2].encode(
                    'unicode_escape')[1:].decode()
                file_name_reverse = file_name + '-' + self.paragraph[self.char_num + 2].encode(
                    'unicode_escape')[1:].decode() + '-' + self.paragraph[self.char_num + 1].encode(
                    'unicode_escape')[1:].decode()
                if file_name_positive + '.png' in self.emoji_codes['emoji_files_name']:
                    self.pass_num = self.char_num + 2
                    emoji_file_name = file_name_positive
                elif file_name_reverse + '.png' in self.emoji_codes['emoji_files_name']:
                    self.pass_num = self.char_num + 2
                    emoji_file_name = file_name_reverse
            except IndexError:
                pass
        return emoji_file_name

    def combine_imgs(self):
        """
        合并图片
        Merge picture
        """
        # 创建下边距图片  Create bottom margin picture
        self.img_bottom = Image.new(mode=self.background_color_mode,
                                    size=(self.pic_width, self.margin_bottom),
                                    color=self.background_color)
        self.img_list.append(self.img_bottom)
        background_widths = self.pic_width
        background_height = self.ZERO
        paste_height = self.ZERO
        for img in self.img_list:
            background_height += img.size[1]
        background_img = Image.new(self.background_color_mode, (background_widths, background_height),
                                   self.background_color)
        for img in self.img_list:
            if self.background_color_mode == self.RGB:
                background_img.paste(img, (self.ZERO, paste_height))
                paste_height += img.size[1]
            elif self.background_color_mode == self.RGBA:
                r, g, b, a = img.split()  # 分离alpha通道
                background_img.paste(img, (self.ZERO, paste_height), mask=a)
                paste_height += img.size[1]
        print('\nImage Finished| Size:', background_img.size)
        return background_img

    def draw(self):
        """
        Main program
        """
        self.split_paragraph()
        self.img_margin_top()
        self.text_draw()
        return self.combine_imgs()
