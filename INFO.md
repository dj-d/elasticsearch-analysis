# Info

## Collection Schema

```json
{
    "commit_id": "",
    "author_name": "",
    "timestamp": "",
    "revision_history": [
        {
            "file_name": "/path/to/file",
            "score": 0.0-1.0,
            "isReadable": true|false,
            "error": "",
            "code": 1.0|2.0|3.0|4.0
        }
    ]
}
```

## Analyzed commits

```json
[
    {
        "interval": "0-300",
        "time": "1h20m"
    },
    {
        "interval": "301-600",
        "time": ""
    }
]
```

## TODO

- [x] Create a new repository on GitHub
- [ ] Setup MongoDB
- [ ] Populate MongoDB with data
- [x] Method to get history of repository
- [x] Method to get the list of changed files in a commit
- [x] Method to calculate the readability score of a file