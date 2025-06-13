// Connect to Socket.IO server
const socket = io();

// Load GUI menu
fetch('/gui/menu')
    .then(res => res.json())
    .then(menu => {
        const menuElement = document.getElementById('gui-menu');
        menu.controls.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="icon-${item.icon}"></i> ${item.name}`;
            li.onclick = () => openPanel(item.panel);
            menuElement.appendChild(li);
        });
    });

// Panel management
function openPanel(panelId) {
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(panelId).classList.add('active');
}

// Terminal functionality
function sendCommand() {
    const command = document.getElementById('terminal-input').value;
    const pcName = document.querySelector('.active-client')?.dataset.pcName;
    if (pcName && command) {
        socket.emit('terminal_command', { pc_name: pcName, command: command });
        document.getElementById('terminal-input').value = '';
    }
}

// File transfer
function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                alert(data.status === 'success' ? 'File uploaded!' : 'Error: ' + data.message);
            });
    }
}

function downloadFile() {
    const filename = document.getElementById('file-download').value;
    if (filename) {
        window.open(`/download/${filename}`, '_blank');
    }
}

// Client updater
function uploadUpdate() {
    const fileInput = document.getElementById('update-file');
    const file = fileInput.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/client/update', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                document.getElementById('update-status').innerText = 
                    data.status === 'success' ? 'Update pushed!' : 'Error: ' + data.message;
            });
    }
}

// Socket.IO listeners
socket.on('terminal_update', data => {
    const terminalOutput = document.getElementById('terminal-output');
    terminalOutput.innerHTML += `<div><strong>${data.pc_name}:</strong> ${data.output}</div>`;
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
});

socket.on('client_update', data => {
    alert(`Client update available! Hash: ${data.hash}`);
});

socket.on('update_clients', clients => {
    // Update client list UI (optional)
    console.log('Clients updated:', clients);
});

// Handle Enter key in terminal
document.getElementById('terminal-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendCommand();
    }
});
