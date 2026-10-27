from pathlib import Path
import json,hashlib,os,sys
root=Path(sys.argv[1]);manifest=Path(sys.argv[2]);out=Path(sys.argv[3]);rows=[]
for row in json.loads(manifest.read_text()):
 path=root/row['path'];actual=hashlib.sha256(path.read_bytes()).hexdigest();assert actual==row['sha256'],row['path'];rows.append({'path':row['path'],'sha256':actual})
out.write_text(json.dumps({'matched':len(rows),'manifest':str(manifest),'files':rows},indent=2),encoding='utf8');print('source matches',len(rows))
