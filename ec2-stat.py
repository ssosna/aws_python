#!/usr/bin/env python

#import pprint
import argparse
import boto.ec2
from config import config
from datetime import datetime
import time
import sys
resource_tags ={}
aws_access_key = config['aws_access_key']
aws_secret_key = config['aws_secret_key']
#access_key = 'AKIAJEJH5QUXQY4NMYZA'
#secret_key = '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'

class ansi_color:
  red    = '\033[31m'
  green  = '\033[32m'
  yellow = '\033[33m'
  reset  = '\033[0m'
  grey   = '\033[1;30m'
  
def set_resource_tags(resource, tags):
  for tag_key, tag_value in tags.iteritems():
    if tag_key not in resource.tags or resource.tags[tag_key] != tag_value:
      print 'Tagging %(resource_id)s with [%(tag_key)s: %(tag_value)s]' % {
       'resource_id': resource.id,
       'tag_key': tag_key,
       'tag_value': tag_value
        }
      resource.add_tag(tag_key, tag_value)    
def get_resource_tags(resource_id,ec2_conn):
  resource_tags ={}
  if resource_id:
    tags = ec2_conn.get_all_tags({ 'resource-id': resource_id })
    for tag in tags:
    # Tags starting with 'aws:' are reserved for internal use
      if not tag.name.startswith('aws:'):
        resource_tags[tag.name] = tag.value
  return resource_tags

def get_ec2_instances(region):
    i=0
    tags=': Tags'+ansi_color.yellow+' =>'+ansi_color.reset
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key)

    for inst in ec2_conn.get_only_instances():
        for k,v in inst.tags.items():
            tags+=' '+k+': '+v       
        
        if inst.state == 'running':
            stat=ansi_color.yellow+' => '+inst.state+ansi_color.reset
        else:
            stat=ansi_color.red+' => '+inst.state+ansi_color.reset
        i+=1  
        print str(i)+' '+ansi_color.grey+region+': '+ansi_color.green+inst.id+'('+inst.instance_type+')'+stat+tags
    
    for vol in ec2_conn.get_all_volumes():
        print region+':',vol.id
 #       tags_volume = get_resource_tags(vol.id,ec2_conn)
 #       description = 'snapshot' 
 #       try:
 #           current_snap = vol.create_snapshot(description)
 #           set_resource_tags(current_snap, tags_volume)
 #           suc_message = 'Snapshot created with description: %s and tags: %s' % (description, str(tags_volume))
 #           print '     ' + suc_message
 #       except Exception, e:
 #           print "Unexpected error:", sys.exc_info()[0]
 #           pass
          
regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1',
                'ap-southeast-1','ap-southeast-2','ap-northeast-1']

parser = argparse.ArgumentParser()
#    parser.add_argument('access_key', help='Access Key');
#    parser.add_argument('secret_key', help='Secret Key');
parser.add_argument('--region',help='Enter region');
parser.add_argument('action',help='show/create/remove/sart/stop');
args = parser.parse_args()
#    global access_key
#    global secret_key
global region
#    access_key = args.access_key
#    secret_key = args.secret_key
region = args.region
#for region in regions: get_ec2_instances('us-west-2')
if args.action == 'show':
  print "Show all instances in region: %s" % (region)
  get_ec2_instances(region)
