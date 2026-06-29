# Zero-Cost Voice & WhatsApp Booking System

An automated booking infrastructure built using open-source tools and free cloud tiers.

## 🚀 Architecture
- **Voice**: Asterisk PBX -> Python STT (Google Web Speech API)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase / Neon)
- **Messaging**: Evolution API (WhatsApp)
- **OCR**: Tesseract (to verify payment screenshots)
- **Payments**: Custom UPI Intent Strings (Zero gateway fees)

## 🛠️ Prerequisites
1. **Supabase/Neon**: Create a free PostgreSQL database.
2. **Evolution API**: Host an instance (e.g., on a VPS or Home Server) and connect your WhatsApp.
3. **Render/Fly.io**: Account for hosting the FastAPI backend (via Docker).
4. **Asterisk**: A running PBX instance to handle incoming voice calls.

## ⚙️ Environment Variables
Set these on your hosting platform:
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `UPI_VPA` | Your UPI ID for payments | `yourname@okaxis` |
| `MERCHANT_NAME` | Your Business Name | `Star Cafe` |
| `EVOLUTION_API_URL` | URL of your Evolution API | `https://evo-api.yoursite.com` |
| `EVOLUTION_API_KEY` | Auth token for Evolution API | `your_secret_token` |
| `EVOLUTION_INSTANCE` | Name of your WhatsApp instance | `booking-bot` |

## 📦 Deployment Steps

### 1. Backend (FastAPI + OCR)
Deploy to Render or Fly.io using the provided `Dockerfile`. It automatically installs Tesseract OCR.
- Point the Webhook in Evolution API to: `https://your-app.render.com/whatsapp-webhook`

### 2. Database
Run `schema.sql` in your SQL editor (Supabase/Neon) or let SQLAlchemy auto-create tables on first run.

### 3. Asterisk Integration (STT)
1. Copy `app/stt_handler.py` to your Asterisk server.
2. Update your dialplan (`extensions.conf`):
   ```ini
   [booking-context]
   exten => s,1,Answer()
   same => n,Record(/tmp/msg.wav,3,30)
   same => n,System(python3 /path/to/stt_handler.py /tmp/msg.wav)
   same => n,Playback(vm-thankyou)
   same => n,Hangup()
   ```

## 🔄 The Flow
1. **Call**: Customer calls; Asterisk records and transcribes the intent.
2. **QR**: Backend sends a UPI QR code to the customer via WhatsApp.
3. **Pay**: Customer pays and sends a screenshot of the receipt back to WhatsApp.
4. **Verify**: Backend performs OCR on the image, verifies the Txn ID, and confirms the booking in the DB.

## 📜 License
MIT