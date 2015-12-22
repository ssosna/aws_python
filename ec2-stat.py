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
    ['No', 'str(index)'],
    ['Resource ID', 'res.id'],
    ['TAGS', 'res_tags'],
    ['State', 'getattr(res,\'state\',\'-none-\')']
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
    index = 0
    table_headers = zip(*PRINT_TABLE_HEADERS_LIST)[0]
    for res in awsResource(args.region, sourceTypeDictProcessing(SOURCE_TO_TYPE,args.resource)).get_resource_data(args.id,args.resource):
        table_string = []
        index += 1
        for tags_key, tags_value in res.tags.items():
            res_tags += ' {0}: {1};'.format(tags_key, tags_value)
        for headers_list_value in zip(*PRINT_TABLE_HEADERS_LIST)[1]:
                table_string.append(eval(headers_list_value))
        output_table.append(table_string)
    print tabulate(output_table, table_headers, tablefmt="grid")


def sourceTypeDictProcessing(outerdict, resource_type):
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
    common = argparse.ArgumentParser()
    common.add_argument('-r', '--region', help='AWS region, default: us-west-2', default='us-west-2', required=True)
    common.add_argument('-t', '--tags', nargs='+', help='Search TAGs, required parameter', default=None, required=True)
    common.add_argument('-s', '--resource', help='Choice resource, required parameter', choices=sourceTypeDictProcessing(SOURCE_TO_TYPE,None),
                        required=True)
    common.add_argument('-i', '--id', help='Resource ID or NAME, optional', default=None, nargs='+')
    common.set_defaults(func=print_result_tabulate)
    args = common.parse_args()
    args.func(args)