
# Running Multiple Instances on a Single Host

It is possible to run **multiple Bergwerk instances** on a single host or virtual machine.  
However, this setup is **not supported out of the box** and requires some manual adjustments to the configuration files — primarily the `docker-compose.yaml` and `Caddyfile` files.

This section will guide you step-by-step through an example setup with **two independent Bergwerk instances**, `bot1` and `bot2`, running on the same host system.

---

## Example: Two Bergwerk Instances

First, clone the Bergwerk repository twice into separate directories:

```bash
git clone https://github.com/HTW-Berlin-KI-Werkstatt/bergwerk bot1
git clone https://github.com/HTW-Berlin-KI-Werkstatt/bergwerk bot2
```

This will create two directories — `bot1` and `bot2` — each containing its own copy of the Bergwerk source files.

---

## Step 1: Adjust the Docker Compose Configuration

Each Bergwerk instance comes with its own `docker-compose.yaml`.  
We need to modify the **Caddy service** in both files to avoid port conflicts and allow proper network aliasing.

### Example: `bot1/docker-compose.yaml`

Locate the **`caddy`** section in the file and replace it with the following:

```yaml
  caddy:
    image: caddy:latest
    env_file:
      - config.env
    restart: always
    volumes:
      - ./bergwerk-caddy/Caddyfile:/etc/caddy/Caddyfile
      - ./bergwerk-caddy/html:/var/www/html
      - ./persist/caddy_data:/data
      - ./persist/caddy_config:/config
    networks:
      netzwerk:
        aliases:
          - bot1_caddy
```

### Example: `bot2/docker-compose.yaml`

Do the same in the `bot2` directory, changing the alias to `bot2_caddy`:

```yaml
  caddy:
    image: caddy:latest
    env_file:
      - config.env
    restart: always
    volumes:
      - ./bergwerk-caddy/Caddyfile:/etc/caddy/Caddyfile
      - ./bergwerk-caddy/html:/var/www/html
      - ./persist/caddy_data:/data
      - ./persist/caddy_config:/config
    networks:
      netzwerk:
        aliases:
          - bot2_caddy
```

Each Caddy container now operates in its own Docker network, without port conflicts.

---

## Step 2: Update Each Caddyfile

Next, adjust both `Caddyfile` configurations (`bot1/bergwerk-caddy/Caddyfile` and `bot2/bergwerk-caddy/Caddyfile`).

The default configuration typically starts with something like:

```
{$SERVER} {

    root * /var/www/html
    file_server

    handle_path /wiki* {
        reverse_proxy wiki:80
    }

    handle /admin* {
        reverse_proxy admin:80 {
            header_up X-Forwarded-Prefix /admin
        }
    }

    handle /socket.io/* {
        reverse_proxy socketio:5005
    }

    handle_errors {
        @404 {
            expression {http.error.status_code} == 404
        }
        rewrite @404 /404.html
        file_server
    }
}
```

Change the **first line** of each file to listen only on port 80, instead of a variable or HTTPS binding:

```
:80 {
```

---

## Step 3: Configure Environment Variables

Each instance requires its own `config.env` file with unique credentials and server URLs.

### Example: `bot1/config.env`

```
MEDIAWIKI_ADMIN=admin
MEDIAWIKI_ADMIN_PASSWORD=secret

BOT_USERNAME=bot
BOT_PASSWORD=secret

SQL_USERNAME=dbuser
SQL_PASSWORD=secret

SERVER=https://bot1.example.com
```

### Example: `bot2/config.env`

```
MEDIAWIKI_ADMIN=admin
MEDIAWIKI_ADMIN_PASSWORD=secret

BOT_USERNAME=bot
BOT_PASSWORD=secret

SQL_USERNAME=dbuser
SQL_PASSWORD=secret

SERVER=https://bot2.example.com
```

Make sure that:
- Each domain (`bot1.example.com` and `bot2.example.com`) points to the **same host IP address**.
- Passwords are strong and unique.
- The `SERVER` variable reflects the intended hostname for each instance.

---

## Step 4: Add an Edge Caddy Server

To handle inbound HTTPS traffic and route it to the correct bot based on hostname, create a third Caddy instance — an **edge proxy**.

Create a new directory `caddy.edge` and add the following two files.

### `docker-compose.yaml`

```yaml
version: "3.9"

services:
  caddy-edge:
    image: caddy:latest
    restart: always
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./Caddyfile.edge:/etc/caddy/Caddyfile
      - ./persist/caddy_data:/data
      - ./persist/caddy_config:/config
    networks:
      - bot1_netzwerk
      - bot2_netzwerk

networks:
  bot1_netzwerk:
    external: true
  bot2_netzwerk:
    external: true
```

### `Caddyfile.edge`

```
https://bot1.example.com {
    reverse_proxy bot1_caddy:80
}

https://bot2.example.com {
    reverse_proxy bot2_caddy:80
}
```

This **edge server** terminates HTTPS connections and forwards traffic to the correct backend instance (`bot1` or `bot2`) using the host header.

---

## Step 5: Starting the Instances

Once all configurations are in place, start each instance sequentially:

```bash
cd bot1
docker compose -p bot1 up -d

cd ../bot2
docker compose -p bot2 up -d

cd ../caddy.edge
docker compose up -d
```

You should now be able to access both chatbots:

- **Bot 1:** [https://bot1.example.com](https://bot1.example.com)
- **Bot 2:** [https://bot2.example.com](https://bot2.example.com)

---

## Summary

You have successfully configured **two independent Bergwerk instances** on a single host using Docker Compose and Caddy.  
The **edge Caddy server** acts as the secure entry point, routing incoming HTTPS traffic to the appropriate backend container based on the domain name.

This approach can be extended to additional instances as needed — just repeat the same pattern with unique directories, ports, and network aliases.
