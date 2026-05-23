# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 8 and greater than 4
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 13
- `AMBER` if final fee <= 25 and greater than 13
- `RED` if final fee > 25

Base risk score components:
- zone `West`: 9
- zone `North`: 5
- zone `East`: 3
- zone `South`: 6
- tier `T1`: 0
- tier `T2`: 3
- tier `T3`: 4
- category `Research`: 1
- category `Agriculture`: 0
- category `Transit`: 3
- category `Medical`: 3
- category `Archives`: 3

Base fee:
- start with 14
- add `quantity * 2`

Standing operational penalties:
- add risk `4` if flag `field` is present
- add risk `2` if flag `vault` is present
- add risk `1` if flag `relay` is present
- add risk `2` if flag `dock` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 7`, add risk `3`
- if `weekend = true`, add fee `2`
