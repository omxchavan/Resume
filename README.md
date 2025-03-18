# Resume Platform

A web application for resume management, candidate profiles, and recruiter dashboards.

## Local Development

1. Clone the repository
2. Create a virtual environment:

```
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Set up environment variables:

```
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:

```
flask db upgrade
```

6. Run the development server:

```
python app.py
```

## Production Deployment

### Option 1: Heroku Deployment

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:

```
heroku login
```

3. Create a new Heroku app:

```
heroku create your-app-name
```

4. Add a PostgreSQL database:

```
heroku addons:create heroku-postgresql:hobby-dev
```

5. Set environment variables:

```
heroku config:set SECRET_KEY=your_strong_secret_key
heroku config:set FLASK_ENV=production
heroku config:set GEMINI_API_KEY=your_gemini_api_key
```

6. Deploy the application:

```
git push heroku main
```

7. Initialize the database:

```
heroku run flask db upgrade
```

### Option 2: Traditional VPS (e.g., DigitalOcean, AWS EC2)

1. Set up a server with Ubuntu/Debian
2. Install required packages:

```
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. Clone the repository:

```
git clone https://your-repository-url.git
cd your-project
```

4. Create a virtual environment and install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Set up environment variables:

```
cp .env.example .env
# Edit .env with your configuration
```

6. Set up Gunicorn systemd service:
   Create a file at `/etc/systemd/system/resume-platform.service`:

```
[Unit]
Description=Resume Platform Gunicorn Service
After=network.target

[Service]
User=your_username
Group=your_group
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/project/venv/bin"
ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

7. Set up Nginx:
   Create a file at `/etc/nginx/sites-available/resume-platform`:

```
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. Enable the Nginx site:

```
sudo ln -s /etc/nginx/sites-available/resume-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

9. Start the Gunicorn service:

```
sudo systemctl start resume-platform
sudo systemctl enable resume-platform
```

## Database Management

For production, it's recommended to use PostgreSQL instead of SQLite:

1. Install PostgreSQL
2. Create a database and user
3. Update your `.env` file with the PostgreSQL connection string:

```
DATABASE_URL=postgresql://username:password@localhost/dbname
```

4. Run migrations:

```
flask db upgrade
```

## Security Considerations

1. Always use HTTPS in production
2. Set a strong SECRET_KEY
3. Keep your .env file secure and never commit it to version control
4. Regularly update dependencies
5. Consider using a web application firewall (WAF)
