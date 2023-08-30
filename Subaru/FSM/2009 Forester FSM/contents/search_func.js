function goIdx(sakuinId){
	top.headFrame.linkPath.hid.value = sakuinId;
	top.bodyFrame.document.location.href = "body.html";
	top.headFrame.document.all.item('headTreeForm').style.display = 'block';
}
function DTCsearch(){
	DTCMatch = 0;
	matchFlg = 0;
	DTCCode = top.document.location.search.split(',')[0].substring(1);
	inputData = DTCCode;
	SYSCode = top.document.location.search.split(',')[1];
	DTCId = ['11','12','13','14','15','16','21','22','31','32','33','34','3A','3B','3C','3D','41','42','45','46','51','53','54','55','58','59','5A','5B','5C','5D','61','62','65','66','81','85','91','92','95','96','B1100','B1101','B1102','B1103','B1104','B1105','B1106','B1401','B1402','B1403','B1404','B1500','B2000','B2001','B2002','B2003','B2004','B2005','B2006','B2007','B2017','B2100','B2101','B2102','B2103','B2104','B2105','B2106','B2107','B2110','B2111','B2112','B2113','B2114','B2115','B2116','B2117','B2200','B2201','B2202','B2203','B2204','B2205','B2206','B2207','B2215','B2216','B2217','C0021','C0022','C0023','C0024','C0025','C0026','C0027','C0028','C0029','C0031','C0032','C0033','C0034','C0035','C0036','C0037','C0038','C0039','C0041','C0042','C0044','C0045','C0047','C0051','C0052','C0054','C0056','C0057','C0061','C0062','C0063','C0064','C0071','C0072','C0073','C0074','C0075','C0076','C0081','E2','E3','E4','E6','E7','E8','E9','EA','EB','EC','ED','EE','F1','F2','F3','F4','F5','F6','F8','F9','FA','P0011','P0016','P0018','P0021','P0026','P0028','P0030','P0031','P0032','P0037','P0038','P0046','P0076','P0077','P0082','P0083','P0088','P0089','P0093','P0097','P0098','P0101','P0102','P0103','P0106','P0107','P0108','P0112','P0113','P0116','P0117','P0118','P0122','P0123','P0125','P0130','P0131','P0132','P0133','P0134','P0137','P0138','P0139','P0140','P0171','P0172','P0182','P0183','P0191','P0192','P0193','P0197','P0198','P0201','P0202','P0203','P0204','P0219','P0222','P0223','P0230','P0244','P0245','P0246','P0301','P0302','P0303','P0304','P0327','P0328','P0335','P0336','P0340','P0341','P0345','P0400','P0403','P0404','P0405','P0406','P0409','P0410','P0413','P0414','P0418','P0420','P0458','P0459','P0462','P0463','P0500','P0512','P0513','P0545','P0546','P0562','P0563','P0600','P0604','P0605','P0606','P0607','P0628','P0629','P0638','P0691','P0692','P0700','P0704','P0705','P0712','P0713','P0715','P0719','P0720','P0724','P0731','P0732','P0733','P0734','P0736','P0741','P0743','P0748','P0753','P0758','P0763','P0768','P0801','P0850','P0851','P0852','P1137','P1160','P1201','P1202','P1203','P1213','P1214','P1232','P1233','P1234','P1380','P1382','P1410','P1418','P1466','P1467','P1468','P1469','P1472','P1473','P1492','P1493','P1494','P1495','P1496','P1497','P1498','P1499','P1518','P1519','P1520','P1521','P1560','P1570','P1571','P1572','P1574','P1576','P1577','P1578','P1607','P1616','P1706','P1707','P1718','P1817','P2004','P2005','P2006','P2007','P2008','P2009','P2011','P2012','P2016','P2017','P2021','P2022','P2032','P2033','P2088','P2089','P2092','P2093','P2100','P2101','P2102','P2103','P2109','P2111','P2122','P2123','P2127','P2128','P2135','P2138','P2146','P2147','P2148','P2149','P2228','P2229','P2413','P2419','P2420','P2432','P2433','P2441','P2444','P2503','P2504','P2633','P2634','P2635','U1201','U1202','U1211','U1212','U1213','U1217','U1221','U1222','U1223','U1227','U1300','U1301','U1302','U1303','U1311','U1321','U1327'];

	if(SYSCode == 'ABG'){
		var SYSArray = ['002'];
	}else if(SYSCode == 'ABS'){
		var SYSArray = ['006'];
	}else if(SYSCode == 'ADA'){
		var SYSArray = ['013'];
	}else if(SYSCode == 'APS'){
		var SYSArray = ['014'];
	}else if(SYSCode == 'BIU'){
		var SYSArray = ['010'];
	}else if(SYSCode == 'C-C'){
		var SYSArray = ['003','043'];
	}else if(SYSCode == 'ENG'){
		var SYSArray = ['008','018','028','038','048','058','068','078','088','098','0a8','0b8','0c8','000','019','020','030','040','050','060','070','080','090'];
	}else if(SYSCode == 'ODS'){
		var SYSArray = ['017'];
	}else if(SYSCode == 'T-M'){
		var SYSArray = ['004','044','011','015','012'];
	}else if(SYSCode == 'TPM'){
		var SYSArray = ['016'];
	}else if(SYSCode == 'VDC'){
		var SYSArray = ['005'];
	}else{
		var SYSArray = 'error';
	}

	for(i = 0; i < DTCId.length; i++){
		if(inputData == DTCId[i]){
			matchFlg = 1;
		}
	}

	if(matchFlg == 1){
		var trHidden = 'trHiddenArray';
		trLength = document.getElementById(DTCCode).all.tags('tr').length;
		SgoIdx = document.getElementById(DTCCode).all.tags('tr')[0].all.tags('td')[2].all.tags('a')[0].href;
		for(i = 0;i < trLength;i++){
			if(SYSArray != 'error'){
				for(j = 0;j < SYSArray.length;j++){
					if(document.getElementById(DTCCode).all.tags('tr')[i].all.tags('td')[2].all.tags('a')[0].href.substring(19,22) == SYSArray[j]){
						SgoIdx = document.getElementById(DTCCode).all.tags('tr')[i].all.tags('td')[2].all.tags('a')[0].href;
						DTCMatch += 1;
					}else{
						trHidden = trHidden + ',' + i;
					}
				}
			}
		}

		if(trLength == '1'){
			eval(SgoIdx);
		}else{
			if(DTCMatch == 1){
				eval(SgoIdx);
			}else if(DTCMatch == 0){
				document.all.item(inputData).style.display = 'block';
			}else{
				if(inputData.length == 2){
					document.all.item(inputData).style.display = 'block';
					for(i = 1;i < trHidden.split(',').length;i++){
						document.getElementById(DTCCode).all.tags('tr')[trHidden.split(',')[i]].style.display = 'none';
					}
				}else{
					document.all.item(inputData).style.display = 'block';
				}
			}
		}
	}else{
		document.all.item('head').style.display = 'none';
		document.all.item('etc').style.display = 'block';
		document.all.item('etc2').style.display = 'none';
	}

}
