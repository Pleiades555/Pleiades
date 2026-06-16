# Ford TSB v4 Notes

This patch focuses on concern/symptom extraction.

Ford bulletins often extract from PDF as:

```text
Issue:
Some vehicles may exhibit...
under certain conditions...
This may be due to...
Service Procedure
```

Earlier parsers could capture only:

```text
Some vehicles may exhibit...
```

The v4 parser now joins multiple wrapped lines and stops at real section boundaries.
