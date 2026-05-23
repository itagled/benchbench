# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 5
- `REVIEW` if final risk score <= 7 and greater than 5
- `DENY` if final risk score > 7

Lane thresholds:
- `GREEN` if final fee <= 17
- `AMBER` if final fee <= 31 and greater than 17
- `RED` if final fee > 31

Base risk score components:
- zone `East`: 5
- zone `North`: 6
- zone `West`: 8
- zone `South`: 4
- tier `T1`: 2
- tier `T2`: 4
- tier `T3`: 4
- category `Medical`: 0
- category `Archives`: 1
- category `Agriculture`: 0
- category `Transit`: 2
- category `Research`: 2

Base fee:
- start with 16
- add `quantity * 3`

Standing operational penalties:
- add risk `2` if flag `relay` is present
- add risk `3` if flag `dock` is present
- add risk `2` if flag `vault` is present
- add risk `2` if flag `field` is present
- if `declared_units != quantity`, add risk `6`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `3`
