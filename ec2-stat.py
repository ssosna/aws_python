#!/usr/bin/env python

import argparse
import boto.ec2 as ec2
import boto.ec2.elb as elb

from tabulate import tabulate

SOURCE_TO_TYPE = {
    'ec2': {
        'instance': 'get_only_instances',
        'image': 'get_all_images',
        'volume': 'get_all_volumes'
    },
    'elb': {
        'elb': 'get_all_load_balancers'}
}


class awsResource:
    def __init__(self, aws_region, aws_res_type):
        self.filter_tags = {}
        self.ec2_connect = eval('{0}.connect_to_region(aws_region)'.format(aws_res_type))

    def tags_parser(self, args):
        # Parsing tags
        for arg_teg_part in range(len(args.tags)):
            tmp = args.tags[arg_teg_part].split('=')
            self.filter_tags['tag:' + tmp[0]] = tmp[1]
        return self.filter_tags

    def get_resource_data(self, args):
        parsed_tags = self.tags_parser(args)
        aws_query = 'self.get_{0}(args.id, parsed_tags)'.format(''.join(args.resource))
        return eval(aws_query)

    def get_instance(self, id, filter_tags):
        return self.ec2_connect.get_only_instances(filters=filter_tags, instance_ids=id)

    def get_image(self, id, filter_tags):
        return self.ec2_connect.get_all_images(filters=filter_tags, image_ids=id)

    def get_volume(self, id, filter_tags):
        return self.ec2_connect.get_all_volumes(filters=filter_tags, volume_ids=id)

    def get_elb(self, id, filter_tags):
        return self.ec2_connect.get_all_load_balancers(load_balancer_names=id)


def print_result_tabulate(args):
    headers_list = [['No', 'str(i)'],
                    ['Resource ID', 'res.id'],
                    ['State', 'res.state'],
                    ['TAGS', 'res_tags']]
    output_table = []
    res_tags = ''
    i = 0
    if args.resource != ['instance']:
        headers_list.remove(['State', 'res.state'])
    table_headers = zip(*headers_list)[0]
    for res in awsResource(args.region, args.resource).get_resource_data(args):
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
    RESOURSE_LIST=[]
    for main_source_type_key in SOURCE_TO_TYPE.keys():
        for second_source_type_key in SOURCE_TO_TYPE[main_source_type_key].keys():
            RESOURSE_LIST.append(second_source_type_key)

    def searchNestedKey(outerdict, key):
        for nesteddict in outerdict.itervalues():
            print nesteddict
            if key in nesteddict:
                return nesteddict[key]

    print searchNestedKey(SOURCE_TO_TYPE,'instance')
    common = argparse.ArgumentParser()
    common.add_argument('-r', '--region', help='AWS region, default: us-west-2', default='us-west-2', required=True)
    common.add_argument('-t', '--tags', nargs='+', help='Search TAGs, required parameter', default=None, required=True)
    common.add_argument('-s', '--resource', help='Choice resource, required parameter', choices=RESOURSE_LIST,
                        required=True)
    common.add_argument('-i', '--id', help='Resource ID or NAME, optional', default=None, nargs='+')
    common.set_defaults(func=print_result_tabulate)
    args = common.parse_args()
    print args
    args.func(args)