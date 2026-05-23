# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 7 and greater than 5
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 14
- `AMBER` if final fee <= 26 and greater than 14
- `RED` if final fee > 26

Base risk score components:
- zone `West`: 9
- zone `East`: 5
- zone `North`: 7
- zone `South`: 9
- tier `T1`: 0
- tier `T2`: 4
- tier `T3`: 4
- category `Transit`: 0
- category `Research`: 0
- category `Agriculture`: 3
- category `Archives`: 1
- category `Medical`: 2

Base fee:
- start with 14
- add `quantity * 4`

Standing operational penalties:
- add risk `3` if flag `field` is present
- add risk `3` if flag `vault` is present
- add risk `1` if flag `dock` is present
- add risk `4` if flag `relay` is present
- if `declared_units != quantity`, add risk `2`
- if `record_age >= 7`, add risk `4`
- if `weekend = true`, add fee `2`
