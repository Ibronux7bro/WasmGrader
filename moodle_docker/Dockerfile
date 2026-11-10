FROM moodlehq/moodle-php-apache:8.2

# Install curl and mariadb client
RUN apt-get update && apt-get install -y curl default-mysql-client && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/www/html /var/moodledata && \
    chown -R www-data:www-data /var/www/html /var/moodledata

# Copy entrypoint
COPY moodle-entrypoint.sh /moodle-entrypoint.sh
RUN chmod +x /moodle-entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/moodle-entrypoint.sh"]
