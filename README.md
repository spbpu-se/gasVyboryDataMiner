# gas-vybory-parser

~СУКА НЕ ЗАБУДЬ ПЕРЕБИЛДИТЬ!!!!!!!!!!!!!!~

```bash
    docker build -t "extractor:latest" . --build-arg start_date="dd.mm.yyyy" --build-arg end_date="dd.mm.yyyy" --build-arg level="local / regional / regcap / federal" --build-arg mongo_ip="0.0.0.0" --build-arg mongo_port="27017" --build-arg mongo_usr="admin" --build-arg mongo_pwd="admin"
    
    docker run -e start_date="dd.mm.yyyy" -e end_date="dd.mm.yyyy" -e level="local / regional / regcap / federal" -e mongo_ip="0.0.0.0" -e mongo_port="27017" -e mongo_usr="admin" -e mongo_pwd="admin" extractor:latest
    
```

# Примерная структура данных

```json
[
  {
    "vrn": 100000000000000,
    "title": "Выборы совета депутатов городского поселения Шумиловский городок",
    "level": "local / regional / regional_capital / federal",
    "date": "11.01.2021"
  },
  {
    "vrn": 100000000000000,
    "oik_id": 0,
  },
  {
    "vrn": 100000000000000,
    "oik_id": 0,
    "candidate_id": 0,
    "name": "Зубенко Михаил Петрович",
    "dob": "10.01.1960",
    "place_of_birth": "Шумиловский городок Ордена Ленина района Мордовской АССР",
    "place_of_living": "г Москва",
    "education": "Мордовский государственный университет им. Н.П. Огарева 1976 Мордовский ордена Дружбы народов госуниверситет имени Н.П. Огарева 1988",
    "employer": "ООО ЧОП Мафиозник",
    "position": "Генеральный директор",
    "deputy_info": "",
    "criminal_record": [],
    "inoagent": "",
    "status": "депутат",
    "subject_of_nominmation": "Партия жуликов и воров (в законе)",
    "nomination": "выдвинут",
    "registration": "зарегистрирован",
    "elected": "избран"
  },
  {
    "vrn": 100000000000000,
    "oik_id": 0,
    "uik_id": 755,
    "total_voters": 1488,
    "recieved_ballots": 1500,
    "issued_ballots_inside": 743,
    "issued_ballots_outside": 12,
    "not_used_ballots": 745,
    "ballots_from_outside_boxes": 12,
    "ballots_from_inside_boxes": 743,
    "invalid_ballots": 15,
    "lost_ballots": 40,
    "not_counted_recieved_ballots": 0,
    "candidates_results": [
      {
        "candidate_id": 0,
        "result": 755
      }
    ]
  }
]
```
