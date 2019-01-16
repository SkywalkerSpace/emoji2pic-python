import os


def organize_file_name(file_dir='AppleEmoji'):
    """
    从emoji图片文件名整理出对应的Unicode
    GET Unicode from file name
    """
    for root, dirs, files in os.walk(file_dir):
        pass

    unicode_to_path = dict()
    initial_unicode = dict()

    for file in files:
        chip_list = file.split('_')
        eng = len(chip_list[0]) + 1 if chip_list[1][:5] != 'emoji' else len(chip_list[0] + chip_list[1]) + 2
        base_name = file[eng:-4].replace('_', '-')
        base_name_chip_list = base_name.split('-')

        unicode_chip_list = list()
        for chip in base_name_chip_list:
            if len(chip) == 2:
                unicode_chip = u'\\x' + chip
            elif len(chip) == 4:
                unicode_chip = u'\\u' + chip
            elif len(chip) == 5:
                unicode_chip = u'\\U000' + chip
            else:
                raise ValueError(chip)
            unicode_chip_list.append(unicode_chip.encode('utf-8').decode('unicode_escape'))

        if initial_unicode.get(unicode_chip_list[0]) is None:
            initial_unicode[unicode_chip_list[0]] = [len(unicode_chip_list)]
        else:
            if len(unicode_chip_list) not in initial_unicode[unicode_chip_list[0]]:
                initial_unicode[unicode_chip_list[0]].append(len(unicode_chip_list))
                initial_unicode[unicode_chip_list[0]] = sorted(initial_unicode[unicode_chip_list[0]], reverse=True)

        unicode_name = ''.join(unicode_chip_list)
        unicode_to_path[unicode_name] = file

    print(initial_unicode)
    print(unicode_to_path)
    return


if __name__ == '__main__':
    organize_file_name()
