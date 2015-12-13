#!/usr/bin/env python

import argparse
import boto.ec2
import boto.ec2.elb
from tabulate import tabulate


def get_resource(args):
    filter_tags = {}

    # Pars tags
    for arg_teg_part in range(len(args.tags)):
        tmp = args.tags[arg_teg_part].split('=')
        filter_tags['tag:' + tmp[0]] = tmp[1]
    if args.resource == ['elb']:
        ec2_conn = boto.ec2.elb.connect_to_region(args.region)
    else:
        ec2_conn = boto.ec2.connect_to_region(args.region)
    functions_dict[''.join(args.resource)](ec2_conn, filter_tags, args.id)


def ami(ec2_conn, filter_tags, id=None):
    print_result_tabulate(ec2_conn.get_all_images(filters=filter_tags, image_ids=id), "false")


def instance(ec2_conn, filter_tags, id=None):
    print_result_tabulate(ec2_conn.get_only_instances(filters=filter_tags, instance_ids=id), "true")


def volume(ec2_conn, filter_tags, id=None):
    print_result_tabulate(ec2_conn.get_all_volumes(filters=filter_tags, volume_ids=id), "false")


def elb(ec2_conn, filter_tags, id=None):
    print_result_tabulate(ec2_conn.get_all_load_balancers(load_balancer_names=id), "false")


def print_result_tabulate(resource, inst_flag):

    header_eval_var = [['No', 'str(i)'],
                       ['Resource ID', 'res.id'],
                       ['State', 'res.state'],
                       ['TAGS', 'res_tags']]
    output_table = []
    res_tags = ''
    i = 0
    if inst_flag == 'false':
        header_eval_var.remove(['State', 'res.state'])
    headers = zip(*header_eval_var)[0]
    for res in resource:
        val = []
        i += 1
        for key, value in res.tags.items():
            res_tags += ' {0}: {1};'.format(key, value)
        for v in zip(*header_eval_var)[1]:
            val.append(eval(v))
        output_table.append(val)
    print tabulate(output_table, headers, tablefmt="grid")


# ------Main entry point----------
if __name__ == "__main__":
    functions_dict = {
        'instance': instance,
        'ami': ami,
        'volume': volume,
        'elb': elb
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
