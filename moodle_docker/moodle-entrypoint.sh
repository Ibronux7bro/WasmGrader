#!/bin/bash
set -e

MOODLE_DIR=/var/www/html
MOODLE_DATA=/var/moodledata

echo "======================================"
echo "  WasmGrader Moodle Setup Starting..."
echo "======================================"

# Step 1: Download Moodle if not present
if [ ! -f "$MOODLE_DIR/version.php" ]; then
    echo "[1/5] Downloading Moodle 4.3..."
    curl -fsSL https://download.moodle.org/download.php/direct/stable403/moodle-latest-403.tgz -o /tmp/moodle.tgz
    echo "[2/5] Extracting Moodle..."
    tar -xzf /tmp/moodle.tgz -C $MOODLE_DIR --strip-components=1
    rm /tmp/moodle.tgz
    chown -R www-data:www-data $MOODLE_DIR
    echo "[2/5] Done."
else
    echo "[1/5] Moodle files already present."
fi

# Step 2: Create data dir
mkdir -p $MOODLE_DATA
chown -R www-data:www-data $MOODLE_DATA
chmod 777 $MOODLE_DATA

# Step 3: Wait for DB
echo "[3/5] Waiting for MariaDB..."
for i in $(seq 1 30); do
    if php -r "new mysqli('mariadb','bn_moodle','bitnami','bitnami_moodle');" 2>/dev/null; then
        echo "      MariaDB is ready!"
        break
    fi
    echo "      Attempt $i/30 — waiting 3s..."
    sleep 3
done

# Step 4: Install Moodle if config.php missing
if [ ! -f "$MOODLE_DIR/config.php" ]; then
    echo "[4/5] Running Moodle CLI installer..."
    php $MOODLE_DIR/admin/cli/install.php \
        --wwwroot=http://localhost \
        --dataroot=$MOODLE_DATA \
        --dbtype=mariadb \
        --dbhost=mariadb \
        --dbname=bitnami_moodle \
        --dbuser=bn_moodle \
        --dbpass=bitnami \
        --adminuser=admin \
        --adminpass=AdminPassword123! \
        --adminemail=admin@wasmgrader.local \
        --fullname="WasmGrader University" \
        --shortname=WGU \
        --agree-license \
        --non-interactive
    echo "[4/5] Moodle installed successfully!"
else
    echo "[4/5] Moodle already configured."
fi

# Step 5: Start Apache
echo "[5/5] Starting Apache..."
export APACHE_DOCUMENT_ROOT=/var/www/html
export APACHE_RUN_USER=www-data
export APACHE_RUN_GROUP=www-data
export APACHE_LOG_DIR=/var/log/apache2
export APACHE_PID_FILE=/var/run/apache2/apache2.pid
export APACHE_RUN_DIR=/var/run/apache2
export APACHE_LOCK_DIR=/var/lock/apache2

# Fix any remaining variable references in Apache config
find /etc/apache2 -name "*.conf" -exec grep -l 'APACHE_DOCUMENT_ROOT' {} \; | \
  xargs -I{} sed -i 's|\${APACHE_DOCUMENT_ROOT}|/var/www/html|g' {}

exec apache2-foreground
