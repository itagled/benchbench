# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 6 and greater than 4
- `DENY` if final risk score > 6

Lane thresholds:
- `GREEN` if final fee <= 15
- `AMBER` if final fee <= 26 and greater than 15
- `RED` if final fee > 26

Base risk score components:
- zone `West`: 5
- zone `East`: 7
- zone `South`: 7
- zone `North`: 9
- tier `T1`: 1
- tier `T2`: 4
- tier `T3`: 6
- category `Agriculture`: 2
- category `Archives`: 1
- category `Medical`: 3
- category `Transit`: 1
- category `Research`: 3

Base fee:
- start with 15
- add `quantity * 4`

Standing operational penalties:
- add risk `4` if flag `relay` is present
- add risk `3` if flag `dock` is present
- add risk `1` if flag `vault` is present
- add risk `1` if flag `field` is present
- if `declared_units != quantity`, add risk `5`
- if `record_age >= 6`, add risk `5`
- if `weekend = true`, add fee `3`
