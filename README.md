# gas-vybory-parser

# Примерная структура данных

Предполагается эта структура данных, но скорее всего произойдет деление на информационный блок о назначенных выборах, блок об округах и их кандидатах и блок результатов на УИКах, которые будут связаны по vrn и, в случае с УИК, id округов

```json
{
  "vrn" : 100000000000000,
  "title" : "Выборы совета депутатов городского поселения Шумиловский городок",
  "level" : "local / regional / federal",
  "date" : "11.01.2021",
  "results" : [
    {
      "district_id" : 0,
      "district_name" : "Сасный округ",
      "candidates_list" : [
        {
          "candidate_id" : 0,
          "name" : "Зубенко Михаил Петрович",
          "dob" : "10.01.1960",
          "place_of_birth" : "Шумиловский городок Ордена Ленина района Мордовской АССР",
          "place_of_living" : "г Москва",
          "education" : "Мордовский государственный университет им. Н.П. Огарева 1976 Мордовский ордена Дружбы народов госуниверситет имени Н.П. Огарева 1988",
          "employer" : "ООО ЧОП Мафиозник",
          "position" : "Генеральный директор",
          "deputy_info" : "",
          "criminal_record" : "",
          "inoagent" : "",
          "status": "депутат",
          "subject_of_nominmation" : "Партия жуликов и воров (в законе)",
          "nomination" : "выдвинут",
          "registration" : "зарегистрирован",
          "elected" : "избран"
        }
      ],
      "polling_station_results" : [
        {
          "commission_id" : 755,
          "total_voters" : 1488,
          "received_ballots" : 1500,
          "issued_ballots_inside" : 743,
          "issued_ballots_outside" : 12,
          "not_used_ballots" : 745,
          "ballots_from_outside_boxes" : 12,
          "ballots_from_inside_boxes" : 743,
          "invalid_ballots" : 15,
          "lost_ballots" : 40,
          "not_counted_received_ballots" : 0,
          "candidates_results": [
            {
              "candidate_id" : 0,
              "result" : 755
            }
          ]
        }
      ]
    }
  ] 
}
```
