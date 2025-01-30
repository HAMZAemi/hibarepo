from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# Initial credentials
USERNAME = "admin"
PASSWORD = "admin"

# Ensure the static folder exists and contains the video file
if not os.path.exists('static'):
    os.makedirs('static')

# HTML templates for login and dashboard page
HTML_TEMPLATE_LOGIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PGdash</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap" rel="stylesheet">
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: 'Poppins', sans-serif;
            background-color: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            width: 320px;
            position: relative;
            z-index: 1;
        }

        .logo img {
            width: 100px;
            margin-bottom: 10px;
        }

        h2 {
            font-family: 'Poppins', sans-serif;
            color: #333;
            margin: 0;
            padding-bottom: 10px;
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }

        button:hover {
            background-color: #0056b3;
        }

        .error {
            margin-top: 10px;
            color: red;
            display: none;
        }

        video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -1;
        }
    </style>
</head>
<body>
    <video autoplay loop muted>
        <source src="/static/video.mp4" type="video/mp4">
    </video>

    <div class="container">
        <div class="logo">
            <img src="https://upload.wikimedia.org/wikipedia/fr/d/d3/Procter_%26_Gamble_2013_%28logo%29.png" alt="PG Logo">
        </div>
        <h2>PGdash</h2>
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <button onclick="login()">Connect</button>
        <div class="error" id="error">Username or password are incorrect. If forgotten, contact admin.</div>
    </div>

    <script>
        function login() {
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    window.location.href = "/dashboard?username=" + username;  // Redirect to dashboard with username
                } else {
                    document.getElementById("error").style.display = "block";
                }
            });
        }
    </script>
</body>
</html>
"""

HTML_TEMPLATE_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PGdash - Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
            background-color: #f4f4f9;
        }

        /* Sidebar styles */
        .sidebar {
            width: 250px;
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            position: fixed;
            top: 0;
            left: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
            transition: width 0.3s ease;
            padding-top: 40px;  /* Espacement pour mieux lire le texte */
        }

        .sidebar.hidden {
            width: 0;
            padding: 0;
        }

        .sidebar h2 {
            font-size: 22px;
            margin-bottom: 20px;
            text-align: center;
            padding-left: 10px; /* Décalage du texte du titre */
        }

        .sidebar .profile {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 40px;
            padding-left: 10px;  /* Décalage de la section profile */
        }

        .sidebar .profile img {
            border-radius: 50%;
            width: 80px;
            height: 80px;
            margin-bottom: 10px;
        }

        .sidebar .profile .username {
            font-size: 18px;
            font-weight: 600;
        }

        .sidebar .profile .status {
            color: #4CAF50;
            font-size: 14px;
        }

        .sidebar .menu {
            list-style-type: none;
            padding: 0;
        }

        .sidebar .menu li {
            margin: 15px 0;
        }

        .sidebar .menu li a {
            color: white;
            text-decoration: none;
            font-size: 16px;
            display: flex;
            align-items: center;
        }

        .sidebar .menu li a:hover {
            background-color: #34495e;
            border-radius: 5px;
            padding: 8px 12px;
        }

        /* Main content area */
        .main-content {
            margin-left: 250px;
            padding: 20px;
            width: calc(100% - 250px);
            transition: margin-left 0.3s ease;
        }

        .main-content h1 {
            font-size: 30px;
            color: #333;
        }

        .button {
            padding: 12px 24px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .button:hover {
            background-color: #0056b3;
        }

        .hide-btn {
            display: none;
            position: absolute;
            top: 20px;
            left: 220px;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .hide-btn.show {
            display: block;
        }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <h2>PGdash</h2>
        <div class="profile">
            <img src="https://img.freepik.com/vecteurs-premium/icone-profil-avatar-par-defaut-image-utilisateur-medias-sociaux-icone-avatar-gris-silhouette-profil-vierge-illustration-vectorielle_561158-3467.jpg" alt="User Avatar" id="avatar">
            <span class="username" id="username">{{ username }}</span>
            <span class="status">Online</span>
        </div>
        <ul class="menu">
            <li><a href="#" onclick="openProfile()">Profile</a></li>
            <li><a href="#">Dashboard</a></li>
            <li><a href="#">Settings</a></li>
            <li><a href="#">Logout</a></li>
        </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <button class="hide-btn" id="toggle-sidebar" onclick="toggleSidebar()">Hide Sidebar</button>
        <h1>Dashboard Content</h1>

        <!-- Profile Section -->
        <div id="profile" style="display:none;">
            <h2>Profile</h2>
            <label for="avatar-upload">Change Avatar</label>
            <input type="file" id="avatar-upload" onchange="changeAvatar()" />
            <label for="username-input">Change Username</label>
            <input type="text" id="username-input" value="{{ username }}" />
            <button onclick="changeUsername()">Update Username</button>
        </div>
    </div>

    <script>
        const username = "{{ username }}";  // Use the username from the backend

        function toggleSidebar() {
            const sidebar = document.getElementById("sidebar");
            const mainContent = document.querySelector(".main-content");
            const button = document.getElementById("toggle-sidebar");

            sidebar.classList.toggle("hidden");
            mainContent.style.marginLeft = sidebar.classList.contains("hidden") ? "0" : "250px";
            button.textContent = sidebar.classList.contains("hidden") ? "Show Sidebar" : "Hide Sidebar";
        }

        function openProfile() {
            const profileSection = document.getElementById("profile");
            profileSection.style.display = profileSection.style.display === "none" ? "block" : "none";
        }

        function changeAvatar() {
            const fileInput = document.getElementById("avatar-upload");
            const avatar = document.getElementById("avatar");

            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    avatar.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        function changeUsername() {
            const newUsername = document.getElementById("username-input").value;
            document.getElementById("username").textContent = newUsername;
        }
    </script>
</body>
</html>
"""

# Route to render login page
@app.route('/')
def login_page():
    return render_template_string(HTML_TEMPLATE_LOGIN)

# Route to handle login logic
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    username = data['username']
    password = data['password']

    if username == USERNAME and password == PASSWORD:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# Route to render dashboard
@app.route('/dashboard')
def dashboard():
    username = request.args.get('username', '')
    return render_template_string(HTML_TEMPLATE_DASHBOARD, username=username)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)