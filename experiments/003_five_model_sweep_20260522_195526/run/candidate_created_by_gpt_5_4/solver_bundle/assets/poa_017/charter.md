# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 5 and greater than 3
- `DENY` if final risk score > 5

Lane thresholds:
- `GREEN` if final fee <= 13
- `AMBER` if final fee <= 22 and greater than 13
- `RED` if final fee > 22

Base risk score components:
- zone `South`: 9
- zone `West`: 9
- zone `East`: 6
- zone `North`: 9
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 5
- category `Archives`: 0
- category `Research`: 3
- category `Agriculture`: 0
- category `Medical`: 3
- category `Transit`: 1

Base fee:
- start with 9
- add `quantity * 3`

Standing operational penalties:
- add risk `2` if flag `relay` is present
- add risk `3` if flag `vault` is present
- add risk `4` if flag `field` is present
- add risk `4` if flag `dock` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 5`, add risk `5`
- if `weekend = true`, add fee `1`
