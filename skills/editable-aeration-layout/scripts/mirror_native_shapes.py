"""Reflect explicitly selected native PPTX shapes without rebuilding a user's deck."""
import argparse, copy, json, uuid
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as E

NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for prefix,url in {**NS,'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','a16':'http://schemas.microsoft.com/office/drawing/2014/main'}.items():E.register_namespace(prefix,url)
EMU=9525
def shape_id(s):
    q=s.find('p:nvSpPr/p:cNvPr',NS)
    return int(q.get('id')) if q is not None else None
def has_text(s):return bool(''.join(t.text or '' for t in s.findall('.//a:t',NS)).strip())
def mirror_shape(s,axis_px,new_id):
    if s.tag!=f"{{{NS['p']}}}sp":raise ValueError('Only individual native shapes are supported; groups must be handled with a group-aware transform.')
    s=copy.deepcopy(s);xf=s.find('p:spPr/a:xfrm',NS)
    if xf is None:raise ValueError('Selected shape has no native transform')
    off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
    off.set('x',str(round(2*axis_px*EMU-int(off.get('x'))-int(ext.get('cx')))))
    if not has_text(s):
        xf.set('rot',str((-int(xf.get('rot','0')))%21600000))
        if xf.get('flipH') in ('1','true'):xf.attrib.pop('flipH',None)
        else:xf.set('flipH','1')
    else:
        # Glyphs stay upright; paragraph anchoring is mirrored too.
        for pp in s.findall('.//a:pPr',NS)+s.findall('.//a:defPPr',NS):
            algn=pp.get('algn','l')
            if algn=='l':pp.set('algn','r')
            elif algn=='r':pp.set('algn','l')
    nv=s.find('p:nvSpPr/p:cNvPr',NS);nv.set('id',str(new_id));nv.set('name','mirrored-'+nv.get('name','shape'))
    for e in s.iter():
        if e.tag.endswith('}creationId'):e.set('id','{'+str(uuid.uuid4()).upper()+'}')
    for t in s.findall('.//a:t',NS):
        if t.text=='左组':t.text='右组'
    return s
def edit_package(source,dest,slide,source_ids,remove_ids,axis):
    if Path(source).resolve()==Path(dest).resolve():raise ValueError('Output must differ from source')
    with ZipFile(source) as z:
        entries={n:z.read(n) for n in z.namelist()}
    path=f'ppt/slides/slide{slide}.xml';r=E.fromstring(entries[path]);tree=r.find('p:cSld/p:spTree',NS)
    index={shape_id(s):s for s in tree if shape_id(s) is not None}
    missing=(set(source_ids)|set(remove_ids))-set(index)
    if missing:raise ValueError(f'Missing selected IDs: {missing}')
    if set(source_ids)&set(remove_ids):raise ValueError('Source and removal IDs overlap')
    selected=set(source_ids)|set(remove_ids)
    for e in r.iter():
        if e.tag.split('}')[-1] in ('stCxn','endCxn') and int(e.get('id','-1')) in selected:
            raise ValueError('Selected shapes have attached connectors; use a reference-aware transform')
        if 'spid' in e.attrib and int(e.get('spid','-1')) in selected:
            raise ValueError('Selected shapes have timing/animation references; use a reference-aware transform')
    new_id=max(index)+1;pairs=[]
    clones=[]
    for sid in source_ids:
        clones.append(mirror_shape(index[sid],axis,new_id));pairs.append({'source_id':sid,'mirror_id':new_id});new_id+=1
    for s in list(tree):
        if shape_id(s) in remove_ids:tree.remove(s)
    for c in clones:tree.append(c)
    entries[path]=E.tostring(r,encoding='utf-8',xml_declaration=True)
    Path(dest).parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,b in entries.items():z.writestr(n,b)
    return pairs
def main():
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--slide',type=int,default=1);p.add_argument('--source-ids',required=True);p.add_argument('--remove-ids',required=True);p.add_argument('--axis-px',type=float,required=True);p.add_argument('--report')
    a=p.parse_args();ids=lambda v:[int(i) for i in v.split(',') if i.strip()]
    pairs=edit_package(a.source,a.output,a.slide,ids(a.source_ids),ids(a.remove_ids),a.axis_px)
    if a.report:Path(a.report).write_text(json.dumps(pairs,indent=2),encoding='utf8')
    print(f'Mirrored {len(pairs)} native shapes. Original input preserved.')
if __name__=='__main__':main()
