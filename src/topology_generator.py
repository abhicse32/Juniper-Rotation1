#!/usr/bin/python
import re,sys,os
from datetime import datetime
import time
import random,string
from xlrd import open_workbook
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

num_users= 10
num_counters= 3
num_out_hosts= 5
num_routers= 1
num_hubs = 1
num_servers= 1
total_ips= num_users+num_out_hosts+num_counters+\
		num_servers+ num_routers+ num_hubs
temp_filename= 'temp_syslogs.txt'

log_str = """<14>1 2013-12-27T12:26:51.853 bhavani RT_FLOW - APPTRACK_SESSION_CREATE_LS [junos@2636.1.1.1.2.35 \
logical-system-name="LSYS1" source-address="14.0.0.1" source-port="32770" destination-address="24.0.0.1" \
destination-port="21" service-name="junos-ftp" application="UNKNOWN" nested-application="UNKNOWN" nat-source-address="14.0.0.1"\
 nat-source-port="32770" nat-destination-address="24.0.0.1" nat-destination-port="21" src-nat-rule-name="None" dst-nat-rule-name="None" \
 protocol-id="6" policy-name="l1z1-l1z3" source-zone-name="l1z1" destination-zone-name="l1z3" session-id-32="120000146" username="N/A"\
  roles="N/A" encrypted="UNKNOWN"]"""

class Node:
	def __init__(self,ip,time_stamp):
		self.node_ip= ip 
		self.epoch_time= time_stamp

	def __eq__(self, obj):
		return self.node_ip==obj.node_ip

	def __ne__(self,obj):
		return (not self.__eq__(obj))

	def __hash__(self):
		return hash(self.node_ip)


def convert_time_to_epoch(str_time):
	ts,ms= str_time.split('.')
	obj=datetime.strptime(ts,"%Y-%m-%dT%H:%M:%S").strftime("%s")
	time_in_ms= int(obj)*1000 + int(ms)
	return time_in_ms

def extract_address(address):
	return address.split('=')[1].strip('\"')

def parse_txt(filename):
	re1= '(?:[\d+-]+T[\d+:\.]+ [\w+-\.]+)'
	# re2= '(?:\w+\@[\w+.]+)'
	re3= '(?:source-address=\"[\d+.]+\")'
	re4= '(?:destination-address=\"[\d+.]+\")'
	re5= '(?:nat-source-address=\"[\d+.]+\")'
	re6= '(?:nat-destination-address=\"[\d+.]+\")'

	obj= re.compile("%s|%s|%s|%s|%s"%(re1,re3,re4,re5,re6))
	parsed_logs=[]

	with open(filename,'r') as reader:
		for lines in reader:
			if "APPTRACK_SESSION_CREATE" in lines:
				m=obj.findall(lines)
				m=m[0].split()+m[1:]
				m[0]= convert_time_to_epoch(m[0])
				parsed_logs.append(m[:2]+[extract_address(x) for x in m[2:]])
	# for log in parsed_logs:
	# 	print log
	return parsed_logs

				

def split_ips(all_ips):
	users_ips,all_ips= all_ips[:num_users],all_ips[num_users:]
	counters_ips, all_ips= all_ips[:num_counters], all_ips[num_counters:]
	out_hosts_ips, all_ips= all_ips[:num_out_hosts], all_ips[num_out_hosts:]
	routers_ips, all_ips = all_ips[:num_routers], all_ips[num_routers:]
	hubs_ips, all_ips = all_ips[:num_hubs], all_ips[num_hubs:]
	servers_ips, all_ips = all_ips[:num_servers], all_ips[num_servers:]	

	return [users_ips,counters_ips,out_hosts_ips,routers_ips,hubs_ips,servers_ips]

def generate_ips(num):
	ip_lst,i=[],0
	while i<num:
		ip_comps= [random.randint(0,255) for k in range(4)]
		ip= '.'.join(map(str,ip_comps))
		if ip not in ip_lst:
			ip_lst.append(ip)
			i+=1
	return ip_lst


def convert_time_to_UTC(time_comps):
	utc_time= '-'.join(map(str,time_comps[:3]))+'T'+':'.join(map(str,time_comps[3:]))
	return utc_time

def generate_time(num):
	pkt_leave_times,i=[],0
	while i<num:
		year= random.randint(1999,2018)
		month= random.randint(1,12)
		day= random.randint(1,28)
		hour= random.randint(0,23)
		mins= random.randint(0,59)
		secs = round(random.uniform(0,59.999),3)
		lst= [year, month, day, hour, mins, secs]
		if lst not in pkt_leave_times:
			pkt_leave_times.append(lst)
			i+=1
 	return pkt_leave_times
	

def format_syslog(size,src_ips,src_nat_ips,device_ips,dest_ips,
	dest_nat_ips,time_stamps,arg='customers'):
	syslog=[]
	
	for i in range(size):
		if arg=='customers':
			out_host_ind= random.randint(0,num_out_hosts-1)
			dest_ip,dest_nat_ip= dest_ips[out_host_ind], dest_nat_ips[out_host_ind]
		else:
			dest_ip, dest_nat_ip = dest_ips[0],dest_nat_ips[0]

		str_= re.sub(r'[\d+-]+T[\d+:\.]+ \w+',"%s"%(time_stamps[i]+' '+device_ips[0]),log_str)
		# str_= re.sub(r'\w+\@[\w+.]+',"user@%s"%device_ips[0],str_)

		str_= re.sub(r'source-address=\"[\d+.]+\"',"source-address=\"%s\""%src_ips[i],str_)
		str_= re.sub(r'destination-address=\"[\d+.]+\"',"destination-address=\"%s\""%dest_ip,str_)
		str_= re.sub(r'nat-source-address=\"[\d+.]+\"',"nat-source-address=\"%s\""%src_nat_ips[i],str_)
		str_= re.sub(r'nat-destination-address=\"[\d+.]+\"',"nat-destination-address=\"%s\""%dest_nat_ip,str_)
		syslog.append(str_)
	return syslog

def write_syslog(syslogs):
	with open(temp_filename,'w') as writer:
		for log in syslogs:
			writer.write(log+'\n')



def generate_syslogs():
	syslogs=list()
	users_pkt_leave_times= generate_time(num_users)
	users_pkt_leave_times= [convert_time_to_UTC(lst) for lst in users_pkt_leave_times]
	counters_pkt_leave_times= generate_time(num_counters)
	hub_pkt_leave_times= [lst[:-1]+[lst[-1]+0.5] for lst in counters_pkt_leave_times]
	counters_pkt_leave_times= [convert_time_to_UTC(lst) for lst in counters_pkt_leave_times]
	hub_pkt_leave_times = [convert_time_to_UTC(lst) for lst in hub_pkt_leave_times]

	total_addresses= generate_ips(total_ips<<1)
	private_ips, nat_ips= total_addresses[:total_ips], total_addresses[total_ips:]
	nodes_private_ips, nodes_nat_ips= split_ips(private_ips),split_ips(nat_ips)

	users_ips, counters_ips, out_hosts_ips, routers_ips, hubs_ips, servers_ips= nodes_private_ips
	users_nat_ips, counters_nat_ips, out_hosts_nat_ips, routers_nat_ips,\
	hubs_nat_ips,servers_nat_ips = nodes_nat_ips
	
	routers_name=[''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+'_')\
	 for i in range(random.randint(5,10)))]
	hubs_name= [''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+'_')\
	 for i in range(random.randint(5,10)))]

	syslogs+=format_syslog(num_users,users_ips,users_nat_ips,routers_name,out_hosts_ips,\
		out_hosts_nat_ips,users_pkt_leave_times,'customers')

	syslogs+=format_syslog(num_counters,counters_ips, counters_nat_ips, routers_name,\
		servers_ips,servers_nat_ips,counters_pkt_leave_times,'counters')

	random.shuffle(syslogs)
	syslogs+=format_syslog(num_counters,counters_ips,counters_nat_ips, hubs_name,\
		servers_ips,servers_nat_ips,hub_pkt_leave_times,'hubs')

	write_syslog(syslogs)

# to run the file type: ./hello.py <syslogs_gile>(not required but included for future purposed)
# it generates syslogs in the file named 'temp_syslogs.txt' in the current working directory

def display_format1(ad_list):
	topology=[]
	for nodes, nbrs in ad_list.iteritems():
		nbrs_lst=list()
		nbrs_lst.append(nodes[0])
		# print "%s"%(nodes[0]),
		for nbr_nodes in nbrs:
			# print "---%s"%(nbr_nodes.node_ip),
			nbrs_lst.append(nbr_nodes.node_ip)
		# print "---%s"%(nodes[1])
		nbrs_lst.append(nodes[1])
		topology.append(nbrs_lst)

	topology.sort(key=lambda x:x[-1])
	for lst in topology:
		print "%s"%(lst[0]),
		for ele in lst[1:]:
			print "---%s"%(ele),
		print



def generate_topology(parsed_logs):
	ad_list=dict()
	for log in parsed_logs:
		n= (log[2],log[3])
		if n not in ad_list:
			ad_list[n]= set()

		ad_list[n].add(Node(log[1],log[0]))

	for key in ad_list:
		ad_list[key]=sorted(ad_list[key],key=lambda x:x.epoch_time)
	# display_format1(ad_list)
	# for n,v in ad_list.iteritems():
	# 	print n
	# 	for x in v:
	# 		print "(%s,%s) "%(x.node_ip,x.epoch_time),
	# 	print
	return ad_list

def parse_csv(filename):
	parsed_logs=list()
	column_list=['destIp','srcIp','deviceId','deviceName','deviceTime']
	reader= pd.read_csv(filename,skipinitialspace=True,sep=',',usecols=column_list)
	print reader.as_matrix()
	for rows in reader.as_matrix():
		parsed_logs.append([rows[4],rows[2],rows[1],rows[0]])

	return parsed_logs


def create_graph(ad_lst,graph_filename):
	edge_list,node_lst=[],set()
	for nodes,nbrs in ad_lst.iteritems():
		# print nodes,
		lst=list(nbrs)
		# for n in lst:
		# 	print n.node_ip,n.epoch_time
		# print
		edge_list.append((nodes[0],lst[0].node_ip))
		node_lst.add(lst[0].node_ip)
		prev=lst[0]
		for nbr in lst[1:]:
			edge_list.append((prev.node_ip,nbr.node_ip))
			prev=nbr
			node_lst.add(nbr.node_ip)
		edge_list.append((lst[-1].node_ip,nodes[1]))

	# print edge_list
	node_lst= list(node_lst)
	labels_map= dict([(x,x) for x in node_lst])
	G= nx.Graph()
	G.add_nodes_from(node_lst,color='blue')
	G.add_edges_from(edge_list)
	color_map=[]
	for n in G.nodes():
		if n in node_lst:
			color_map.append('b')
		else:
			color_map.append('r')
	nx.draw(G,node_color=color_map,with_labels=True)#with_labels=True
	plt.show()
	# plt.savefig(graph_filename)

if __name__=='__main__':
	filename= sys.argv[1]
	graph_filename= sys.argv[2]
	if filename.endswith('.csv'):
		parsed_logs= parse_csv(filename)
	else:
		parsed_logs= parse_txt(filename)
		
	ad_list= generate_topology(parsed_logs)
	create_graph(ad_list,graph_filename)
