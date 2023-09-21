from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import filetype
import os
import re
import PyPDF2



def gen_pdf(files, output):
    out_stream = PyPDF2.PdfWriter()

    for file in files:

        type = filetype.guess(file)

        def append_pdf(pdf):
            reader = PyPDF2.PdfReader(pdf, strict=False)
            for i in range(0, len(reader.pages)):
                out_stream.add_page(reader.pages[i])

        print("添加文件", file)
        if type.extension == "pdf":
            append_pdf(file)
        else:
            pdf = f"{file}.pdf"
            with Image.open(file) as image:
                if image.mode == "RGBA":
                    image = image.convert("RGB")
                image.save(pdf, "PDF")
            append_pdf(pdf)
            os.remove(pdf)

    out_stream.write(open(output, "wb"), )

    print("合并成功", output)


def listdirex(dir):
    return list(map(lambda x: os.path.join(dir, x), sorted(os.listdir(dir), key=lambda x: x.zfill(50))))


def main():
    try:

        input_files = []

        while True:

            try:

                input_files.clear()

                files = input("请输入需要合并的文件或文件夹，使用空格分隔，只支持图片和pdf：")

                if files.lower() in ["q", "e", "quit", "exit"]:
                    return

                files = list(filter(lambda x: x, re.split("\s+", files)))

                input_files = []

                def get_files(*files, exts=("jpg", "jpeg", "png", "bmp", "webp", "pdf"), ignore_error=True):

                    for file in files:
                        if os.path.isfile(file):
                            type = filetype.guess(file)
                            if type:
                                type = type.extension
                            if type in exts:
                                input_files.append(file)
                                print("\r检索文件...%d" % len(input_files), end=" ")
                            else:
                                if not ignore_error:
                                    raise Exception(f"{file}文件格式不对，只支持{exts}格式")

                        elif os.path.isdir(file):
                            get_files(*listdirex(file))
                        else:
                            if not ignore_error:
                                raise Exception(f"{file}不是有效的文件。")

                print("")
                get_files(*files)
                print("")

                input_files = sorted(input_files)

                if len(input_files) == 0:
                    raise Exception("请输入需要合并的文件")

                print(f"发现待合并的文件{len(input_files)}个")

                break


            except BaseException as e:
                print("\033[1;31m发生错误\033[0m", str(e))
                continue

        output_file = input("请输入需要生成的pdf文件[result.pdf]：")

        if output_file == "":
            output_file = "result.pdf"
        else:
            output_file = f"{output_file}.pdf"

        # gen_pdf(input_files[0:500], output_file)
        gen_pdf(input_files, output_file)

    except BaseException as e:
        print("\033[1;31m发生错误\033[0m", str(e))


if __name__ == '__main__':
    main()
