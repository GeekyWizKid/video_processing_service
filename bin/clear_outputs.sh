#!/bin/bash

# 获取当前脚本所在目录的路径
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
OUTPUT_DIR="$BASE_DIR/outputs"

# 检查目录是否存在
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "目录 $OUTPUT_DIR 不存在。"
  exit 1
fi

# 删除目录及其子目录中的所有文件，但保留文件夹结构
find "$OUTPUT_DIR" -type f -exec rm -f {} \;

echo "已删除 $OUTPUT_DIR 内容"


UPLOAD_DIR="$BASE_DIR/uploads"

# 检查目录是否存在
if [ ! -d "$UPLOAD_DIR" ]; then
  echo "目录 $UPLOAD_DIR 不存在。"
  exit 1
fi

# 删除目录及其子目录中的所有文件，但保留文件夹结构
find "$UPLOAD_DIR" -type f -exec rm -f {} \;

echo "已删除 $UPLOAD_DIR 内容"