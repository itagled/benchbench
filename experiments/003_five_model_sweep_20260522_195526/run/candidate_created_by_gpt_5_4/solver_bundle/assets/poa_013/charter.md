# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 7 and greater than 3
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 11
- `AMBER` if final fee <= 25 and greater than 11
- `RED` if final fee > 25

Base risk score components:
- zone `West`: 4
- zone `North`: 8
- zone `East`: 4
- zone `South`: 4
- tier `T1`: 0
- tier `T2`: 2
- tier `T3`: 5
- category `Medical`: 2
- category `Agriculture`: 2
- category `Transit`: 2
- category `Archives`: 3
- category `Research`: 1

Base fee:
- start with 18
- add `quantity * 5`

Standing operational penalties:
- add risk `4` if flag `field` is present
- add risk `4` if flag `relay` is present
- add risk `1` if flag `vault` is present
- add risk `1` if flag `dock` is present
- if `declared_units != quantity`, add risk `5`
- if `record_age >= 5`, add risk `2`
- if `weekend = true`, add fee `4`
