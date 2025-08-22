

import re

def extract_oracle_content(text: str):
    """
    從文字中抓出包含 'oracle' 的片段，
    片段範圍是從 '>' 到 '<'，並保留其中的文字。
    """
    # 找出 >...< 中包含 oracle 的片段
    pattern = re.compile(r'>([^<>]*?oracle[^<>]*?)<', re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

def extract_oracle_content_no_re(text: str):
    """
    不使用re
    """
    results = []
    start = 0
    while True:
        gt = text.find('>', start)
        if gt == -1:
            break
        lt = text.find('<', gt)
        if lt == -1:
            break
        segment = text[gt+1:lt]  # 去掉 > 和 <
        if 'oracle' in segment.lower():  # 忽略大小寫
            results.append(segment)
        start = lt + 1
    return results

def extract_oracle_content_keyword(text: str, key_word: str):
    """
    從文字中抓出包含指定關鍵字的片段，
    片段範圍是從 '>' 到 '<'，並保留其中的文字。
    """
    pattern = re.compile(rf'>([^<>]*?{re.escape(key_word)}[^<>]*?)<', re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

# 範例文字
html_text = """
<table class="is-table-longdescription">
<tbody>
<tr>
<th>CORE        11.2.0.2.0      Production</th>
</tr>
<tr>
<th>NLSRTL Version 11.2.0.2.0 - Production</th>
</tr>
<tr>
<th>Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production</th>
</tr>
<tr>
<th>PL/SQL Release 11.2.0.2.0 - Production</th>
</tr>
<tr>
<th>TNS for Linux: Version 11.2.0.2.0 - Production</th>
</tr>
</tbody>
</table>
"""

# results = extract_oracle_content(html_text)
# for r in results:
#     print(r)
# results = extract_oracle_content_no_re(html_text)
# for r in results:
#     print(r)

results = extract_oracle_content_keyword(html_text, "Production")
for r in results:
    print(r)