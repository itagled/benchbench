# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 7 and greater than 3
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 15
- `AMBER` if final fee <= 23 and greater than 15
- `RED` if final fee > 23

Base risk score components:
- zone `East`: 5
- zone `North`: 8
- zone `West`: 8
- zone `South`: 8
- tier `T1`: 0
- tier `T2`: 2
- tier `T3`: 5
- category `Research`: 1
- category `Agriculture`: 0
- category `Transit`: 3
- category `Archives`: 1
- category `Medical`: 3

Base fee:
- start with 8
- add `quantity * 2`

Standing operational penalties:
- add risk `4` if flag `relay` is present
- add risk `2` if flag `vault` is present
- add risk `2` if flag `field` is present
- add risk `3` if flag `dock` is present
- if `declared_units != quantity`, add risk `6`
- if `record_age >= 7`, add risk `5`
- if `weekend = true`, add fee `3`
