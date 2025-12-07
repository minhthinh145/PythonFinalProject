#!/bin/bash
# Test API Script for DKHP System
# Usage: ./test_api.sh [sv|pdt|gv|tlk|tk]

API_URL="http://localhost/api"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Account credentials (verified working)
SV_USER="49.01.104.145"
SV_PASS="123456"
PDT_USER="pdt01"
PDT_PASS="123456"
GV_USER="GV001"
GV_PASS="123456"
TLK_USER="tlk.cntt"
TLK_PASS="123456"
TK_USER="tk.cntt"
TK_PASS="123456"

# Try passwords (fallback)
PASSWORDS=("123456" "12345" "password123")

# Login function - API uses Vietnamese field names
login() {
    local username=$1
    local password=$2
    local response=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"tenDangNhap\":\"$username\", \"matKhau\":\"$password\"}")
    
    # API returns 'token' not 'accessToken'
    local token=$(echo "$response" | jq -r '.data.token // empty')
    local success=$(echo "$response" | jq -r '.isSuccess // false')
    
    if [ "$success" = "true" ] && [ -n "$token" ]; then
        echo "$token"
    else
        echo ""
    fi
}

# Try login with multiple passwords
try_login() {
    local username=$1
    local role=$2
    
    echo -e "${YELLOW}=== Testing $role Login ($username) ===${NC}"
    
    for pwd in "${PASSWORDS[@]}"; do
        echo -n "  Trying password: $pwd ... "
        TOKEN=$(login "$username" "$pwd")
        if [ -n "$TOKEN" ]; then
            echo -e "${GREEN}SUCCESS${NC}"
            echo "  Token: ${TOKEN:0:50}..."
            eval "${role}_TOKEN=\"$TOKEN\""
            return 0
        else
            echo -e "${RED}FAILED${NC}"
        fi
    done
    
    echo -e "${RED}  All passwords failed for $username${NC}"
    return 1
}

# API test function
test_api() {
    local method=$1
    local endpoint=$2
    local token=$3
    local data=$4
    
    echo -e "\n${YELLOW}>>> $method $endpoint${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$API_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -X "$method" "$API_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Pretty print
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
}

# Main
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DKHP API Test Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Login all accounts
try_login "$SV_USER" "SV"
try_login "$PDT_USER" "PDT"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Export these tokens:${NC}"
echo -e "${GREEN}========================================${NC}"
echo "export SV_TOKEN=\"$SV_TOKEN\""
echo "export PDT_TOKEN=\"$PDT_TOKEN\""

# Quick test
if [ -n "$SV_TOKEN" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Quick SV API Tests${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    test_api "GET" "/hoc-ky-hien-hanh" "$SV_TOKEN"
    test_api "GET" "/sv/tra-cuu-hoc-phan?hoc_ky_id=f416c2df-acea-4dd5-9e24-e8a36a56276b" "$SV_TOKEN"
fi
