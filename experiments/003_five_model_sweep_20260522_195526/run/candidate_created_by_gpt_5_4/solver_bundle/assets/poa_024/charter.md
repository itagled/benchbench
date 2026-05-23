# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 7 and greater than 5
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 15
- `AMBER` if final fee <= 29 and greater than 15
- `RED` if final fee > 29

Base risk score components:
- zone `West`: 6
- zone `South`: 3
- zone `North`: 3
- zone `East`: 9
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 5
- category `Medical`: 2
- category `Agriculture`: 0
- category `Transit`: 2
- category `Archives`: 2
- category `Research`: 1

Base fee:
- start with 9
- add `quantity * 3`

Standing operational penalties:
- add risk `1` if flag `field` is present
- add risk `1` if flag `relay` is present
- add risk `1` if flag `vault` is present
- add risk `1` if flag `dock` is present
- if `declared_units != quantity`, add risk `5`
- if `record_age >= 7`, add risk `2`
- if `weekend = true`, add fee `2`
