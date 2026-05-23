# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 7 and greater than 4
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 13
- `AMBER` if final fee <= 22 and greater than 13
- `RED` if final fee > 22

Base risk score components:
- zone `South`: 7
- zone `East`: 4
- zone `West`: 9
- zone `North`: 3
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 4
- category `Transit`: 2
- category `Medical`: 2
- category `Research`: 2
- category `Archives`: 0
- category `Agriculture`: 2

Base fee:
- start with 15
- add `quantity * 5`

Standing operational penalties:
- add risk `1` if flag `dock` is present
- add risk `1` if flag `relay` is present
- add risk `1` if flag `vault` is present
- add risk `3` if flag `field` is present
- if `declared_units != quantity`, add risk `4`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `1`
