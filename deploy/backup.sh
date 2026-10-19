#!/bin/sh
# Nightly dump, copied to NAS_PATH when it is set. Keeps 30 days.
# Waits for the database so the container does not crash-loop on first start.

until pg_isready -h db -U steadytype -d steadytype >/dev/null 2>&1; do
  sleep 5
done

while true; do
  stamp=$(date +%Y-%m-%d)
  tmp="/backups/.steadytype-$stamp.sql.gz"
  final="/backups/steadytype-$stamp.sql.gz"
  if pg_dump -h db -U steadytype -d steadytype | gzip > "$tmp"; then
    mv "$tmp" "$final"
    if [ -n "${NAS_PATH:-}" ] && [ -d "$NAS_PATH" ]; then
      cp "$final" "$NAS_PATH/" || echo "Could not copy to $NAS_PATH" >&2
    fi
    find /backups -name 'steadytype-*.sql.gz' -mtime +30 -delete
  else
    rm -f "$tmp"
    echo "Backup failed at $stamp" >&2
  fi
  sleep 86400
done
