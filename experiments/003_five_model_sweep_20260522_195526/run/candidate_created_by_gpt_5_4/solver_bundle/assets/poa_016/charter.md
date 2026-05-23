# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 3
- `REVIEW` if final risk score <= 7 and greater than 3
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 13
- `AMBER` if final fee <= 25 and greater than 13
- `RED` if final fee > 25

Base risk score components:
- zone `West`: 6
- zone `North`: 3
- zone `South`: 3
- zone `East`: 4
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 5
- category `Research`: 3
- category `Archives`: 2
- category `Medical`: 2
- category `Transit`: 1
- category `Agriculture`: 2

Base fee:
- start with 12
- add `quantity * 2`

Standing operational penalties:
- add risk `2` if flag `relay` is present
- add risk `3` if flag `dock` is present
- add risk `1` if flag `vault` is present
- add risk `2` if flag `field` is present
- if `declared_units != quantity`, add risk `3`
- if `record_age >= 6`, add risk `4`
- if `weekend = true`, add fee `2`
