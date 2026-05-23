# Charter

Decision thresholds:
- `ALLOW` if final risk score <= 4
- `REVIEW` if final risk score <= 8 and greater than 4
- `DENY` if final risk score > 8

Lane thresholds:
- `GREEN` if final fee <= 17
- `AMBER` if final fee <= 26 and greater than 17
- `RED` if final fee > 26

Base risk score components:
- zone `North`: 8
- zone `East`: 4
- zone `West`: 5
- zone `South`: 4
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 4
- category `Medical`: 2
- category `Transit`: 2
- category `Archives`: 0
- category `Research`: 3
- category `Agriculture`: 2

Base fee:
- start with 18
- add `quantity * 4`

Standing operational penalties:
- add risk `1` if flag `field` is present
- add risk `4` if flag `relay` is present
- add risk `4` if flag `dock` is present
- add risk `4` if flag `vault` is present
- if `declared_units != quantity`, add risk `7`
- if `record_age >= 6`, add risk `2`
- if `weekend = true`, add fee `4`
