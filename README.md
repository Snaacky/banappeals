## Getting started

The applications web app is deployed into a production environment using [Docker](https://docs.docker.com/engine/reference/run/) images. As such, the install guide will focus on deployment via Docker. The install guide assumes that you already have Docker and [docker-compose](https://docs.docker.com/compose/) installed.

You will also need a Discord application, the ID, and secret for that bot, and to configure the callback (redirect) URL before installation. You can create a new Discord application [here](https://discord.com/developers/).

## Install

**Step 1:** Add the bot to the guild you want for users to be able to join with the appopriate OAuth2 scope.

**Step 2:** Download the `docker-compose.yml` to your local file system with `curl`, `wget`, etc. like so:
```
$ wget https://github.com/snaacky/banappeals/blob/master/docker-compose.yml
```

**Step 3:** Create a `.env` file in the same folder as you saved your `docker-compose.yml` and fill out the following:

```env
# The Discord application client ID from https://discordapp.com/developers/
DISCORD_CLIENT_ID=

# The Discord application client secret from from https://discordapp.com/developers/
DISCORD_CLIENT_SECRET=

# The Discord redirect (callback) URL set in https://discordapp.com/developers/
# Generally, this should be set to: https://domain.com/callback
DISCORD_REDIRECT_URI=

# The Discord bot token from from https://discordapp.com/developers/
DISCORD_BOT_TOKEN=

# The folder on the host OS where the database will be stored.
DATABASE_FOLDER=

# Whether or not OAuth should accept insecure transport, set to 0 for dev, 1 for production.
OAUTHLIB_INSECURE_TRANSPORT=

# Comma separated list of the user IDs that are allowed to access the management page.
EDITORS=

# The guild ID that users will be joining if their application is accepted.
GUILD_ID=

# The port for the Docker container to bind to on the host OS.
PORT=

# Whether or not we're currently accepting applications, set True for accepting, False for closed.
ACCEPTING=

# The number of months an account must exist for before it is eligible to fill out an application. 
MIN_ACCOUNT_MONTHS=

# The Proxycheck API key that will be used for proxy, VPN, and Tor detection.
# Proxy checking functionality is automatically disabled if this variable is commented out.
PROXYCHECK_KEY=

# Comma separated list of the user IDs that are allowed to access the administration page.
ADMINS=
```

**Step 4:** Pull the Docker image by executing `docker-compose pull` in the same folder as the `docker-compose.yml`

**Step 5:** Start the web app by executing `docker up -d`

### Build

Building the repository from source is similar to the process above.

**Step 1:** Clone the entire repository to your local file system
```
$ git clone https://github.com/snaacky/banappeals.git
```

**Step 2:** Create a `.env` file in the folder you cloned and fill out the above.

**Step 3:** Build from source with the development `docker-compose-dev.yml` file

```
$ docker-compose -f "docker-compose-dev.yml" up -d --build --remove-orphans
```

## Built on

The web app relies predominantly on the following projects:

* [Python](https://www.python.org/)
* [SQLite](https://www.sqlite.org/index.html)
* [Docker](https://www.docker.com/)
* [Flask](https://github.com/pallets/flask)
* [Gunicorn](https://gunicorn.org/)
* [Flask-Discord](https://github.com/weibeu/Flask-Discord)
* [dataset](https://dataset.readthedocs.io)
* [Bootstrap](https://getbootstrap.com/)
