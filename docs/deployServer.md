# Running the Application with systemd

## 1. Create the service

```bash
sudo nano /etc/systemd/system/webviewer.service
```

Add:

```ini
[Unit]
Description=WebViewer Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Internship_Project_Helsinki_University
ExecStart=/home/ubuntu/anaconda3/envs/webViewer/bin/gunicorn --workers 1 --timeout 600 --bind 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 2. Start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable webviewer
sudo systemctl start webviewer
```

## 3. Check the service

```bash
sudo systemctl status webviewer
```

## 4. View the logs

```bash
sudo journalctl -u webviewer -f
```

## 5. Stop the service

```bash
sudo systemctl stop webviewer
```

## Access the application

Open:

```text
http://SERVER_PUBLIC_IP:5000
```
