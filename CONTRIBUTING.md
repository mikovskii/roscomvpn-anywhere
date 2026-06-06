# Участие в разработке

## Сообщения об ошибках

Перед созданием issue:

1. Обновите подписанный набор кнопкой **Update**.
2. Проверьте назначенное действие: DIRECT, REJECT или нужный прокси.
3. Убедитесь, что одновременно не установлены DEFAULT и WHITELIST.
4. Укажите домен или CIDR, ожидаемый и фактический маршрут, версию Anywhere и
   выбранный профиль.

Не публикуйте приватные ссылки на VPN-подписки, ключи и конфигурации серверов.

## Изменения кода

Для локальной проверки используйте:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_anywhere.py
```

Для воспроизводимой генерации понадобятся локальные копии версий GeoIP и
GeoSite, указанных в `sources.json`:

```sh
python3 scripts/generate_anywhere.py \
  --geosite /path/to/roscomvpn-geosite \
  --geoip /path/to/roscomvpn-geoip
```

Pull request должен содержать тест для новой логики и не должен включать
ручные изменения сгенерированных `.arrs`, которые нельзя воспроизвести
генератором.

## Изменения списков

Ошибки в исходных доменных или IP-списках лучше исправлять в соответствующем
upstream-проекте:

- https://github.com/hydraponique/roscomvpn-geosite
- https://github.com/hydraponique/roscomvpn-geoip
