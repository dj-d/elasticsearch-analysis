```shell
git log --pretty=format:"%H|%an|%at" > /home/dj-d/Repositories/GitHub/asd_exam/history.txt
```

- ```%H``` - commit hash
- ```%an``` - author name
- ```%at``` - author time, UNIX timestamp

```shell
git show --name-only --pretty="" <commit-id>
```

### Steps

- [ ] Create a new repository on GitHub
- [ ] Setup MongoDB
- [ ] Populate MongoDB with data
  ```json
    {
        "commit_id": "",
        "author_name": "",
        "author_date": "",
        "unreadable_classes": [
            {
                "file_name": "",
                "score": ""
            }
        ]
    }
  ```
- [x] Method to get the list of files in a commit
- [x] Method to get the readability score of a file

### References

- [Git - git-log Documentation](https://git-scm.com/docs/pretty-formats)