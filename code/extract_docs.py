import player, level, main, inspect
import sys
import os

def get_docs(module, module_name):
    print(f"\n========================================================")
    print(f" MODULE: {module_name}")
    print(f"========================================================\n")
    
    # Get classes in the module
    for class_name, obj in inspect.getmembers(module, inspect.isclass):
        # Only get classes defined in this module
        if obj.__module__ == module.__name__:
            print(f"CLASS: {class_name}")
            class_doc = inspect.getdoc(obj)
            if class_doc:
                print(f"Mô tả: {class_doc}\n")
            
            # Get methods in the class
            for func_name, func_obj in inspect.getmembers(obj, inspect.isfunction):
                method_doc = inspect.getdoc(func_obj)
                if method_doc:
                    print(f"  Method: {func_name}()")
                    print(f"  Chi tiết: {method_doc}\n")
            print("-" * 40)

# Set up output to file
output_file = 'DOCSTRINGS_REPORT.txt'
original_stdout = sys.stdout

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        sys.stdout = f
        print("PHỤ LỤC 2: TÀI LIỆU DOCSTRING CỦA DỰ ÁN CYCLE OF CURSE\n")
        get_docs(player, "PLAYER (Nhân vật)")
        get_docs(level, "LEVEL (Màn chơi & Camera)")
        get_docs(main, "MAIN (Khởi chạy hệ thống)")
        print("\n--- BÁO CÁO KẾT THÚC ---")
    
    sys.stdout = original_stdout
    print(f"Successfully generated {output_file} in the current directory.")
except Exception as e:
    sys.stdout = original_stdout
    print(f"Error occurred: {e}")
