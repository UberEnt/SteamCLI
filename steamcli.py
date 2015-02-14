#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Small CLI tool to dynamically map api.steampowered.com to a command line.
#
# Copyright (c) 2015 Uber Entertainment, Inc. All rights reserved.
# Authored by Jørgen P. Tjernø <jorgenpt@gmail.com>
#
# Licensed under the MIT license, see the LICENSE file in the current directory.


import argparse
import json
import requests

from operator import itemgetter
from pprint   import pprint
from sys      import stderr, exit, argv
from urllib   import urlencode

# To help with output encoding in Windows terminals.
import codecs
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

# Mapping of returned parameter types to funcs that argparse will use to
# coerce user input.
PARAMETER_TYPEMAP = {
    'uint64': int,
    'int64': int,
    'uint32': int,
    'int32': int,
    'float': float,
    'bool': bool,
    'string': str,
    'rawbinary': bytes,
}


def filter_none_values(d):
    return dict((k, v) for k, v in d.iteritems() if v is not None)


def argparser_for_method(prog, method):
    parser = argparse.ArgumentParser(prog=prog)

    for parameter in method['parameters']:
        paramargs = {
            'type': PARAMETER_TYPEMAP[parameter['type']],
            'required': not parameter['optional'],
        }
        if 'description' in parameter:
            paramargs['help'] = parameter['description']

        name = '--%s' % parameter['name']
        parser.add_argument(name, **paramargs)

    return parser


def find_method(interfaces, interface_name, method_name, version):
    matching_interfaces = filter(lambda interface: interface['name'] == interface_name, interfaces)
    if len(matching_interfaces) < 1:
        return (None, None)

    interface = matching_interfaces[0]
    methods = interface['methods']
    matching_methods = filter(lambda method: method['name'] == method_name, methods)
    if len(matching_methods) < 1:
        return (interface, None)

    if version is None:
        version = max(map(itemgetter('version'), matching_methods))

    matching_methods = filter(lambda method: method['version'] == version, matching_methods)
    if len(matching_methods) < 1:
        return (interface, None)

    return (interface, matching_methods[0])


BASE_URL = 'https://api.steampowered.com'
def method_url(interface, method):
    return "%s/%s/%s/v%04i/" % (BASE_URL, interface['name'], method['name'], method['version'])


def get_interfaces(args):
    # TODO: Cache this value, so we don't make so many requests.
    url = method_url({'name': 'ISteamWebAPIUtil'}, {'name': 'GetSupportedAPIList', 'version': 1})
    params = {'format': 'json'}
    if args.key:
        params['key'] = args.key
    url += '?%s' % urlencode(params)

    if args.verbose:
        print " ! GET request for %s" % url
    response = requests.get(url)
    return response.json()['apilist']['interfaces']


def list_commands(args):
    interfaces = get_interfaces(args)
    for interface in interfaces:
        if args.interface and interface['name'] != args.interface:
            continue

        print "> %s:" % interface['name']

        for method in interface['methods']:
            if args.method and method['name'] != args.method:
                continue
            if 'description' in method:
                print '    %s v%i [%s]: %s' % (method['name'], method['version'], method['httpmethod'], method['description'])
            else:
                print '    %s v%i [%s]' % (method['name'], method['version'], method['httpmethod'])

            if args.interface:
                for parameter in method['parameters']:
                    mandatory_mark = '*'
                    if parameter['optional']:
                        mandatory_mark = ' '
                    print '        %s %s %s: %s' % (mandatory_mark, parameter['type'], parameter['name'], parameter['description'])

    if args.interface:
        print '* = required argument'

    return True


def call_command(args):
    interfaces = get_interfaces(args)

    interface, method = find_method(interfaces, args.interface, args.method, args.method_version)
    if not interface:
        print >>stderr, "Invalid interface: %s" % args.interface
        print >>stderr, "Valid values are:"
        print >>stderr, "    %s" % ', '.join(map(itemgetter('name'), interfaces))
        return False

    if not method:
        print >>stderr, "Invalid method: %s" % args.method
        print >>stderr, "Valid values are:"
        print >>stderr, "    %s" % ', '.join(map(itemgetter('name'), interface['methods']))
        return False

    # Little bit of ugliness to have nice `call FooBar baz --help` output.
    original_args = ['steamcli.py'] + argv[1:]
    if len(args.parameters):
        original_args = original_args[:-len(args.parameters)]
    cmd = ' '.join(original_args)

    # Parse the arguments for our specific method, and turn it in to a dict.
    arguments = argparser_for_method(cmd, method).parse_args(args.parameters)
    # Omit any optional arguments that have not been provided.
    arguments = filter_none_values(arguments.__dict__)

    if args.key:
        arguments['key'] = args.key
    arguments['format'] = 'json'

    url = method_url(interface, method)
    response = None
    if method['httpmethod'] != 'POST':
        if len(arguments) > 0:
            url += '?%s' % urlencode(arguments)
        if args.verbose:
            print " ! GET request for %s" % url
        response = requests.get(url)
    else:
        if args.verbose:
            print " ! POST request for %s, body:" % url
            pprint(arguments)
        response = requests.post(url, data=json.dumps(arguments), headers={ 'Content-Type': 'application/json' })

    if args.raw:
        print response.text
    else:
        pprint(response.json())

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', '-k', help='publisher API key for SteamWorks access (https://partner.steamgames.com/documentation/webapi#creating for details)')
    parser.add_argument('--verbose', '-v', help='print verbosely', action='store_true')
    parser.add_argument('--raw', '-r', help='print output raw (probably JSON)', action='store_true')
    commands = parser.add_subparsers()

    commands_subcommand = commands.add_parser('commands', description='list all SteamAPI commands (results will differ with & without --key)')
    commands_subcommand.add_argument('interface', nargs='?')
    commands_subcommand.add_argument('method', nargs='?')
    commands_subcommand.set_defaults(func=list_commands)

    call_subcommand = commands.add_parser('call', description='call a specific SteamAPI command')
    call_subcommand.add_argument('interface')
    call_subcommand.add_argument('method')
    call_subcommand.add_argument('--method-version', help='what version of the method to call, if there are multiple. default is latest.', type=int)
    call_subcommand.add_argument('parameters', nargs=argparse.REMAINDER)
    call_subcommand.set_defaults(func=call_command)

    args = parser.parse_args()

    if not args.func(args):
        exit(1)


if __name__ == '__main__':
    main()
