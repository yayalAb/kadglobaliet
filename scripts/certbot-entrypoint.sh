#!/bin/sh
set -e

# Show logs immediately when stdout is not a TTY (docker compose logs)
export PYTHONUNBUFFERED=1

DOMAIN="${SSL_DOMAIN:-kadglobaltrading.com}"
EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"
WEBROOT=/var/www/certbot
CERT="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
RETRY_SECONDS="${CERTBOT_RETRY_SECONDS:-300}"
RENEW_INTERVAL="${CERTBOT_RENEW_INTERVAL:-43200}"

echo "Certbot: domain=${DOMAIN} www.${DOMAIN} email=${EMAIL}"

# Nginx must be up to answer the ACME webroot challenge
echo "Certbot: waiting 15s for nginx..."
sleep 15
echo "Certbot: nginx wait complete"

request_certificate() {
    certbot certonly --webroot \
        -w "$WEBROOT" \
        -d "$DOMAIN" \
        -d "www.${DOMAIN}" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive \
        --keep-until-expiring \
        --expand
}

if [ ! -f "$CERT" ]; then
    echo "Certbot: requesting initial certificate for ${DOMAIN}..."
    until request_certificate; do
        echo "Certbot: certificate request failed — retrying in ${RETRY_SECONDS}s (check DNS points to this server)"
        sleep "$RETRY_SECONDS"
    done
    echo "Certbot: initial certificate obtained"
else
    echo "Certbot: existing certificate found at ${CERT}"
fi

echo "Certbot: watching for renewals every ${RENEW_INTERVAL}s"

while true; do
    sleep "$RENEW_INTERVAL"
    if certbot renew --webroot -w "$WEBROOT" --quiet; then
        echo "Certbot: renewal check complete"
    fi
done
