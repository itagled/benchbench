# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 5 and greater than 3
- `DENY` if final risk score > 5

Lane thresholds:
- `GREEN` if final fee <= 17
- `AMBER` if final fee <= 27 and greater than 17
- `RED` if final fee > 27

Base risk score components:
- zone `West`: 7
- zone `North`: 9
- zone `South`: 7
- zone `East`: 9
- tier `T1`: 0
- tier `T2`: 4
- tier `T3`: 4
- category `Transit`: 0
- category `Medical`: 2
- category `Archives`: 2
- category `Research`: 1
- category `Agriculture`: 3

Base fee:
- start with 17
- add `quantity * 3`

Standing operational penalties:
- add risk `4` if flag `dock` is present
- add risk `2` if flag `field` is present
- add risk `2` if flag `relay` is present
- add risk `3` if flag `vault` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 7`, add risk `2`
- if `weekend = true`, add fee `2`
