# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 5 and greater than 3
- `DENY` if final risk score > 5

Lane thresholds:
- `GREEN` if final fee <= 16
- `AMBER` if final fee <= 28 and greater than 16
- `RED` if final fee > 28

Base risk score components:
- zone `North`: 3
- zone `West`: 6
- zone `East`: 6
- zone `South`: 4
- tier `T1`: 2
- tier `T2`: 2
- tier `T3`: 4
- category `Archives`: 2
- category `Agriculture`: 2
- category `Research`: 1
- category `Transit`: 2
- category `Medical`: 3

Base fee:
- start with 15
- add `quantity * 5`

Standing operational penalties:
- add risk `2` if flag `relay` is present
- add risk `2` if flag `field` is present
- add risk `4` if flag `vault` is present
- add risk `3` if flag `dock` is present
- if `declared_units != quantity`, add risk `6`
- if `record_age >= 5`, add risk `4`
- if `weekend = true`, add fee `1`
