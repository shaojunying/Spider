#!/bin/bash

# 想从下面的文件中提取大模型的输入。
# 1. 大模型的输入都被包含在 $start 与 $end 之间
# 2. 大模型的输入可能跨行
# 最终希望得到的输出为：
# ----提示词分界线----
#
# 提示词1-第1行
# 提示词1-第2行
#
# ----提示词分界线----
#
# 提示词2-第1行

# 日志文件
file='2024-11-21.log.py'

# 提示词会被 $start与$end包围
start="user, content="
end=')], stream=0,'

# 查找并提取 $start 和 $end 之间的内容
# pcre2grep 可以支持更加复杂的regex，支持跨行匹配
# -M 跨行匹配
# -o 只输出匹配到的内容
# (\n|.)*?尽可能匹配包括\n的任何内容
# \Q \E之间的内容会被当做普通字符串处理。从而避免被转义

# sed 前面返回的内容会包含 $start, $end本身，这一步替换掉这两者
pcre2grep -Mo "$start(\n|.)*?\Q$end\E" $file |
  sed -e "s/^$start/\n----提示词分界线----\n\n/" \
      -e "s/$end$//" > sentences.txt