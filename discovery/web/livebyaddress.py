#!/usr/bin/env python
#
#   hostmap
#
#   Author:
#    Alessandro `jekil` Tanasi <alessandro@tanasi.it>
#
#   License:
#
#    This file is part of hostmap.
#
#    hostmap is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    hostmap is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with hostmap.  If not, see <http://www.gnu.org/licenses/>.


import re
from urlparse import urlparse
from twisted.web import client
from lib.output.logger import log


class livebyaddress:
    """ 
    Check against microsoft Live
    @author: Alessandro Tanasi
    @license: GNU Public License version 3
    @contact: alessandro@tanasi.it
    @bug: This get only the first 10 pages of search results
    """


    def require(self):
        """
        Sets plugin requirements
        """
        
        # Possible values are:
        # ip
        # domain
        # nameserver
        # hostname
        return "ip"



    def run(self, hd, ip):
        """
        Query Microsoft Live! using dork ip: to get a list of domains
        """        
        self.job = "%s-%s" % (__name__, ip)
        hd.job(self.job, "starting")
        
        # Fetching only the first ten pages thanks to the strange behaviour of Live
        # that prevent me to get the exact number of pages to fetch.
        # Number of page, in ten to ten format (ex. 1, 11, 21...)
        first = 1
        self.runners = 10
        while first < 102:
            url = "http://search.msn.com/results.aspx?q=ip:%s&first=%s" % (ip, first)
            
            # Search
            query = client.getPage(url)
            query.addCallback(self.__callSuccess, hd)
            query.addErrback(self.__callFailure, hd)
            
            first = first + 10
        
        hd.job(self.job, "waiting")
    

    def __callFailure(self, failure, hd):
        """
        If a live search run fails
        """
        self.runners = self.runners - 1
        if self.runners == 0 :
            hd.job(self.job, "failure")


    def __callSuccess(self, success, hd):
        """
        If a live search run success
        """
        # Regexp to catch fqdn
        regexp = "<li><h3><a href=\"(.*?)\" "
        # Cast object, paranoid mode
        page = str(success)
        # Grep
        results = re.findall(regexp, page, re.I | re.M)
        
       # Add new found hosts
        for host in set(results):
            host = urlparse(host).hostname
            hd.notifyHost(host)
            log.debug("Plugin %s added result: %s" % (__name__, host))
        
        self.runners = self.runners - 1
        if self.runners == 0 :
            hd.job(self.job, "done")
