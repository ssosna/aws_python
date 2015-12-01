#!/usr/bin/env python

import argparse
import boto.ec2
import boto.ec2.elb
import sys

resource_tags ={}
inst_id = ''

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

def get_ec2_instances(ec2_conn,operation,inst_id):
    i=0
    tags=ansi_color.yellow+': Tags =>'
    if operation == 'start':
      instances = ec2_conn.get_only_instances(instance_ids=inst_id)
      print 'Starting instance id= %s ' % inst_id
      instances[0].start()

    if operation == 'stop':
      instances = ec2_conn.get_only_instances(instance_ids=inst_id)
      print 'Stoping instance id= %s ' % inst_id
      instances[0].stop()

    if operation == 'list':
      instances = ec2_conn.get_only_instances(filters=filter_tags)
#      print 'Found instance with tag=', filter_tags
      for inst in instances:
          for k,v in inst.tags.items():
              tags+=' '+k+': '+v       
          if inst.state == 'running':
              stat=ansi_color.yellow+' => '+inst.state+ansi_color.reset
          else:
              stat=ansi_color.red+' => '+inst.state+ansi_color.reset
          i+=1  
          print str(i)+') '+ansi_color.grey+args.region+': '+ansi_color.green+inst.id+'('+inst.instance_type+')'+stat+tags+ansi_color.reset
          
def get_ec2_volumes(ec2_conn,vol_id):
    i=0
    vol_tags=ansi_color.yellow+': Tags =>'
    for vol in ec2_conn.get_all_volumes(filters=filter_tags):
      for k,v in vol.tags.items():
        vol_tags+=' '+k+': '+v       
      i+=1
      print str(i)+') '+args.region+':',vol.id,vol_tags+ansi_color.reset
 
def get_ec2_ami(ec2_conn,ami_id):
    i=0
    vol_tags=ansi_color.yellow+': Tags =>'
    for vol in ec2_conn.get_all_images(filters=filter_tags):
      for k,v in vol.tags.items():
        vol_tags+=' '+k+': '+v       
      i+=1
      print str(i)+') '+args.region+':',vol.id,vol_tags+ansi_color.reset
 
 
def get_ec2_elb(ec2_elb_conn,elb_id):
    i=0
    elb_tags=ansi_color.yellow+': Tags =>'
    for vol in ec2_elb_conn.get_all_load_balancers(load_balancer_names=filter_tags):
      for k,v in vol.tags.items():
        elb_tags+=' '+k+': '+v       
      i+=1
      print str(i)+') '+args.region+':',vol.id,elb_tags+ansi_color.reset 
 
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
#------Main entry point----------          
regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1',
                'ap-southeast-1','ap-southeast-2','ap-northeast-1']
filter_tags={}
parser = argparse.ArgumentParser()
#    parser.add_argument('access_key', help='Access Key');
#    parser.add_argument('secret_key', help='Secret Key');
parser.add_argument('-r',help='Region',dest='region',default='us-west-2');
parser.add_argument('-i',help='INSTANCE ID or leave empty for search ALL instances in the region',dest='inst_id',default='',nargs='*');
parser.add_argument('-a',help='AMI ID or leave empty for search ALL AMI in the region',dest='ami_id',default='',nargs='*');
parser.add_argument('-e',help='ELB ID or leave empty for search ALL ELB in the region',dest='elb_id',default='',nargs='*');
parser.add_argument('-v',help='VOL ID or leave empty for search ALL volumes in the region',dest='vol_id',default='',nargs='*');
parser.add_argument('-t',nargs='+',help='search TAGs',dest='tags',default=None);
parser.add_argument('action',help='show/create/remove/sart/stop');
args = parser.parse_args()
#    global access_key
#    global secret_key
#    access_key = args.access_key
#    secret_key = args.secret_key

#print args
#print sys.argv

if '-r' in sys.argv:
#  ec2_conn = boto.ec2.connect_to_region(args.region,aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_key)
  ec2_conn = boto.ec2.connect_to_region(args.region)
# Pars tags if set
if args.tags != None:
  for i in range(len(args.tags)):
    tmp=args.tags[i].split('=')
    filter_tags['tag:'+tmp[0]] = tmp[1]
# Case action
if args.action == "list":
  if '-i' in sys.argv:
    print "--------------------------INSTANCE-------------------------"
    get_ec2_instances(ec2_conn,args.action,args.inst_id)
  if '-v' in sys.argv:
    print "--------------------------VOLUME---------------------------"
    get_ec2_volumes(ec2_conn,args.vol_id)
  if '-a' in sys.argv:
    print "--------------------------AMI------------------------------"
    get_ec2_ami(ec2_conn,args.ami_id)
  if '-e' in sys.argv:
    print "--------------------------ELB-------------------------------"
    ec2_elb_conn=boto.ec2.elb.connect_to_region(args.region)
    get_ec2_elb(ec2_elb_conn,args.elb_id)