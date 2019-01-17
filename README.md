# emoji2pic-python
Apple emoji and text to image

## 介绍

使用Python Pillow根据unicode将文本和emoji绘制到图片上  
可自选字体，字号，行距，页边距，颜色，图片宽度和透明度  

## 开发进度
https://emojipedia.org/apple/ios-12.1/
目前完成匹配Apple iOS 12.1 emoji 共2776个   

## 问题

1、根据像素绘制文本，只适合等宽字体。很多字体的拉丁字母都不等宽，比如雅黑  
解决方法：使用ascii_up字段，支持自定义ASCII范围的拉丁字母的字体，也可使用ascii_width字段调节拉丁字母宽度  
2、使用独立拉丁字母字体时，会造成字体下沉几像素  
解决方法：使用ascii_up字段，自定义拉丁字母上浮

## 依赖库

Python Pillow  

## 使用方法

|字段|说明|格式|必传|
|:---:|:---:|:---:|:---:|
|text|文本内容|char|yes|
|font|字体文件路径|char|yes|
|emoji_folder|emoji图片文件夹路径|char|yes|
|width|图片宽度|int|no|
|font_size|文字大小|int|no|
|font_color|文字颜色|RGB/RGBA|no|
|color_mode|图片底色模式|char|no|
|background_color|图片底色|RGB/RGBA|no|
|line_space|行间距|int|no|
|left|左边距|int|no|
|right|右边距|int|no|
|top|上边距|int|no|
|bottom|下边距|int|no|
|half_font|半角字符字体路径|char|no|
|half_font_width|半角字符字体宽度|int|no|
|half_font_offset|半角字符纵轴偏移量|int|no|
|emoji_offset|emoji纵轴偏移量|int|no|
|progress_bar|控制台输出进度条|boolean|no|

## 简单入门实例

# License
MIT license.
