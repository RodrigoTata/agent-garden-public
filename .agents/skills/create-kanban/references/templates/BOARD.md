<!-- kanban: title="{{BOARD_TITLE}}" brand="{{PROJECT}}" icon="{{ICON}}" lang="{{LANG}}" primary="{{PRIMARY}}" guide="{{GUIDE_HREF}}" prefix="{{PREFIX}}" wip="{{WIP}}" -->
# {{PROJECT}} Kanban board

Agents: read this file before choosing or starting work. The rules are in [README.md](README.md), and how agents use the board is in [{{RULE_PATH}}]({{RULE_LINK}}). Move a row here **and** update the item file's `status` in the same commit, then run `python scripts/render_board.py` to regenerate [BOARD.html](BOARD.html). Never edit the HTML by hand. WIP limit for ⚙️ IN-DEVELOPMENT: {{WIP}}.

**Next free id:** `{{PREFIX}}-001`

## 📥 INBOX (one per area, no ids)

| Area | Inbox | Items |
|---|---|---|
{{INBOX_ROWS}}

## 🔥 NEEDS-GRILLING

| ID | Title | Type | Priority | Area | Blocked by |
|---|---|---|---|---|---|

## 📋 READY-TO-DEV

| ID | Title | Type | Priority | Area | Blocked by |
|---|---|---|---|---|---|

## ⚙️ IN-DEVELOPMENT

| ID | Title | Type | Priority | Area | Branch |
|---|---|---|---|---|---|

## 🧪 IN-QA

| ID | Title | Type | Priority | Area | QA report |
|---|---|---|---|---|---|

## ✅ DONE

| ID | Title | Type | Area | {{DONE_COLUMN}} |
|---|---|---|---|---|

## 🗑️ DROPPED

| ID | Title | Reason |
|---|---|---|
