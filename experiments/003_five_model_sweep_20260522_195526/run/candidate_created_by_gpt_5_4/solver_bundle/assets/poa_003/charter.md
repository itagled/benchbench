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
- zone `West`: 3
- zone `North`: 6
- zone `East`: 4
- zone `South`: 3
- tier `T1`: 1
- tier `T2`: 2
- tier `T3`: 6
- category `Transit`: 2
- category `Research`: 1
- category `Agriculture`: 0
- category `Medical`: 3
- category `Archives`: 2

Base fee:
- start with 11
- add `quantity * 3`

Standing operational penalties:
- add risk `1` if flag `relay` is present
- add risk `1` if flag `vault` is present
- add risk `3` if flag `dock` is present
- add risk `3` if flag `field` is present
- if `declared_units != quantity`, add risk `4`
- if `record_age >= 5`, add risk `3`
- if `weekend = true`, add fee `3`
