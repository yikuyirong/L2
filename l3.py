from PIL import Image, ImageDraw, ImageFont
import functools
import os
import l2
import l4

import datetime
import dateutil.relativedelta
import dateutil.parser

import uuid

total_width = 210 * 5
total_height = 297 * 5


def genQuestionPage(dir:str, index:int , title:str, font):
    cols = 3
    rows = 5

    title_font_size = 30
    question_font_size = 24
    # answer_font_size = 18

    # guid = uuid.uuid1()
    # guid = title

    image = Image.new("RGB", size=(total_width, total_height), color=(255, 255, 255))
    image_draw = ImageDraw.Draw(image)
    imagefont = functools.partial(ImageFont.truetype, font=font)

    # answer_font = imagefont(size=answer_font_size)
    # (answer_width, answer_height) = image_draw.textsize(text="test", font=answer_font)

    # 打印标题
    title = f"Page{index} {title}"
    title_font = imagefont(size=title_font_size)
    (x,y,title_width, title_height) = image_draw.textbbox((0,0),text=title, font=title_font)
    title_height = title_height + 10
    image_draw.text(xy=(10, 10), text=title, fill=0, font=title_font)

    # 打印题目
    answer = []
    g = l4.getRandEquation()
    i = 1

    question_height = (total_height - title_height) / rows
    question_width = total_width / cols

    font = imagefont(size=question_font_size)

    for row in range(0, rows):
        for col in range(0, cols):
            (equ, result) = next(g)
            words = equ.split()
            words_width = 0

            for j,word in enumerate(words):
                width = image_draw.textlength(word + '  ',font)
                if words_width + width > question_width - 40:
                    words.insert(j,'\n')
                    words_width = 0
                else:
                    words_width = words_width + width

            image_draw.text(
                xy=(col * question_width + 10, row * question_height + title_height + 10),
                text=f"{i}.  {'、'.join(words)}", fill=0,
                font=font)

            answer.append("(%02d)%-6s" % (i, result))

            i = i + 1

    # 打印答案
    answer_line = [f"Page{index}"]

    # x_end = 0
    # while x_end < total_width:
    #     image_draw.line(xy=(x_end, total_height - answer_height * 5, x_end + 10, total_height - answer_height * 5), fill=0)
    #     x_end = x_end + 20
    #
    # image_draw.text(xy=(10, total_height - answer_height * 4), text=f"Page{index} {guid}", fill=0,font=answer_font)
    # image_draw.text(xy=(10, total_height - answer_height * 3), text=" ".join(answer[0:10]), fill=0, font=answer_font)
    # image_draw.text(xy=(10, total_height - answer_height * 2), text=" ".join(answer[10:20]), fill=0, font=answer_font)

    i = 0
    while i < len(answer):
        answer_line.append(" ".join(answer[i:i + 10]))
        i = i + 10

    image_file = os.path.join(dir, "%03d.jpg" % index)

    image.save(image_file, "JPEG")

    return (image_file, answer_line)


def genAnswerPage(dir, pagenum, answer_lines,font):
    image = Image.new("RGB", size=(total_width, total_height), color=(255, 255, 255))

    image_draw = ImageDraw.Draw(image)

    imagefont = ImageFont.truetype(font=font, size=18)

    (x,y,width, height) = image_draw.textbbox((0,0) ,"text", font=imagefont)

    i = 0
    for answer_line in answer_lines:

        for answer in answer_line:

            image_draw.text(xy=(10, i * height), text=answer, fill=0, font=imagefont)
            i = i + 1

        x_end = 0
        while x_end < total_width:
            image_draw.line(xy=(x_end, i * height + height / 2, x_end + 10, i * height + height / 2), fill=0)
            x_end = x_end + 20
        i = i + 1

    image_file = os.path.join(dir, "%03d.jpg" % pagenum)
    image.save(image_file, "JPEG")
    return image_file


def main():
    pagenum = input("输入需要生成的页数：")

    start = input("输入起始日期[yyyy-mm-dd]：")
    
    if start == '':
        start = datetime.date.today()
    else:
        start = dateutil.parser.parse(start)


    print(start)

    dir = os.path.join('MathExam',start.strftime('%Y%m%d'))

    if not os.path.isdir(dir):
        os.makedirs(dir)
        
        
        
    font = r'./fonts/MSYH.TTC'

    file_infos = [genQuestionPage(dir, i + 1,  f"{(start+ datetime.timedelta(days=i)).strftime('%Y-%m-%d')} 开始时间______________ 结束时期______________"   ,font) for i in range(0, int(pagenum))]

    files = list(map(lambda x: x[0], file_infos))

    answer_lines = list(map(lambda x: x[1], file_infos))

    # 生成答案页
    files.append(genAnswerPage(dir,int(pagenum) + 1, answer_lines,font))

    l2.gen_pdf(files, os.path.join(dir, f"{start.strftime('%Y%m%d')}.pdf"))


if __name__ == '__main__':
    main()
