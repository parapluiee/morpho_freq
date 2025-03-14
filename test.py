from nltk.corpus import brown

#I (prs)
#He (prs)
#I (past)
#I had (past)
#I am (progressive)

def get_form_to_lemma(file_path):
    form_to_lemma = dict()
    unimorph_lemmas = set()
    with open(file_path) as f:
        for line in f:
            sp = line.split('\t')
            if sp[2][0] == 'V':
             form_to_lemma[sp[1]] = sp[0]
             unimorph_lemmas.add(sp[0])
    return unimorph_lemmas, form_to_lemma


def get_lemma_to_segmentation(file_path):
    out = dict()
    with open(file_path) as f:
        for line in f:
            print(line)
            sp = line.split('\t')
            if (sp[2][0] != 'V'):
                continue
            if (sp[0] not in out.keys()):
                out[sp[0]] = set()
            seg_split = sp[3].split('|')
            if len(seg_split) > 1:
                out[sp[0]].add(sp[3].split('|')[1].strip('\n'))
    return out


def main():
    unimorph_lemmas, form2lemma = get_form_to_lemma('eng/eng')
    print("Number of unique verb forms in eng_unimorph: {}".format(len(form2lemma.keys())))
    print(f"Number of unique verb lemmas in eng_unimorph : {len(unimorph_lemmas)}")
    verbs = [x[0] for x in brown.tagged_words() if x[1][0] == 'V']


    print("Number of verb forms not in brown corpus: {}".format(len(set([word for word in verbs if word not in form2lemma.keys()]))))

    
    lemmas = list()
    for verb in verbs:
        if (verb in form2lemma.keys()):
            lemmas.append(form2lemma[verb])
    lemmas_in_brown = set(lemmas)
    print(f"Number of verbs (all forms) in brown : {len(verbs)}")
    print(f"Numbers of verbs accounted for in unimorph : {len(lemmas)}")
    print("Number of unimporph verb lemmas in brown: {}".format(len(lemmas_in_brown)))
    lemma_to_seg = get_lemma_to_segmentation('eng/eng.segmentations')
    classes = dict()
    classes_set = set()
    for lemma in lemmas_in_brown:
        
        if lemma in lemma_to_seg.keys():
            classes[lemma] = lemma_to_seg[lemma]
            classes_set.add(tuple(lemma_to_seg[lemma]))
    print("Number of classes: {}".format(len(classes_set))) 
    counts = dict.fromkeys(classes_set, 0)
    class_lemmas = dict()
    for lemma in lemmas:
        #if tuple(classes[lemma]) == ('en', 'ing','ed'):
        #    print(f"{lemma} : {classes[lemma]}")
        counts[tuple(classes[lemma])]+= 1
        if tuple(classes[lemma]) not in class_lemmas:
            class_lemmas[tuple(classes[lemma])] = set()
        class_lemmas[tuple(classes[lemma])].add(lemma)
    #print(counts) 
    #print(len(verbs))
    #print(len(lemmas))
    print(counts)
    for cla in class_lemmas:
        if counts[cla] < 200:
            print(cla, " : ", class_lemmas[cla])
main()
