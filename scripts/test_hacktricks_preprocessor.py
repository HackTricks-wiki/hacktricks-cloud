"""Regression tests for rendering links to README chapters."""

import json
import subprocess
import sys
from pathlib import Path


def test_readme_chapter_links_render_as_index_pages(tmp_path):
    preprocessor = Path(__file__).resolve().parents[1] / "hacktricks-preprocessor.py"
    context = {"config": {"preprocessor": {"hacktricks": {"env": "dev"}}}}
    content = """[AppSync](../appsync/README.md#authorization)
[Query](../appsync/README.md?view=details#authorization)
[Details][details]

[details]: ../appsync/README.md#authorization

{{#ref}}
../appsync/README.md#authorization
{{#endref}}

<a href="../appsync/README.md#authorization">Raw HTML</a>
[Remote](https://example.com/appsync/README.md)
[Unlisted](../unlisted/README.md)
`[Example](../appsync/README.md)`

```markdown
[Example](../appsync/README.md)
```
"""
    items = [
        {"Chapter": {"path": name, "source_path": name, "content": text, "sub_items": []}}
        for name, text in [("source/README.md", content), ("appsync/README.md", "## Authorization")]
    ]
    result = subprocess.run(
        [sys.executable, str(preprocessor)],
        input=json.dumps([context, {"items": items}]),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    rendered = json.loads(result.stdout)["items"][0]["Chapter"]["content"]
    assert rendered.count("../appsync/index.html#authorization") == 4
    assert "../appsync/index.html?view=details#authorization" in rendered
    assert "https://example.com/appsync/README.md" in rendered
    assert "../unlisted/README.md" in rendered
    assert rendered.count("[Example](../appsync/README.md)") == 2
