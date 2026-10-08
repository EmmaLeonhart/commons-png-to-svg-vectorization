"""Assign each land unit a unique color, render, register against the target PNG, report which unit has which color."""
import re, subprocess, sys, json
import numpy as np
from PIL import Image
from lxml import etree
SVG='scratch/Provinces_of_Japan.svg'; TARGET='data_lake/downloads/kinai-hyuga/Kinai-and-Hyuga-Province-in-Japan-RA.png'
NS='{http://www.w3.org/2000/svg}'
tree=etree.parse(SVG); root=tree.getroot()
layer1=root.find(f".//{NS}g[@id='layer1']")
# units: direct children of layer1 (g or path) whose fill is land
units=[]
for el in layer1:
    st=el.get('style','')
    if 'fill:#fcf5e3' in st: units.append(el)
for k,el in enumerate(units, start=1):
    col='#%02x%02x%02x'%(k*3%256, (k*7)%256, 200)
    for e in [el]+list(el.iter(f'{NS}path')):
        st=e.get('style','')
        st=re.sub(r'fill:[^;]*', f'fill:{col}', st); st=re.sub(r'stroke:[^;]*','stroke:none',st)
        e.set('style', st+';shape-rendering:crispEdges')
for lid in ['layer2','layer5','layer3']:
    l=root.find(f".//{NS}g[@id='{lid}']"); l.set('style','display:none')
# lakes (daf0fd paths in layer1) -> black
for e in layer1.iter(f'{NS}path'):
    if 'fill:#daf0fd' in e.get('style',''): e.set('style', re.sub(r'fill:[^;]*','fill:#000000',e.get('style'))+';stroke:none;shape-rendering:crispEdges')
S=int(sys.argv[1]) if len(sys.argv)>1 else 1
tree.write('scratch/ids.svg')
subprocess.run([sys.executable,'scratch/render.py','scratch/ids.svg','scratch/ids.png',str(S)],check=True)
ids=np.array(Image.open('scratch/ids.png').convert('RGB')).astype(int)
idx=np.zeros(ids.shape[:2],int)
for k in range(1,len(units)+1):
    m=(ids[:,:,0]==k*3%256)&(ids[:,:,1]==(k*7)%256)&(ids[:,:,2]==200); idx[m]=k
np.save('scratch/idx.npy',idx)
json.dump([u.get('id') for u in units],open('scratch/units.json','w'))
print(len(units),'units; land px',(idx>0).sum())
