#!/bin/sh
# Nightly dump. Copies to NAS_PATH when it is set. Keeps 30 days.
while true; do
  stamp=$(date +%Y-%m-%d)
  pg_dump -h db -U steadytype -d steadytype | gzip > "/backups/steadytype-$stamp.sql.gz"
  if [ -n "$NAS_PATH" ] && [ -d "$NAS_PATH" ]; then
    cp "/backups/steadytype-$stamp.sql.gz" "$NAS_PATH/"
  fi
  find /backups -name 'steadytype-*.sql.gz' -mtime +30 -delete
  sleep 86400
done
