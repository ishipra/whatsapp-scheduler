# Running WhatsApp Scheduler

## Environment Variables Required

Make sure you have a `.env` file with:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+xxxxxxxx
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Prerequisites

**IMPORTANT: Run migrations FIRST before starting any services:**
```bash
python manage.py migrate
```

This creates the required database tables. You only need to do this once (or after pulling new migrations).

## Option 1: Run All Services Together (Development)

```bash
./run_all.sh
```

This will run:
1. Database migrations (automatically)
2. Django server (port 8000)
3. Scheduler loop (enqueues messages every 30s)
4. Worker (processes messages from Redis)

## Option 2: Run Commands Separately (4 Terminal Windows)

**IMPORTANT: Run migrations FIRST before starting any services:**
```bash
python manage.py migrate
```

### Terminal 1: Start Redis
```bash
brew services start redis
```

### Terminal 2: Django Server
```bash
python manage.py runserver
```

### Terminal 3: Scheduler Loop
```bash
python manage.py scheduler_loop
```

### Terminal 4: Worker
```bash
python manage.py worker
```

## Single Pod Deployment

For production deployment in a single pod/container, use:

```bash
./start.sh
```

Or set as your container's CMD/ENTRYPOINT. This script:
- Runs migrations on startup
- Starts scheduler_loop in background
- Starts worker in background  
- Runs Django server in foreground (keeps container alive)

**Yes, a single pod can handle all of this!** The scheduler_loop and worker run as background processes, while the Django server runs in the foreground.

