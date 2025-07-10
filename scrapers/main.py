import asyncio
import re
from wise.wise_spider import WiseSpider
from xoom.xoom_spider import XoomSpider

def extract_total_fee(fees_string: str) -> float:
    match = re.search(r'Total: (\d+\.\d{2}) USD', fees_string)
    return float(match.group(1)) if match else float('inf')


async def main():
    global sorted_fees
    spiders = [WiseSpider(), XoomSpider()]
    scraped_data_hashmap = {}
    for spider in spiders:
        data = spider.scrape()

        # Extract total fee and store in hashmap
        total_fee = extract_total_fee(data['transaction_fees'])
        scraped_data_hashmap[total_fee] = data

        # Sort hashmap by fees (keys)
        sorted_fees = sorted(scraped_data_hashmap.keys())
        spider.close()

    for fees in sorted_fees:
        print(scraped_data_hashmap[fees])


if __name__ == "__main__":
    asyncio.run(main())