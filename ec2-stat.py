#!/usr/bin/env python

import argparse
import boto.ec2 as ec2
import boto.ec2.elb as elb

from tabulate import tabulate

SOURCE_TO_TYPE = {
    'ec2': {
        'instance': 'get_only_instances(filters=filter_tags, instance_ids=aws_id)',
        'image': 'get_all_images(filters=filter_tags, image_ids=aws_id)',
        'volume': 'get_all_volumes(filters=filter_tags, volume_ids=aws_id)'
    },
    'elb': {
        'elb': 'get_all_load_balancers(load_balancer_names=aws_id)'}
}

PRINT_TABLE_HEADERS_LIST = [
    ['No', 'str(i)'],
    ['Resource ID', 'res.id'],
    ['State', 'res.state'],
    ['TAGS', 'res_tags']
]

class awsResource:
    def __init__(self, aws_region, aws_resource_type):
        self.filter_tags = {}
        self.aws_resource_type = aws_resource_type
        self.ec2_connect = eval('{0}.connect_to_region(aws_region)'.format(self.aws_resource_type[0]))

    def tags_parser(self, args):
        # Parsing tags
        for arg_teg_part in range(len(args.tags)):
            tmp = args.tags[arg_teg_part].split('=')
            self.filter_tags['tag:' + tmp[0]] = tmp[1]
        return self.filter_tags

    def get_resource_data(self, aws_id,aws_resource):
        filter_tags = self.tags_parser(args)
        aws_query = 'self.ec2_connect.{0}'.format(self.aws_resource_type[1])
        return eval(aws_query)


def print_result_tabulate(args):
    output_table = []
    res_tags = ''
    i = 0
    if args.resource != ['instance']:
        headers_list.remove(['State', 'res.state'])
    table_headers = zip(*headers_list)[0]
    for res in awsResource(args.region, SourceTypeDictProcessing(SOURCE_TO_TYPE,args.resource)).get_resource_data(args.id,args.resource):
        val = []
        i += 1
        for key, value in res.tags.items():
            res_tags += ' {0}: {1};'.format(key, value)
        for headers_list_value in zip(*headers_list)[1]:
            val.append(eval(headers_list_value))
        output_table.append(val)
    print tabulate(output_table, table_headers, tablefmt="grid")

def SourceTypeDictProcessing(outerdict, resource_type):
        processing_result_data=[]
        for nesteddict in outerdict.keys():
            for nestedpair in outerdict[nesteddict].keys():
                if resource_type:
                    if resource_type in nestedpair:
                        processing_result_data= [nesteddict, outerdict[nesteddict][nestedpair]]
                else:
                    processing_result_data.append(nestedpair)
        return processing_result_data

# ------Main entry point----------
if __name__ == "__main__":
    print SourceTypeDictProcessing(SOURCE_TO_TYPE,'instance')
    print SourceTypeDictProcessing(SOURCE_TO_TYPE,None)
    common = argparse.ArgumentParser()
    common.add_argument('-r', '--region', help='AWS region, default: us-west-2', default='us-west-2', required=True)
    common.add_argument('-t', '--tags', nargs='+', help='Search TAGs, required parameter', default=None, required=True)
    common.add_argument('-s', '--resource', help='Choice resource, required parameter', choices=SourceTypeDictProcessing(SOURCE_TO_TYPE,None),
                        required=True)
    common.add_argument('-i', '--id', help='Resource ID or NAME, optional', default=None, nargs='+')
    common.set_defaults(func=print_result_tabulate)
    args = common.parse_args()
    print args
    args.func(args)