import random


def getRandEquation():

    chufa_count = 0

    while True:
        x = random.randint(2, 99)
        y = random.randint(10, 999)
        z = random.randint(1, x - 1)

        if random.randint(1,2) == 1: #生成乘法算式
            yield (f"{y}×{x}=", f"{x*y}")

        else: #生成除法算式
            x = random.randint(2,20)
            if random.randint(1,2) == 1: #有余数
                result = x * y + z
                yield (f"{result}÷{x}=", f"{y}..{z}" )
            else:
                result = x * y
                yield (f"{result}÷{x}=", y)
            
            

def getEnglishTests():

    while(True):
        words = []
        for i in range(0,random.randint(4,20)):
            words.append(''.zfill(random.randint(4, 10)))

        yield (' '.join(words),' '.join(words))
        
def getShiCiTest():
    
    shicis = []
    with open('./ShiCiExam/Dicts/source.txt',encoding='utf-8') as file:
        shicis = file.readlines()
        
        

    shicis = list(filter(lambda s: not s.startswith('#'),shicis))

    random.shuffle(shicis)
    
    index = 0
    
    while True:
        
        shici = shicis[index % len(shicis)]        
        cs = shici.split('|')
        index = index + 1
        yield(f'[{cs[0]}]{cs[1]}',f'{cs[0]}{cs[1]}{cs[2]}{cs[3]}\n{cs[4]}')
    

if __name__ == '__main__':
    # g = getRandEquation()
    # g = getEnglishTests()
    g = getShiCiTest()
    
    for x in range(10):
        print(next(g))
