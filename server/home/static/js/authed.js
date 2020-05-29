let url = new URL(domen+'/api/private/js');

function checkreqs() {
    for (var t in reqs) {
		var xhr = new XMLHttpRequest();

		url.searchParams.set('token', t);
		url.searchParams.set('task', reqs[t]);

		xhr.open('GET', url, false);
		xhr.send();
				
		if (xhr.status != 200) {
		    console.log(`Ошибка ${xhr.status}: ${xhr.statusText}`);
		}
		else {
		    var answer = JSON.parse(xhr.responseText);
		    
		    if (answer.is_done == 0)
				return;

		    var progress = document.getElementById('progressbar_forjs_'+reqs[t]);
		    if (progress == null)
				window.location.reload(false);
		    if (progress.getAttribute('aria-valuenow') != answer.is_done.toString()) {
				progress.setAttribute('aria-valuenow', answer.is_done.toString());
				progress.setAttribute('style', `width: ${answer.is_done.toString()}%`);
				progress.innerHTML = `Идет анализ данных выполненно ${answer.is_done.toString()}%`;

				if (answer.is_done == 100)
				    window.location.reload(false);				

				var resp = document.getElementById('response_forjs_'+reqs[t]);
				resp.innerHTML = answer.data;
		    }
		}
	}
}

setInterval(checkreqs, 2000);
