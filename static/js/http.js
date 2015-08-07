function sendHttpRequest(callback, method, url, is_async, body) {
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			callback(xhr.responseText);
		}
	}
	xhr.open(method, url, is_async);
	xhr.send(body);
	if(!is_async && xhr.status == 200) {
        return xhr.responseText;
    }
}

function sendGetRequest(callback, url, is_async) {
	sendHttpRequest(callback, 'GET', url, is_async);
}

function sendPostRequest(callback, url, is_async, body) {
	sendHttpRequest(callback, 'POST', url, is_async, body);
}