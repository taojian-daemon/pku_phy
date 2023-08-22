#coding: utf8
import requests
from lxml import etree
import re
import json

url = f"https://www.phy.pku.edu.cn/system/resource/tsites/portal/queryteacher.jsp?collegeid=1520&isshowpage=false&postdutyid=0&postdutyname=%E6%95%99%E7%A0%94%E4%BA%BA%E5%91%98&facultyid=&disciplineid=0&rankcode=0&jobtypecode=JOB_TYPE_ID927559%2CJOB_TYPE_ID024588%2CJOB_TYPE_ID056883%2CJOB_TYPE_ID959332%2CJOB_TYPE_ID091962%2CJOB_TYPE_ID945233%2C01114%2CJOB_TYPE_ID280117%2C01110%2C00319%2C01106%2C01120%2C01112%2C01119%2C00318%2C00305%2C00315%2C01113%2C01108%2C01103%2C01102%2C00311%2C00303%2C01104%2C00107%2CJOB_TYPE_ID069686%2CJOB_TYPE_ID011361%2C&enrollid=0&pageindex=1&pagesize=10&login=false&profilelen=10&honorid=0&pinyin=&teacherName=&searchDirection=&viewmode=10&viewOwner=1539754034&viewid=275976&siteOwner=1539754034&viewUniqueId=u12&showlang=zh_CN&actiontype="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    #"Cookie": 'Hm_lvt_c7896bb34c3be32ea17322b5412545c0=1692610598; Hm_lpvt_c7896bb34c3be32ea17322b5412545c0=1692671043; JSESSIONID=94959DB81001F795D873ABEF05AA8B93'
}
response = requests.get(url,headers=headers)
#print(response.json())
total = response.json()["totalpage"] + 1

data_list = []
for pageindex in range(1,total):
    print("now_page:", pageindex)
    url = f"https://www.phy.pku.edu.cn/system/resource/tsites/portal/queryteacher.jsp?collegeid=1520&isshowpage=false&postdutyid=0&postdutyname=%E6%95%99%E7%A0%94%E4%BA%BA%E5%91%98&facultyid=&disciplineid=0&rankcode=0&jobtypecode=JOB_TYPE_ID927559%2CJOB_TYPE_ID024588%2CJOB_TYPE_ID056883%2CJOB_TYPE_ID959332%2CJOB_TYPE_ID091962%2CJOB_TYPE_ID945233%2C01114%2CJOB_TYPE_ID280117%2C01110%2C00319%2C01106%2C01120%2C01112%2C01119%2C00318%2C00305%2C00315%2C01113%2C01108%2C01103%2C01102%2C00311%2C00303%2C01104%2C00107%2CJOB_TYPE_ID069686%2CJOB_TYPE_ID011361%2C&enrollid=0&pageindex={pageindex}&pagesize=10&login=false&profilelen=10&honorid=0&pinyin=&teacherName=&searchDirection=&viewmode=10&viewOwner=1539754034&viewid=275976&siteOwner=1539754034&viewUniqueId=u12&showlang=zh_CN&actiontype="
    response = requests.get(url,headers=headers)
    #print(response.json())
    data_json = response.json()
    teacherData = data_json["teacherData"]

    for each in teacherData:
        each_url = each['url']
        print("now_url:",each_url)
        t_data = {}
        t_data['姓名'] = each['name']
        t_data['邮箱'] = each['email']
        t_data['职称'] = each['prorank']
        t_data['所在单位'] = each['unit']
        t_data['出生日期'] = each['birthday']
        t_data['联系电话'] = each['contact']
        t_data['办公地点'] = each['officeLocation']

        try:
            html = requests.get(each_url,headers=headers,timeout=5).content.decode('utf8')
            #print(html)
            selector = etree.HTML(html)


            more_url = 'https://faculty.pku.edu.cn/'+selector.xpath('/html/body/div[2]/div[3]/div[2]/div[1]/div[2]/div/div[2]/a/@href')[0]
            more_html = requests.get(more_url, headers=headers).content.decode('utf8')
            #print(more_html)
            more_sel = etree.HTML(more_html)
            t_data['简介'] = ''
            for p in more_sel.xpath('//*[@id="l"]//p'):
                ptext = p.xpath('string(.)')
                t_data['简介'] = t_data['简介'] + ptext
            t_data['教育经历'] = ''
            for div in selector.xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[1]/div/div[2]//div'):
                if div.xpath('./div[1]'):
                    t_data['教育经历'] = t_data['教育经历'] + div.xpath('./div[1]/span/text()')[0] + '\n'
                if div.xpath('./div[2]'):
                    for span in div.xpath('./div[2]//span'):
                        t_data['教育经历'] = t_data['教育经历'] + span.xpath('string(.)') + ' | '
            t_data['工作经历'] = ''
            for div in selector.xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[2]/div/div[2]//div'):
                if div.xpath('./div[1]'):
                    t_data['工作经历'] = t_data['工作经历'] + div.xpath('./div[1]/span/text()')[0] + '\n'
                if div.xpath('./div[2]'):
                    for span in div.xpath('./div[2]//span'):
                        t_data['工作经历'] = t_data['工作经历'] + span.xpath('string(.)') + ' | '

            t_data['基本信息'] = ''
            if selector.xpath('//*[@id="tabs"]/div[2]/div[1]/div/a/@href'):
                info_url = 'https://faculty.pku.edu.cn/'+selector.xpath('//*[@id="tabs"]/div[2]/div[1]/div/a[1]/@href')[0]
                info_html = requests.get(info_url, headers=headers).content
                #print(info_html)
                into_sel = etree.HTML(info_html)
                for div in into_sel.xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[2]/div/div//div'):
                    for span in div.xpath('.//span'):
                        t_data['基本信息'] = t_data['基本信息'] + str(span.xpath('string(.)'))
                    t_data['基本信息'] = t_data['基本信息'] + '\n'

            t_data['研究方向'] = ''
            if len(selector.xpath('//*[@id="tabs"]/div[2]/div[2]/div//a')) > 1:
                research_url = 'https://faculty.pku.edu.cn/' + selector.xpath('//*[@id="tabs"]/div[2]/div[2]/div/a[1]/@href')[0]
                research_html = requests.get(research_url, headers=headers).content
                #print(info_html)
                research_sel = etree.HTML(research_html)
                for a in research_sel.xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[2]//a'):
                    t_data['研究方向'] = t_data['研究方向'] + str(a.xpath('./text()')[0]) + '\n'
            else:
                for a in selector.xpath('//*[@id="tabs"]/div[2]/div[2]/div//a'):
                    t_data['研究方向'] = t_data['研究方向'] + str(a.xpath('./text()')[0]) + '\n'

            #print(t_data)

        except:
            print("pass")
        data_list.append(t_data)
        #break
    #break
#print(data_list)
with open("data.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(data_list, indent=4, ensure_ascii=False))
