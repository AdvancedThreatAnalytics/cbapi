#
# CARBON BLACK API
# Copyright, Carbon Black, Inc 2013
# technology-support@carbonblack.com
#

import requests
import urllib
import json
from requests.auth import HTTPDigestAuth

class CbApi(object):
    """ Python bindings for Carbon Black API 
    Example:

    import cbapi
    cb = cbapi.CbApi("http://cb.example.com", "admin", "pa$$w0rd")
    # get metadata for all svchost.exe's not from c:\\windows
    procs = cb.processes(r"process_name:svchost.exe -path:c:\\windows\\")  
    for proc in procs['results']:
        proc_detail = cb.process(proc['id'])
        print proc_detail['process']['start'], proc_detail['process']['hostname'], proc_detail['process']['path']
    """
    def __init__(self, server, ssl_verify=True, token=None):
        """ Requires:
                server -    URL to the Carbon Black server.  Usually the same as 
                            the web GUI.
                ssl_verify - verify server SSL certificate
                token - this is for CLI API interface
        """

        if not server.startswith("http"): 
            raise TypeError("Server must be URL: e.g, http://cb.example.com")

        self.server = server.rstrip("/")
        self.ssl_verify = ssl_verify
        self.token = token
        self.token_header = {'X-Auth-Token': self.token}

    def info(self):
        """ Provide high-level information about the Carbon Black Enterprise Server.

            **NOTE** This function is provided for convenience and may change in
                     future versions of the Carbon Black API

            Returns a python dictionary with the following field:
                - version - version of the Carbon Black Enterprise Server
        """
        r = requests.get("%s/api/info" % self.server, headers=self.token_header, verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from endpoint: %s" % (r.status_code))
        return json.loads(r.content)
    
    def process_search(self, query_string, start=0, rows=10, sort="last_update desc"):
        """ Search for processes.  Arguments: 

            query_string -      The Cb query string; this is the same string used in the 
                                "main search box" on the process search page.  "Contains text..."
                                See Cb Query Syntax for a description of options.

            start -             Defaulted to 0.  Will retrieve records starting at this offset.
            rows -              Defaulted to 10. Will retrieve this many rows. 
            sort -              Default to last_update desc.  Must include a field and a sort
                                order; results will be sorted by this param.

            Returns a python dictionary with the following primary fields:
                - results - a list of dictionaries describing each matching process
                - total_results - the total number of matches
                - elapsed - how long this search took
                - terms - a list of strings describing how the query was parsed
                - facets - a dictionary of the facet results for this saerch
        """

        # setup the object to be used as the JSON object sent as a payload
        # to the endpoint
        params = {
            'sort': sort, 
            'facet': ['true', 'true'], 
            'rows': rows, 
            'cb.urlver': ['1'], 
            'q': [query_string], 
            'start': start}

        # do a post request since the URL can get long
        # @note GET is also supported through the use of a query string
        r = requests.post("%s/api/v1/process" % self.server, headers=self.token_header,
                          data=json.dumps(params), verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from endpoint: %s" % (r.status_code))
        return r.json()

    def process_summary(self, id, segment):
        """ get the detailed metadata for a process.  Requires the 'id' field from a process
            search result, as well as a segement, also found from a process search result.
    
            Returns a python dictionary with the following primary fields:
                - process - metadata for this process
                - parent -  metadata for the parent process
                - children - a list of metadata structures for child processes
                - siblings - a list of metadata structures for sibling processes
        """
        r = requests.get("%s/api/v1/process/%s/%s" % (self.server, id, segment), headers=self.token_header, verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from endpoint: %s" % (r.status_code))
        return r.json()

    def process_events(self, id, segment):
        """ get all the events (filemods, regmods, etc) for a process.  Requires the 'id' and 'segment_id' fields
            from a process search result"""
        r = requests.get("%s/api/v1/process/%s/%s/event" % (self.server, id, segment), headers=self.token_header, verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from endpoint: %s" % (r.status_code))
        return r.json()

    def binary_search(self, query_string, start=0):
        """ Search for binaries.  Arguments: 

            query_string -      The Cb query string; this is the same string used in the 
                                "main search box" on the binary search page.  "Contains text..."
                                See Cb Query Syntax for a description of options.

            start -             Defaulted to 0.  Will retrieve records starting at this offset.
            rows -              Defaulted to 10. Will retrieve this many rows. 
            sort -              Default to last_update desc.  Must include a field and a sort
                                order; results will be sorted by this param.

            Returns a python dictionary with the following primary fields:
                - results - a list of dictionaries describing each matching binary
                - total_results - the total number of matches
                - elapsed - how long this search took
                - terms - a list of strings describing how the query was parsed
                - facets - a dictionary of the facet results for this saerch
        """
        args = {"cburlver": 1, 'start': start}
        if len(query_string) > 0:
            args['q'] = query_string

        query = urllib.urlencode(args)
        r = requests.get("%s/api/v1/binary?%s" % (self.server, query),
                             headers=self.token_header, verify=self.ssl_verify)
        print "%s/api/v1/binary?%s" % (self.server, query)
        if r.status_code != 200:
            raise Exception("Unexpected response from endpoint: %s" % (r.status_code))
        return r.json()

    def binary_summary(self, md5):
        """ get the metadata for a binary.  Requires the md5 of the binary.

            Returns a python dictionary with the binary metadata. """
        r = requests.get("%s/api/v1/binary/%s/summary" % (self.server, md5),
                             headers=self.token_header, verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from endpoint: %s" % (r.status_code))
        return r.json()

    def binary(self, md5hash):
        '''
        download binary based on md5hash
        '''

        r = requests.get("%s/api/v1/binary/%s" % (self.server, md5hash),
                         headers=self.token_header, verify=self.ssl_verify)

        if r.status_code != 200:
            raise Exception("Unexpected response from /api/v1/binary: %s" % (r.status_code))
        return r._content
        
    def sensors(self, query_parameters={}):
        '''
        get sensors, optionally specifying searchcriteria
        
        as of this writing, supported search criteria are:
          ip - any portion of an ip address
          hostname - any portion of a hostname, case sensitive

        returns a list of 0 or more matching sensors 
        '''

        url = "%s/api/v1/sensor?" % (self.server,)
        for query_parameter in query_parameters.keys():
            url += "%s=%s&" % (query_parameter, query_parameters[query_parameter])

        r = requests.get(url, headers=self.token_header, verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from /api/sensor: %s" % (r.status_code))
        
        return r.json()

    def sensor(self, sensor_id):
        '''
        get information describing a single sensor, as specified by sensor id
        '''

        url = "%s/api/v1/sensor/%d" % (self.server, sensor_id)
        r = requests.get(url, headers=self.token_header, verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception("Unexpected response from %s" % (url,))

        return r.json()

if __name__ == '__main__':

    import unittest
    import sys

    global cb

    class CbApiTestCase(unittest.TestCase):
        def test_info(self):
            cb.info()

        def test_sensors_plain(self):
            cb.sensors()

        def test_sensors_ip_query(self):
            cb.sensors({'ip':'255.255.255.255'})

        def test_sensors_hostname_query(self):
            cb.sensors({'hostname':'unlikely_host_name'})

        def test_binary_stuff(self):
            binaries = cb.binary_search("cmd.exe")
            for binary in binaries['results']:
                cb.binary_summary(binary['md5'])
                cb.binary(binary['md5'])

        def test_process_stuff(self):
            processes = cb.process_search("cmd.exe")
            for process in processes['results']:
                process_summary = cb.process_summary(process['id'], process['segment_id'])
                process_events = cb.process_events(process['id'], process['segment_id'])

    if 3 != len(sys.argv):
        print "usage   : python cbapi.py server_url api_token"
        print "example : python cbapi.py https://cb.my.org 3ab23b1bdhjj3jdjcjhh2kl\n"
        sys.exit(0)
   
    # instantiate a global CbApi object
    # all unit tests will use this object
    # 
    cb = CbApi(sys.argv[1], token=sys.argv[2])
   
    # remove the server url and api token arguments, as unittest
    # itself will try to interpret them
    #
    del sys.argv[2]
    del sys.argv[1]

    # run the unit tests
    #
    unittest.main()
