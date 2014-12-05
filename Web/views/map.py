import re
import time
import datetime
import sys
import os

try:
    import pygeoip
except ImportError:
    print "Install pygeoip"
    print "\tpip install pygeoip"
    pass

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import render_to_response

from Web.models.connection import Connection

reload(sys)
sys.setdefaultencoding('utf-8')

gi = pygeoip.GeoIP(settings.GEOIP_COUNTRY_IPV4, pygeoip.MEMORY_CACHE)
gi6 = pygeoip.GeoIP(settings.GEOIP_COUNTRY_IPV6, pygeoip.MEMORY_CACHE)
gic = pygeoip.GeoIP(settings.GEOIP_CITY_IPV4, pygeoip.STANDARD)
gic6 = pygeoip.GeoIP(settings.GEOIP_CITY_IPV6, pygeoip.STANDARD)

LAT_PATTERN = "{{latLng:[{:-f},{:-f}], count:'{}', host:'{}'}},"
COUNTRY_PATTERN = '"{0}":{1},'

# Regular expressions
IPV6_PATTERN = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
IPV4_PATTERN = "((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
reipv4 = re.compile(IPV4_PATTERN)
reipv6 = re.compile(IPV6_PATTERN)

def countriesMap(request, version):
    date_now = datetime.date.today() - datetime.timedelta(days=settings.RESULTS_DAYS)
    conn = Connection.objects.filter(
        connection_timestamp__gt=time.mktime(
            date_now.timetuple()
        )
    ).values(
        'remote_host'
    )
    data = {}
    for c in conn:
        if (version == None or version == '4') and (reipv4.match(c['remote_host']) is not None):
            cc = gi.country_code_by_addr(c['remote_host'])
        elif (version == None or version == '6') and (reipv6.match(c['remote_host']) is not None):
            cc = gi6.country_code_by_addr(c['remote_host'])
        else:
            cc = ""

        if cc != "":
            try:
                data[cc] += 1
            except:
                data[cc] = 1

    var = "var gdpData = {"
    for country in data:
        var = var + COUNTRY_PATTERN.format(
            country,
            str(data[country])
        )
    var = var.rstrip(',') + "};"
    return render_to_response(
        'maps/countries.html',
        {
            'cc': var
        },
        context_instance=RequestContext(request)
    )


def attackersMap(request, version):
    date_now = datetime.date.today() - datetime.timedelta(days=settings.RESULTS_DAYS)
    conn = Connection.objects.filter(
        connection_timestamp__gt=time.mktime(
            date_now.timetuple()
        )
    ).values(
        'remote_host'
    )
    var = "var gdpData = ["
    counts = {}
    for c in conn:
        if ((version == None or version == '4') and reipv4.match(c['remote_host']) is not None) or ((version == None or version == '6') and reipv6.match(c['remote_host']) is not None):
            try:
                counts[c['remote_host']] += 1
            except:
                counts[c['remote_host']] = 1

    for c in counts:
        if (reipv4.match(c) is not None):
            cc = gic.record_by_addr(c)
        elif (reipv6.match(c) is not None):
            cc = gic6.record_by_addr(c)
        else:
            cc = ""

        if cc:
            var = var + LAT_PATTERN.format(
                cc['latitude'],
                cc['longitude'],
                counts[c],
                str(c)
            )

    var = var.rstrip(',') + "];"
    return render_to_response(
        'maps/attackers.html',
        {
            'attackers': var
        },
        context_instance=RequestContext(request)
    )

# vim: set expandtab:ts=4
