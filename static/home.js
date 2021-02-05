let audioIN = { audio: true }; 

navigator.mediaDevices.getUserMedia(audioIN)
.then(function (mediaStreamObj) { 
	let audio = document.querySelector('audio'); 
	if ("srcObject" in audio) { 
	  audio.srcObject = mediaStreamObj; 
	}

	let start = document.getElementById('startRec');
	let stop = document.getElementById('stopRec'); 
	let stopLec = document.getElementById('btnStopLec'); 
	let startLec = document.getElementById('btnStartLec'); 

	var options = {mimeType: "audio/webm"};
	recorder = new MediaRecorder(mediaStreamObj, options); 

	start.addEventListener('click', function (e) { 
		recorder.start(); 
	}); 

	stop.addEventListener('click', function (e) { 
		recorder.stop();
	});

	stopLec.addEventListener('click', function (e) { 
		fetch('/send', {
			method: "POST",
			body: ""
		}).then(response => response.text())
		.then((response) => {
			console.log(response)
		})
		.catch(err => console.log(err))
	});

	startLec.addEventListener('click', function (e) { 
		fetch('/start', {
			method: "POST",
			body: ""
		}).then(response => response.text())
		.then((response) => {
			console.log(response)
		})
		.catch(err => console.log(err))
	});

	recorder.ondataavailable = function (e) { 
		chunks.push(e.data); 
	} 

	var chunks = []; 

	recorder.onstop = function (e) {
		blob = new Blob(chunks, {'type': 'audio/webm'});
		console.log(blob);
		
		fetch('/audio', {
			method: "post",
			body: blob
		})
		.then(response => response.text())
			.then((response) => {
				console.log(response)
			})
			.catch(err => console.log(err))
		
		chunks = [];
	}
	
}).catch(function (err) { 
	console.log(err.name, err.message); 
}); 