#!/usr/bin/env python

import sys
import topology_generator as tp
from random import shuffle,randint,sample,uniform
import re

def generate_random_time():
	year= randint(1999,2029)
	month = randint(1,12)
	day= randint(1,28)
	hour=randint(0,23)
	mins= randint(0,59)
	secs = round(uniform(0,50.999),3)
	return [year, month, day, hour, mins, secs]


def create_src_dest_pairs(src_addresses, dest_addresses):
	address_indices=map(lambda x: range(len(x)),[src_addresses,dest_addresses])
	sizes=map(lambda x: len(x),address_indices)
	l= lambda x,y,z: x*(y/z) + x[:y%z]

	if sizes[0] < sizes[1]:
		address_indices[0] = l(address_indices[0],sizes[1],sizes[0])
	else:
		address_indices[1] = l(address_indices[1],sizes[0],sizes[1])

	map(lambda x: shuffle(x),address_indices)

	# return [(src_addresses[address_indices[0][i]],dest_addresses[address_indices[1][i]])\
	#  for i in range(len(address_indices[0]))]
	return map(lambda x: (src_addresses[address_indices[0][x]],\
		dest_addresses[address_indices[1][x]]),range(len(address_indices[0])))

def generate_syslogs(src_dest_pairs,devices,writer):
	sessions_map=dict()
	log_str= tp.log_str
	for src_dest in src_dest_pairs:
		src,dest= src_dest
		if src not in sessions_map:
			sessions_map[src]=randint(10**3,10**7)
		else:
			sessions_map[src]+=1

		start_time= generate_random_time()
		for i in range(len(devices)):
			start_time[-1]=round(start_time[-1]+uniform(200,500)*0.001,3)
			leave_time=tp.convert_time_to_UTC(start_time)

			str_= re.sub(r'[\d+-]+T[\d+:\.]+ \w+',"%s"%(leave_time+' '+devices[i][0]),log_str)
			str_= re.sub(r'\w+\@[\w+.]+',"user@%s"%devices[i][1],str_)
	
			str_= re.sub(r'source-address=\"[\d+.]+\"',"source-address=\"%s\""%src,str_)
			str_= re.sub(r'destination-address=\"[\d+.]+\"',"destination-address=\"%s\""%dest,str_)
			str_= re.sub(r'nat-source-address=\"[\d+.]+\"',"nat-source-address=\"%s\""%\
				tp.binary_to_ip(tp.generate_random_binary_string(32)),str_)
			str_= re.sub(r'nat-destination-address=\"[\d+.]+\"',"nat-destination-address=\"%s\""%
				tp.binary_to_ip(tp.generate_random_binary_string(32)),str_)

			str_=re.sub(r'session-id-32=\"\d+\"',"session-id-32=\"%d\""%(sessions_map[src]),str_)
			writer.write(str_+'\n')


def create_network():
	addresses= tp.generate_addresses()
	# assuming that there are as many firewalls/devices as the number of pool of addresses
	# and packets sent by/destined to ith pool of addresses pass through ith firewall/device
	devices= [('fw'+str(i),tp.binary_to_ip(tp.generate_random_binary_string(32)))\
	 for i in range(len(addresses))]

	with open('syslog_4.txt','w') as writer:
		src_dest_pairs= create_src_dest_pairs(addresses[0],addresses[1])
		intermediate_devices=devices[0:1]+devices[5:8]+devices[1:2]
		generate_syslogs(src_dest_pairs,intermediate_devices,writer)
		
		src_dest_pairs= create_src_dest_pairs(addresses[0],addresses[4])
		intermediate_devices = [devices[0],devices[8],devices[4]]
		generate_syslogs(src_dest_pairs,intermediate_devices,writer)

		src_dest_pairs = create_src_dest_pairs(addresses[5],addresses[2])
		intermediate_devices = devices[5:7]+devices[2:3]
		generate_syslogs(src_dest_pairs,intermediate_devices,writer)

		src_dest_pairs = create_src_dest_pairs(addresses[7],addresses[3])
		intermediate_devices = devices[7:8]+devices[1:4]
		generate_syslogs(src_dest_pairs,intermediate_devices,writer)

		src_dest_pairs = create_src_dest_pairs(addresses[6],addresses[8])
		intermediate_devices = devices[6:]
		generate_syslogs(src_dest_pairs,intermediate_devices,writer)

		src_dest_pairs = create_src_dest_pairs(addresses[2],addresses[4])
		intermediate_devices = devices[2:5]
		generate_syslogs(src_dest_pairs,intermediate_devices,writer)


if __name__=='__main__':
	create_network()