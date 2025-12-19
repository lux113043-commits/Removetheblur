"""
主程序入口 - AI图片清晰化Agent
"""
import argparse
import sys
from pathlib import Path
from deblur_agent import DeblurAgent


def main():
    parser = argparse.ArgumentParser(
        description="AI图片清晰化Agent - 使用固定提示词通过DALL-E 3生成清晰图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用
  python main.py input.jpg
  
  # 指定输出路径
  python main.py input.jpg -o output.jpg
  
  # 调整输出尺寸（如2160x3240）
  python main.py input.jpg -s 2160x3240
  
  # 完整示例
  python main.py photo.jpg -o result.jpg -s 2160x3240

注意: 使用固定提示词"请把这个图变成全景深，整个画面中模糊虚化的地方变清晰，边缘锐利。"
使用OpenAI Images API (gpt-image-1.5模型) 直接编辑现有图片，不带mask整图修复。
        """
    )
    parser.add_argument(
        "input",
        type=str,
        help="输入图片路径（必需）"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出图片路径（默认：输入文件名_clear.jpg）"
    )
    parser.add_argument(
        "-s", "--size",
        type=str,
        default=None,
        help="目标尺寸，格式：WIDTHxHEIGHT（例如：1792x1024）。注意：DALL-E 3支持的尺寸为1024x1024, 1792x1024, 1024x1792"
    )
    
    args = parser.parse_args()
    
    # 验证输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：输入文件不存在: {input_path}")
        sys.exit(1)
    
    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_clear.jpg"
    
    # 解析目标尺寸（默认1024×1536）
    target_size = (1024, 1536)  # 默认尺寸
    if args.size:
        try:
            width, height = map(int, args.size.split('x'))
            target_size = (width, height)
        except ValueError:
            print(f"错误：无效的尺寸格式: {args.size}，应使用 WIDTHxHEIGHT 格式")
            sys.exit(1)
    else:
        print(f"使用默认目标尺寸: {target_size[0]}x{target_size[1]}")
    
    # 创建Agent并处理
    print("=" * 60)
    print("AI图片清晰化Agent")
    print("使用OpenAI Images API编辑图片")
    print("固定提示词: 请把这个图变成全景深，整个画面中模糊虚化的地方变清晰，边缘锐利。")
    if target_size == (1024, 1536):
        print("将切分成两张1024×1024分别修复，然后无缝拼接")
    print("=" * 60)
    
    agent = DeblurAgent()
    result = agent.process_image(
        input_path=args.input,
        output_path=str(output_path),
        target_size=target_size
    )
    
    if result["success"]:
        print("\n" + "=" * 60)
        print("✓ 处理完成！")
        print("=" * 60)
        print(f"原始尺寸: {result['original_size'][0]}x{result['original_size'][1]}")
        print(f"最终尺寸: {result['final_size'][0]}x{result['final_size'][1]}")
        print(f"输出文件: {result['output_path']}")
        print("=" * 60)
    else:
        print(f"\n✗ 错误：处理失败")
        print(f"原因: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

