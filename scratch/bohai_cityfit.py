import sys,json; sys.argv=['x']
src=open('files/bohai-sea-map/build.py',encoding='utf8').read().split("if __name__ == '__main__':")[0]
exec(src)
import numpy as np
from scipy import optimize
cities={'Beijing':((116.40,39.90),(114,291)),'Busan':((129.04,35.10),(614,538)),'Vladivostok':((131.89,43.12),(705,134)),
'Shanghai':((121.47,31.23),(294,738)),'Seoul':((126.98,37.57),(524,426)),'Hiroshima':((132.46,34.39),(756,573)),'Shenyang':((123.43,41.80),(386,213)),'Dalian':((121.61,38.91),(316,349)),'Qingdao':((120.38,36.07),(262,491)),'Pyongyang':((125.75,39.02),(476,352))}
def res(p):
    f=projector(p); e=[]
    for (ll,xy) in cities.values():
        X,Y=f(*ll); e+= [X-xy[0],Y-xy[1]]
    return np.array(e)
r=optimize.least_squares(res,[125,30,45,3.4,470,440],bounds=([100,5,6,0.5,-2000,-2000],[150,80,85,20,3000,3000]))
print([round(v,4) for v in r.x], 'rms px', np.sqrt((r.fun**2).mean()))
print('IoU',1-loss(list(r.x)))
json.dump(list(r.x),open(PAR,'w'))
for k,(ll,xy) in cities.items():
    X,Y=projector(r.x)(*ll); print(k, round(float(X)-xy[0],1), round(float(Y)-xy[1],1))
