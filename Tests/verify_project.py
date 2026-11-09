import json, plistlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
m = json.loads((root/'Shared/sms_model.json').read_text('utf8'))
assert len(m['labels']) == 7
assert len(m['bias']) == len(m['labels'])
assert len(m['weights']) > 1000
assert all(len(v) == len(m['labels']) for v in m['weights'].values())
assert (root/'NOVA-SMS-Shield-AI.xcodeproj/project.pbxproj').exists()
for p in [root/'NOVA-SMS-Shield-AI/Info.plist',root/'MessageFilter/Info.plist']:
    assert plistlib.load(open(p,'rb'))
print('Project sanity OK | labels:',m['labels'],'| weights:',len(m['weights']))
