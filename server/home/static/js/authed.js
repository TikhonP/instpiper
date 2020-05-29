function luboe_imya(slovar){
var domen = 'http://...'
var URL = '/domen/checkrequest?token='
for (var elem in slovar){
var xhr = new XMLHttpRequest();
xhr.open('GET',URL+elem , true);
xhr.send({'task':slovar[elem]});
		
if (xhr.status != 200) {
    alert(xhr.status + ': ' + xhr.statusText);
}

else {
        var stat = xhr.responseText;
	for (var elem_2 in stat){
	    if (elem_2 == is_done){
		 if (stat[elem_2] > min){
		     min = stat[elem_2]
		 }
	    }
	}
    }
}

}
