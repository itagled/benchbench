# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 8 and greater than 4
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 10
- `AMBER` if final fee <= 20 and greater than 10
- `RED` if final fee > 20

Base risk score components:
- zone `South`: 6
- zone `North`: 8
- zone `East`: 3
- zone `West`: 8
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 6
- category `Research`: 2
- category `Transit`: 0
- category `Medical`: 1
- category `Agriculture`: 3
- category `Archives`: 3

Base fee:
- start with 16
- add `quantity * 3`

Standing operational penalties:
- add risk `2` if flag `vault` is present
- add risk `4` if flag `dock` is present
- add risk `3` if flag `field` is present
- add risk `2` if flag `relay` is present
- if `declared_units != quantity`, add risk `2`
- if `record_age >= 5`, add risk `4`
- if `weekend = true`, add fee `3`
