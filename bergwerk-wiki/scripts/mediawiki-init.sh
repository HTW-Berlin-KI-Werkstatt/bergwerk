#!/bin/bash
echo "Mediawiki initialization script for database : $MYSQL_DATABASE on $SERVER."

if [ -f "$WIKI_DIR/LocalSettings.php" ]; then
    echo "MediaWiki is already installed. Exiting..."
    exit 0
fi

while true; do
    sudo -u www-data php maintenance/install.php \
        --server=$SERVER \
        --scriptpath=/wiki/w \
        --dbtype mysql \
        --dbname wiki_db \
        --dbuser $SQL_USERNAME \
        --dbpass $SQL_PASSWORD \
        --dbserver db \
        --pass $MEDIAWIKI_ADMIN_PASSWORD \
        chatbot_wiki admin
    
    if [ $? -eq 0 ]; then
        echo "MediaWiki installation completed successfully."
        break
    else
        echo "MediaWiki installation failed. Retrying in 5 secs..."
        sleep 5
    fi
done

sudo -u www-data php maintenance/run.php createAndPromote $BOT_USERNAME $BOT_PASSWORD --bot


echo "wfLoadExtension( 'VisualEditor' );" >> $WIKI_DIR/LocalSettings.php
echo "wfLoadExtension( 'WikiMarkdown' );" >> $WIKI_DIR/LocalSettings.php
echo "\$wgShowExceptionDetails = true;" >> $WIKI_DIR/LocalSettings.php
echo "\$wgAllowMarkdownExtra = true;" >> $WIKI_DIR/LocalSettings.php

echo "\$wgGroupPermissions['*']['read'] = false;" >> $WIKI_DIR/LocalSettings.php
echo "\$wgGroupPermissions['*']['edit'] = false;" >> $WIKI_DIR/LocalSettings.php
echo "\$wgGroupPermissions['*']['createaccount'] = false;" >> $WIKI_DIR/LocalSettings.php


echo "\$wgHiddenPrefs[] = 'language';" >> $WIKI_DIR/LocalSettings.php
echo "\$wgHiddenPrefs[] = 'variant';" >> $WIKI_DIR/LocalSettings.php
echo "\$wgHiddenPrefs[] = 'noconvertlink';" >> $WIKI_DIR/LocalSettings.php
echo "\$wgLanguageCode = 'en';" >> $WIKI_DIR/LocalSettings.php    # 'de'
echo "\$wgRateLimits['edit']['user'] = [ 1000, 60 ];" >> $WIKI_DIR/LocalSettings.php
echo "\$wgEnableUploads = true;" >> $WIKI_DIR/LocalSettings.php

git clone https://github.com/kuenzign/WikiMarkdown.git $WIKI_DIR/extensions/WikiMarkdown

cd $WIKI_DIR; composer update --ignore-platform-req=php

