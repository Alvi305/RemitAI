import asyncio
from wise.wise_spider import WiseSpider

async def main():
    spider = WiseSpider()
    data = spider.scrape()
    print(data)
    spider.close()

if __name__ == "__main__":
    asyncio.run(main())