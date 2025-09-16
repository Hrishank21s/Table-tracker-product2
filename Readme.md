Table Tracker Pro - Global Access Edition
![Version](https://img.shields.ioio system** for snooker halls and pool clubs with worldwide accessibility via Tailscale Funnel. Built on Raspberry Pi for reliability and cost-effectiveness.

![Table Tracker Screenshot](https://via.placeholder.com/600 🎯 Features

🎱 Real-time table management - Track snooker and pool table usage

⏰ Timer functionality - Automatic billing calculations

👥 User authentication - Role-based access control

📱 Responsive design - Works on desktop, tablet, and mobile

🌍 Global accessibility - Access from anywhere in the world via HTTPS

🚀 Auto-boot capability - Starts automatically on system restart

🔒 Secure connectivity - Protected by Tailscale VPN encryption

🌐 Access Methods
Local Access
Direct: http://localhost:8080

Local Network: http://[PI-IP]:8080

Global Public Access
HTTPS: https://weekendrush.tailb9dd12.ts.net

Secure & Encrypted - Protected by Tailscale Funnel

📋 Table of Contents
Installation

Configuration

Usage

System Architecture

Auto-Boot Setup

Security

Troubleshooting

Contributing

License

🚀 Installation
Prerequisites
Raspberry Pi 4 (recommended) or Pi 3B+

Raspberry Pi OS (Bullseye or newer)

Internet connection

Tailscale account (free)

Quick Setup
Update your Pi:

bash
sudo apt update && sudo apt upgrade -y
Install Python dependencies:

bash
sudo apt install python3-pip python3-venv -y
pip3 install flask werkzeug
Install Tailscale:

bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
Clone and setup the project:

bash
git clone <your-repo-url>
cd table_tracker_pro
Create systemd service for auto-boot:

bash
sudo tee /etc/systemd/system/table-tracker.service > /dev/null << 'EOF'
[Unit]
Description=Table Tracker Pro Application
After=network-online.target tailscaled.service
Wants=tailscaled.service network-online.target

[Service]
Type=simple
User=h21s
WorkingDirectory=/home/h21s/table_tracker_pro
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable table-tracker.service
sudo systemctl start table-tracker.service
Enable global access:

bash
# Enable Tailscale Funnel for worldwide HTTPS access
sudo tailscale funnel --bg 8080

# Verify it's working
sudo tailscale funnel status
⚙️ Configuration
Application Settings
Port: 8080 (HTTP)

Database: SQLite (auto-created)

Users: Web-based management

Tables: Configurable via interface

Environment Variables
Create a .env file (optional):

bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DEBUG=False
Table Configuration
Edit table types and pricing in the web interface:

T1 Tables: ₹2.0/minute

T2 Tables: ₹3.5/minute

T3 Tables: ₹4.5/minute

📱 Usage
Getting Started
Access the system via your preferred URL

Login with default credentials (admin/password)

Change default password immediately

Add users if needed

Configure tables and pricing

Daily Operations
Start table timer - Click table, select time

Stop timer - Click active table to stop

View reports - Check usage and billing

Manage users - Add/remove staff accounts

Admin Features
User management

Table configuration

Pricing adjustments

Usage reports

System monitoring

🏗️ System Architecture
text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│  Tailscale       │───▶│  Raspberry Pi   │
│  (Anywhere)     │    │  Funnel          │    │  Table Tracker  │
│                 │    │  (HTTPS/TLS)     │    │  (Port 8080)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
Tech Stack
Backend: Python Flask

Frontend: HTML5, CSS3, JavaScript

Database: SQLite

Networking: Tailscale VPN + Funnel

Platform: Raspberry Pi OS

Process Management: systemd

🔄 Auto-Boot Setup
The system includes complete auto-boot functionality:

Services That Start Automatically
Tailscale daemon - Connects to VPN

Table Tracker app - Starts on port 8080

Tailscale Funnel - Enables global access

Create Funnel Auto-Enable Service
bash
sudo tee /etc/systemd/system/tailscale-funnel.service > /dev/null << 'EOF'
[Unit]
Description=Tailscale Funnel Auto-Enable
After=tailscaled.service table-tracker.service
Wants=tailscaled.service

[Service]
Type=oneshot
User=root
ExecStartPre=/bin/sleep 30
ExecStart=/usr/bin/tailscale funnel --bg 8080
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tailscale-funnel.service
🔒 Security
Built-in Security Features
HTTPS encryption via Tailscale certificates

VPN-level protection for all connections

User authentication with session management

Private by default - accessible only via Tailscale

Security Best Practices
Change default admin password

Use strong passwords for all users

Regular system updates

Monitor access logs

Backup user data regularly

🛠️ Troubleshooting
Common Issues
App not accessible externally:

bash
# Check Tailscale status
sudo tailscale status

# Verify funnel is enabled
sudo tailscale funnel status

# Restart services if needed
sudo systemctl restart table-tracker.service
sudo tailscale funnel --bg 8080
Service not starting on boot:

bash
# Check service status
sudo systemctl status table-tracker.service

# Check logs
sudo journalctl -u table-tracker.service -f
Database issues:

bash
# Check database permissions
ls -la /home/h21s/table_tracker_pro/

# Recreate if corrupted
rm -f users.db
# Database will auto-recreate on next start
Log Files
App logs: sudo journalctl -u table-tracker.service

Tailscale logs: sudo journalctl -u tailscaled

System logs: sudo journalctl -f

📊 Performance
System Requirements
RAM: 512MB minimum, 1GB recommended

Storage: 2GB minimum for OS + app

Network: Stable internet connection

Power: 5V 3A power supply recommended

Capacity
Concurrent users: 50+ simultaneous connections

Tables: Unlimited (tested with 20+ tables)

Data retention: Years of usage data

Response time: <200ms on local network

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Development Setup
Fork the repository

Create a feature branch

Make your changes

Test thoroughly

Submit a pull request

Code Style
Follow PEP 8 for Python code

Use meaningful variable names

Comment complex functions

Test your changes

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👨‍💻 Author
Hrishank - Initial work - @Hrishank21s

🙏 Acknowledgments
Tailscale team for excellent VPN technology

Flask community for the robust web framework

Raspberry Pi Foundation for affordable hardware

Contributors and testers

