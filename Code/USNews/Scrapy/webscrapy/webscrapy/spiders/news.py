import scrapy
import pandas as pd
import re
from scrapy.crawler import CrawlerProcess
class ImdbSpider(scrapy.Spider):
    name = "news"
    def start_requests(self):
        # count=0
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
        }
        for url in range(1,21):
            # print(count)
            count+=1
            yield scrapy.Request(url='https://www.usnews.com/best-graduate-schools/api/search?format=json&program=top-engineering-schools&specialty=eng&_page='+str(url), headers = HEADERS, callback=self.parse)

    def parse(self, response):
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
        }
        data1 = response.json()
        print(data1)
        NAME = data1['data']['items']
        for col in range(len(data1['data']['items'])):
            yield {
                    "title": NAME[col]['name']
                }
            yield scrapy.Request(url=NAME[col]['url'], headers = HEADERS, callback=self.parse1)
    def parse1(self, response):
        print(1)
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
        }
        output = pd.DataFrame()
        main_div = response.css('div.QuadForms__SlateFormOverride-sc-16t3xqe-0.eRjJyc')
        
        header = main_div[0].css('div.HeadingBox__HeadingContainer-sc-3hze40-0.ehwbfA')[0]
        
        title = header.css('div.Villain__TitleContainer-sc-1y12ps5-6 h1.Heading-sc-1w5xk2o-0')

        ranking_para = header.css('p.ProfileHeading__RankingParagraph-sc-1n3m2r3-4')
        
        content = main_div[0].css('div.Content-sc-837ada-0.kkKJUL.content')

       
        LD = ""
        for div in content.css('div.Raw-slyvem-0.gLcszj'):
            for p in div.css('p'):
                LD = LD + p.css('::text').get().strip('\n\t')

        dicto={}
        dicto["Institute"] = title.css('::text').get()+title.css('span::text').get()
        dicto["Ranking"] = ranking_para.css('span span::text').get()
        dicto["Location"] = ranking_para.css('span.Hide-kg09cx-0.fjAwZI span.ProfileHeading__LocationSpan-sc-1n3m2r3-2.itOQkU::text').get()[2:]
        dicto["Short Description"] = content.css('p.Paragraph-sc-1iyax29-0.klVaTa::text').get()
        dicto["Long Description"] = LD

        # print("Location", dicto["Location"])
        for div in content.css('div.mb6'):
            for sec in div.css('section.SchoolData__NonPremiumAccordionSection-sc-6qayxq-5.eAkMfq'):
                for dt in sec.css('div.DataField__DataFieldWrapper-qjl95u-4.dNeDrd.t-font-fam.mb4'):
                    div_element = dt.css('div.DataField__DataWrapper-qjl95u-7.gPoMCR div.DataField__Data-qjl95u-2.cpvibk')
                    if len(div_element):
                        email_element = div_element.css('div.SchoolData__LowercasedBox-sc-6qayxq-3.bfuLbU')
                        if len(email_element):
                            ans = email_element.css('::text').get()
                        elif len(div_element.css('a')):
                            ans = div_element.css('a').attrib['href']
                        else:   
                            div_html = div_element.extract_first()
                            div_text = re.search(r'<!-- -->(.+?)</div>', div_html).group(1)
                            ans = div_text
                    dicto[dt.css('div.DataField__Title-qjl95u-1.cZXvCQ span::text').get()] = ans
                male_female = 0
                for mf in sec.css('div.BarChartStacked__Legend-wgxhoq-4.iLdLaQ div'):
                    if male_female<2:
                        element = mf.css('::text').get()
                        dicto[element] = mf.css('b::text').get()
                        male_female +=1
                    else:
                        break

        output = output.append(dicto, ignore_index=True)
        output.to_csv('output_final.csv', mode='a', index=False,header=False)   
                    