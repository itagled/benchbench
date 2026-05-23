# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 7 and greater than 4
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 15
- `AMBER` if final fee <= 27 and greater than 15
- `RED` if final fee > 27

Base risk score components:
- zone `South`: 4
- zone `East`: 6
- zone `West`: 4
- zone `North`: 3
- tier `T1`: 0
- tier `T2`: 4
- tier `T3`: 6
- category `Medical`: 2
- category `Research`: 3
- category `Transit`: 1
- category `Archives`: 3
- category `Agriculture`: 2

Base fee:
- start with 9
- add `quantity * 2`

Standing operational penalties:
- add risk `1` if flag `relay` is present
- add risk `2` if flag `vault` is present
- add risk `3` if flag `field` is present
- add risk `4` if flag `dock` is present
- if `declared_units != quantity`, add risk `6`
- if `record_age >= 6`, add risk `2`
- if `weekend = true`, add fee `2`
