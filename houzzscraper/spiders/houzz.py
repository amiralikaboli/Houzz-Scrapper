import scrapy

from houzzscraper.items import HouzzProductItem


class HouzzSpider(scrapy.Spider):
    name = 'houzz'
    start_urls = [
        'https://www.houzz.com/products/beds',
        'https://www.houzz.com/products/chairs',
        'https://www.houzz.com/products/dining-tables',
        'https://www.houzz.com/products/sofas-and-sectionals',
    ]

    def start_requests(self):
        for page_number in range(5):
            for product_url in self.start_urls:
                page_product_url = f'{product_url}/p/{36 * page_number}'
                yield scrapy.Request(url=page_product_url, callback=self.parse_product_page)

    def parse_product_page(self, response: scrapy.http.Response):
        item_urls = response.css('.hz-product-card__link::attr(href)').getall()

        for item_url in item_urls:
            yield response.follow(item_url, callback=self.parse_item_page)

        # next_page_url = response.css('.hz-pagination-link--next::attr(href)').get()
        # if next_page_url is not None:
        #     next_page_url = response.urljoin(next_page_url)
        #     yield scrapy.Request(next_page_url, callback=self.parse_product_page)

    def parse_item_page(self, response: scrapy.http.Response):
        thumb_urls = response.css('.alt-images__thumb img::attr(src)').getall()
        first_image_url = response.css('.view-product-image-print::attr(src)').get()

        image_urls = generate_image_urls(thumb_urls, first_image_url)

        item = HouzzProductItem()
        item['url'] = response.url
        item['title'] = response.css('.view-product-title::text').get()
        item['keywords'] = response.css('.product-keywords__word::text').getall()
        item['images'] = image_urls[:2]

        yield item


def generate_image_urls(thumb_urls, first_image_url):
    if first_image_url is None:
        return []

    if len(thumb_urls) == 0:
        return first_image_url

    try:
        first_image_code = first_image_url.split('/')[-2].split('_')[0]
    except:
        return first_image_url

    image_urls = []
    for thumb_url in thumb_urls:
        try:
            thumb_code = thumb_url.split('/')[-1].split('_')[0]
            image_urls.append(first_image_url.replace(first_image_code, thumb_code))
        except:
            pass

    return image_urls
