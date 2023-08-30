//
function goIdx(sakuinId){
//alert("test1 "+top.headFrame.linkPath.hid.value);
	top.headFrame.linkPath.hid.value = sakuinId;
	top.bodyFrame.document.location.href = "body.html";
//¥Ø¥Ã¥À¡¼¤Î¥×¥EÀ¥¦¥ó¥á¥Ë¥å¡¼¤òÉ½¼¨¤¹¤E
	top.headFrame.document.all.item('headTreeForm').style.display = 'block';
}
function goBodyChg(htmlFile){
	top.bodyFrame.document.location.href = htmlFile;
//¥Ø¥Ã¥À¡¼¤Î¥×¥EÀ¥¦¥ó¥á¥Ë¥å¡¼¤ò±£¤¹
	top.headFrame.document.all.item('headTreeForm').style.display = 'none';
}
function linkPathSet(){
// ³¨ÌÜ¼¡¡¢º÷°ú¤«¤é¥Eó¥¯¤¹¤EÈ¤­¤Ë¡¢¥Ø¥Ã¥À¡¼¤Î±£¤·ID ¤ò¼èÆÀ¤¹¤E
var linkPath = top.headFrame.linkPath.hid.value;
var linkPathDir = linkPath.substring(0, 4);
	if (top.headFrame.linkPath.hid.value != "nothing"){
//¥»¥Ã¥È¤µ¤EÆ¤¤¤ED ¤¬7·ES123456)¤Î¥Eó¥¯Àè¤ËÂĞ±ş¡£¤½¤EÊ³°¤ÏÄÌ¾EÎËÜÊ¸(10·å°Ê¾å¤ÎID)
//mylinkSet() ¤Ï¡¢data/honbun.js ¤Îfunction
		if (linkPath.length == 7) {
			linkPath = mylinkSet(linkPath);
		}
		document.location.href = "../" + linkPathDir + "/" + linkPath + ".html";
		top.headFrame.linkPath.hid.value = "nothing"
		chgFile = "../../" + "tree" + linkPath.substring(1,2) + ".html";
		chgLev = "tree" + linkPath.substring(1,2) + ".html";
// ¥×¥EÀ¥¦¥ó¤Î¥á¥Ë¥å¡¼ÊÑ¹¹
		top.headFrame.document.F1.S1.value = chgLev;
// º¸¥Ú¡¼¥¸¤ÎÊÑ¹¹
		parent.menuFrame.document.location.href = chgFile; // ¡ÖS904001a17¡×->¡Ö../../tree9.html¡×;
	}
}
//º÷°ú¥Ú¡¼¥¸ÍÑ¸¡ºE
function idxsearch(idxId){
idx_ID = ['idx_ea','idx_eb','idx_ec','idx_ed','idx_ee','idx_ef','idx_eg','idx_eh','idx_ei','idx_ej','idx_ek','idx_el','idx_em','idx_en','idx_eo','idx_ep','idx_er','idx_es','idx_et','idx_eu','idx_ev','idx_ew','idx_ey'];
	for(i = 0; i < idx_ID.length; i++){
		if(idxId == idx_ID[i]){
			parent.main.document.all.item(idx_ID[i]).style.display = "block";
			parent.main.document.location.href = 'sakuin_main.html#top';
		}
		else{
			parent.main.document.all.item(idx_ID[i]).style.display = "none";
		}
	}
}
//ÇÛÀş¿Ş¥Ú¡¼¥¸ÍÑ¸¡ºE
function haisenzuSearch(idxId){
idx_ID = ['idx_ea','idx_eb','idx_ec','idx_ed','idx_ee','idx_ef','idx_eg','idx_eh','idx_ei','idx_ek','idx_en','idx_eo','idx_ep','idx_er','idx_es','idx_et','idx_ev','idx_ew','idx_ks','idx_st'];
	for(i = 0; i < idx_ID.length; i++){
		if(idxId == idx_ID[i]){
			parent.main.document.all.item(idx_ID[i]).style.display = "block";
			parent.main.document.location.href = "wiring_main_result.html#top";
			for(j = 1; j < idx_ID.length; j++){
				parent.main.document.all.item('top_' + j).style.display = 'none';
			}
		}
		else{
			parent.main.document.all.item(idx_ID[i]).style.display = "none";
		}
	}
}
//ÇÛÀş¿Ş¥Ú¡¼¥¸Á´ÉôÉ½¼¨
function haisenzuAll(){
idx_ID = ['idx_ea','idx_eb','idx_ec','idx_ed','idx_ee','idx_ef','idx_eg','idx_eh','idx_ei','idx_ek','idx_en','idx_eo','idx_ep','idx_er','idx_es','idx_et','idx_ev','idx_ew','idx_ks','idx_st'];
	for(i = 0; i < idx_ID.length; i++){
		if(parent.main.document.all.item(idx_ID[i]).style.display == 'none'){
			parent.main.document.all.item(idx_ID[i]).style.display = 'block';
		}
	}
	for(j = 1; j < idx_ID.length; j++){
			parent.main.document.all.item('top_' + j).style.display = 'block';
	}
}
//DTC¥³¡¼¥É¸¡ºE¥Õ¥©¡¼¥à¤ÎÃÍ¤ò¥Ø¥Ã¥À¤Î±£¤·¥Õ¥©¡¼¥à¤ËÆş¤EE
function sendInput(){
inputData = document.myForm1.myMes.value;
top.headFrame.linkPath.hid.value = inputData;
top.bodyFrame.document.location.href = 'dtc_result.html';
}
//DTC¥³¡¼¥É¸¡ºE¥Ø¥Ã¥À¤Î±£¤·¥Õ¥©¡¼¥à¤ÎÃÍ¤ò¼õ¤±¼è¤Ã¤ÆÂĞ±ş¤·¤¿¥Ú¡¼¥¸¤ËÈô¤Ğ¤¹
function DTCsearch(){
inputData = top.headFrame.linkPath.hid.value;
DTCId = ['11','12','13','14','15','16','21','22','31','32','33','34','3A','3B','3C','3D','41','42','45','46','51','53','54','55','58','59','5A','5B','5C','5D','61','62','65','66','81','85','91','92','95','96','B1100','B1101','B1102','B1103','B1104','B1105','B1106','B1401','B1402','B1403','B1404','B1500','B2000','B2001','B2002','B2003','B2004','B2005','B2006','B2007','B2017','B2100','B2101','B2102','B2103','B2104','B2105','B2106','B2107','B2110','B2111','B2112','B2113','B2114','B2115','B2116','B2117','B2200','B2201','B2202','B2203','B2204','B2205','B2206','B2207','B2215','B2216','B2217','C0021','C0022','C0023','C0024','C0025','C0026','C0027','C0028','C0029','C0031','C0032','C0033','C0034','C0035','C0036','C0037','C0038','C0039','C0041','C0042','C0044','C0045','C0047','C0051','C0052','C0054','C0056','C0057','C0061','C0062','C0063','C0064','C0071','C0072','C0073','C0074','C0075','C0076','C0081','E2','E3','E4','E6','E7','E8','E9','EA','EB','EC','ED','EE','F1','F2','F3','F4','F5','F6','F8','F9','FA','P0011','P0016','P0018','P0021','P0026','P0028','P0030','P0031','P0032','P0037','P0038','P0046','P0076','P0077','P0082','P0083','P0088','P0089','P0093','P0097','P0098','P0101','P0102','P0103','P0106','P0107','P0108','P0112','P0113','P0116','P0117','P0118','P0122','P0123','P0125','P0130','P0131','P0132','P0133','P0134','P0137','P0138','P0139','P0140','P0171','P0172','P0182','P0183','P0191','P0192','P0193','P0197','P0198','P0201','P0202','P0203','P0204','P0219','P0222','P0223','P0230','P0244','P0245','P0246','P0301','P0302','P0303','P0304','P0327','P0328','P0335','P0336','P0340','P0341','P0345','P0400','P0403','P0404','P0405','P0406','P0409','P0410','P0413','P0414','P0418','P0420','P0458','P0459','P0462','P0463','P0500','P0512','P0513','P0545','P0546','P0562','P0563','P0600','P0604','P0605','P0606','P0607','P0628','P0629','P0638','P0691','P0692','P0700','P0704','P0705','P0712','P0713','P0715','P0719','P0720','P0724','P0731','P0732','P0733','P0734','P0736','P0741','P0743','P0748','P0753','P0758','P0763','P0768','P0801','P0850','P0851','P0852','P1137','P1160','P1201','P1202','P1203','P1213','P1214','P1232','P1233','P1234','P1380','P1382','P1410','P1418','P1466','P1467','P1468','P1469','P1472','P1473','P1492','P1493','P1494','P1495','P1496','P1497','P1498','P1499','P1518','P1519','P1520','P1521','P1560','P1570','P1571','P1572','P1574','P1576','P1577','P1578','P1607','P1616','P1706','P1707','P1718','P1817','P2004','P2005','P2006','P2007','P2008','P2009','P2011','P2012','P2016','P2017','P2021','P2022','P2032','P2033','P2088','P2089','P2092','P2093','P2100','P2101','P2102','P2103','P2109','P2111','P2122','P2123','P2127','P2128','P2135','P2138','P2146','P2147','P2148','P2149','P2228','P2229','P2413','P2419','P2420','P2432','P2433','P2441','P2444','P2503','P2504','P2633','P2634','P2635','U1201','U1202','U1211','U1212','U1213','U1217','U1221','U1222','U1223','U1227','U1300','U1301','U1302','U1303','U1311','U1321','U1327'];
	matchFlg = 0;
	for(i = 0; i < DTCId.length; i++){
		if(inputData == DTCId[i]){
			matchFlg = 1;
		}
	}
	if(matchFlg == 1){
		document.all.item(inputData).style.display = 'block';
	}
	else if(top.headFrame.linkPath.hid.value == 'ALL'){
		for(j = 0; j < DTCId.length; j++){
			document.all.item(DTCId[j]).style.display = 'block';
		}
		for(k = 1; k < (DTCId.length / 5) + 1; k++){
			document.all.item('top_' + k).style.display = 'block';
		}
	}
	else{
		document.all.item('head').style.display = 'none';
		document.all.item('etc').style.display = 'block';
		document.all.item('etc2').style.display = 'none';
	}
}
//DTC¥³¡¼¥É¸¡ºEÁ´É½¼¨ÍÑ
function DTCAll(){
top.headFrame.linkPath.hid.value = 'ALL';
top.bodyFrame.document.location.href = 'dtc_result.html';
}

