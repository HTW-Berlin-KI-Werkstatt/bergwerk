FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

ENV SERVER ${SERVER}
ENV MEDIAWIKI_ADMIN ${MEDIAWIKI_ADMIN}
ENV MEDIAWIKI_ADMIN_PASSWORD ${MEDIAWIKI_ADMIN_PASSWORD}

# Directories locations
ENV HTML_DIR /var/www/html
ENV DATA_DIR /var/www/data
ENV WIKI_DIR ${HTML_DIR}/w

ENV NGINX_CONFIG_FILE_BASE ./config/nginx/nginx.conf
ENV NGINX_CONFIG_FILE_CUSTOM ./config/nginx/default.conf

# Media Wiki Version
ENV MEDIAWIKI_MAJOR_VERSION 1.41
ENV MEDIAWIKI_VERSION 1.41.1
ENV MEDIAWIKI_EXT_VERSION REL1_41

# Create directory for web site files and data files
RUN mkdir -p ${WIKI_DIR} && mkdir -p ${DATA_DIR}
RUN chown -R www-data:www-data ${DATA_DIR}
RUN chown -R www-data:www-data ${WIKI_DIR}

RUN mkdir -p ${WIKI_DIR}/images/
RUN chmod -R 777 ${WIKI_DIR}/images/
RUN chown -R www-data:www-data ${WIKI_DIR}/images/

# Volumes to store database and medias (images...) files
VOLUME ${DATA_DIR}

# We work in WikiMedia root directory
WORKDIR ${WIKI_DIR}


RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-requests \
    jq \
    sudo \
    git \
    composer \
    curl \
    nginx \
    php8.3-fpm \
    php8.3-sqlite3 \
    php8.3-gd \
    php8.3-xml \
    php8.3-curl \
    php8.3-mbstring \
    php8.3-intl \
    php8.3-mysql \
    zip \
    unzip \
    php-zip \
    ca-certificates \
    sqlite3 && \
    apt-get clean

# MediaWiki setup
RUN curl -fSL "https://releases.wikimedia.org/mediawiki/${MEDIAWIKI_MAJOR_VERSION}/mediawiki-${MEDIAWIKI_VERSION}.tar.gz" -o mediawiki.tar.gz \
	&& tar -xz --strip-components=1 -f mediawiki.tar.gz \
	&& rm mediawiki.tar.gz \
	&& chown -R www-data:www-data skins cache

COPY config/mediawiki/composer.local.json ${WIKI_DIR}/composer.local.json

# Copy Nginx configuration
COPY ${NGINX_CONFIG_FILE_BASE} /etc/nginx/nginx.conf
COPY ${NGINX_CONFIG_FILE_CUSTOM} /etc/nginx/conf.d/default.conf

# Configure PHP-fpm
COPY config/php-fpm/*.conf /etc/php/8.3/fpm/pool.d/
COPY config/php-fpm/*.ini /etc/php/8.3/fpm/conf.d/

COPY scripts/start.sh /usr/local/bin/
COPY scripts/load_data.py /usr/local/bin/
COPY scripts/mediawiki-init.sh /usr/local/bin/
RUN chmod a+x /usr/local/bin/*.sh

COPY data /tmp/data
COPY configuration.txt /tmp/data/configuration.wikitext

# Expose port 80
EXPOSE 80

ENTRYPOINT ["start.sh"]
CMD ["sleep", "infinity"]
