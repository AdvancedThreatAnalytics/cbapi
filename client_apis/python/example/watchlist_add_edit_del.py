#!/usr/bin/env python
#
#The MIT License (MIT)
#
# Copyright (c) 2015 Bit9 + Carbon Black
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# -----------------------------------------------------------------------------
#  <Short Description>
#
#  <Long Description>
#
#  last updated 2015-06-28 by Ben Johnson bjohnson@bit9.com
#

import sys
import optparse
import cbapi

def build_cli_parser():
    parser = optparse.OptionParser(usage="%prog [options]", description="Add, Edit, and Delete a Watchlist")

    # for each supported output type, add an option
    #
    parser.add_option("-c", "--cburl", action="store", default=None, dest="url",
                      help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_option("-a", "--apitoken", action="store", default=None, dest="token",
                      help="API Token for Carbon Black server")
    parser.add_option("-n", "--no-ssl-verify", action="store_false", default=True, dest="ssl_verify",
                      help="Do not verify server SSL certificate.")
    return parser

def watchlist_output(watchlist):
    '''
    output information about a watchlist
    '''

    # output the details about the watchlist
    #
    print '\n'
    print '    %-20s | %s' % ('field', 'value')
    print '    %-20s + %s' % ('-' * 20, '-' * 60)
    print '    %-20s | %s' % ('id', watchlist['id'])
    print '    %-20s | %s' % ('name', watchlist['name'])
    print '    %-20s | %s' % ('date_added', watchlist['date_added'])
    print '    %-20s | %s' % ('last_hit', watchlist['last_hit'])
    print '    %-20s | %s' % ('last_hit_count', watchlist['last_hit_count'])
    print '    %-20s | %s' % ('search_query', watchlist['search_query'])
    print '\n'

def main(argv):
    parser = build_cli_parser()
    opts, args = parser.parse_args(argv)
    if not opts.url or not opts.token:
        print "Missing required param; run with --help for usage"
        sys.exit(-1)

    # build a cbapi object
    #
    cb = cbapi.CbApi(opts.url, token=opts.token, ssl_verify=opts.ssl_verify)

    # add a watchlist
    # for the purposes of this test script, hardcode the watchlist type, name, and query string
    #
    print "-> Adding watchlist..."
    watchlist = cb.watchlist_add(
        'events',
        'test watchlist',
        'process_name:notepad.exe')
    print "-> Watchlist added [id=%s]" % (watchlist['id'])

    # get record describing this watchlist  
    #
    print "-> Querying for watchlist information..."
    watchlist = cb.watchlist(watchlist['id'])
    print "-> Watchlist queried; details:" 
    watchlist_output(watchlist)

    # edit the search query of the just-added watchlist
    #
    print "-> Modifying the watchlist query..."
    watchlist['search_query'] = 'process_name:calc.exe'
    cb.watchlist_modify(watchlist['id'], watchlist)
    print "-> Watchlist modified" 

    # get record describing this watchlist  
    #
    print "-> Querying for watchlist information..."
    watchlist = cb.watchlist(watchlist['id'])
    print "-> Watchlist queried; details:" 
    watchlist_output(watchlist)
 
    # delete the just-added watchlist
    #
    print "-> Deleting Watchlist..."
    cb.watchlist_del(watchlist['id'])
    print "-> Watchlist deleted"

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
