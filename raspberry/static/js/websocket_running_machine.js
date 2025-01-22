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
        /* todo: design buttons according to state
                'run': MACHINE.running,
                'pause': MACHINE.pause,
                'speed': MACHINE.speed,
        */
        for (const error of data.errors) {
            const errorContainer = document.querySelector('#errors');
            if ([...errorContainer.children].some(el => el.textContent === data.message)) {
                continue; // Error already shown
            }
            // add new error-element
            const errorElement = document.createElement('p');
            errorElement.className = 'text-red-500';
            errorElement.textContent = error;
            errorContainer.appendChild(errorElement);
        }
    });
});


// Funktion zum Verbindungsaufbau mit dem Websocket-Server
function connectWebSocket() {
    // const socket = io('http://127.0.0.1:5000');
    const websocket = new WebSocket("wss://127.0.0.1:5000");

    websocket.onopen = function (event) {
        console.log("Connected to Websocket");
    }

    websocket.onclose = function () {
        console.log('Connection with Websocket Closed!');
    };

    websocket.onerror = function (error) {
        console.log('Error in Websocket Occured: ' + error);
    };

    // Websocket Event-Listener für Status-Updates
    websocket.onmessage = function (e) {
        console.log('Message from Websocket: ' + e.data);

        // Nachricht als JSON parsen
        let message = JSON.parse(e.data);

        // Typ der Nachricht prüfen und entsprechend handeln
        switch (message.type) {
            case 'state_update':
                console.log('State Update:', message.data);
                // Aktualisiere die Anzeige der Maschine
                document.querySelector('#program_name').innerText = message.data.program_name;
                document.querySelector('#state').innerText = message.data.state;
                document.querySelector('#steps').innerText = message.data.step;

                // Fehler aktualisieren
                const errorContainer = document.querySelector('#errors');
                for (const error of message.data.errors) {
                    if ([...errorContainer.children].some(el => el.textContent === error)) {
                        continue; // Fehler bereits angezeigt
                    }
                    const errorElement = document.createElement('p');
                    errorElement.className = 'text-red-500';
                    errorElement.textContent = error;
                    errorContainer.appendChild(errorElement);
                }
                break;

            case 'error':
                console.error('Error:', message.data.message);
                alert(message.data.message); // Fehler als Popup anzeigen
                break;

            case 'confirmation':
                console.log('Confirmation:', message.data.message);
                break;

            default:
                console.warn('Unknown message type:', message.type);
        }
    };


    // Button-Event-Handler registrieren
    document.querySelector('#resume_button').addEventListener('click', () => {
        socket.emit('command', {command: 'resume'});
    });

    document.querySelector('#pause_button').addEventListener('click', () => {
        socket.emit('command', {command: 'pause'});
    });

    document.querySelector('#stop_button').addEventListener('click', () => {
        websocket.emit('command', {command: 'stop'});
    });
}

// Verbindung aufbauen, sobald die Seite geladen ist
// document.addEventListener('DOMContentLoaded', () => {
//     connectWebSocket();
// });
