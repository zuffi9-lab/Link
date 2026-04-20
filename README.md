# My Links (аналог Linktree с админкой)

Минималистичный сервис для личной страницы со ссылками:
- публичная страница `/`
- админка `/admin` (логин/пароль)
- SQLite в volume
- запуск в контейнере

## Локальный запуск

```bash
docker build -t my-links:latest .
docker run --rm -p 8080:8080 \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=admin123 \
  -e SECRET_KEY='your-secret-key' \
  -v $(pwd)/data:/data \
  my-links:latest
```

Откройте `http://localhost:8080`.

## Разворачивание на TrueNAS SCALE через YAML

1. Создайте dataset для данных, например:
   - `/mnt/tank/apps/my-links`
2. В TrueNAS откройте **Apps → Discover Apps → Custom App**.
3. Вставьте содержимое `truenas-compose.yaml` как Compose/YAML.
4. Обязательно поменяйте:
   - `ADMIN_PASSWORD`
   - `SECRET_KEY`
   - путь в `volumes` под ваш pool/dataset
5. Опубликуйте app и проверьте:
   - `http://<IP_TRUENAS>:8080`

## Переменные окружения

- `ADMIN_USERNAME` — логин админа
- `ADMIN_PASSWORD` — пароль админа
- `SECRET_KEY` — секрет Flask-сессии (обязательно случайная строка)
- `DB_PATH` — путь к sqlite БД (по умолчанию `/data/links.db`)

## Безопасность (рекомендации)

- Не оставляйте стандартные логин/пароль.
- Ограничьте доступ к `/admin` через reverse-proxy (например, только из локальной сети).
- Добавьте HTTPS через Traefik/Nginx Proxy Manager/Cloudflare Tunnel.
