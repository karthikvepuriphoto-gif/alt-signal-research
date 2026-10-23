import json,sys
t=open(sys.argv[1]).read();i=t.index('{');j=t.rindex('}');d=json.loads(t[i:j+1])
print(d.get('meta'), [x['created_at'][:10] for x in d.get('data',[])][-3:], len(d.get('data',[])))
