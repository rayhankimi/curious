server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
    }

    location /static/media {
        alias /vol/web/media;
    }

    location / {
        add_header Access-Control-Allow-Origin "${FRONTEND_DOMAIN}" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;

        uwsgi_pass ${APP_HOST}:${APP_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;

    }
}

