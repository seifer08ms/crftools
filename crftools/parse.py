#!/usr/bin/env python3
# coding=utf-8
# 预测函数测试
# import codecs
# import sys
import CRFPP
import re
# import collections

# 根据BIE标签合并相应字


def find_element_in_list(element, list_element):
    try:
        list_element.index(element)
        return True
    except ValueError:
        return False


def getStr_InList_ByKey(key, list_i, list_v=None):
    try:
        idx = list_i.index(key)
        if list_v is None:
            list_v = list_i
        return list_v[idx]
    except ValueError:
        return ""


def gen_word_class(words, tags):
    ss = words
    tags_class = [
        re.compile('^._').sub(
            '', tags[i]) for i in range(
            0, len(tags))]
    tags_uniclass = list(set(tags_class))
    tags_uniclass.sort(key=tags_class.index)
    # print(tags_class)
    if(find_element_in_list('O', tags_uniclass)):
        print("O-tags found")
        o_inx = [i for i in range(len(tags_class)) if tags_class[i] == 'O']
        tags_class = [i for j, i in enumerate(tags_class) if j not in o_inx]
        ss = [i for j, i in enumerate(ss) if j not in o_inx]
        tags = [i for j, i in enumerate(tags) if j not in o_inx]
    if (tags[0].startswith('I_') or tags[0].startswith('E_')):
        tags[0] = 'B_' + tags[0][1:]
        print("something wrong with tags")

    for i in range(1, len(tags)):
        if (tags[i - 1].startswith('E_') or
                tags[i - 1].startswith('S_') or
                tags[i - 1] == 'O') and \
                (tags[i].startswith('I_') or tags[i].startswith('E_')):
            tags[i] = 'B_' + tags[i][1:]
            print("something wrong with tags")

    tags_b = [tags[i].startswith('B_') for i in range(0, len(tags))]
    tags_e = [tags[i].startswith('E_') for i in range(0, len(tags))]
    tags_s = [tags[i].startswith('S_') for i in range(0, len(tags))]
    addr_com = [""] * (sum([x for x in tags_b]) + sum([x for x in tags_s]))
    class_com = [""] * (sum([x for x in tags_b]) + sum([x for x in tags_s]))
    # print(tags_uniclass)
    i = 0
    # print(tags_b)
    jj = 0
    while i < len(ss):
        class_cur = tags_class[i]
        j = i + 1
        while j < len(tags):
            if tags_e[j] is True or tags_s[j] is True:
                break
            j += 1
        addr_com[jj] = "".join(ss[i: j + 1])
        class_com[jj] = class_cur
        # print( class_com[jj],addr_com[jj])
        i = j + 1
        jj += 1
    # print(class_com)
    # print(addr_com)
    return (addr_com, class_com)


def merge_number(rawss):
    """
    合并数字
    """
    ss = list(rawss)
    isdigit = [y.isdigit() for y in [i for i in ss]]
    sy = [y for y in [i for i in ss]]
    i = 0
    while i < len(isdigit):
        if isdigit[i]:
            for j in range(i, len(isdigit)):
                if isdigit[j] is not True:
                    break
            if j == len(isdigit) - 1 and isdigit[j]:
                j = j + 1
            sy[i] = "".join(ss[i: j])
            for ii in range(i + 1, j):
                sy[ii] = ''
            i = j
        i += 1
    return(list(filter(None, sy)))


def parse(inputstr, model_path="/crf/model"):
    content_words = merge_number(inputstr.replace(' ', '').replace('\n', ''))
    tags = list()
    try:
        tagger = CRFPP.Tagger("-m " + model_path)
        tagger.clear()
        for word in content_words:
            word = word.strip()
            # print(word)
            if word:
                # tagger.add(word.encode('utf-8'))
                tagger.add(word)  # python3
        tagger.parse()
        # print ("column size: " , tagger.xsize())
        # print ("token size: " , tagger.size())
        # print ("tag size: " , tagger.ysize())
        # print ("tagset information:")
        # ysize = tagger.ysize()
        # for i in range(0, ysize-1):
        # print ("tag " , i , " " , tagger.yname(i))
        size = tagger.size()  # tagger.add的数据大小
        xsize = tagger.xsize()
        # print(xsize)
        for i in range(0, size):
            for j in range(0, xsize):
                # char = tagger.x(i, j).decode('utf-8')
                tag = tagger.y2(i)
                # print(content_words[i],tag)
                tags.append(tag)
    except Exception as e:
        print("RuntimeError: ", e)
    try:
        ss_gen = gen_word_class(content_words, tags)
    except Exception as e:
        print("RuntimeError: ", e)
        print(content_words, tags)

    # dict_table = collections.OrderedDict(province='',
    #                   city='',
    #                   district='',
    #                   LOC='',
    #                   road='',
    #                   road_number='',
    #                   addr_raw='')
    dict_table = dict()
    keys = [
        tagger.yname(i).replace(
            'B_',
            '').replace(
            'I_',
            '').replace(
            'E_',
            '').replace(
                'S_',
            '')
        for i in range(0, tagger.ysize()) if tagger.yname(i) != 'O']
    keys = list(set(keys))
    # keys = [
    #     "name",
    #     "province",
    #     "city",
    #     "district",
    #     "suburb",
    #     "road",
    #     "road_number",
    #     "LOC",
    #     "build_number",
    #     "addr_raw"]
    for i in range(len(keys)):
        if i == len(keys) - 1:
            dict_table[keys[i]] = "".join(content_words).strip()
        else:
            dict_table[keys[i]] = re.sub('\W+', '', getStr_InList_ByKey(
                keys[i], ss_gen[1], ss_gen[0]))
    # dict_table['addr_raw'] = "".join(content_words).strip()
    # dict_table = {k: dict_table[k] for k in keys}
    dict_table = dict((k, dict_table[k]) for k in keys)
    # print(dict_table)
    return dict_table
