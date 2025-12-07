# Payment Gateway Setup Guide

## Current Issues Fixed ✅

1. **Frontend Access**: Use `http://localhost` instead of `http://localhost:5173`
2. **Return URL**: Updated to `http://localhost/payment/result`
3. **Requests module**: Added to requirements.txt and installed

## Testing Payment with MoMo/VNPay/ZaloPay

### 1. Access the Application

- **Frontend**: http://localhost (mapped from port 5173)
- **Backend API**: http://localhost:8000

### 2. Setup ngrok for IPN Testing

MoMo/VNPay/ZaloPay need to send IPN (Instant Payment Notification) callbacks to your backend. Since your backend is running locally, you need **ngrok** to expose it to the internet.

#### Install ngrok:

```bash
# Download and install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Or download directly
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

#### Run ngrok:

```bash
# Start ngrok tunnel to backend (port 8000)
ngrok http 8000
```

You'll see output like:

```
Forwarding  https://abc-123-xyz.ngrok-free.app -> http://localhost:8000
```

#### Update .env file:

Copy the ngrok URL and update your `.env`:

```env
UNIFIED_IPN_URL=https://your-ngrok-url.ngrok-free.app/api/payment/ipn
```

Then restart backend:

```bash
docker compose restart backend
```

### 3. Test Payment Flow

1. **Login** as student: `49.01.104.145` / `123456`
2. Go to **Thanh toán học phí** page
3. Select semester (Học kỳ)
4. Click **Thanh toán** button
5. Choose payment method:
   - MoMo
   - VNPay
   - ZaloPay
6. You'll be redirected to payment gateway
7. After payment, you'll return to `http://localhost/payment/result`
8. MoMo will send IPN to your ngrok URL

### 4. Monitor IPN Callbacks

Watch backend logs to see IPN processing:

```bash
docker logs dkhp-backend -f
```

You should see:

```
[IPN] Received from momo: {...}
```

### 5. Testing Without Real Payment

For development, you can use MoMo/VNPay **sandbox environments**:

- **MoMo Test**: Use test credentials (already configured in .env)
- **VNPay Sandbox**: https://sandbox.vnpayment.vn/
- **ZaloPay Sandbox**: Use test app credentials

## Current Configuration

### Environment Variables (.env)

```env
# Frontend runs on port 80 (mapped from 5173)
FRONTEND_URL=http://localhost

# IPN callback URL (requires ngrok)
UNIFIED_IPN_URL=https://unrustic-irving-privative.ngrok-free.dev/api/payment/ipn

# MoMo Test Credentials
MOMO_PARTNER_CODE=MOMO
MOMO_ACCESS_KEY=F8BBA842ECF85
MOMO_SECRET_KEY=K951B6PE1waDMi640xX08PD3vg6EkVlz
MOMO_ENDPOINT=https://test-payment.momo.vn
```

## Troubleshooting

### Issue: "No module named 'requests'"

**Fixed**: Added `requests>=2.31.0` to requirements.txt and rebuilt backend

### Issue: "Unable to connect to localhost:5173"

**Solution**: Use `http://localhost` (port 80) instead

### Issue: IPN not received

**Check**:

1. ngrok is running: `ngrok http 8000`
2. UNIFIED_IPN_URL in .env matches ngrok URL
3. Backend restarted after changing .env
4. Check ngrok web interface: http://127.0.0.1:4040

### Issue: Payment redirect fails

**Check**:

1. FRONTEND_URL is set to `http://localhost` (not :5173)
2. Payment result page exists at `/payment/result`
3. Router has the route configured

## Quick Start Script

Run this to start everything:

```bash
# 1. Start Docker containers
docker compose up -d

# 2. Start ngrok in new terminal
ngrok http 8000

# 3. Copy ngrok URL and update .env
# Then restart backend
docker compose restart backend

# 4. Access frontend
# http://localhost
```

## Payment Flow Diagram

```
Student Browser
    ↓
[Thanh toán học phí] → POST /api/payment/create
    ↓
Backend creates payment
    ↓
Redirect to MoMo/VNPay/ZaloPay
    ↓
Student completes payment
    ↓
Payment gateway sends IPN → ngrok → POST /api/payment/ipn
    ↓
Backend updates payment status
    ↓
Student redirected → http://localhost/payment/result
```
