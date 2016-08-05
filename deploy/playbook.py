#!/bin/env python
#coding=utf-8
#author=Lian Shifeng

import json
import os
from datetime import datetime

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook import Playbook
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.stats import AggregateStats
from ansible.plugins.callback import CallbackBase
from ansible.utils.unicode import to_bytes

class ResultCallback(CallbackBase):
	'''
	rewrite callback by owner 
	'''   
	def __init__(self,*args,**kwargs):
		super(ResultCallback,self).__init__(*args,**kwargs)
        	self.res = []
        	self.summary = {}
        	self.host_ok = {}  
        	self.host_unreachable = {}  
       		self.host_failed = {}

        def _new_play(self, play):
        	return {
            		'play': {
                		'name': play.name,
                		'id': str(play._uuid)
            		},
            		'tasks': []
        	}

    	def _new_task(self, task):
        	return {
            		'task': {
                	'name': task.name,
                	'id': str(task._uuid)
            	},
            	'hosts': {}
        	}

   	def v2_playbook_on_play_start(self, play):
        	self.res.append(self._new_play(play))

    	def v2_playbook_on_task_start(self, task, is_conditional):
        	self.res[-1]['tasks'].append(self._new_task(task))
 
	def v2_runner_on_ok(self, result, **kwargs):
		host = result._host
		rlt = result._result
		if rlt['invocation']:
                	del rlt['invocation']
        	self.res[-1]['tasks'][-1]['hosts'][host.name] = rlt

    	def v2_runner_on_unreachable(self, result):
		host = result._host
        	self.res[-1]['tasks'][-1]['hosts'][host.name] = result._result

    	def v2_runner_on_failed(self, result,  *args, **kwargs):  
		host = result._host
        	self.res[-1]['tasks'][-1]['hosts'][host.name] = result._result
        

    	def v2_playbook_on_stats(self, stats):
        	"""Display info about playbook statistics"""

        	hosts = sorted(stats.processed.keys())

        	for h in hosts:
            		s = stats.summarize(h)
            		self.summary[h] = s


class MyRun(object):
	'''
 	rewrite run method 
	'''	
  
	MSG_FORMAT = "%(time)s - %(plays)s - %(tasks)s - %(stats)s\n\n"
	
	def __init__(self,*args,**kwargs):
		self.inventory = None
		self.variable_manager = None
 		self.loader = None  
        	self.options = None  
        	self.passwords = None  
        	self.callback = None  
       	 	self.__initialize()  
        	self.results = {}
	
	def __initialize(self):
		
		Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax','connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args','become','become_method','become_user','verbosity', 'check'])
		self.variable_manager = VariableManager()
		self.loader = DataLoader()
		self.options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='smart', module_path=None, forks=100, remote_user='root', private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method=None, become_user='root', verbosity=None, check=False)

		self.passwords = {}
		self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list='/etc/ansible/hosts')
		self.variable_manager.set_inventory(self.inventory)
	
	def run(self,mission_id,role_name,exe_group):			
                '''
		 create play with tasks actually run it
		'''
		tqm = None
		try:
                        retry_path = '/etc/ansible/main.yml'
			inventory_path = [retry_path]
			self.results_callback = ResultCallback()
                        extra_vars = {}
			extra_vars['host_list'] = exe_group
			extra_vars['role_name'] = role_name
			extra_vars['run_id'] = mission_id
			self.variable_manager.extra_vars = extra_vars
    			pbex = PlaybookExecutor(
              			playbooks=inventory_path, 
              			inventory=self.inventory, 
              			variable_manager=self.variable_manager, 
              			loader=self.loader, 
              			options=self.options, 
              			passwords=self.passwords,
          		)

    			pbex._tqm._stdout_callback = self.results_callback
    			result = pbex.run()
		finally:
    			if tqm is not None:
        			tqm.cleanup()
	
	def get_results(self,mission_id):
		path = os.path.join("/var/log/ansible/",mission_id)
		now = datetime.now()
		result = self.results_callback.res
		playname = result[-1]['play']['name']
		data = result[-1]['tasks']
		summary = json.dumps(self.results_callback.summary,indent=4)
		output = {
			 'time' : now,
                         'plays': playname, 
			 'tasks': json.dumps(data,indent=4,sort_keys=True),
		         'stats': summary
		}
		msg = to_bytes(self.MSG_FORMAT % output)
		with open(path,"ab") as fd:
			fd.write(msg)
		return summary

