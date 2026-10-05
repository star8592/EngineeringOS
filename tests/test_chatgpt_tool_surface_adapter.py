import sys
sys.path.insert(0,'src/engineeringos')
from chatgpt_tool_surface_adapter import adapt,HostSurfaceAdapterError

doc={'tools':[
 {'name':'get_task_status','description':'Continue a task\n\n```ts\nmcp__DevControl__get_task_status(args: { task_id: string }): Promise<{ result: any }>;\n```'},
 {'name':'read_process_logs','description':'Read logs\n\n```ts\nmcp__DevControl__read_process_logs(args: {\ndevice_id: string,\nid: integer, // minimum: 1\nmax_bytes?: integer, // minimum: 1, maximum: 1048576\noffset?: integer, // minimum: 0\n}): Promise<{ result: any }>;\n```'},
 {'name':'browser_act','description':'Act\n\n```ts\nmcp__DevControl__browser_act(args: {\naction_name: "activate" | "set_value",\n// Opaque local secret reference\nsecret_ref?: string,\n}): Promise<{ result: any }>;\n```'}
]}
out=adapt(doc);by={x['name']:x for x in out['tools']}
assert out['schema']=='devcontrol.chatgpt-host-surface.v2'
assert by['get_task_status']['description']=='Continue a task'
assert by['get_task_status']['input_contract']['properties']['task_id']=={'required':True,'type':'string'}
p=by['read_process_logs']['input_contract']['properties']
assert p['id']['minimum']==1 and p['max_bytes']['maximum']==1048576 and p['offset']['required'] is False
a=by['browser_act']['input_contract']['properties']
assert a['action_name']['enum']==['activate','set_value'] and a['secret_ref']['description']=='Opaque local secret reference'
try:adapt({'tools':[{'name':'x','description':'no signature'}]});raise AssertionError()
except HostSurfaceAdapterError as e:assert str(e)=='HOST_SIGNATURE_MISSING'
print('10 host-surface-adapter invariants passed')
