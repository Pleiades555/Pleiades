// 0924 ���ĥ꡼�Υ�˥塼�򡢱��ڡ�����URL��������ƿ�ĥ����
// Ʊ���ܥ���Υե��ƥ���(2002.10.8)

function expandAndCollapse(menuItem, menusrc){

//var menuItem;
//var menusrc;
	if( menuItem.style.display == "none"){
		menuItem.style.display = "block";
		menusrc.src = "./image/opened.gif";
	} else {
		menuItem.style.display = "none";
		menusrc.src = "./image/closed.gif";
	}

}

function selectAndShow(pageId){

//var pageId;
var pageLink;
var pagePath;
var showLink;
var srcURL;
var preSrcURL;
var iconName = "document.gif";
var documentURL;
var currentDocumentName;
var documentNameLength = 15;
var currentDocumentId;

	pageLink = pageId.substring(0, 10);
	pagePath = pageId.substring(0, 4);
	showLink = "./data/" + pagePath + "/" + pageId + ".html";
	parent.mainFrame.location.href = showLink;

// �ɥ�����ȤΥ���������ѹ����뤿�� "document.gif" ��
// ������ʬ�� URL ����Ф�

	srcURL = parent.menuFrame.document.all.item(pageId).src;
	preSrcURL = srcURL.substring(0, (srcURL.length - (iconName.length)));

// ����������ѹ�
// ���ߤ� mainFrame �� URL ����Ф�

	documentURL = parent.mainFrame.document.URL;
	currentDocumentName = documentURL.substring((documentURL.length - documentNameLength), documentURL.length);

// currentDocumentName �ˤϸ���ɽ������Ƥ���ڡ����Υե�����̾�����äƤ���
// ��.html�פ�������ե�����̾��Ĺ���ϡ�10�פ˸���

	currentDocumentId = currentDocumentName.substring(0, 10);
	myitemsrc = preSrcURL + "selected.gif"
	myitemsrcorg = preSrcURL + "document.gif"

	if(parent.menuFrame.document.all.item(pageId).src == myitemsrcorg){
		parent.menuFrame.document.all.item(pageId).src = myitemsrc;
	if(pageId.substring(1, 2) == currentDocumentId.substring(1, 2)){
		parent.menuFrame.document.all.item(currentDocumentId).src = myitemsrcorg;
		}
	}

// 20020922 treeindex �ڡ����ΰ��־�Υ�󥯤򱦥ڡ�����ưŪ��Ʊ��������
// �ֱ��ڡ����Ȥ�Ʊ���פϥ�󥯤κǽ�ʤΤ� links[0]
// ���䤹�����뤿�ᡢ���Ϥ��Υ֥�å�(Sa01674g21 �ʤ� Sa01674)�ˤ��Ƥ���

	parent.menuFrame.document.links[0].href = "#" + pageId.substring(0, 7);

}

//---------------------------------------------------------------------------
// 0924 ���ĥ꡼�Υ�˥塼�򡢱��ڡ�����URL��������ƿ�ĥ����
function treeCheck(){
(new Image()).src = "image/selected.gif";

var pageLink;
var pagePath;
var showLink;
var srcURL;
var preSrcURL;
var iconName = "document.gif";
var documentURL;
var currentDocumentName;
var documentMenuNameLength = 10;
var documentMainNameLength = 15;
var currentDocumentId;

// ����������ѹ�
// ���ߤ� mainFrame �� URL ����Ф�

	documentMenuURL = parent.menuFrame.document.location.href;
	documentMainURL = myURL = parent.mainFrame.document.location.href;

	currentDocumentMenuName = documentMenuURL.substring((documentMenuURL.length - documentMenuNameLength), documentMenuURL.length);
	currentDocumentMainName = documentMainURL.substring((documentMainURL.length - documentMainNameLength), documentMainURL.length);

//�ĥ꡼�ե������ 5 ���ܤȡ���ʸ�ե������ 2 ���ܤ���Ӥ��ơ����ƥ��꡼��Ʊ���Ȥ��ˡ���˥塼��ĥ����
currentMenuId = currentDocumentMenuName.substring(4,5);
currentMainId = currentDocumentMainName.substring(1,2);
MainId = currentDocumentMainName.substring(0,10);
	if (currentMenuId == currentMainId){
		menuExpand(MainId);
		}
// Ʊ���ܥ���Υե��ƥ���

	viewDouki();

//
}

// Ʊ���ܥ���Υե��ƥ���(2002.10.8)
function viewDouki(){
var offY = 4; //btn �κ������ɽ������
	sy = document.body.scrollTop;
	document.all["closerToHome"].style.top = sy + offY;
	setTimeout("viewDouki()",1000);
}



function menuExpand(itemId){

	var itemId;
	var itemImg;
	var itemIdParent;
	var itemIdParentImg;
	var itemIdGrand;
	var itemIdGrandImg;

// ����������ѹ����ƥĥ꡼�򳫤����ᡢɬ�פ� id �����

	itemIdGrand = "_" + itemId.substring(0, 4); // * _S001
	itemIdGrandImg = itemId.substring(0, 4) + "src"; // * S001src
	itemIdParent = "_" + itemId.substring(0, 7); // * _S001001
	itemIdParentImg = itemId.substring(0, 7) + "src"; // * S001001src

// �ĥ꡼��ɽ�����ѹ�

	// ====================================================================
	// Modified by Daitec (2006/4/11)
	// Reason: 
	//   To fix the JavaScript Runtime Error: "Object not defined. Line 139"
	// Cause:
	//   When link icon is clicked in other than GI section and
	//     if the target link is a SIE without folder icon in the GI section, 
	//     then the original code tried to apply display style to a null object.
	// Remedy:
	//    Check the first 4 letters of the category ID (parent ID) of target SIE.
	//    If the SIE belongs to the null parent, then use the code from the original
	//    source to change the display style property.
	// Remarks:
	//    This is original bug (error) that exists originally in the sample.
	//    Daitec has fixed the bug by this modification.
	// ====================================================================
	var compID;
	compID =  itemId.substring(0, 4);
	if((compID != "Sa01") && (compID != "Sa02") && (compID != "Sa03") && (compID != "Sa04") && (compID != "Sa05") && (compID != "Sa06") && (compID != "Sa07") && (compID != "Sa09"))
	{
		parent.menuFrame.document.all.item(itemIdGrand).style.display = "block";
		parent.menuFrame.document.all.item(itemIdGrandImg).src = "./image/opened.gif";
		parent.menuFrame.document.all.item(itemIdParent).style.display = "block";
		parent.menuFrame.document.all.item(itemIdParentImg).src = "./image/opened.gif";
	} 
	// ====================================================================


// ----------------------------------------------------------------------

var srcURL;
var preSrcURL;
var iconName = "document.gif";

// �ɥ�����ȤΥ���������ѹ����뤿�� "document.gif" ��
// ������ʬ�� URL ����Ф�

	srcURL = parent.menuFrame.document.all.item(itemId).src;
	preSrcURL = srcURL.substring(0, (srcURL.length - (iconName.length)));

// ����������ѹ�
// ������ id �� itemId �˳�Ǽ�Ѥ�

// ��.html�פ�������ե�����̾��Ĺ���ϡ�10�פ˸���

	if(parent.menuFrame.document.all.item(itemId).src == (preSrcURL + "document.gif")){
		parent.menuFrame.document.all.item(itemId).src = preSrcURL + "selected.gif";
	}

	document.links[0].href = "#" + itemId.substring(0, 7);

}

// ----------------------------------------------------------------------
