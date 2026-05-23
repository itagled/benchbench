# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 5 and greater than 3
- `DENY` if final risk score > 5

Lane thresholds:
- `GREEN` if final fee <= 10
- `AMBER` if final fee <= 21 and greater than 10
- `RED` if final fee > 21

Base risk score components:
- zone `East`: 6
- zone `South`: 7
- zone `North`: 9
- zone `West`: 5
- tier `T1`: 2
- tier `T2`: 2
- tier `T3`: 5
- category `Archives`: 0
- category `Research`: 2
- category `Agriculture`: 3
- category `Medical`: 3
- category `Transit`: 1

Base fee:
- start with 15
- add `quantity * 3`

Standing operational penalties:
- add risk `4` if flag `dock` is present
- add risk `4` if flag `vault` is present
- add risk `3` if flag `field` is present
- add risk `2` if flag `relay` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `1`
