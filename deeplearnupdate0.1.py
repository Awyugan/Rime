# 可以运行基础的中文序列，无法处理英文序列import pinyinimport osimport redef get_pinyin_representation(word):    if word.isascii() and word.isalpha():        return word.lower()    elif all(char.isalpha() or char.isspace() for char in word) and re.search(r'[a-zA-Z]', word):        abbreviation = ''.join([w[0] for w in word.lower().split()])        return abbreviation    elif all(char.isalpha() or char.isspace() for char in word):        return pinyin.get(word, format='strip', delimiter=' ')    else:        return Nonedef read_original_file(filename):    try:        entries = []        with open(filename, 'r', encoding='utf-8') as f:            content = f.read()            header, entries_section = content.split("...\n", 1)            entries = [line.strip() for line in entries_section.strip().split('\n') if line.strip()]        return header + "...\n\n", entries # Add an extra newline after ...    except Exception as e:        print(f"Error reading original file: {e}")        return "", []def read_vocab_file(filename, original_entries):    original_entries_set = set(original_entries)    new_entries = []    try:        with open(filename, 'r', encoding='utf-8') as f:            lines = f.readlines()        for word in lines:            word = word.strip()            pinyin_representation = get_pinyin_representation(word)            if pinyin_representation:                entry = f"{word}\t{pinyin_representation}"                if entry not in original_entries_set:                    new_entries.append(entry)            else:                print(f"Skipping invalid entry: {word}")        return new_entries    except Exception as e:        print(f"Error reading file: {e}")        return []def sort_entries_by_key(entries):    return sorted(entries, key=lambda x: x.split('\t')[0])def write_entries_to_file(header, original_entries, new_entries, filename):    try:        temp_filename = filename + '.temp'        sorted_entries = sort_entries_by_key(list(set(original_entries + new_entries)))        if sorted_entries:            with open(temp_filename, 'w', encoding='utf-8') as f: # Write to temp file                f.write(header)                for entry in sorted_entries:                    f.write(f"{entry}\n")            print(f"Temp file written to {temp_filename}. Please review it before replacing the original file.")            # Ask for confirmation to merge            confirmation = input("Do you want to merge the temp file into the original file? Type 'yes' to confirm: ")            if confirmation.lower() == 'yes':                os.rename(temp_filename, filename)                print(f"File {filename} has been updated successfully.")            else:                print(f"Merge aborted. Temp file is still available at {temp_filename}.")        else:            print("No valid entries found to write to the file.")    except Exception as e:        print(f"Error writing to file: {e}")input_vocab_file = 'input_vocab.txt'output_yaml_file = 'luna_pinyin.deeplearning.dict.yaml'# Read original file (header, entries)header, original_entries = read_original_file(output_yaml_file)# Read new vocab file, excluding entire entries already in original entriesnew_entries = read_vocab_file(input_vocab_file, original_entries)# Write to temp file, preserving header, and sorting by keywrite_entries_to_file(header, original_entries, new_entries, output_yaml_file)