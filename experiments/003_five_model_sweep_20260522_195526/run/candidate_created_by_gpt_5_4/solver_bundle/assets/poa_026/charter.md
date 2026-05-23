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
- zone `South`: 8
- zone `North`: 7
- zone `East`: 5
- zone `West`: 5
- tier `T1`: 2
- tier `T2`: 3
- tier `T3`: 4
- category `Transit`: 1
- category `Research`: 1
- category `Agriculture`: 3
- category `Archives`: 2
- category `Medical`: 2

Base fee:
- start with 17
- add `quantity * 5`

Standing operational penalties:
- add risk `2` if flag `vault` is present
- add risk `1` if flag `dock` is present
- add risk `3` if flag `relay` is present
- add risk `2` if flag `field` is present
- if `declared_units != quantity`, add risk `5`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `2`
