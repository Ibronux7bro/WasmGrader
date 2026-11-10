#!/bin/bash
set -e

MOODLE_DIR=/var/www/html
DATA_DIR=/var/moodledata
CONFIG_FILE=$MOODLE_DIR/config.php

# Wait for MariaDB
echo "[*] Waiting for MariaDB to be ready..."
for i in $(seq 1 30); do
    if php -r "
        \$conn = @mysqli_connect(
            getenv('MOODLE_DB_HOST') ?: 'mariadb',
            getenv('MOODLE_DB_USER') ?: 'bn_moodle',
            getenv('MOODLE_DB_PASS') ?: 'bitnami',
            getenv('MOODLE_DB_NAME') ?: 'bitnami_moodle',
            getenv('MOODLE_DB_PORT') ?: 3306
        );
        exit(\$conn ? 0 : 1);
    " 2>/dev/null; then
        echo "[+] MariaDB is ready!"
        break
    fi
    echo "    Attempt $i/30 - waiting..."
    sleep 3
done

# Generate config.php if not present
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[*] Generating Moodle config.php..."
    cat > $CONFIG_FILE <<EOF
<?php
unset(\$CFG);
global \$CFG;
\$CFG = new stdClass();

\$CFG->dbtype    = 'mysqli';
\$CFG->dblibrary = 'native';
\$CFG->dbhost    = '${MOODLE_DB_HOST:-mariadb}';
\$CFG->dbname    = '${MOODLE_DB_NAME:-bitnami_moodle}';
\$CFG->dbuser    = '${MOODLE_DB_USER:-bn_moodle}';
\$CFG->dbpass    = '${MOODLE_DB_PASS:-bitnami}';
\$CFG->prefix    = 'mdl_';
\$CFG->dboptions = array(
    'dbpersist' => 0,
    'dbport'    => ${MOODLE_DB_PORT:-3306},
    'dbsocket'  => '',
);

\$CFG->wwwroot   = 'http://localhost';
\$CFG->dataroot  = '$DATA_DIR';
\$CFG->admin     = 'admin';
\$CFG->directorypermissions = 0777;

\$CFG->wasmgrader_api_url = '${WASM_API_URL:-http://wasm-evaluator:8080}';
\$CFG->wasmgrader_api_key = '${WASM_API_KEY:-moodle_wasm_secret_key_2026}';

require_once(__DIR__ . '/lib/setup.php');
EOF
    chown www-data:www-data $CONFIG_FILE
fi

# Install Moodle if not installed
if php $MOODLE_DIR/admin/cli/isinstalled.php 2>/dev/null | grep -q "false"; then
    echo "[*] Running Moodle installation..."
    php $MOODLE_DIR/admin/cli/install_database.php \
        --agree-license \
        --adminuser="${MOODLE_ADMIN_USER:-admin}" \
        --adminpass="${MOODLE_ADMIN_PASS:-AdminPassword123!}" \
        --adminemail="${MOODLE_ADMIN_EMAIL:-admin@wasmgrader.local}" \
        --fullname="WasmGrader LMS" \
        --shortname="WasmGrader" \
        --lang=en \
        --non-interactive \
        2>&1 || echo "[!] Install may have already run."
    echo "[+] Moodle installed!"
fi

# Copy WasmGrader plugin if present
PLUGIN_SRC="/wasmcode_plugin"
PLUGIN_DST="$MOODLE_DIR/mod/assign/submission/wasmcode"
if [ -d "$PLUGIN_SRC" ] && [ ! -d "$PLUGIN_DST" ]; then
    echo "[*] Installing WasmGrader Moodle plugin..."
    cp -r $PLUGIN_SRC $PLUGIN_DST
    chown -R www-data:www-data $PLUGIN_DST
    echo "[+] Plugin installed at $PLUGIN_DST"
fi

echo "[+] Starting Apache..."
exec "$@"
