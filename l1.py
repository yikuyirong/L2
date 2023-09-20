
import requests
import requests_async
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import os
import hashlib
from pydub import AudioSegment
import random
import re
from datetime import datetime
import nls_app
import asyncio
import aiofile

from enum import Enum

class ExamLx(Enum):
    听英语写汉语 = 0
    听汉语写英语 = 1
    随机 = 2


class HearingExam():
    appKey = nls_app.appKey
    accessKeyId = nls_app.accessKeyId
    secret = nls_app.secret
    def __init__(self, student: str, file: str, countPerExam: int, outputDir) -> None:
        self.student = student
        self.file = file
        self.countPerExam = countPerExam
        self.token = self.getToken()
        self.outputDir = os.path.join(outputDir)
        if not os.path.isdir(self.outputDir):
            os.mkdir(self.outputDir)
    
    # 获取Token
    def getToken(self):
        client = AcsClient(ak=self.accessKeyId,
                           secret=self.secret, region_id="cn-shanghai")
        request = CommonRequest()
        request.set_method("POST")
        request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
        request.set_version("2019-02-28")
        request.set_action_name("CreateToken")

        resp = client.do_action_with_exception(request)
        resp = json.loads(resp.decode())
        err_message = resp.get("ErrMsg")

        if err_message != "":
            raise BaseException(err_message)
        else:
            return resp.get("Token").get("Id")

    # 获取语音合成数据
    async def getTtsData_async(self, text, voice="Xiaoyun", volumn=50, speechRate=0, pitchRate=0):
        print(text)
        key = f"{text}_{voice}_{volumn}_{speechRate}_{pitchRate}"
        key_md5 = hashlib.md5(key.encode()).hexdigest()
        cacheDir = os.path.join(self.outputDir, "cache")
        if not os.path.isdir(cacheDir):
            os.mkdir(cacheDir)
        cache_file = os.path.join(cacheDir, key_md5)

        if os.path.isfile(cache_file):
            # print("cached")
            async with aiofile.async_open(cache_file, "rb") as file:
                return await file.read()
        else:
            # print("not cached")
            url = "https://nls-gateway-cn-beijing.aliyuncs.com/stream/v1/tts"
            headers = {
                "Content-Type": "application/json"
            }
            body = {
                "appkey": self.appKey,
                "text": text,
                "token": self.token,
                "format": "mp3",
                "voice": voice,
                "volumn": volumn,
                "speech_rate": speechRate,
                "pitch_rate": pitchRate,
            }
            print(body)
            resp = await requests_async.post(url, json=body, headers=headers)
            if resp.status_code == 200:
                data = resp.content
                async with aiofile.async_open(cache_file, "wb") as file:
                    await file.write(data)
                return data
            else:
                raise BaseException(resp.raise_for_status())

    # 合并音频文件
    async def combineDatas_async(self, datas, outputFile):
        output = None
        for data in datas:
            tmp = hashlib.md5(data).hexdigest() + ".mp3"
            async with aiofile.async_open(tmp, "wb") as file:
                await file.write(data)
            if output:
                output += AudioSegment.from_mp3(tmp)
            else:
                output = AudioSegment.from_mp3(tmp)
            os.remove(tmp)

        output.export(outputFile)
        

    # flag 0 听英语写汉语 1 听汉语写英语 2 随机
    async def genExams_async(self, outputDir, flag:ExamLx , count:int = 1):

        # region 准备输出目录
        outputDir = os.path.join(self.outputDir, outputDir)
        if os.path.isdir(outputDir):
            for file in os.listdir(outputDir):
                os.remove(os.path.join(outputDir, file))
        else:
            os.mkdir(outputDir)
        # endregion
        
        #region 拿到所有行
        
        lines = []

        with open(self.file, "r", encoding="utf-8") as file:
            # 去掉无用行
            def filterLines(line):
                if line:
                    return not line.startswith("#") and line != "\n"
                else:
                    return False
            # 取所有行
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
            lines = list(filter(filterLines, lines))

        #endregion

        index = 1
        answers = [f'英语测试答案 {outputDir} \n']
        
        #生成测试，返回答案
        async def gen_exam_async(index)->str:

            _lines = lines[:]
            # 打乱顺序
            random.shuffle(_lines)
            _lines = _lines[0:self.countPerExam]

            text = f"<speak bgm='http://nls.alicdn.com/bgm/2.wav' backgroundMusicVolumn='30' rate='-200' ><break time='2s' /><w>{self.student}</w>同学，你好，现在是听力测试时间。请你根据听到的中文或英文写出对应的翻译。每个词说两遍。<break time='1s' /></speak>"
            audios = [await self.getTtsData_async(text, "Aitong")]
            
            #测试答案
            _answers = [f"Exam {index} \n"]

            # 循环处理每个单词
            for i, line in enumerate(_lines):
                ds = list(filter(lambda x: x, re.split("[|]+", line)))[0:2]

                s = ['donna','luca']
                if flag == ExamLx.听汉语写英语 or (flag == ExamLx.随机 and random.randint(-10, 9) >= 0):
                    s = ['zhiyuan','zhida']
                    ds.reverse()

                text = f"<speak>{i + 1}<break time='1s' /></speak>"
                audios.append(await self.getTtsData_async(text, "Luca"))

                text = f"<speak>{ds[0]}<break time='2s' /></speak>"
                audios.append(await self.getTtsData_async(text, s[0]))

                text = f"<speak>{ds[0]}<break time='8s' /></speak>"
                audios.append(await self.getTtsData_async(text, s[1]))

                _answers.append(f'{i+1}. {" ".join(ds)} ')

            
            text = "本次测试结束"
            audios.append(await self.getTtsData(text, "Aitong"))

            # 合成语音
            self.combineDatas_async(audios, os.path.join(
                outputDir, f"Exam_{index}.mp3"))
            
            return ' '.join(_answers)
        
        
        answers.append(await asyncio.gather( [asyncio.create_task(gen_exam_async(i)) for i in range(count) ] )) 

        # 写入答案
        async with aiofile.async_open(os.path.join(outputDir, f"Answer.txt"), "w", encoding="utf-8") as file:
                await file.writelines(answers)

async def main_async():
    
    student = input('请输入学生姓名[0 翟静逸 1 翟绍祖]:')
    if student == '0':
        student = '翟静逸'
    elif student == '1':
        student = '翟绍祖'
    else:
        raise BaseException('学生无效')
    
    file = input("输入测试题库文件:")
    file = f'HearingExam/Dict/{file}.txt'
    if not os.path.isfile(file):
        raise BaseException(f'{file}不是有效的文件')

    examCount = input("需要生成的测试数量[5]:")
    if not examCount.isnumeric():
        examCount = 5
    else:
        examCount = max(1, int(examCount))
    countPerExam = input("每个测试的题目数[25]:")

    if not countPerExam.isnumeric():
        countPerExam = 25
    else:
        countPerExam = max(1, int(countPerExam))
    exam = HearingExam(student, file, countPerExam, "HearingExam")

    flag = input('请输入测试类型(0 听英文写汉语 1 听汉语写英文 2 随机 )[0]:')
    if not flag.isnumeric():
        flag = ExamLx(0)
    else:
        flag = ExamLx(int(flag))

    outputDir = f"{student}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{flag.name}"
    exam.genExams(outputDir, flag,examCount)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_async())
    loop.close()
