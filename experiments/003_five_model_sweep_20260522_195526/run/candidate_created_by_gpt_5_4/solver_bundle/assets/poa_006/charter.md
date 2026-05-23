# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 7 and greater than 3
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 10
- `AMBER` if final fee <= 19 and greater than 10
- `RED` if final fee > 19

Base risk score components:
- zone `West`: 8
- zone `East`: 9
- zone `South`: 4
- zone `North`: 9
- tier `T1`: 1
- tier `T2`: 3
- tier `T3`: 6
- category `Medical`: 1
- category `Archives`: 0
- category `Research`: 2
- category `Agriculture`: 0
- category `Transit`: 1

Base fee:
- start with 10
- add `quantity * 4`

Standing operational penalties:
- add risk `3` if flag `vault` is present
- add risk `2` if flag `field` is present
- add risk `3` if flag `relay` is present
- add risk `1` if flag `dock` is present
- if `declared_units != quantity`, add risk `6`
- if `record_age >= 5`, add risk `4`
- if `weekend = true`, add fee `1`
