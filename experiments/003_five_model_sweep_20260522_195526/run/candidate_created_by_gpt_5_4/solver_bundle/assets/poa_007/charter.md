# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 7 and greater than 3
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 10
- `AMBER` if final fee <= 23 and greater than 10
- `RED` if final fee > 23

Base risk score components:
- zone `East`: 8
- zone `West`: 8
- zone `South`: 8
- zone `North`: 5
- tier `T1`: 0
- tier `T2`: 4
- tier `T3`: 4
- category `Archives`: 1
- category `Research`: 0
- category `Transit`: 1
- category `Medical`: 3
- category `Agriculture`: 3

Base fee:
- start with 18
- add `quantity * 5`

Standing operational penalties:
- add risk `3` if flag `relay` is present
- add risk `1` if flag `field` is present
- add risk `1` if flag `vault` is present
- add risk `1` if flag `dock` is present
- if `declared_units != quantity`, add risk `3`
- if `record_age >= 7`, add risk `5`
- if `weekend = true`, add fee `4`
