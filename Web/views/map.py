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


def countriesMap(request):
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
        try:
            ip = IPAddress(c['remote_host'])
            if ip.version == 4:
                cc = gi.country_code_by_addr(c['remote_host'])
            elif ip.version == 6:
                cc = gi6.country_code_by_addr(c['remote_host'])

            if cc != "":
                try:
                    data[cc] += 1
                except:
                    data[cc] = 1

        except:
            pass

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


def attackersMap(request):
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
        try:
            ip = IPAddress(c['remote_host'])
            try:
                counts[c['remote_host']] += 1
            except:
                counts[c['remote_host']] = 1
        except:
            pass

    for c in counts:
        try:
            ip = IPAddress(c)
            if ip.version == 4:
                cc = gic.record_by_addr(c)
            elif ip.version == 6:
                cc = gic6.record_by_addr(c)

            if cc:
                var = var + LAT_PATTERN.format(
                    cc['latitude'],
                    cc['longitude'],
                    counts[c],
                    str(c)
                )
        except:
            pass

    var = var.rstrip(',') + "];"
    return render_to_response(
        'maps/attackers.html',
        {
            'attackers': var
        },
        context_instance=RequestContext(request)
    )

# vim: set expandtab:ts=4
