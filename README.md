# My Links (аналог Linktree с админкой)

Минималистичный сервис для личной страницы со ссылками:
- публичная страница `/`
- админка `/admin` (логин/пароль)
- редактирование, скрытие и удаление ссылок
- SQLite в volume
- запуск в контейнере на TrueNAS SCALE

## Локальный запуск

```bash
docker build -t my-links:latest .
docker run --rm -p 8080:8080 \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=admin123 \
  -e SECRET_KEY='your-secret-key' \
  -e PROFILE_TITLE='Мои проекты' \
  -e PROFILE_SUBTITLE='Куда меня найти' \
  -v $(pwd)/data:/data \
  my-links:latest
```

Откройте `http://localhost:8080`.

## Разворачивание на TrueNAS SCALE через YAML

1. Создайте dataset для данных, например: `/mnt/tank/apps/my-links`.
2. В TrueNAS откройте **Apps → Discover Apps → Custom App**.
3. Вставьте содержимое `truenas-compose.yaml` как Compose/YAML.
4. Измените `ADMIN_PASSWORD` или лучше задайте `ADMIN_PASSWORD_HASH`.
5. Измените `SECRET_KEY` на длинную случайную строку.
6. Проверьте путь в `volumes` под ваш pool/dataset.
7. Опубликуйте app и откройте `http://<IP_TRUENAS>:8080`.

## Публикация в интернет (рекомендуемая схема)

- Публикуйте сервис через reverse-proxy (Traefik / Nginx Proxy Manager / Caddy).
- Настройте HTTPS и домен (например, `links.example.com`).
- Ограничьте доступ к `/admin` по IP или через дополнительную auth-защиту в reverse-proxy.

## Переменные окружения

- `ADMIN_USERNAME` — логин админа.
- `ADMIN_PASSWORD` — пароль админа (базовый вариант).
- `ADMIN_PASSWORD_HASH` — хэш пароля (приоритетнее, безопаснее).
- `SECRET_KEY` — секрет Flask-сессии (обязательно случайная строка).
- `DB_PATH` — путь к sqlite БД (по умолчанию `/data/links.db`).
- `PROFILE_TITLE` — заголовок публичной страницы.
- `PROFILE_SUBTITLE` — подзаголовок публичной страницы.

### Как сгенерировать хэш пароля

```bash
python3 - <<'PY'
from werkzeug.security import generate_password_hash
print(generate_password_hash("StrongPassword123!"))
PY
```

Подставьте результат в `ADMIN_PASSWORD_HASH` и не используйте `ADMIN_PASSWORD` в открытом виде.
