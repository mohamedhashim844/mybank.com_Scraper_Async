import httpx
from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup
import pandas as pd


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

def start_urls():
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
    timeout = httpx.Timeout(10.0)
    r = httpx.get(url,headers=headers,timeout=timeout,follow_redirects=True)
    html = HTMLParser(r.content)
    all_links = []
    for links in html.css('.readmore'):
        link = links.css_first('a').attributes['href']
        all_links.append(link)
    for pages in html.css('.inactive.cafe_pagination-item'):
        page = pages.css_first('a').attributes['href']
        r_2 = httpx.get(page,headers=headers,timeout=timeout,follow_redirects=True)
        html_2 = HTMLParser(r_2.content)
        for links_2 in html_2.css('.readmore'):
            link2 = links_2.css_first('a').attributes['href']
            all_links.append(link2)
    return all_links
def parse(url):
    timeout = httpx.Timeout(10.0)
    r = httpx.get(url,headers=headers,timeout=timeout,follow_redirects=True)
    html = HTMLParser(r.content)
    title = None         # initialize the variable with a default value before the loop
    available = None     # because it will give me UnboudlocalErrror
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
    print(product)
    return product

def save_to_csv(output):
    df = pd.DataFrame(output)
    df.to_csv('mybank.csv',index=False)

def main():
    last_output = []
    first_urls = start_urls()
    for urls in first_urls:
        out = pagination(urls)
        for out_1 in out:
            data = parse(out_1)
            last_output.append(data)
            save_to_csv(last_output)
    save_to_csv(last_output)
if __name__ == '__main__':
    main()