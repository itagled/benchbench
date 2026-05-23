# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 8 and greater than 5
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 15
- `AMBER` if final fee <= 25 and greater than 15
- `RED` if final fee > 25

Base risk score components:
- zone `South`: 7
- zone `West`: 5
- zone `East`: 6
- zone `North`: 3
- tier `T1`: 1
- tier `T2`: 4
- tier `T3`: 5
- category `Archives`: 0
- category `Agriculture`: 2
- category `Research`: 1
- category `Medical`: 1
- category `Transit`: 1

Base fee:
- start with 14
- add `quantity * 5`

Standing operational penalties:
- add risk `3` if flag `field` is present
- add risk `2` if flag `relay` is present
- add risk `3` if flag `vault` is present
- add risk `2` if flag `dock` is present
- if `declared_units != quantity`, add risk `3`
- if `record_age >= 7`, add risk `4`
- if `weekend = true`, add fee `2`
