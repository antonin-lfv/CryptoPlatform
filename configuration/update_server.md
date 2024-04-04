# Stop the application
```bash
sudo systemctl stop CryptoPlatform
```

# Go into the project directory
```bash
cd /home/debian/CryptoPlatform
```

# Pull the latest changes
```bash
sudo git pull origin main
```

# Install the latest dependencies
```bash
pip install -r requirements.txt
```

# Migration of the database
Init migration, run the following command:
```bash
flask db init
```

To create a new migration, run the following command:
```bash
flask db migrate -m "migration message"
```

To apply the migration, run the following command:
```bash
flask db upgrade
```

To delete the history of the migration, run the following command:
```bash
sudo rm -rf migrations/
```

# Start the application
```bash
sudo systemctl start CryptoPlatform
```

# Check the status of the application
```bash
sudo systemctl status CryptoPlatform
```

# Check the status with journalctl
```bash
sudo journalctl -u CryptoPlatform
```

# Check the logs
```bash
sudo journalctl -u CryptoPlatform -e
```
