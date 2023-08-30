/*
Mugi's Popup Menu ver2.07
Copyright 2000-2002 Mugi
mail : mugi@wa2.so-net.ne.jp
site : http://mugi.ca.tc/

このスクリプトは自由に改造して構いません

*/

var current="",timer,ready=false,ie,nn,d1,op

function popupmenu(e,id,menux,menuy){
hidemenu()
current=id
if(timer)clearTimeout(timer)
if(ie||op)e=window.event
if(!menux||!menuy){
if(ie||op){
menux=e.clientX+document.body.scrollLeft
menuy=e.clientY+document.body.scrollTop
}else{
menux=e.pageX
menuy=e.pageY
}
}
if(ie||d1){
with(document.all(id)){
style.left=menux
style.top=menuy
style.visibility="visible"
}
}else
if(nn){
with(document.layers[id]){
left=menux
top=menuy
visibility="show"
}
}
}

var doposcheck=false

function poscheck(e){
if(doposcheck){
if(ie||op)e=window.event
var l,t,w,h,x,y
if(ie||d1){
l=document.all(current).offsetLeft
t=document.all(current).offsetTop
w=document.all(current).offsetWidth
h=document.all(current).offsetHeight
x=eval("e.clientX+"+(op?0:ie?"document.body.scrollLeft":"window.pageXOffset"))
y=eval("e.clientY+"+(op?0:ie?"document.body.scrollTop":"window.pageYOffset"))
if(x<l||x>l+w||y<t||y>t+h)hidemenu()
}else
if(nn){
l=document.layers[current].left
t=document.layers[current].top
w=document.layers[current].document.width
h=document.layers[current].document.height
if(e.pageX<l||e.pageX>l+w||e.pageY<t||e.pageY>t+h)hidemenu()
}
}
}

function hidemenu(){
if(current!=""){
if(ie||d1)document.all(current).style.visibility="hidden"
else
if(nn)document.layers[current].visibility="hide"
doposcheck=false
}
}

function hide(){
if(!ready){timer=setTimeout("hide();doposcheck=true",100);return}
timer=setTimeout('if(!doposcheck){hidemenu()}',1000)
}

function initmenu(){
ie=!!document.all
nn=!!document.layers
d1=!!document.getElementById
op=!!window.opera
if(!ie&&d1)
document.all=function(id){return document.getElementById(id)}
if(!(ie||d1||nn))return
if(nn)document.captureEvents(Event.MOUSEMOVE)
document.onmousemove=poscheck
var over=function(e){doposcheck=true;if(nn&&e.target.constructor!=Layer)document.routeEvent(e)}
for(i=1;;i++){
if((nn&&!document.layers["menu"+i])||(!nn&&!document.all("menu"+i)))break
if(nn){
document.layers["menu"+i].captureEvents(Event.MOUSEOVER)
document.layers["menu"+i].onmouseover=over
}else{
document.all("menu"+i).onmouseover=over
}
}
ready=true
}
window.onload=initmenu

