import httpx
from selectolax.parser import HTMLParser
import asyncio
import pandas as pd


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

def start_urls():
    # this function parse the first list of links that i need to parse information from
    url = 'https://mytreats.maybank.com/cardpromotions/malaysia/retail-listing/'
    timeout = httpx.Timeout(10.0)
    r = httpx.get(url,headers=headers,timeout=timeout)
    html = HTMLParser(r.content)
    start_links = []
    for links in html.css('section.elementor-element.elementor-element-35ad13c div.elementor-col-14'):
        link = links.css_first('div.elementor-col-14').attributes['data-column-clickable']
        start_links.append(link)
    return start_links

def pagination(url):
    # this function deal parsing first page links and dealing with pagination
    r =  httpx.get(url,headers=headers,follow_redirects=True,timeout=50)
    html = HTMLParser(r.content)
    all_links = []
    for links in html.css('.readmore'):
        link = links.css_first('a').attributes['href']
        all_links.append(link)
    for page_number in html.css('.inactive.cafe_pagination-item'):
        page = page_number.css_first('a').attributes['href']
        r_2 =  httpx.get(page,headers=headers,follow_redirects=True,timeout=50)
        html_2 = HTMLParser(r_2.content)
        for links_2 in html_2.css('.readmore'):
            link_2 = links_2.css_first('a').attributes['href']
            all_links.append(link_2)
    return all_links
    
async def parse(url):
    # this function take all urls and parse the information from it 
    async with httpx.AsyncClient() as clinet :
        r = await clinet.get(url,headers=headers,timeout=50,follow_redirects=True)
        html = HTMLParser(r.content)
        title = None         # initialize the variable with a default value before the loop
        available = None     # to avoid UnboudlocalErrror
        promotion = None
        terms_and_conditions = None
        link = url
        for info in html.css('div[data-elementor-type="single"] section:nth-of-type(3)'):
            try:
                title = info.css_first('h1.elementor-heading-title.elementor-size-default').text()
                available = info.css_first('div.elementor-text-editor.elementor-clearfix').text()
                p_selector = info.css('[data-element_type="widget"] div.elementor-text-editor.elementor-clearfix p')
                if p_selector:
                    for p in p_selector:
                        promotion = p.text().strip()
                else:
                    for li in info.css('[data-element_type="widget"] div.elementor-text-editor.elementor-clearfix ul li'):
                        promotion = li.text().strip()

                for terms in html.css('div[data-elementor-type="single"] section:nth-of-type(4)'):
                        p_selector = terms.css('[data-element_type="widget"] div.elementor-text-editor.elementor-clearfix p')
                        if p_selector:
                            for p in p_selector:
                                terms_and_conditions = p.text().replace('\n','').strip()
                        else:
                            for li in info.css('[data-element_type="widget"] div.elementor-text-editor.elementor-clearfix ul'):
                                terms_and_conditions = li.text().replace('\n','').strip()
            except AttributeError:
                return None
        product = {
            'title' : title,
            'available': available,
            'promotion': promotion,
            'terms_and_conditions': terms_and_conditions,
            'link': link
        }
        return product

def save_to_csv(output):
    # this function take the output of the tasks and save it to csv
    df = pd.DataFrame(output)
    df.to_csv('mybank_asyncio.csv',index=False)

async def main():
    tasks = []
    first_urls = start_urls()
    for urls in first_urls:
        all_urls = pagination(urls)
        print(all_urls)
        for url in all_urls:
            tasks.append(asyncio.create_task(parse(url)))
        info_output = await asyncio.gather(*tasks)
        print(info_output)
    save_to_csv(info_output)

if __name__ == '__main__':
    asyncio.run(main())

