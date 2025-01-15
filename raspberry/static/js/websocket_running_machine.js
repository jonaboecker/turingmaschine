import {io} from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

// Connect to server
const socket = io();

// Websocket Event-Listener for Status-Updates
socket.on('state_update', (data) => {

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

// Websocket Event-Listener for errors (show as popup)
socket.on('error', (data) => {
    console.error('Websocket: ', data.message);
    alert(data.message);
});

// Websocket Event-Listener for confirmation
socket.on('confirmation', (data) => {
    console.log('Websocket: ', data.message);
});

// Button-Event-Handler
document.querySelector('#resume_button').addEventListener('click', () => {
    socket.emit('command', {command: 'resume'});
});

document.querySelector('#pause_button').addEventListener('click', () => {
    socket.emit('command', {command: 'pause'});
});

document.querySelector('#stop_button').addEventListener('click', () => {
    socket.emit('command', {command: 'stop'});
});
