FROM php:8.2-apache

# Install PHP extensions required by Moodle
RUN apt-get update && apt-get install -y \
    libpng-dev libjpeg-dev libfreetype6-dev \
    libzip-dev libxml2-dev libicu-dev \
    libxslt1-dev libssl-dev curl unzip \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
       gd zip xml intl xsl soap opcache \
       mysqli pdo pdo_mysql \
    && pecl install redis && docker-php-ext-enable redis \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# PHP configuration for Moodle
RUN echo "max_input_vars = 5000" >> /usr/local/etc/php/conf.d/moodle.ini \
    && echo "post_max_size = 128M" >> /usr/local/etc/php/conf.d/moodle.ini \
    && echo "upload_max_filesize = 128M" >> /usr/local/etc/php/conf.d/moodle.ini \
    && echo "memory_limit = 256M" >> /usr/local/etc/php/conf.d/moodle.ini \
    && echo "max_execution_time = 300" >> /usr/local/etc/php/conf.d/moodle.ini

# Download Moodle 4.3 (LTS, stable on Docker)
RUN curl -fsSL https://download.moodle.org/download.php/direct/stable403/moodle-latest-403.tgz \
    -o /tmp/moodle.tgz \
    && tar -xzf /tmp/moodle.tgz -C /var/www/html --strip-components=1 \
    && rm /tmp/moodle.tgz \
    && chown -R www-data:www-data /var/www/html

# Moodle data directory
RUN mkdir -p /var/moodledata && chown www-data:www-data /var/moodledata

# Apache config
RUN a2enmod rewrite
COPY moodle-apache.conf /etc/apache2/sites-available/000-default.conf

# Entrypoint script
COPY moodle-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
