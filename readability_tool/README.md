# A Comprehensive Model for Code Readability
This is the tool associated with the paper "A Comprehensive Model for Code Readability" (JSEP 2018).

## Setup
To run the tool, extract both the files (`rsm.jar` and `readability.classifier`) in the same folder. `rsm.jar` is an executable JAR which can be directly used to compute code readability.

## Computing code readability
`rsm.jar` can be used to compute either:

- the readability of a given snippet stored in a file
- the readability of a Java class, computed as the mean readability of all the methods that compose it.

To compute code readability, use the following command, specifying at least a file name:

```bash
java -jar rsm.jar {filename} [{filename2} {filename3} ... {filenameN}]
```

Examples:

```bash
java -jar rsm.jar test.java # Compute the readability of a file
java -jar rsm.jar test.java test2.java # Compute the readability of two files
java -jar rsm.jar src/**/*.java # Compute the readability of a project
```

## Extract metrics
`rsm.jar` can also be used to compute all the features on which the comprehensive model is based (structural, visual, and textual). You can extract the values of all the metrics from a given snippet by using the following command:

```bash
java -cp rsm.jar it.unimol.readability.metric.runnable.ExtractMetrics {filename}
```

The output will be a list of couples `{metric name}: {value}` (one per line).
Example (partial output):

```
New Identifiers words AVG: 0.7625
New Identifiers words MIN: 0.0
New Abstractness words AVG: 5.253731343283582
New Abstractness words MAX: 8.0
New Abstractness words MIN: 0.0
```

The first word (e.g., "New") indicates the paper in which the metric was introduced:

- `New` → The new metrics introduced in our JSEP 2018 paper (Textual); each metric name ends with a word that indicates the aggregation used (`AVG`, `MAX`, and `MIN` for average, maximum and minimum, respectively);
- `BW` → The metrics introduced by Buse and Weimer (Structural); the second word of each metric name indicates the aggregation used (`Avg` and `Max` for average and maximum, respectively);
- `Posnett` → The metrics introduced by Posnett et al. (Structural)
- `Dorn` → The metrics introduced by Dorn (mostly visual)

The names of the textual metrics extracted by the tool (the one with the prefix `New`) are different from the ones reported in the JSEP paper. Please use the following mapping to identify them:

- Comments and Identifiers Consistency (`CIC`): `Commented words`
- Comments and Identifiers Consistency with synonyms (`CIC_{syn}`): `Synonym commented words`
- Identifier Terms in Dictionary (`ITID`): `Identifiers words`
- Narrow Meaning Identifiers (`NMI`): `Abstractness words`
- Comments Readability (`CR`): `Comments readability`
- Number of Meanings (`NM`): `Number of senses`
- Textual Coherence (`TC`): `Text Coherence`
- Number of Concepts (`NOC`): `Semantic Text Coherence`

The other metrics marked as `New` are either old versions of the same metrics or experimental ones. They are not used in the final model.
