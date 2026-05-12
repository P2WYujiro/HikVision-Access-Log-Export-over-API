# HikVision-Access-Log-Export-over-API
Python HikVision ACS access log exporting API script.

````md
## Экспорт событий доступа Hikvision

Скрипт `hik_acsevent_export.py` выгружает события доступа с устройства Hikvision через ISAPI и сохраняет их в CSV. Опционально можно дополнительно создать XLSX-файл.

### Требования

- Python 3
- `curl`
- Для экспорта в XLSX:
pip install openpyxl
````

### Использование

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user admin \
  --password "PASSWORD" \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv
```

### Экспорт в CSV и XLSX

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user admin \
  --password "PASSWORD" \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv \
  --xlsx events.xlsx
```

### Запрос пароля вручную

Чтобы не передавать пароль в командной строке, используйте `-`:

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user admin \
  --password - \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out events.csv
```

### Полезные параметры

| Параметр      | Описание                                    |
| ------------- | ------------------------------------------- |
| `--ip`        | IP-адрес устройства                         |
| `--user`      | Пользователь, по умолчанию `admin`          |
| `--password`  | Пароль или `-` для ручного ввода            |
| `--start`     | Начало периода выгрузки                     |
| `--end`       | Конец периода выгрузки                      |
| `--out`       | Путь к CSV-файлу                            |
| `--xlsx`      | Путь к XLSX-файлу, опционально              |
| `--only-card` | Выгружать только события по картам          |
| `--max`       | Размер страницы запроса, по умолчанию `200` |
| `--minor`     | Код события `minor`, по умолчанию `0`       |

### Пример только для событий по картам

```bash
python3 hik_acsevent_export.py \
  --ip 192.168.1.50 \
  --user admin \
  --password - \
  --start "2025-12-01T00:00:00+03:00" \
  --end "2026-01-30T23:59:59+03:00" \
  --out card_events.csv \
  --only-card
```

```
```
