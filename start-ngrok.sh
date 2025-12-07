#!/bin/bash
# Start ngrok tunnel for payment IPN testing

echo "🚀 Starting ngrok tunnel for backend (port 8000)"
echo ""
echo "After ngrok starts:"
echo "1. Copy the HTTPS forwarding URL (e.g., https://abc-123.ngrok-free.app)"
echo "2. Update .env file:"
echo "   UNIFIED_IPN_URL=https://your-ngrok-url.ngrok-free.app/api/payment/ipn"
echo "3. Restart backend: docker compose restart backend"
echo ""
echo "Press Ctrl+C to stop ngrok"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found!"
    echo ""
    echo "Install ngrok:"
    echo "  wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    echo "  tar -xvzf ngrok-v3-stable-linux-amd64.tgz"
    echo "  sudo mv ngrok /usr/local/bin/"
    echo ""
    echo "Or use apt:"
    echo "  curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null"
    echo "  echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list"
    echo "  sudo apt update && sudo apt install ngrok"
    exit 1
fi

# Start ngrok
ngrok http 8000
