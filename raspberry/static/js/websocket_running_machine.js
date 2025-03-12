$(document).ready(function () {
    //const ctx = document.getElementById("myChart").getContext("2d");
    console.log("Document is ready");

    //connect to the socket server.
    //   var socket = io.connect("http://" + document.domain + ":" + location.port);
    var socket = io.connect();
    if (socket !== undefined) {
        console.log("Connected to Socket Server");
    } else {
        console.error("Not Connected to Socket Server");
    }

    //receive details from server
    socket.on("xxx", function (msg) {
        console.log("Received sensorData :: " + msg.hihi + " :: ");

    });

    socket.on('state_update', function (data) {

        document.querySelector('#program_name').innerText = data.program_name;
        document.querySelector('#state').innerText = data.state;
        document.querySelector('#steps').innerText = data.step;
        document.querySelector('#position').innerText = (data.position === 0) ? '0 unbekannte Position, Homing' : (data.position === -2) ? 'Band-ende erreicht' : data.position;
        document.querySelector('#speed').value = data.speed;
        document.querySelector('#resume_button').className = data.run && !data.pause ? 'bg-blue-500 text-white px-4 py-2 rounded' : 'bg-gray-300 bg-blue-500 px-4 py-2 rounded';
        document.querySelector('#pause_button').className = data.pause ? 'bg-blue-500 text-white px-4 py-2 rounded' : 'bg-gray-300 bg-blue-500 px-4 py-2 rounded';
        document.querySelector('#stop_button').className = data.should_stop ? 'bg-blue-500 text-white px-4 py-2 rounded' : 'bg-gray-300 bg-blue-500 px-4 py-2 rounded';

        for (const error of data.errors) {
            const errorContainer = document.querySelector('#errors');
            if ([...errorContainer.children].some(el => el.textContent === error)) {
                continue; // Error already shown
            }
            // add new error-element
            const errorElement = document.createElement('p');
            errorElement.className = 'text-red-500';
            errorElement.textContent = error;
            errorContainer.appendChild(errorElement);
        }
    });

    socket.on('error', function (data) {
        console.error('Error:', data.message);
        alert(data.message); // Fehler als Popup anzeigen
    });

    socket.on('confirmation', function (data) {
        console.log('Confirmation:', data.message);
    });

    socket.on('default', function (data) {
        console.warn('Unknown message type:', data);
    });

    // Event-Handler für den Speed-Input registrieren
    document.querySelector('#speed').addEventListener('change', (event) => {
        socket.emit('command', {command: 'speed', value: event.target.value});
    });

    // Button-Event-Handler registrieren
    document.querySelector('#resume_button').addEventListener('click', () => {
        socket.emit('command', {command: 'resume'});
    });

    document.querySelector('#pause_button').addEventListener('click', () => {
        socket.emit('command', {command: 'pause'});
    });

    document.querySelector('#stop_button').addEventListener('click', () => {
        socket.emit('command', {command: 'stop'});
    });
});


