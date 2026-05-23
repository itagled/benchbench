# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 7 and greater than 5
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 12
- `AMBER` if final fee <= 21 and greater than 12
- `RED` if final fee > 21

Base risk score components:
- zone `South`: 7
- zone `North`: 5
- zone `West`: 4
- zone `East`: 7
- tier `T1`: 0
- tier `T2`: 2
- tier `T3`: 4
- category `Research`: 3
- category `Agriculture`: 1
- category `Archives`: 3
- category `Transit`: 3
- category `Medical`: 0

Base fee:
- start with 14
- add `quantity * 4`

Standing operational penalties:
- add risk `3` if flag `dock` is present
- add risk `3` if flag `relay` is present
- add risk `1` if flag `vault` is present
- add risk `3` if flag `field` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 7`, add risk `4`
- if `weekend = true`, add fee `2`
