from __future__ import absolute_import, unicode_literals

import json
import re
from typing import Dict, Text


def efficient_string_replace(ref_id_open_token, ref_id_end_token, input, replacements):
    # type: (Text, Text, Text, Dict[Text, Text]) -> Text
    r = re.compile(re.escape(ref_id_open_token) + "(.*?)" + re.escape(ref_id_end_token))

    def replacement(match):
        replacement.performed = True  # no nonlocal keyword in py2
        return replacements[match.group(1)]

    for _ in range(len(replacements) + 1):  # limit retries to avoid endless loop
        replacement.performed = False
        input = r.sub(replacement, input)
        if not replacement.performed:
            break
    else:
        raise RuntimeError("Cyclic replacement pattern found")

    return input


def clean_for_json(s):
    # type: (Text) -> Text
    # make json array and remove [" and "]
    return json.dumps([s])[2:-2]
