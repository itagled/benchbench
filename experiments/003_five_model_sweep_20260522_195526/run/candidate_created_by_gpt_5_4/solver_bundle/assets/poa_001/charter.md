# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 8 and greater than 4
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 13
- `AMBER` if final fee <= 24 and greater than 13
- `RED` if final fee > 24

Base risk score components:
- zone `South`: 8
- zone `North`: 8
- zone `East`: 9
- zone `West`: 7
- tier `T1`: 2
- tier `T2`: 3
- tier `T3`: 4
- category `Agriculture`: 3
- category `Medical`: 2
- category `Transit`: 3
- category `Research`: 1
- category `Archives`: 0

Base fee:
- start with 11
- add `quantity * 3`

Standing operational penalties:
- add risk `4` if flag `relay` is present
- add risk `3` if flag `dock` is present
- add risk `1` if flag `field` is present
- add risk `1` if flag `vault` is present
- if `declared_units != quantity`, add risk `2`
- if `record_age >= 6`, add risk `3`
- if `weekend = true`, add fee `2`
