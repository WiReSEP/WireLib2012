var delayclean;
function clean () {

	document.getElementById("login").style.visibility='hidden';
	document.getElementById("search").style.visibility='hidden';
	return;
}

function mouseonmenu(j) {
	if(delayclean){
		cleartimer();
	}
	menu(j);
}

function cleandelay() {
	delayclean=setTimeout("clean()",500);
}

function cleartimer() {
	clearTimeout(delayclean);
}

function menu (i) {
	switch(i) {
   		case 1: {
			selects = document.getElementsByClassName("pop1");
			for(var i=0; i<selects.length; ++i) {
			  selects[i].style.visibility="visible"
			}
			document.getElementById("search").style.visibility='hidden';
			return;
		}
		case 2: {
			document.getElementById("login").style.visibility='hidden';
			document.getElementById("search").style.visibility='visible';
			return;
   		}
		case 3: {
			document.getElementById("login").style.visibility='hidden';
			document.getElementById("search").style.visibility='visible';
			return;
		}
	}
}
