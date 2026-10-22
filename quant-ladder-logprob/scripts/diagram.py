import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; els=[]
def box(i,x,y,w,h,text,color):
 common=dict(angle=0,strokeColor='#25334a',backgroundColor=color,fillStyle='hachure',strokeWidth=2,strokeStyle='solid',roughness=1,opacity=100,groupIds=[],frameId=None,roundness={'type':3},seed=i*71,version=1,versionNonce=i*43,isDeleted=False,boundElements=None,updated=1,link=None,locked=False)
 els.append(dict(common,id=f'b{i}',type='rectangle',x=x,y=y,width=w,height=h))
 els.append(dict(common,id=f't{i}',type='text',x=x+14,y=y+17,width=w-28,height=67.5,text=text,fontSize=18,fontFamily=1,textAlign='center',verticalAlign='top',baseline=63,containerId=None,originalText=text,autoResize=True,lineHeight=1.25,backgroundColor='transparent',roundness=None))
def arrow(i,x,y,dx,dy):
 els.append(dict(id=f'a{i}',type='arrow',x=x,y=y,width=abs(dx),height=abs(dy),angle=0,strokeColor='#25334a',backgroundColor='transparent',fillStyle='solid',strokeWidth=2,strokeStyle='solid',roughness=1,opacity=100,groupIds=[],frameId=None,roundness={'type':2},seed=i*87,version=1,versionNonce=i,isDeleted=False,boundElements=None,updated=1,link=None,locked=False,points=[[0,0],[dx,dy]],lastCommittedPoint=None,startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow',elbowed=False))
box(1,20,30,270,115,'Public ARC-Easy\nExclude original 150 + pilot\nFreeze fresh questions','#e9effa')
box(2,355,30,280,115,'Qwen3-0.6B\nBF16, Q8, Q4, Q3, Q2\nPinned GGUF weights','#eaf5ee')
arrow(1,295,87,55,0)
box(3,30,230,275,120,'Four cyclic rotations\nScore A / B / C / D\nMap back to answer text','#fff4d9')
box(4,365,230,275,120,'Secondary check\nScore complete options\nMean token logprob','#f4eafb')
arrow(2,465,150,-295,70); arrow(3,505,150,0,70)
box(5,190,435,310,120,'Paired item accuracy\nAccuracy + letter counts\n95% bootstrap intervals','#e9effa')
arrow(4,165,360,100,65); arrow(5,505,360,-100,65)
(R/'figures/diagram.excalidraw').write_text(json.dumps({'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':els,'appState':{'viewBackgroundColor':'#ffffff','gridSize':None},'files':{}},indent=2))
