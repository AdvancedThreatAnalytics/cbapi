import sys
import struct
import socket
import pprint
import optparse 

# in the github repo, cbapi is not in the example directory
sys.path.append('../src/cbapi')

import cbapi 

def build_cli_parser():
    parser = optparse.OptionParser(usage="%prog [options]", description="Dump Binary Info")

    # for each supported output type, add an option
    #
    parser.add_option("-c", "--cburl", action="store", default=None, dest="url",
                      help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_option("-a", "--apitoken", action="store", default=None, dest="token",
                      help="API Token for Carbon Black server")
    parser.add_option("-i", "--id", action="store", default=None, dest="id")
    return parser

def truncate(string, length):
    if len(string) + 2 > length:
        return string[:length] + "..."
    return string

def main(argv):
    parser = build_cli_parser()
    opts, args = parser.parse_args(argv)
    if not opts.url or not opts.token or not opts.id:
        print "Missing required param; run with --help for usage"
        sys.exit(-1)

    # build a cbapi object
    #
    cb = cbapi.CbApi(opts.url, token=opts.token)

    # get record describing this watchlist  
    #
    watchlist = cb.watchlists(opts.id) 

    # output the details about the watchlist
    #
    print '%-20s | %s' % ('field', 'value')
    print '%-20s + %s' % ('-' * 20, '-' * 60)
    print '%-20s | %s' % ('id', watchlist['id'])
    print '%-20s | %s' % ('name', watchlist['name'])
    print '%-20s | %s' % ('date_added', watchlist['date_added'])
    print '%-20s | %s' % ('last_hit', watchlist['last_hit'])
    print '%-20s | %s' % ('last_hit_count', watchlist['last_hit_count'])
    print '%-20s | %s' % ('search_query', watchlist['search_query'])

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
