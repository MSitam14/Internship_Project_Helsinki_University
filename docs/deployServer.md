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

Environment="PATH=/home/ubuntu/anaconda3/envs/webViewer/bin:/home/ubuntu/anaconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"

ExecStart=/home/ubuntu/anaconda3/envs/webViewer/bin/gunicorn \
    --workers 1 \
    --timeout 3600 \
    --bind 0.0.0.0:5000 \
    wsgi:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

(may need to change the `User`, `WorkingDirectory`, and `Environment` paths based on your setup)

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
sudo journalctl -u webviewer -f -o cat
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
