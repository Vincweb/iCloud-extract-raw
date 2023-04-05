# Python scrypt

By Vincent Caudron 
with pyicloud

https://github.com/picklepete/pyicloud

## Others

https://github.com/RhetTbull/osxphotos


## Script sort photo

```sh
#!/bin/bash

for file in ./IMPORTS/*; do
    if [ -f "$file" ]; then
        date=$(exiftool -d ':%Y/%m/%d' -DateTimeOriginal "$file" | cut -d ':' -f 3)
        echo "$date : $file"
        mkdir -p "$date"
        mv "$file" "$date"
    fi
done
```