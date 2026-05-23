# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 8 and greater than 4
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 16
- `AMBER` if final fee <= 30 and greater than 16
- `RED` if final fee > 30

Base risk score components:
- zone `West`: 5
- zone `North`: 9
- zone `East`: 8
- zone `South`: 8
- tier `T1`: 2
- tier `T2`: 3
- tier `T3`: 6
- category `Research`: 2
- category `Transit`: 3
- category `Medical`: 1
- category `Archives`: 0
- category `Agriculture`: 1

Base fee:
- start with 18
- add `quantity * 3`

Standing operational penalties:
- add risk `2` if flag `relay` is present
- add risk `1` if flag `vault` is present
- add risk `3` if flag `field` is present
- add risk `1` if flag `dock` is present
- if `declared_units != quantity`, add risk `3`
- if `record_age >= 6`, add risk `4`
- if `weekend = true`, add fee `3`
