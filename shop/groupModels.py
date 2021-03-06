# -*- coding: utf-8 -*-
import re
from math import fsum


class word:
    def __init__(self, word):
        if word == '': word = ' '
        self.word=word
        self.word_as_list=self.split_word(word)
        self.pattern=self.create_pattern(self.word_as_list)
    def split_word(self, word):
        if word == " ": return " "

        dD=re.compile(u'([^\D-]+)(-*)([^\D-]*)(-*)([^\d-]*)(-*)([^\d-]*)', re.U)
        Dd=re.compile(u'([^\d-]+)(-*)([^\d-]*)(-*)([^\D-]*)(-*)([^\D-]*)', re.U)



        if word[0].isdigit():
            l=dD.findall(word)
        else:
            l=Dd.findall(word)
        return [i.strip() for j in l for i in j if i!='']

    def create_pattern(self, l):
        s=''
        for i in l:
            if i[0].isdigit(): s+='1'
            elif i[0].isalpha(): s+='0'
            else: s+=i
        return s

    def subwords(self, maxlen=10):
        if len(self.word_as_list) == 1:
            return self.word
        res = []
        selflist = filter(lambda k: k!="-", self.word_as_list)
        for l in range(1,min(len(selflist)+1,maxlen+1)):
            for preflen in range(len(selflist)-l+1):
                res.append("".join(selflist[preflen:l+preflen]))
        return res

    def vect(self, elempos, n):
        selfelems = self.word_as_list
        v = [0 for i in range(n)]

        for el in selfelems:
            if elempos.has_key(el):
                v[elempos[el]] = 1

        return v

    def __unicode__(self):
        return self.word

    def __str__(self):
        return self.word

class model:
    def __init__(self, mod, id, splitter=None):
        self.id = id

        if splitter == None: self.words=[word(i) for i in mod.split()]
        else: self.words=[word(i) for i in mod.split(splitter)]

        self.pattern=[i.pattern for i in self.words]
        self.kwphr = set()


    def addtabs(self, positions):
        newwords = []
        #print positions
        for k,i in positions.items():     # [2,0,0,1,0,3]
            #print i, self.words[i].word
            if i != -1:
                newwords.append(self.words[i])
            else:
                newwords.append(word(" "))
        self.words = newwords

    def delwd(self, num):
        del self.words[num]

    def elemsandpairs(self):
        resset = set()

        for wd in self.words:
            if wd.word != " ":
                resset |= set(wd.subwords(2))

        return resset

    def vect(self, elempos, n):

        v = [0 for i in range(n)]

        for el in self.elemsandpairs():
            if elempos.has_key(el.lower()):
                v[elempos[el.lower()]] = 1

        return v


    def find_closest_word(self, el, elarr, el_sizearr ):
        tmp = dict(filter(lambda (k,v): v == el, elarr.iteritems() ))
        score = 0
        ind = None

        for key in tmp.keys():
            if el_sizearr[key] > score:
                ind = key
                score = el_sizearr[key]

        return key


    def checkphrase(self, phrase, grpatt=""):
        if grpatt == "": grpatt = self.pattern
        wordsin = []
        wordsout = []
        phrase_words = phrase.split()
        #phrase_splited_words = [unicode(el).lower() for wd in phrase_words for el in word(wd).word_as_list ]
        self_splited_words = {}
        el_size = {}
        pos = 0

        for ind,obj in enumerate(self.words):
            if obj.word == " ":
                pos += len(grpatt[ind])
                continue
            for el in obj.word_as_list:
                el = unicode(el).lower()
                self_splited_words[pos] = el
                el_size[pos] = float(len(el))/len(obj.word)
                pos +=1

        #print self_splited_words

        modlen = len(self_splited_words)

        patt = {}
        for wd_i,wd in enumerate(phrase_words):
            self_splited_words_copy = self_splited_words.copy()

            for el in word(wd).word_as_list:
                el = unicode(el).lower()

                if el == "-":
                    try:
                        patt[wd_i].append(el)
                    except:
                        patt[wd_i] = [el]

                if el in self_splited_words.values():
                    '''найти наиболее близкое слово'''
                    elpos = self.find_closest_word(el, self_splited_words, el_size)
                    self_splited_words.pop(elpos)
                    try:
                        if el != "-": patt[wd_i].append(elpos)
                    except:
                        if el != "-": patt[wd_i] = [elpos]
                else:
                    if el != "-":
                        wordsout.append(wd)
                        try: del patt[wd_i]
                        except: pass
                        self_splited_words = self_splited_words_copy
                        break

            if patt.has_key(wd_i): wordsin.append(wd)


        l = 0.0
        tmppatt = patt.copy()
        for k,v in tmppatt.items():
            if    v[-1] == "-":
                patt[k].pop()
                if len(patt[k]) == 0: patt.pop(k)
            else: l += len(v)

        intersect = l/float(modlen)

        return intersect, wordsin, wordsout, patt

    def get_subphrathe(self, patt, grpatt):
        self_splited_words = {}
        pos = 0
        for ind,obj in enumerate(self.words):
            if obj.word == " ":
                pos += len(grpatt[ind])
                continue
            for el in obj.word_as_list:
                el = unicode(el).lower()
                self_splited_words[pos] = el
                pos +=1

        res = []
        for k,arr in patt.items():
            s = ""
            if len(set(arr) - set(self_splited_words.keys())) == 0:
                for num in arr:
                    if num == "-":
                        s += num
                    else: s += self_splited_words[num]
                res.append(s)

        return res

    def __unicode__(self):
        return " ".join([str(w.word) for w in self.words])

    def __str__(self):
        return " ".join([str(w.word) for w in self.words])




class ModelGroup:
    def __init__(self, mods):
        self.models = mods
        self.pattern = mods[0].pattern
        self.patlen = len(mods[0].pattern)
        self.smwdcount = int(fsum([len(wd) for wd in self.pattern]))
        self.kwpatt = {}
        self.kwphr = []
        self.pospopularity = {}


    def addmodel(self, mod):
            self.models.append(mod)

    def update_pattern(self):
        num = 0
        while num < self.patlen:
            patt = self.pattern[num]
            if patt != " ": num += 1; continue

            td  = self.gettd(num)
            if len(td) == 0:
                del self.pattern[num]
                self.patlen -= 1
                self.deltd(num)

            else:
                self.pattern[num] = td[0].pattern
                num += 1
        
        self.smwdcount = int(fsum([len(wd) for wd in self.pattern]))

    def getW(self):
        deg = 0.0
        for pos in range(len(self.pattern)):
            deg += self.comparetdself(self.gettd(pos))

        return 0.5*deg/float(len(self.pattern))

    def deltd(self, num):
        for mod in self.models:
            mod.delwd(num)

    def gettd(self, num):
        return [ w.words[num] for w in self.models if w.words[num].word !=" " ]


    def gettdset(self, num):
        res = set()
        tmp = set()
        for mod in self.models:
            wd = mod.words[num]
            if wd.word not in tmp:
                res.add(wd)
                tmp.add(wd.word)

        return res

    def getsubtd(self, num, subnum):
        return [ w.words[num].word_as_list[subnum] for w in self.models if w.words[num].word !=" " ]

    def getsubtdset(self, num, subnum):
        return set(self.getsubtd(num, subnum))

    def tdwidth(self, num):
        return len(self.models[0].words[num].pattern)

    def get_subphrathes(self, patt):
        res = set()

        for mod in self.models:
            res.add(" ".join(mod.get_subphrathe(patt, self.pattern)))

        return res
    
    
    def get_populest_subphrathes(self):
        res = set()
        
        self_popularpos_sorted = [ item[0].split(',') for item in sorted(self.pospopularity.iteritems(), key=lambda (k,v): -v )] 
        for k,popularpos in enumerate(self_popularpos_sorted):
            self_popularpos_sorted[k] = map(lambda i: i if i=='-' else int(i), popularpos)

        for mod in self.models:
            if len(self.pospopularity) > 0:
                for popularpos in self_popularpos_sorted:
                    patt = {0:popularpos}
                    subphr = " ".join(mod.get_subphrathe(patt, self.pattern))
                    subphr = subphr.strip()
                    if len(subphr) > 0: 
                        res.add(subphr)
                        break
            else:
                popularpos = [0]
                
                patt = {0:popularpos}
                subphr = " ".join(mod.get_subphrathe(patt, self.pattern))
                subphr = subphr.strip()
                res.add(subphr)



        return res


    def kwphrase_check(self, phrase, friq=1):
        unitedpatt = {}
        finalunitedpatt = {}
        average_intersect = 0
        wordsoutset = set()

        for model in self.models:
            intersect, wordsin, wordsout, patt = model.checkphrase(phrase, self.pattern)
            if len(wordsoutset)>0: wordsoutset &= set(wordsout)
            else: wordsoutset = set(wordsout)
            #print intersect, patt
            if intersect < 0.1: continue
            for wpos,elposarr in patt.items():
                elposarr = ','.join([str(it) for it in elposarr])
                if not unitedpatt.has_key(wpos): unitedpatt[wpos] = {}
                if unitedpatt[wpos].has_key(elposarr): unitedpatt[wpos][elposarr] += 1
                else: unitedpatt[wpos][elposarr] = 1

                if self.pospopularity.has_key(elposarr): self.pospopularity[elposarr] += friq
                else: self.pospopularity[elposarr] = friq

        elposarr_wpos = {}
        for wpos,elposarrdict in unitedpatt.items():
            for elposarr,fric in elposarrdict.items():
                if elposarr_wpos.has_key(elposarr):
                    if fric > elposarr_wpos[elposarr][1]:
                        unitedpatt[elposarr_wpos[elposarr][0]][elposarr] = 0
                        elposarr_wpos[elposarr] = [wpos, fric]
                    else:
                        unitedpatt[wpos][elposarr] = 0

                else:
                    elposarr_wpos[elposarr] = [wpos, fric]

        for wpos,elposarrdict in unitedpatt.items():
            unitedpatt[wpos] = dict(filter(lambda (k,v): v > 0, elposarrdict.iteritems() ))

        unitedpatt = dict(filter(lambda (k,v): len(v) > 0, unitedpatt.iteritems() ))

        for wpos,elposarrdict in unitedpatt.items():
                '''предпочтение целому слову'''
                if len(elposarrdict) > 1:
                    bestecore = max(elposarrdict.values())

                    if bestecore > 1:
                        elposarrdict = dict(filter(lambda (k,v): v == bestecore, elposarrdict.iteritems() ))

                if len(elposarrdict) > 1:
                    popularity = 0
                    for elposarr in elposarrdict.keys():
                        if self.pospopularity[elposarr] > popularity:
                            popularity = self.pospopularity[elposarr]
                            finalunitedpatt[wpos] = elposarr.split(',')
                else:
                    try:finalunitedpatt[wpos] = unitedpatt[wpos].keys()[0].split(',')
                    except:

                        print [str(m) for m in self.models ]
                        print unicode(phrase)


                finalunitedpatt[wpos] = map(lambda i: i if i=='-' else int(i), finalunitedpatt[wpos])

                average_intersect += len(finalunitedpatt[wpos])

        average_intersect = float(average_intersect)/self.smwdcount

        return average_intersect , finalunitedpatt, wordsoutset

    def get_popular_words_pos(self, count):
        posarrs = [item[0].split(',') for item in sorted(self.pospopularity.iteritems(), key=lambda (k,score): score )]

        elemsset = set()
        res = []
        while count > 0 and len(posarrs) > 0:
            toparr = posarrs.pop()
            toparr = map(lambda i: i if i=='-' else int(i), toparr)
            if len(set(toparr) & elemsset) == 0:
                elemsset |= set(toparr)
                res.append(toparr)
                count -= 1

        return res

    def get_popular_words(self, count):

        count1 = count
        positions = self.get_popular_words_pos(count1)
        positions = dict(enumerate(positions))

        res = set()
        for mod in self.models:
            subphr = mod.get_subphrathe(positions, self.pattern)
            if len(subphr) == count:
                res.add(" ".join(subphr))

        return res

    def subgroup_pos(self, subgr):
        positions = {}
        for i in range(len(self.pattern)):
            positions[i]=-1

        degin = 0.0

        for i, pat in enumerate(subgr.pattern):
            tdnum = -1
            maxintersect = 0

            for j, selfpat in enumerate(self.pattern):
                if selfpat != pat: continue
                intersect = self.comparetd(subgr.gettd(i), self.gettd(j))
                #print selfpat, pat, [i.word for i in subgr.gettd(i)], self.gettd(j)[0].word
                #print intersect
                if intersect > maxintersect and positions[j] == -1:
                    maxintersect = intersect
                    tdnum = j


            if tdnum == -1:
                return -1,-1
            else:
                positions[tdnum] = i
                degin += maxintersect

            degin = 2.0*degin/float(len(self.pattern)+len(subgr.pattern))

        return positions,degin

    def addsubgroup(self, subgr, positions=False):

        if(positions == False):
            positions,degin = self.subgroup_pos(subgr)

        for model in subgr.models:
            model.addtabs(positions)
            self.addmodel(model)

        return 0


    def comparetd(self, td1, td2):
        count = 0.0
        for word1 in td1:
            for word2 in td2:
                if word1.word == " " or word2.word == " ": continue
                if word1.word == word2.word:
                    count += 1
                else:
                    for pair in zip(word2.word_as_list, word1.word_as_list):
                        if pair[0] == pair[1]: count += (1.0*len(pair[1]))/(1.0*len(word2.word))
                if len(word1.pattern) > 1:
                    if [len(el) for el in word1.word_as_list] == [len(el) for el in word2.word_as_list]:
                        count += len(word1.pattern)*0.25

        return count

    def comparetdself(self, td):
        count = 0.0
        for k1,word1 in enumerate(td):
            for k2,word2 in enumerate(td):
                if k1 == k2: continue
                if word1.word == " " or word2.word == " ": continue
                if word1.word == word2.word:
                    count += 1
                else:
                    for pair in zip(word2.word_as_list, word1.word_as_list):
                        if pair[0] == pair[1]: count += (1.0*len(pair[1]))/(1.0*len(word2.word))

        return count

    def get_selfintersected_td(self):
        res = {}
        for num in range(self.patlen):
            td = self.gettd(num)
            selfintersect = self.comparetdself(td)
            if selfintersect > 0:
                res[num] = selfintersect/float(len(td))

        return res

    def get_represent_td(self):

        maxdict = {}
        max = 0.0
        for num, selfpat in enumerate(self.pattern):
            td = self.gettd(num)
            selfintersect = self.comparetdself(td)
            if selfintersect > 0.0:
                maxdict[num] = selfintersect

        maxdict = [ item for item in sorted(maxdict.iteritems(), key=lambda (k,v): v ) ]

        return maxdict

'''
testmod = [model(mod="galaxy&note&&",id=1,splitter="&"), model(mod="galaxy&r&&",id=1,splitter="&"), model(mod="galaxy&s&sclcd&i9003",id=1,splitter="&"), model(mod="star&ii&&",id=1,splitter="&"), model(mod="corby&ii&&",id=1,splitter="&"),  model(mod="galaxy&s&plus&i9001",id=1,splitter="&"),  model(mod="galaxy&s&&",id=1,splitter="&")]

tMg = ModelGroup(testmod)
tMg.update_pattern()
print tMg.kwphrase_check(u"телефон samsung galaxy s ii")
'''

#print model(mod="gt-i5800 galaxy 580",id=1).checkphrase("мобильные телефоны samsung  gt")



