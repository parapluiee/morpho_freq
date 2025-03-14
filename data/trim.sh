#!/bin/bash

cat $1 | jq -c 'if .pos == "verb" and .head_templates[0].name == "fr-verb" and has("forms") then {"word": .word, "pos": .pos, forms: .forms} else empty end' | sed '$!s/$/,/' | sed '1 i\{"verbs": [' > fr_verbs.jsonl
echo ']}' >> fr_verbs.jsonl


