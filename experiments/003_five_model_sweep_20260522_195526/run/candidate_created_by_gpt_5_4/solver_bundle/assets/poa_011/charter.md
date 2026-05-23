# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 8 and greater than 5
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 10
- `AMBER` if final fee <= 18 and greater than 10
- `RED` if final fee > 18

Base risk score components:
- zone `North`: 9
- zone `West`: 7
- zone `East`: 4
- zone `South`: 9
- tier `T1`: 2
- tier `T2`: 2
- tier `T3`: 5
- category `Research`: 0
- category `Medical`: 0
- category `Transit`: 1
- category `Agriculture`: 3
- category `Archives`: 3

Base fee:
- start with 8
- add `quantity * 3`

Standing operational penalties:
- add risk `1` if flag `vault` is present
- add risk `1` if flag `field` is present
- add risk `3` if flag `relay` is present
- add risk `3` if flag `dock` is present
- if `declared_units != quantity`, add risk `3`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `4`
