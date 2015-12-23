#!/usr/bin/env python

import argparse
import boto.ec2 as ec2
import boto.ec2.elb as elb
from tabulate import tabulate
from collections import namedtuple

type_to_source = namedtuple('type_to_source', 'source, function')

# Default sources, resources and functions map
SOURCE_TO_TYPE = {
    'ec2': {
        'instance': 'get_only_instances(filters=filter_tags, instance_ids=aws_id)',
        'image': 'get_all_images(filters=filter_tags, image_ids=aws_id)',
        'volume': 'get_all_volumes(filters=filter_tags, volume_ids=aws_id)'
    },
    'elb': {
        'elb': 'get_all_load_balancers(load_balancer_names=aws_id)'}
}

# Table headers and data variables
PRINT_TABLE_HEADERS_LIST = [
    ['No', 'str(index)'],
    ['Resource ID', 'res.id'],
    ['TAGS', 'res_tags'],
    ['State', 'getattr(res,\'state\',\'-none-\')']
]

TYPE_TO_SOURCE = {
    type: type_to_source(source=source, function=function)
    for source in SOURCE_TO_TYPE
    for type, function in SOURCE_TO_TYPE[source].iteritems()
    }


class awsResource:
    def __init__(self, aws_region, aws_source_type):
        self.aws_source_type = aws_source_type
        self.ec2_connect = eval('{0}.connect_to_region(aws_region)'.format(self.aws_source_type))

    @staticmethod
    def tags_parser(aws_tags):
        # Parsing tags which received from command line
        aws_tags = ['tag:{}'.format(item) for item in aws_tags]
        filter_tags = [
            item.split('=')
            for item in aws_tags
            ]
        return dict(filter_tags)

    def get_resource_data(self, aws_id, aws_resource, aws_tags):
        # Function gets data from AWS according to the query
        # Output: list of resources data
        output_data_table = list()
        res_tags = str()
        filter_tags = self.tags_parser(aws_tags)
        resource_data = eval('self.ec2_connect.{0}'.format(aws_resource))
        for index, res in enumerate(resource_data):
            table_string = []
            print res.tags.items()
            for tags_key, tags_value in res.tags.items():

                res_tags += ' {}: {};'.format(tags_key, tags_value)
            for headers_list_value in zip(*PRINT_TABLE_HEADERS_LIST)[1]:
                table_string.append(eval(headers_list_value))
            output_data_table.append(table_string)
        print output_data_table
        return output_data_table


def print_result_tabulate(args):
    """
    Print function
    :param args          : Variable contains arguments from command line:
    :param args.region   : AWS region
    :param args.id       : AWS resource ID
    :param args.tags     : User's TAGs in list format
    :param args.resource : Selected AWS resource type from SOURCE_TO_TYPE dict

    :return: table output, for example:
            +------+---------------+--------------------------------+---------+
            |   No | Resource ID   | TAGS                           | State   |
            +======+===============+================================+=========+
            |    1 | i-31d610e8    | AppVer: 1.2.2.2.5; Name: LAMP; | stopped |
            +------+---------------+--------------------------------+---------+
    """
    table_headers = zip(*PRINT_TABLE_HEADERS_LIST)[0]
    output_table = awsResource(args.region, TYPE_TO_SOURCE[args.resource].source). \
        get_resource_data(args.id, TYPE_TO_SOURCE[args.resource].function, args.tags)
    print tabulate(output_table, table_headers, tablefmt="grid")


# ------Main entry point----------
if __name__ == "__main__":
    common = argparse.ArgumentParser()
    common.add_argument('-r', '--region', help='AWS region, default: us-west-2', default='us-west-2', required=True)
    common.add_argument('-t', '--tags', nargs='+', help="Search TAGs, required parameter", default=None, required=True)
    common.add_argument('-s', '--resource', help='Choice resource, required parameter',
                        choices=TYPE_TO_SOURCE.keys(), required=True)
    common.add_argument('-i', '--id', help='Resource ID or NAME, optional', default=None, nargs='+')
    common.set_defaults(func=print_result_tabulate)
    args = common.parse_args()
    args.func(args)
