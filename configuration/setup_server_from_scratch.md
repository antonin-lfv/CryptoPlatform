# First installation
sudo apt update
sudo apt upgrade

# Get git
sudo apt install git

# Get ufw
sudo apt-get install ufw

# Get pyenv
curl https://pyenv.run | bash

# Pyenv config
nano ~/.bashrc
# Add the following lines
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
# Save and exit
source ~/.bashrc

# Same for profile
nano ~/.profile
# Add the following lines
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
# Save and exit
source ~/.profile

# Install python 3.11.0
pyenv install 3.11.0

# Init the environment
pyenv global 3.11.0

# Init env file
```bash
echo "ADMIN_EMAIL=$mail$" > .env
echo "ADMIN_USERNAME=$username$" >> .env
echo "ADMIN_PASSWORD=$password$" >> .env
```

# Clone the repo
git clone https://github.com/antonin-lfv/CryptoPlatform.git CryptoPlatform
cd CryptoPlatform

# Requirements
pip install -r requirements.txt

# reverse proxy
sudo apt install nginx

# nginx config
sudo nano /etc/nginx/sites-available/CryptoPlatform
# Add the following lines
```nginx
server {
    listen 80;
    server_name 51.178.46.60;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

# activate the config
sudo ln -s /etc/nginx/sites-available/CryptoPlatform /etc/nginx/sites-enabled/

# test the config
sudo nginx -t

# restart nginx
sudo systemctl restart nginx

# firewall
sudo ufw allow 'Nginx Full'

# Use systemd to manage the Gunicorn process
sudo nano /etc/systemd/system/CryptoPlatform.service
# Add the following lines
# (Gunicorn found by the command : which gunicorn)
```
[Unit]
Description=Gunicorn instance to serve CryptoPlatform
After=network.target

[Service]
User=debian
Group=www-data
WorkingDirectory=/home/debian/CryptoPlatform
ExecStart=/home/debian/.pyenv/shims/gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

# Start and enable the service
sudo systemctl start CryptoPlatform
sudo systemctl enable CryptoPlatform

# Check the status
sudo systemctl status CryptoPlatform