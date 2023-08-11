# 只提取input_vocab.txt文件中的中文，排序按拼音顺序，先生成temp文件，之后在命令行中确认# 添加去重、排序、确认合并提示# 输出temp文件的绝对位置# temp文件yes/no，yes合并temp到主文件，no则删除temp文件并结束# 合并文件为文件编号import pinyinimport osimport reimport globfrom tkinter import filedialogfrom tkinter import Tkfrom send2trash import send2trashdef choose_input_files():    choice = input("Choose input option: 1. Select one or more files, 2. Use default input_vocab.txt\n选择输入选项：1. 选择一个或多个文件，2. 使用默认的 input_vocab.txt\n")    if choice == '1':        root = Tk()        root.withdraw()        file_paths = filedialog.askopenfilenames(title='Select input files', filetypes=[('Text files', '*.txt')])        return list(file_paths), False    elif choice == '2':        return ['input_vocab.txt'], True    else:        print("Invalid choice. Please try again./无效选择。请重试。")        return None, Falsedef choose_yaml_file():    yaml_files = glob.glob('*.dict.yaml')    if not yaml_files:        print("No .dict.yaml files found in the current directory./当前目录中未找到 .dict.yaml 文件。")        return None    print("Please choose a .dict.yaml file to modify:/请选择要修改的 .dict.yaml 文件：")    for i, file in enumerate(yaml_files):        print(f"{i + 1}. {file}")    choice = input("Enter the number of the file you want to modify:/输入要修改的文件编号：")    try:        selected_file = yaml_files[int(choice) - 1]        return selected_file    except (ValueError, IndexError):        print("Invalid choice. Please try again./无效选择。请重试。")        return Nonedef process_files(input_files, output_yaml_file):    # Read original file (header, entries)    header, original_entries = read_original_file(output_yaml_file)    # Read new vocab files    new_entries = []    for input_file in input_files:        new_entries.extend(read_vocab_file(input_file, original_entries))    # Write to temp file, preserving header, and sorting by key    return write_entries_to_file(header, original_entries, new_entries, output_yaml_file)def cleanup(input_files, use_default):    if use_default:        for input_file in input_files:            send2trash(input_file)            with open(input_file, 'w', encoding='utf-8') as f:                pass            print(f"File {input_file} has been moved to trash and a new empty file has been created./文件 {input_file} 已移至垃圾箱，并已创建新的空文件。")def get_pinyin_representation(word):    if all(char.isalpha() or char.isspace() for char in word):        return pinyin.get(word, format='strip', delimiter=' ')    else:        return Nonedef read_original_file(filename):    try:        entries = []        with open(filename, 'r', encoding='utf-8') as f:            content = f.read()            header, entries_section = content.split("...\n", 1)            entries = [line.strip() for line in entries_section.strip().split('\n') if line.strip()]        return header + "...\n\n", entries # Add an extra newline after ...    except Exception as e:        print(f"Error reading original file: {e}")        return "", []def read_vocab_file(filename, original_entries):    original_entries_set = set(original_entries)    new_entries = []    try:        with open(filename, 'r', encoding='utf-8') as f:            lines = f.readlines()        for line in lines:            line = line.strip()            chinese_word_match = re.search(r'[\u4e00-\u9fff]+', line) # 匹配中文部分            if chinese_word_match:                chinese_word = chinese_word_match.group()                pinyin_representation = get_pinyin_representation(chinese_word)                if pinyin_representation:                    entry = f"{chinese_word}\t{pinyin_representation}"                    if entry not in original_entries_set:                        new_entries.append(entry)                else:                    print(f"Skipping invalid entry: {line}")        print("De-duplication of entries was successful./条目的重复数据删除成功。") # 去重成功的提示        return new_entries    except Exception as e:        print(f"Error reading file: {e}")        return []def sort_entries_by_key(entries):    sorted_entries = sorted(entries, key=lambda x: pinyin.get(x.split('\t')[0], format="strip"))    print("Sorting of entries by pinyin was successful./按拼音排序条目成功了。") # 排序成功的提示    return sorted_entriesdef write_entries_to_file(header, original_entries, new_entries, filename):    try:        temp_filename = filename + '.temp'        sorted_entries = sort_entries_by_key(list(set(original_entries + new_entries)))        if sorted_entries:            with open(temp_filename, 'w', encoding='utf-8') as f: # Write to temp file                f.write(header)                for entry in sorted_entries:                    f.write(f"{entry}\n")            absolute_temp_filename = os.path.abspath(temp_filename)            print(f"Temp file written to {absolute_temp_filename}. Please review it before replacing the original file./临时文件已写入 {absolute_temp_filename}。请在替换原始文件前查看它。") # 输出绝对路径            # Ask for confirmation to merge            confirmation = input("Do you want to merge the temp file into the original file? Type 'yes' to confirm or 'no' to discard. Type 'yes' to confirm, 'no' to discard./是否要将临时文件合并到原始文件中？输入 'yes' 确认，'no' 放弃。")            if confirmation.lower() == 'yes':                os.rename(temp_filename, filename)                print(f"File {filename} has been updated successfully./文件 {filename} 已成功更新。")                return True            else:                os.remove(temp_filename) # 删除临时文件                print(f"Merge aborted. Temp file {absolute_temp_filename} has been deleted./合并已中止。临时文件 {absolute_temp_filename} 已被删除。") # 输出删除临时文件的消息                return False        else:            print("No valid entries found to write to the file./未找到有效条目写入文件。")            return False    except Exception as e:        print(f"Error writing to file: {e}/写入文件时出错：{e}")        return Falseinput_files, use_default = choose_input_files()if input_files:    output_yaml_file = choose_yaml_file()    if output_yaml_file:        merge_successful = process_files(input_files, output_yaml_file)        if merge_successful:            cleanup(input_files, use_default)    else:        print("Operation aborted./操作已中止。")else:    print("No valid input files selected. Operation aborted./未选择有效的输入文件。操作已中止。")