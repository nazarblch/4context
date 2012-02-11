# -*- coding: utf-8 -*-

def del_substr(str, badwords): #        Удаляем в строке str все слова из badwords    
    str=str.strip().center(len(str)+2)
    for word in badwords:
        word = word.strip().center(len(word)+2) 
        while str.find(word) >= 0:
            index = str.find(word)
            str = ' '.join([str[:index],str[index+len(word):]])           
    str=str.strip()
    return str

def del_str(lst, used_words): #         Удаляем строки из lst если в них содержится слово из used_words
    clear_lst = []
    for str in lst:
        it = iter(range(len(used_words) + 1))
        str = str.strip().center(len(str)+2)
        for word in used_words:
            word = word.strip().center(len(word)+2)
            if word in str: it.next()
        if it.next() == 0: clear_lst.append(str.strip())
    return clear_lst
        
        
        
        
lst = ['dsf sfs dfskjf ', 'qewfbcu fdis dnusdfg', 'fdf', '12gvcg2 1jg3 g23', 'fdis g23']
used = ['fdis', 'g23']
