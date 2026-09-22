"""The unified diff parser.

Finding line numbers are measured against the new version of the file, so
the parser has to track the new-file counter correctly through added,
removed, and context lines. No model calls.
"""

import review

SIMPLE = """diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -10,3 +10,4 @@ def handler():
     existing = 1
+    added = 2
     trailing = 3
     final = 4
"""

MULTI_HUNK = """diff --git a/models.py b/models.py
--- a/models.py
+++ b/models.py
@@ -1,2 +1,3 @@
 import sqlite3
+import os
 from pathlib import Path
@@ -50,4 +51,5 @@ def search():
     conn = get_conn()
-    sql = "SELECT 1"
+    sql = "SELECT %s" % query
     return conn.execute(sql)
"""

TWO_FILES = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,1 +1,2 @@
 one
+two
diff --git a/b.py b/b.py
--- a/b.py
+++ b/b.py
@@ -5,1 +5,2 @@
 five
+six
"""

DELETED_FILE = """diff --git a/gone.py b/gone.py
--- a/gone.py
+++ /dev/null
@@ -1,2 +0,0 @@
-one
-two
"""

NEW_FILE = """diff --git a/new.py b/new.py
new file mode 100644
--- /dev/null
+++ b/new.py
@@ -0,0 +1,3 @@
+first
+second
+third
"""


def test_single_added_line_gets_the_right_number():
    assert review.parse_unified_diff(SIMPLE) == {"app.py": {11}}


def test_context_lines_advance_the_counter_but_are_not_reported():
    changed = review.parse_unified_diff(SIMPLE)
    assert 10 not in changed["app.py"]
    assert 12 not in changed["app.py"]


def test_multiple_hunks_each_reset_the_counter():
    changed = review.parse_unified_diff(MULTI_HUNK)
    assert changed["models.py"] == {2, 52}


def test_removed_lines_do_not_advance_the_new_file_counter():
    changed = review.parse_unified_diff(MULTI_HUNK)
    # The removed "SELECT 1" sat at old line 51. The added line that
    # replaces it is new line 52, not 53.
    assert 53 not in changed["models.py"]


def test_two_files_are_tracked_separately():
    assert review.parse_unified_diff(TWO_FILES) == {"a.py": {2}, "b.py": {6}}


def test_the_b_prefix_is_stripped_from_paths():
    assert list(review.parse_unified_diff(SIMPLE)) == ["app.py"]


def test_a_deleted_file_contributes_nothing():
    assert review.parse_unified_diff(DELETED_FILE) == {}


def test_a_new_file_reports_all_of_its_lines():
    assert review.parse_unified_diff(NEW_FILE) == {"new.py": {1, 2, 3}}


def test_an_empty_diff_is_empty_not_an_error():
    assert review.parse_unified_diff("") == {}


def test_a_diff_with_no_changes_yields_an_empty_line_set():
    unchanged = """--- a/x.py
+++ b/x.py
@@ -1,2 +1,2 @@
 one
 two
"""
    assert review.parse_unified_diff(unchanged) == {"x.py": set()}


def test_hunk_header_without_a_line_count_is_parsed():
    single = """--- a/y.py
+++ b/y.py
@@ -7 +7 @@
-old
+new
"""
    assert review.parse_unified_diff(single) == {"y.py": {7}}


def test_text_before_the_first_file_header_is_ignored():
    noisy = "some git preamble\nwarning: whatever\n" + SIMPLE
    assert review.parse_unified_diff(noisy) == {"app.py": {11}}
