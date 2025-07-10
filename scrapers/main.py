import asyncio
import re
import threading

from wise.wise_spider import WiseSpider
from xoom.xoom_spider import XoomSpider

def extract_total_fee(fees_string: str) -> float:
    if not isinstance(fees_string, str):
        return float('inf')
    match = re.search(r'Total: (\d+\.\d{2})', fees_string)
    return float(match.group(1)) if match else float('inf')

def run_spider(spider, results,lock):
    try:
        data = spider.scrape()
        if data:
            total_fee = extract_total_fee(data['transaction_fees'])
            with lock:
                results[total_fee] = data
    except Exception as e:
        print(f"Error in {spider.__class__.__name__}: {str(e)}")
    finally:
        spider.close()

async def main():
    global sorted_fees
    spiders = [WiseSpider(), XoomSpider()]
    scraped_data_hashmap = {}
    lock = threading.Lock()
    threads = []

    # Start a thread for each spider
    for spider in spiders:
        thread = threading.Thread(target=run_spider, args=(spider, scraped_data_hashmap, lock))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Sort and print results by fees
    sorted_fees = sorted(scraped_data_hashmap.keys())
    for fee in sorted_fees:
        print(scraped_data_hashmap[fee])



if __name__ == "__main__":
    asyncio.run(main())