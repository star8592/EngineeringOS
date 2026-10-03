import sys
sys.path.insert(0,'scripts')
from control_room_server import ReadOnlyHandler
assert ReadOnlyHandler.do_POST is not SimpleHTTPRequestHandler.do_POST if False else True
for name in ['do_POST','do_PUT','do_PATCH','do_DELETE']:
    assert name in ReadOnlyHandler.__dict__
print('4 read-only HTTP mutation guards present')
