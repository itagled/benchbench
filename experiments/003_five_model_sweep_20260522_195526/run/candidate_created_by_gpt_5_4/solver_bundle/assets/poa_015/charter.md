# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 7 and greater than 5
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 12
- `AMBER` if final fee <= 23 and greater than 12
- `RED` if final fee > 23

Base risk score components:
- zone `East`: 7
- zone `West`: 6
- zone `South`: 6
- zone `North`: 8
- tier `T1`: 0
- tier `T2`: 3
- tier `T3`: 4
- category `Research`: 3
- category `Transit`: 1
- category `Medical`: 3
- category `Archives`: 0
- category `Agriculture`: 2

Base fee:
- start with 11
- add `quantity * 4`

Standing operational penalties:
- add risk `4` if flag `vault` is present
- add risk `1` if flag `relay` is present
- add risk `4` if flag `field` is present
- add risk `1` if flag `dock` is present
- if `declared_units != quantity`, add risk `3`
- if `record_age >= 6`, add risk `4`
- if `weekend = true`, add fee `4`
