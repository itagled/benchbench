# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 8 and greater than 5
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 12
- `AMBER` if final fee <= 23 and greater than 12
- `RED` if final fee > 23

Base risk score components:
- zone `East`: 6
- zone `South`: 4
- zone `North`: 7
- zone `West`: 5
- tier `T1`: 0
- tier `T2`: 4
- tier `T3`: 6
- category `Agriculture`: 1
- category `Research`: 1
- category `Medical`: 3
- category `Archives`: 3
- category `Transit`: 3

Base fee:
- start with 14
- add `quantity * 5`

Standing operational penalties:
- add risk `2` if flag `dock` is present
- add risk `3` if flag `relay` is present
- add risk `4` if flag `field` is present
- add risk `1` if flag `vault` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `4`
