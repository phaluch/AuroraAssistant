#!/bin/bash

print_tree() {
    local dir="$1"
    local prefix="$2"

    # List all items in the directory
    local items=("$dir"/*)
    local count=${#items[@]}

    for ((i=0; i<count; i++)); do
        local item="${items[i]}"
        local base_item=$(basename "$item")
        local is_last=$((i == count - 1))

        if [ -d "$item" ]; then
            echo "${prefix}${is_last:+└── }${is_last:-├── }$base_item"
            # Recurse with new prefix
            new_prefix="${prefix}${is_last:+    }${is_last:-│   }"
            print_tree "$item" "$new_prefix"
        else
            echo "${prefix}${is_last:+└── }${is_last:-├── }$base_item"
        fi
    done
}

# Default to current directory if none provided
root_dir="${1:-.}"
echo "$root_dir"
print_tree "$root_dir" ""
