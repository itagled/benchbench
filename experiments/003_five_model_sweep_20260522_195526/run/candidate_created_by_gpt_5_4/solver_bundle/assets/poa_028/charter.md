# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 9 and greater than 5
- `DENY` if final risk score > 9

Lane thresholds:
- `GREEN` if final fee <= 13
- `AMBER` if final fee <= 24 and greater than 13
- `RED` if final fee > 24

Base risk score components:
- zone `South`: 8
- zone `West`: 3
- zone `East`: 7
- zone `North`: 7
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 4
- category `Archives`: 3
- category `Research`: 0
- category `Transit`: 3
- category `Agriculture`: 2
- category `Medical`: 1

Base fee:
- start with 11
- add `quantity * 2`

Standing operational penalties:
- add risk `2` if flag `relay` is present
- add risk `3` if flag `field` is present
- add risk `4` if flag `dock` is present
- add risk `3` if flag `vault` is present
- if `declared_units != quantity`, add risk `5`
- if `record_age >= 5`, add risk `3`
- if `weekend = true`, add fee `3`
