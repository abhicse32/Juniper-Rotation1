#!/usr/bin/env python
import sys,os
import topology_generator as tp

class Node:
	def __init__(self):
		self.left= None
		self.right= None

class BST:
	def __init__(self):
		self.root= Node()

	def insert_ip(self,ip_string):
		temp_node= self.root
		for bit in ip_string:
			if bit=='0':
				if not temp_node.left:
					temp_node.left=Node()
				temp_node= temp_node.left
			else:
				if not temp_node.right:
					temp_node.right= Node()
				temp_node= temp_node.right

	# function to verify the correctness of the implementation
	def print_levelwise_aux(self,que):
		if not que:
			return
		temp_queue= list()
		for nodes in que[-1::-1]:
			if nodes.left:
				print '0',
				temp_queue.insert(0,nodes.left)

			if nodes.right:
				print '1',
				temp_queue.insert(0,nodes.right)
		del que
		print
		self.print_levelwise_aux(temp_queue)


	def print_levelwise(self):
		self.print_levelwise_aux([self.root])

	def get_subnets(self,root_,subnet):
		if not root_:
			return True
		elif (not root_.left) and (not root_.right):
			return (True,[tp.binary_to_ip(subnet)])

		elif root_.left and root_.right:
			left_info = self.get_subnets(root_.left,subnet+'0')
			right_info = self.get_subnets(root_.right, subnet+'1')
			if left_info[0] and right_info[0]:
				return (True, [tp.binary_to_ip(subnet.ljust(32,'0'))+'/'+str(32-len(subnet))])
			else:
				return (False, left_info[1]+right_info[1])
		else:
			if root_.left:
				return (False, self.get_subnets(root_.left,subnet+'0')[1])
			else:
				return (False, self.get_subnets(root_.right,subnet+'1')[1])



if __name__=='__main__':
	bst= BST()
	bst.insert_ip('100111100')
	bst.insert_ip('100111101')
	bst.insert_ip('100111110')
	bst.insert_ip('100111111')
	bst.insert_ip('100010101')
	bst.insert_ip('100010001')
	bst.insert_ip('100010000')
	lst=bst.get_subnets(bst.root,'')
	print lst
	# bst.insert_ip('100100110')
	# bst.insert_ip('101011000')
	# print topology_generator.binary_to_ip('1101')
	# bst.print_levelwise()


