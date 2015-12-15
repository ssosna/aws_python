#!/usr/bin/env python

import argparse
#import boto.ec2
#import boto.ec2.elb
from tabulate import tabulate
import boto.ec2 as ec2
import boto.ec2.elb as elb

class ec2_class:

    def connect(self, args):
        global filter_tags
        filter_tags = {}
        global ec2_conn
        ec2_conn = None
        if args.resource == ['elb']:
            ec2_conn = elb.connect_to_region(args.region)
        else:
            ec2_conn = ec2.connect_to_region(args.region)
        return ec2_conn

    def tags_parser(self, args):
        # Parsing tags
        for arg_teg_part in range(len(args.tags)):
            tmp = args.tags[arg_teg_part].split('=')
            filter_tags['tag:' + tmp[0]] = tmp[1]
        return filter_tags


def get_resource(cl_args):
    ec2 = ec2_class()
    ec2_resource = ec2.connect(cl_args)
    res_name_to_str=''.join(cl_args.resource)
    if res_name_to_str == 'elb':
        resource_query = 'ec2.connect(args).{0}(load_balancer_names={1})'. \
            format(functions_dict.get(res_name_to_str), cl_args.id)
    else:
        resource_query = 'ec2.connect(args).{0}(filters={1}, {2}_ids={3})'. \
            format(functions_dict.get(res_name_to_str), ec2.tags_parser(cl_args), res_name_to_str, cl_args.id)
    print_result_tabulate(eval(resource_query), res_name_to_str)


def print_result_tabulate(resource_data, resource_name):
    headers_list = [['No', 'str(i)'],
                    ['Resource ID', 'res.id'],
                    ['State', 'res.state'],
                    ['TAGS', 'res_tags']]
    output_table = []
    res_tags = ''
    i = 0
    if resource_name != 'instance':
        headers_list.remove(['State', 'res.state'])
    table_headers = zip(*headers_list)[0]
    for res in resource_data:
        val = []
        i += 1
        for key, value in res.tags.items():
            res_tags += ' {0}: {1};'.format(key, value)
        for headers_list_value in zip(*headers_list)[1]:
            val.append(eval(headers_list_value))
        output_table.append(val)
    print tabulate(output_table, table_headers, tablefmt="grid")


# ------Main entry point----------
if __name__ == "__main__":
    functions_dict = {
        'instance': 'get_only_instances',
        'image': 'get_all_images',
        'volume': 'get_all_volumes',
        'elb': 'get_all_load_balancers'
    }
    common = argparse.ArgumentParser()
    common.add_argument('-r', '--region', help='AWS region, default: us-west-2', default='us-west-2', required=True)
    common.add_argument('-t', '--tags', nargs='+', help='Search TAGs, required parameter', default=None, required=True)
    common.add_argument('-s', '--resource', help='Choice resource, required parameter', choices=functions_dict.keys(),
                        nargs=1, required=True)
    common.add_argument('-i', '--id', help='Resource ID or NAME, optional', default=None, nargs='+')
    common.set_defaults(func=get_resource)
    args = common.parse_args()
    args.func(args)
'''
 def __init__(self, source, region):
    conn = self.source.elb.connect_to_region(self.region)
eval
return ec2.connect(args).{0}(load_balancer_names={1}

'''