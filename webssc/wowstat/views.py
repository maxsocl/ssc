# -*- coding: utf-8 -*-

import httplib2
import ConfigParser
import xml.etree.ElementTree as etree
from django.template.response import TemplateResponse


config = ConfigParser.RawConfigParser()
config.read('/home/maksim/PycharmProjects/ssc/webssc/conf.ini')
login = config.get('wowza', 'login')
password = config.get('wowza', 'password')

translate = {
    'veltonMedium46.stream': 'Поле Металлист. Низкое качество',
    'veltonQuality46.stream': 'Поле Металлист. Высокое качество',
    'veltonMedium47.stream': 'Детская площадка. Низкое качество',
    'veltonQuality47.stream': 'Детская площадка. Высокое качество',
    'veltonMedium48.stream': 'Вид на Металлист. Низкое качество',
    'veltonQuality48.stream': 'Вид на Металлист. Высокое качество',
    'veltonMedium49.stream': 'Пл. свободы. Низкое качество',
    'veltonQuality49.stream': 'Пл. свободы. Высокое качество',
    'veltonMedium50.stream': 'Донецк. Низкое качество',
    'veltonQuality50.stream': 'Донецк. Высокое качество',
    'veltonMedium51.stream': 'Днепропетровск. Низкое качество',
    'veltonQuality51.stream': 'Днепропетровск. Высокое качество',
    'veltonMedium52.stream': 'Одесса. Низкое качество',
    'veltonQuality52.stream': 'Одесса. Высокое качество',
    'veltonMedium53.stream': 'Полтава. Низкое качество',
    'veltonQuality53.stream': 'Полтава. Высокое качество',
    'veltonMedium54.stream': 'Зеркальная струя. Низкое качество',
    'veltonQuality54.stream': 'Зеркальная струя. Высокое качество',
    'veltonMedium55.stream': 'Киев. Низкое качество',
    'veltonQuality55.stream': 'Киев. Высокое качество',
}


def wowza(request):
    h = httplib2.Http('/home/maksim/PycharmProjects/ssc/webssc/wowstat/.cache')
    h.add_credentials(login, password)

    with open('/home/maksim/PycharmProjects/ssc/webssc/wowstat/.cache/xml', mode='w') as a_file:
        a_file.write(h.request('http://85.90.192.233:8086/connectioncounts/')[1].decode('utf-8'))

    tree = etree.parse('/home/maksim/PycharmProjects/ssc/webssc/wowstat/.cache/xml')
    root = tree.getroot()

    detail = []
    for child in root.find('VHost').find('Application').find('ApplicationInstance').findall('Stream'):
        detail.append([child.findall('Name')[0].text, child.findall('SessionsTotal')[0].text])

    for i in detail:  # change Wowza stream name (name.stream) to human readable
        if i[0] in translate:
            i[0] = translate[i[0]]

    #if day == ' ': day = str(time.localtime().tm_mday)
    #if mon == ' ': mon = str(time.localtime().tm_mon)
    #if year == ' ': year = str(time.localtime().tm_year)
    #test = []
    #with open('/home/maksim/scripts/wowza/'+day+'.'+mon+'.'+year+'-wowza.log', mode='r') as a_file:
    #    list = a_file.read().split('|')
    #    for i in list:
    #      tmp = i.split('-')
    #      test.append(tmp)
    #    test.pop()
    #title = day+'.'+mon+'.'+year

    #conn_string = "host='localhost' port='19992' dbname='wowza' user='postgres' password='kiwi_mx_strm13Dax'"
    #conn = psycopg2.connect(conn_string)

    #cur = conn.cursor()
    #cur.execute('select * from summary order by -id limit 288;')

    #summary = []
    #for i in reversed(cur.fetchall()):
    #    summary.append([i[1], i[2]])

    #conn.commit()
    #cur.close()
    #conn.close()

    return TemplateResponse(request, 'wowstat/wowza.html', {'detail': detail})