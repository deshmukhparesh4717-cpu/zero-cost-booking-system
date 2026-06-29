#!/bin/bash

echo "🚀 Initializing Zero-Cost Booking System Setup..."

# 1. Create directory structure
mkdir -p app data

# 2. Check for Tesseract (Local dev check)
if ! command -v tesseract &> /dev/null
then
    echo "⚠️ Warning: Tesseract OCR is not installed locally. Deployment via Docker will handle this, but local tests might fail."
else
    echo "✅ Tesseract OCR found."
fi

# 3. Create .env template
cat <<EOT > .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
UPI_VPA=yourname@upi
MERCHANT_NAME="Your Business"
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your_key
EVOLUTION_INSTANCE=booking-bot
BACKEND_URL=http://localhost:8080/voice-receive
EOT

echo "✅ Created .env template. Please update it with your actual credentials."
echo "✅ Project files are ready for deployment."
echo "👉 To run locally: docker build -t booking-system . && docker run -p 8080:8080 --env-file .env booking-system"