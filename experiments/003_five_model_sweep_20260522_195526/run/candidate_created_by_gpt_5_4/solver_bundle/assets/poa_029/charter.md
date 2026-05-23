# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 6 and greater than 4
- `DENY` if final risk score > 6

Lane thresholds:
- `GREEN` if final fee <= 16
- `AMBER` if final fee <= 29 and greater than 16
- `RED` if final fee > 29

Base risk score components:
- zone `West`: 4
- zone `South`: 7
- zone `North`: 3
- zone `East`: 9
- tier `T1`: 2
- tier `T2`: 3
- tier `T3`: 5
- category `Archives`: 0
- category `Research`: 1
- category `Agriculture`: 2
- category `Medical`: 0
- category `Transit`: 3

Base fee:
- start with 17
- add `quantity * 4`

Standing operational penalties:
- add risk `1` if flag `dock` is present
- add risk `4` if flag `vault` is present
- add risk `4` if flag `relay` is present
- add risk `1` if flag `field` is present
- if `declared_units != quantity`, add risk `4`
- if `record_age >= 6`, add risk `3`
- if `weekend = true`, add fee `4`
