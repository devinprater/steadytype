# Deploying SteadyType

One Ubuntu 24.04 machine, a domain pointing at it, Docker, and Compose.

1. Copy the repository to the server.
2. In `deploy/`, create `.env`:

```
DOMAIN=typing.your-school.org
POSTGRES_PASSWORD=a long random password
STEADYTYPE_SECRET=another long random string
STEADYTYPE_SCHOOL_NAME=Your School
STEADYTYPE_TIMEZONE=America/Chicago
NAS_PATH=/mnt/nas/steadytype
```

`NAS_PATH` is optional. Without it, backups stay on the server and the setup says so.

3. Start everything: `docker compose up -d --build`
4. Create the first administrator:

```
docker compose exec web python -m steadytype_server.setup --username owner
```

It prompts for the password and never prints it.

5. Open `https://$DOMAIN/signin`.

Nightly backups land in the `backups` volume, and in `NAS_PATH` when set. Restore with
`gunzip -c file.sql.gz | docker compose exec -T db psql -U steadytype steadytype`.

Updates: `git pull && docker compose up -d --build`. Take a backup first.
