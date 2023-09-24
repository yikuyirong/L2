from PIL import Image, ImageDraw, ImageFont
import functools
import os
import l2
import l4_generator as l4

import datetime
import dateutil.relativedelta
import dateutil.parser

class ExamPrint():
    
    def __init__(self,dir, col_count:int,row_count:int,generator) -> None:
        self.page_width = 210 * 5
        self.page_height = 297 * 5
        self.dir = dir
        self.col_count = col_count
        self.row_count = row_count
        self.basefont = functools.partial(ImageFont.truetype, font=r'./fonts/MSYH.TTC')
        self.generator = generator

    def genQuestionPage(self, index:int , title:str):

        title_font_size = 30
        question_font_size = 24
        # answer_font_size = 18

        # guid = uuid.uuid1()
        # guid = title

        image = Image.new("RGB", size=(self.page_width, self.page_height), color=(255, 255, 255))
        image_draw = ImageDraw.Draw(image)

        # answer_font = imagefont(size=answer_font_size)
        # (answer_width, answer_height) = image_draw.textsize(text="test", font=answer_font)

        # 打印标题
        title = f"Page{index} {title}"
        title_font = self.basefont(size=title_font_size)
        (x,y,title_width, title_height) = image_draw.textbbox((0,0),text=title, font=title_font)
        title_height = title_height + 10
        image_draw.text(xy=(10, 10), text=title, fill=0, font=title_font)

        # 打印题目
        answer = []

        i = 1

        question_height = (self.page_height - title_height) / self.row_count
        question_width = self.page_width / self.col_count

        font = self.basefont(size=question_font_size)

        for row in range(0, self.row_count):
            for col in range(0, self.col_count):
                (equ, result) = next(self.generator)
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


        i = 0

        while i < len(answer):
            answer_line.append(" ".join(answer[i:i + 10]))
            i = i + 10

        image_file = os.path.join(self.dir, "%03d.jpg" % index)

        image.save(image_file, "JPEG")

        return (image_file, answer_line)


    def genAnswerPage(self,pagenum, answer_lines):
        image = Image.new("RGB", size=(self.page_width, self.page_height), color=(255, 255, 255))

        image_draw = ImageDraw.Draw(image)

        imagefont = self.basefont(size=18)

        height = 10

        for answer_line in answer_lines:

            for answer in answer_line:
                
                (_,_,_,_height) = image_draw.multiline_textbbox((0,0),answer,imagefont)
                
                print(answer)

                image_draw.multiline_text(xy=(10, height), text=answer, fill=0, font=imagefont)
                
                height = height + _height

            #画分割虚线
            x_end = 0
            while x_end < self.page_width:
                image_draw.line(xy=(x_end, height + 5 , x_end + 10,  height + 5), fill=0)
                x_end = x_end + 20
                
            height = height + 5


        image_file = os.path.join(self.dir, "%03d.jpg" % pagenum)
        image.save(image_file, "JPEG")
        return image_file
            

def main():
    
    flag = input("测试类型[0 数学测试 1 诗词测试]").strip()
    
    if flag not in ['0','1']:
        raise BaseException('无效的测试类型')

    pagenum = input("输入需要生成的页数：")

    start = input("输入起始日期[yyyy-mm-dd]：")
    
    if start == '':
        start = datetime.date.today()
    else:
        start = dateutil.parser.parse(start)

    print(start)
    
    dir = os.path.join( 'MathExam' if flag == '0' else 'ShiCiExam' ,start.strftime('%Y%m%d'))

    if not os.path.isdir(dir):
        os.makedirs(dir)

    examPrint = ExamPrint(dir,3,5, l4.getRandEquation()) if flag == '0' else ExamPrint(dir,2,2, l4.getShiCiTest())

    file_infos = [examPrint.genQuestionPage(i + 1,  f"{(start+ datetime.timedelta(days=i)).strftime('%Y-%m-%d')} 开始时间______________ 结束时间______________" ) for i in range(0, int(pagenum))]

    files = list(map(lambda x: x[0], file_infos))

    answer_lines = list(map(lambda x: x[1], file_infos))

    # 生成答案页
    files.append(examPrint.genAnswerPage(int(pagenum) + 1, answer_lines))

    l2.gen_pdf(files, os.path.join(dir, f"{start.strftime('%Y%m%d')}.pdf"))


if __name__ == '__main__':
    main()
