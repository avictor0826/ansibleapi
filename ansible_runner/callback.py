from ansible.plugins.callback import CallbackBase

class ResutlCallback(CallbackBase):
  def __init__(self, *args, **kwargs):
    super(ResutlCallback, self).__init__(*args, **kwargs)
    self.hosts = []

  def v2_runner_on_unreachable(self, result, ignore_errors=False):
    self.hosts.append({'host':result._host.get_name(), 'result':None, 'success':False, 'msg':'unreachable'})

  def v2_runner_on_ok(self, result):
    self.hosts.append({'host':result._host.get_name(), 'result':result._result, 'success':True, 'msg':'ok'})

  def v2_runner_on_failed(self, result, ignore_errors=False):
    self.hosts.append({'host':result._host.get_name(), 'result':result._result, 'success':False, 'msg':'failed'})

  def get(self):
    return self.hosts
