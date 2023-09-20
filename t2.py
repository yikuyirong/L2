

import requests_async
import asyncio
import aiohttp

async def getToken_async():
    pass

async def getData_async():
            url = "https://www.baidu.com"
            headers = {
                "Content-Type": "application/json"
            }
            body = {
                "data":"abc"
            }
            print(body)

            #resp = await requests_async.post(url,  json=body, headers=headers)
            
            # resp = await requests_async.get(url)
            
            async with aiohttp.ClientSession() as client:
                resp = await client.get(url)
            
                print(resp.content) 
    
    

async def main_async():
    await getData_async()

if __name__ == '__main__':
    asyncio.run(main_async())
