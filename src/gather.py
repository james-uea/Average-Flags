import os
import aiohttp
import aiofiles
import asyncio
from aiohttp import ClientSession, TCPConnector
from asyncio import Semaphore

API_URL = 'https://api.github.com/repos/pronouns/pride-flags-png/contents/flags'
DEST_DIR = 'flags'
MAX_CONCURRENT_REQUESTS = 5
MAX_RETRIES = 3
RETRY_DELAY = 1

async def download_file(session, url, dest, semaphore):
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with aiofiles.open(dest, 'wb') as f:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                await f.write(chunk)
                        print(f'Successfully downloaded {dest}')
                        return
                    elif response.status == 403:
                        print(f'Rate limit exceeded. Waiting before retry...')
                        await asyncio.sleep(60)  # Wait for 60 seconds before retrying
                    else:
                        print(f'Failed to download {url}. Status: {response.status}')
            except aiohttp.ClientError as e:
                print(f'Error downloading {url}: {str(e)}')
            
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f'Failed to download {url} after {MAX_RETRIES} attempts')

async def main():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)
    connector = TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
    
    async with ClientSession(connector=connector) as session:
        try:
            async with session.get(API_URL) as response:
                if response.status == 200:
                    contents = await response.json()
                    tasks = []
                    for item in contents:
                        if item['type'] == 'file':
                            file_url = item['download_url']
                            file_name = os.path.join(DEST_DIR, item['name'])
                            tasks.append(download_file(session, file_url, file_name, semaphore))
                    await asyncio.gather(*tasks)
                else:
                    print(f'Failed to fetch contents of the flags folder. Status code: {response.status}')
        except aiohttp.ClientError as e:
            print(f'Error fetching contents: {str(e)}')

if __name__ == '__main__':
    asyncio.run(main())