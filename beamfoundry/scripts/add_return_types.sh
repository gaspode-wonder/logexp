#!/usr/bin/env bash
set -euo pipefail

# Iterate through all blueprint route files
find logexp/app/bp -type f -name "routes.py" | while read -r file; do
    echo "Processing $file"

    # Ensure the file has "from typing import Any"
    if ! grep -q "from typing import Any" "$file"; then
        awk '
            /^[[:space:]]*(from|import) / { last_import = NR }
            { lines[NR] = $0 }
            END {
                for (i = 1; i <= NR; i++) {
                    print lines[i]
                    if (i == last_import) {
                        print "from typing import Any"
                    }
                }
            }
        ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    fi

    # Add -> Any to untyped route handlers
    sed -E -i.bak \
        's/^( *def [a-zA-Z0-9_]+\([^)]*\)) *:$/\1 -> Any:/g' \
        "$file"

done

echo "Done."
