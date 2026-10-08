"""Fit font-size / letter-spacing / position per label so rendered ink bbox matches the PNG's."""
import sys, json, subprocess, importlib.util
import numpy as np
from PIL import Image
spec=importlib.util.spec_from_file_location('b','files/kinai-hyuga/build.py'); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
TARGET={ 'label-izumo-ja':(550,721,298,366),'label-izumo':(505,763,380,436),'label-kinai-ja':(1063,1235,233,302),
'label-kinai':(1036,1266,314,371),'label-kinai-count':(950,1350,382,445),'label-hyuga-ja':(372,531,978,1045),
'label-hyuga':(314,583,1060,1132),'label-hyuga-alt':(254,642,1128,1200),'num-1':(1175,1225,495,536),'num-2':(1111,1167,515,556),
'num-3':(1160,1208,565,606),'num-4':(1110,1160,595,636),'num-5':(1194,1249,636,677),'legend-title':(918,1193,888,945),
'legend-1':(766,1369,961,1029),'legend-2':(766,1233,1039,1108),'legend-3':(766,1305,1118,1185),'legend-4':(765,1219,1195,1264),'legend-5':(766,1278,1274,1341)}
WEIGHT=sys.argv[1] if len(sys.argv)>1 else '600'
params=json.load(open('scratch/fit.json')) if len(sys.argv)>2 else {l[0]:dict(size=l[3],ls=0.0) for l in b.LABELS}
ROW=220
def render():
    texts=[]
    for i,(lid,*_ ,text) in enumerate(b.LABELS):
        p=params[lid]
        texts.append(f'<text x="50" y="{i*ROW+160}" style="font-size:{p["size"]}px;letter-spacing:{p["ls"]}px">{text.replace("&","&amp;")}</text>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{ROW*len(b.LABELS)}"><rect width="100%" height="100%" fill="#fff"/><g style="font-family:{b.FONT};font-weight:{WEIGHT}">{"".join(texts)}</g></svg>'
    open('scratch/fit.svg','w',encoding='utf8').write(svg)
    subprocess.run([sys.executable,'scratch/render.py','scratch/fit.svg','scratch/fit.png','1'],check=True,capture_output=True)
    a=np.array(Image.open('scratch/fit.png').convert('L'))<100
    out={}
    for i,(lid,*_) in enumerate(b.LABELS):
        ys,xs=np.nonzero(a[i*ROW:(i+1)*ROW]); out[lid]=(int(xs.min())-50,int(xs.max())+1-50,int(ys.min())-160,int(ys.max())+1-160)
    return out
for it in range(4):
    bb=render()
    for lid,(x0,x1,y0,y1) in bb.items():
        tx0,tx1,ty0,ty1=TARGET[lid]; p=params[lid]; n=len([c for c in next(l[5] for l in b.LABELS if l[0]==lid)])
        p['size']=round(p['size']*(ty1-ty0)/(y1-y0),2)
        if it>0 and n>1: p['ls']=round(p['ls']+((tx1-tx0)-(x1-x0))/(n-1),2)
        p['x0'],p['y0']=tx0-x0,ty1-y1  # pen x such that ink left matches; baseline shift
        p['err']=((x1-x0)-(tx1-tx0),(y1-y0)-(ty1-ty0))
json.dump(params,open('scratch/fit.json','w'),indent=1)
for k,v in params.items(): print(k,v)
