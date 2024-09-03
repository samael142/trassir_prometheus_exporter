Экспортер собирает SNMP метрики с устройств TRASSIR.
Парсит строку с количеством камер и разделяет её на 2 метрики: Текущее количесво камер и максимальное количетво камер, так же убирает знак % в cpu_usage 
Запускать в докер на любом свободном порту, метрики возвращаются по адресу http://[адрес экспортера]:[порт экспортера]/metrics?target=[адрес трассира]
Пример конфигурации prometheus.yml
- job_name: 'trassir'
  scrape_interval: 5m
  scrape_timeout: 4m
  static_configs:
    - targets: ['192.168.10.1']
      labels:
        name: 'Трассир01'
    - targets: ['192.168.20.1']
      labels:
        name: 'Трассир02'
    - targets: ['192.168.30.1']
      labels:
        name: 'Трассир03'
  metrics_path: /metrics
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: 192.168.153.95:5000
