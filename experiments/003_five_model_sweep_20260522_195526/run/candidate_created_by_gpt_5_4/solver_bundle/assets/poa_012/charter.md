# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 8 and greater than 4
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 12
- `AMBER` if final fee <= 26 and greater than 12
- `RED` if final fee > 26

Base risk score components:
- zone `East`: 3
- zone `West`: 5
- zone `North`: 7
- zone `South`: 3
- tier `T1`: 2
- tier `T2`: 3
- tier `T3`: 6
- category `Archives`: 2
- category `Agriculture`: 1
- category `Medical`: 3
- category `Research`: 3
- category `Transit`: 2

Base fee:
- start with 15
- add `quantity * 4`

Standing operational penalties:
- add risk `2` if flag `dock` is present
- add risk `4` if flag `relay` is present
- add risk `3` if flag `vault` is present
- add risk `3` if flag `field` is present
- if `declared_units != quantity`, add risk `6`
- if `record_age >= 5`, add risk `5`
- if `weekend = true`, add fee `4`
