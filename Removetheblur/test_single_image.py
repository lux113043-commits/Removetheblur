"""
测试单张图片处理，用于诊断API调用问题
"""
import os
from pathlib import Path
from deblur_agent import DeblurAgent

def test_single_image():
    """测试处理单张图片"""
    # 使用第一张失败的图片
    test_image = Path("D:/ceshituppian/005.png")
    
    if not test_image.exists():
        print(f"错误: 图片不存在: {test_image}")
        return
    
    print("=" * 60)
    print("测试单张图片处理")
    print("=" * 60)
    print(f"测试图片: {test_image}")
    print(f"图片存在: {test_image.exists()}")
    print()
    
    # 检查环境变量
    print("环境变量检查:")
    print(f"  ALL_PROXY: {os.environ.get('ALL_PROXY', 'Not set')}")
    print(f"  SOCKS_PROXY: {os.environ.get('SOCKS_PROXY', 'Not set')}")
    print(f"  HTTPS_PROXY: {os.environ.get('HTTPS_PROXY', 'Not set')}")
    print()
    
    try:
        # 初始化agent
        print("正在初始化AI处理器...")
        agent = DeblurAgent()
        print("✓ AI处理器初始化成功")
        print()
        
        # 处理图片
        output_path = Path("test_output_005_clear.jpg")
        print(f"开始处理图片...")
        print(f"输出路径: {output_path}")
        print()
        
        result = agent.process_image(
            input_path=str(test_image),
            output_path=str(output_path),
            target_size=(1024, 1536)
        )
        
        print()
        print("=" * 60)
        print("处理结果:")
        print("=" * 60)
        print(f"成功: {result.get('success', False)}")
        if result.get('success'):
            print(f"输出文件: {result.get('output_path')}")
            print(f"原始尺寸: {result.get('original_size')}")
            print(f"最终尺寸: {result.get('final_size')}")
        else:
            print(f"错误: {result.get('error', '未知错误')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 发生异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_image()



