/* File Name: domlib.js
 * Copyright (C) 2001 Masayuki AOKI
 * e-mail: info@maokis.com
 * url: http://maokis.com
 * Last Updated: June 29, 2002.
 */
_checkClient = function(){
 this.version=navigator.appVersion;
 this.browser=navigator.userAgent;
 this.op6=this.browser.match(/opera 6/i) && window.opera;
 this.ie5 = (this.browser.match(/msie 5/i) && !this.op6);
 this.ie6 = (this.browser.match(/msie 6/i) && !this.op6);
 this.ieU = (this.ie5 || this.ie6);
 this.nsU=(this.version.match(/[5-9]\./i) && this.browser.match(/netscape/i));
 this.mzU=(this.browser.match(/gecko/i) && !this.nsU);
 return this;
}
var client = new _checkClient();
if(!client.version.match(/[5-9]\./i)){alert(" These scripts work with Ver5/6.x Browser. "); history.go(-1);}

myLayer = function(ID){
 var m = this;
 m.id = ID;
 m.lyr = document.getElementById(m.id);
 m.lyrs = m.lyr.childNodes;
 m.css = m.lyr.style;
 m.imgs = m.lyr.getElementsByTagName("IMG");
 m.css.position = "absolute";
 m.ref = m.id + "REF";
 eval(m.ref + "=this");
}
myLayer.prototype.show = function(){this.css.visibility="visible";};
myLayer.prototype.hide = function(){this.css.visibility="hidden";};
myLayer.prototype.moveTo=function(x,y){var m=this;m.css.left=x+"px";m.css.top=y+"px";m.x=m.lyr.offsetLeft;m.y=m.lyr.offsetTop;}
myLayer.prototype.clipTo=function(t,r,b,l){var m=this;m.clip=new Object();m.l=l;m.t=t;m.r=r;m.b=b;m.css.clip="rect("+m.t+"px, "+m.r+"px, "+m.b+"px, "+m.l+"px)"; m.clip.l=l;m.clip.t=t;m.clip.r=r;m.clip.b=b;m.clip.w=(r-l);m.clip.h=(b-t);}
myLayer.prototype.resizeTo=function(w,h){this.css.width=w+"px";this.w=w;this.css.height=h+"px";this.h=h;this.clipTo(0,this.w,this.h,0);}
myLayer.prototype.setZ=function(z){this.css.zIndex=z;this.z=z;}
myLayer.prototype.background = function(back){if((""+back).indexOf(".")!=-1)this.css.backgroundImage="url("+back+")";else this.css.backgroundColor=back;if(back==null){this.css.backgroundImage="";this.css.backgroundColor="";}}
myLayer.prototype.resizeBy=function(dw,dh){this.resizeTo(this.w+dw,this.h+dh);this.clipTo(0,this.w,this.h,0);}
myLayer.prototype.setBox=function(x,y,w,h){var m=this;m.moveTo(x,y);m.resizeTo(w,h);m.clipTo(0,w,h,0);}
myLayer.prototype.output=function(s){if(s!=null)this.lyr.innerHTML=s;else return;}
myLayer.prototype.moveBy=function(x,y){var m=this;m.moveTo(m.x+x,m.y+y);}
myLayer.prototype.slideTo=function(x,y,step,spd){var m=this;if(!m.slideActive){m.slideActive=true;m.oPath=0;m.routeX=[];m.routeY=[];m.routeX[0]=m.x;m.routeY[0]=m.y;for(i=1;i<=step;i++){m.routeX[i]=m.routeX[i-1]+(x-m.x)/step;m.routeY[i]=m.routeY[i-1]+(y-m.y)/step;m.routeX[step]=x;m.routeY[step]=y}}else{m.oPath++;m.moveTo(m.routeX[m.oPath],m.routeY[m.oPath])}m.engine=setTimeout(m.ref+".slideTo("+x+","+y+","+step+","+spd+")",spd);if(m.oPath==step){clearTimeout(m.engine);m.slideActive=false}}
myLayer.prototype.clipBy=function(dt,dr,db,dl){var m=this;m.clipTo(m.clip.t+dt,m.clip.r+dr,m.clip.b+db,m.clip.l+dl)}
myLayer.prototype.load=function(x,y,w,h,url){var m=this;if(arguments[0]==null){while(this.lyr.hasChildNodes())this.lyr.removeChild(this.lyr.lastChild)}else{m.setBox(x,y,w,h);var ifrm="iframe_"+this.id;m.url=url;ifrm_load=0;m.iframe='<iframe onload="ifrm_load=1" id='+ifrm+' frameborder=0 width='+w+' height='+h+' src='+m.url+' style=\'left:0;top:0;width:'+w+';height:'+h+';z-index:0;\'></iframe><div style="position:absolute;font:Normal 9pt Arial;color:#333333; width:'+w+';height:'+h+';text-align:center;background:snow;z-index:10;"><br><br><br>Now Loading Page : '+url+'<br> Please Wait in a moment...</div>';m.output(m.iframe);m.iframes=[];m.iframes.i=0;m.iframes[m.iframes.i++]=new myLayer(ifrm);var j=m.iframes.length-1;m.iframes[j].setBox(0,0,w,h);if(client.ieU||client.mzU){if(!ifrm_load){m.updateFrame(j)}else if(ifrm_load){this.lyrs[1].style.display="none"}}else if(client.nsU)this.lyrs[1].style.display="none"}}
myLayer.prototype.updateFrame=function(j){if(ifrm_load){clearTimeout(this.engine);ifram_load=0;this.lyrs[1].style.display="none"}else{this.engine=setTimeout(this.ref+".updateFrame("+j+")",100)}}
myLayer.prototype.setUp=function(x,y,w,h,back,content,z){ this.setBox(x,y,w,h);this.background(back);this.output(content);if(z)this.setZ(z);}
myLayer.prototype.setBorder=function(cb){this.css.border=cb;if(client.nsU||client.mzU){var bw=!this.css.borderWidth?1:parseInt(this.css.borderWidth);this.setBox(this.x,this.y,this.w-2*bw,this.h-bw*2);this.w=this.w+2*bw;this.h=this.h+bw*2;this.clipTo(0,this.w+2*bw,this.h+2*bw,0)}}
myLayer.prototype.setFont=function(){var a=arguments;this.css.font=a[0];this.css.color=a[1];this.css.textAlign=a[2];if(a[3])this.setBorder(a[3])}
myLayerInit=function(){var lyrs=document.getElementsByTagName("DIV");for(var i=0;i<lyrs.length;i++){if(lyrs[i].id){eval(lyrs[i].id.toLowerCase()+'=new myLayer("'+lyrs[i].id+'")');eval(lyrs[i].id.toLowerCase()).setBox(0,0,0,0)}}docW=(client.ieU||client.op6)?document.body.offsetWidth:window.innerWidth;docH=(client.ieU||client.op6)?document.body.offsetHeight:window.innerHeight;}
_Process=function(){iloading_bar.clipTo(0,_loading_pitch*(_imgsLoaded++),8,0);if(_imgsLoaded>=_imgFiles.length){_CallEE();_msg_box.hide();loading_bar.hide();iloading_bar.hide()}}
_CallEE = function(){setTimeout('status=" Download Finished!"',10);}

ImageLoader = function(){
 var _boxTop = 200;
 var _boxWidth = 400;
 var _boxHeight = 120;
 var _boxMsg = "<br>Now Loading Images...";
 var _boxbgColor = "#FFD200";
 var _boxFont = "Bold 10pt Verdana";
 var _boxFontColor = "Black";
 var _boxBorder = "groove 5px #5D7400";

 var _barWidth = 250;
 var _barHeight = 10;
 var _barColor = "#0FFC00";
 var _barBorder = "solid 1px #777777";

 var a=arguments;_imgs=[];_imgFiles=a;_imgsLoaded=0;_loading_pitch=parseInt(_barWidth/a.length);
 var l_bw = _loading_pitch*(a.length-1)+2;
 docW = (client.ieU||client.op6)?document.body.clientWidth:window.innerWidth;
 docH = (client.ieU||client.op6)?document.body.clientHeight:window.innerHeight;
 makeNewDiv("_MSG_BOX",null,[(docW-400)/2,_boxTop,_boxWidth,_boxHeight,_boxbgColor,_boxMsg,100]);
 _msg_box.setFont(_boxFont,_boxFontColor,"CENTER",_boxBorder);
 makeNewDiv("LOADING_BAR",null,[(docW-l_bw)*.5,_boxTop+55,l_bw,_barHeight,null,null,101]);
 loading_bar.css.border = _barBorder; loading_bar.setFont("500 9px Arial","#FFFFFF","center",_barBorder);
 makeNewDiv("iLOADING_BAR","LOADING_BAR",[0,0,_barWidth,_barHeight-parseInt(loading_bar.css.borderWidth),_barColor,null,100]); iloading_bar.clipTo(0,1,8,0);
 for(i=0;i<a.length;i++){var im=a[i].split("/");var il=im.length-1;var aiImgs=im[il].split(".")[0]+"Img";eval(aiImgs+'=new Image()');eval(aiImgs+'.src="'+a[i]+'"'); _imgs[i]=new Image();_imgs[i].src=a[i];_Loaded(i);}}
_Loaded = function(i){(_imgs[i].complete)?_Process():setTimeout('_Loaded('+i+')',200);}
function makeNewLayer(tag,Id,parent,prop){var newLayer;newLayer=document.createElement(tag);newLayer.id=Id;if(parent){document.getElementById(parent).appendChild(newLayer)}else document.body.appendChild(newLayer);eval(Id.toLowerCase()+' = new myLayer("'+Id+'")');if(prop){eval(Id.toLowerCase()).setUp(prop[0],prop[1],prop[2],prop[3],prop[4],prop[5],prop[6])}}
function makeNewDiv(Id,parent,prop){var newDiv=null;newDiv=document.createElement("DIV");newDiv.setAttribute("id",Id);document.body.appendChild(newDiv);if(parent){document.getElementById(parent).appendChild(newDiv)}else{document.body.appendChild(newDiv)}eval(Id.toLowerCase()+' = new myLayer("'+Id+'")');if(prop){eval(Id.toLowerCase()).setUp(prop[0],prop[1],prop[2],prop[3],prop[4],prop[5],prop[6])}}
function preLoadImgArray(imgNo,imgFile){for(i=0;i<=imgNo;i++){this[i]=new Image();this[i].src=imgFile+i+'.png'}return this}
function E(c){c==null?alert("OK"):alert(c)}
function S(s){status=s}
/* 
END of domlib.js
 */