// 0924 左ツリーのメニューを、右ページのURLを取得して伸張する
// 同期ボタンのフローティング(2002.10.8)

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

// ドキュメントのアイコンを変更するため "document.gif" の
// 前の部分の URL を取り出す

	srcURL = parent.menuFrame.document.all.item(pageId).src;
	preSrcURL = srcURL.substring(0, (srcURL.length - (iconName.length)));

// アイコンの変更
// 現在の mainFrame の URL を取り出す

	documentURL = parent.mainFrame.document.URL;
	currentDocumentName = documentURL.substring((documentURL.length - documentNameLength), documentURL.length);

// currentDocumentName には現在表示されているページのファイル名が入っている
// 「.html」を除いたファイル名の長さは「10」に固定

	currentDocumentId = currentDocumentName.substring(0, 10);
	myitemsrc = preSrcURL + "selected.gif"
	myitemsrcorg = preSrcURL + "document.gif"

	if(parent.menuFrame.document.all.item(pageId).src == myitemsrcorg){
		parent.menuFrame.document.all.item(pageId).src = myitemsrc;
	if(pageId.substring(1, 2) == currentDocumentId.substring(1, 2)){
		parent.menuFrame.document.all.item(currentDocumentId).src = myitemsrcorg;
		}
	}

// 20020922 treeindex ページの一番上のリンクを右ページと動的に同期させる
// 「右ページとの同期」はリンクの最初なので links[0]
// 見やすくするため、戻りはそのブロック(Sa01674g21 なら Sa01674)にしている

	parent.menuFrame.document.links[0].href = "#" + pageId.substring(0, 7);

}

//---------------------------------------------------------------------------
// 0924 左ツリーのメニューを、右ページのURLを取得して伸張する
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

// アイコンの変更
// 現在の mainFrame の URL を取り出す

	documentMenuURL = parent.menuFrame.document.location.href;
	documentMainURL = myURL = parent.mainFrame.document.location.href;

	currentDocumentMenuName = documentMenuURL.substring((documentMenuURL.length - documentMenuNameLength), documentMenuURL.length);
	currentDocumentMainName = documentMainURL.substring((documentMainURL.length - documentMainNameLength), documentMainURL.length);

//ツリーファイルの 5 桁目と、本文ファイルの 2 桁目を比較して、カテゴリーが同じときに、メニューを伸張する
currentMenuId = currentDocumentMenuName.substring(4,5);
currentMainId = currentDocumentMainName.substring(1,2);
MainId = currentDocumentMainName.substring(0,10);
	if (currentMenuId == currentMainId){
		menuExpand(MainId);
		}
// 同期ボタンのフローティング

	viewDouki();

//
}

// 同期ボタンのフローティング(2002.10.8)
function viewDouki(){
var offY = 4; //btn の左からの表示位置
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

// アイコンを変更してツリーを開くため、必要な id を取得

	itemIdGrand = "_" + itemId.substring(0, 4); // * _S001
	itemIdGrandImg = itemId.substring(0, 4) + "src"; // * S001src
	itemIdParent = "_" + itemId.substring(0, 7); // * _S001001
	itemIdParentImg = itemId.substring(0, 7) + "src"; // * S001001src

// ツリーの表示を変更

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

// ドキュメントのアイコンを変更するため "document.gif" の
// 前の部分の URL を取り出す

	srcURL = parent.menuFrame.document.all.item(itemId).src;
	preSrcURL = srcURL.substring(0, (srcURL.length - (iconName.length)));

// アイコンの変更
// リンク先の id は itemId に格納済み

// 「.html」を除いたファイル名の長さは「10」に固定

	if(parent.menuFrame.document.all.item(itemId).src == (preSrcURL + "document.gif")){
		parent.menuFrame.document.all.item(itemId).src = preSrcURL + "selected.gif";
	}

	document.links[0].href = "#" + itemId.substring(0, 7);

}

// ----------------------------------------------------------------------
