#!/usr/bin/env python

import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.playbook import Playbook
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor import playbook_executor
from ansible import context
import ansible.constants as C
from callback import ResutlCallback

class AnsibleRunner:
    def __init__(self, playbook, hostnames=None, inventory=None, extra_vars=None,):
        self.playbook = playbook
        self.hostnames = hostnames
        self.inventory = inventory
        self.extra_vars = extra_vars
        context.CLIARGS = ImmutableDict(connection='smart', module_path=['/usr/share/ansible'], forks=10, become=None,
                                        become_method=None, become_user=None, check=False, diff=False,syntax=False,start_at_task=None)
        self._output="Not yet run"
        self.run_success = True
        self._stats = ""

    def run(self):

        #debug
        print("Playbook : "+ self.playbook)
        print("Hostlist:",self.hostnames)
        print("Inventory: ",self.inventory)
        print("extra_args: ",self.extra_vars)
        # initialize needed objects
        self.loader = DataLoader() # Takes care of finding and reading yaml, json and ini files
        self.passwords = dict(vault_pass='secret')

        # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
        self.results_callback = ResutlCallback()

        # create inventory, use path to host config file as source or hosts in a comma separated string
        if self.hostnames is None:
            self.inventory = InventoryManager(loader=self.loader, sources=self.inventory)
        else:
            self.inventory = InventoryManager(loader=self.loader, sources=",".join(self.hostnames)+",")

        # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        if isinstance(self.extra_vars,dict):
            self.variable_manager._extra_vars = self.extra_vars
            print("Debug: Setting extra_vars: ",self.variable_manager._extra_vars)
        #### GET Play from playbook file###
        print("Debug: Loading plays from playbook")
        play = Playbook.load(self.playbook, variable_manager=self.variable_manager, loader=self.loader).get_plays()[0]
        print("Debug: Loaded play 1 from playbook : ", play)
        # Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
        self.tqm = None
        try:
            self.tqm = TaskQueueManager(
                      inventory=self.inventory,
                      variable_manager=self.variable_manager,
                      loader=self.loader,
                      passwords=self.passwords,
                      stdout_callback=self.results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
                  )
            print("Debug: Task Queue manager intialized")
            result = self.tqm.run(play) # most interesting data for a play is actually sent to the callback's methods
            print("Debug: TQM stats for failures")
            self._stats = self.tqm._stats
            print("Debug: TQM stats retrieved")
            hosts = sorted(self._stats.processed.keys())
            for h in hosts:
                t = self._stats.summarize(h)
                #print (t)
                if t['unreachable'] > 0 or t['failures'] > 0:
                    self.run_success = False
        except Exception as e:
            print(e)
            self.run_success = False
        finally:
            # we always need to cleanup child procs and the structures we use to communicate with them
            if self.tqm is not None:
                self.tqm.cleanup()
            self._output=self.results_callback.get()
            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
            return self.run_success

    def output(self):
        return self._output


if __name__ == "__main__":
    print("runnin main")
    a=AnsibleRunner('../firstplaybook.yml',hostnames=['epdlapp023'],extra_vars={"abc":"asdlfkjasdfj"},inventory=None)
    print("run successful or not:",a.run())
    print(a.output())
