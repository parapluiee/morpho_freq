#order
#ind.prs.1.pl
#mood.tense.person.num
import json
from itertools import chain
import re
import sys
from conllu import parse
def clean_data(lexeme_list, replacements, disallowed, irrelevant):
    #disallowed tag deletion
    for lexeme in lexeme_list: 
        lexeme["forms"] = [form for form in lexeme["forms"] if not any(bad_tag in form["tags"] for bad_tag in disallowed_tags)]
        for form in lexeme["forms"]:
            form["tags"] = [tag for tag in form["tags"] if tag not in irrelevant_tags]
            #I would prefer this but python disallows unpacking in list comprehension
            #form["tags"] = [*replacement_pairs[tag] for tag in form["tags"] if tag in replacement_pairs.keys() else tag]
            form["tags"] = list(set(chain.from_iterable([replacement_pairs[tag] if tag in replacement_pairs.keys() else [tag] for tag in form["tags"]])))
    
    return [lexeme for lexeme in lexeme_list if lexeme["forms"]]



class MorphNode:
    def __init__(self, reg, alt_name, sub_class=[]):
        self.regex = reg
        self.sub_class = sub_class
        self.alt_name = alt_name
        #print(alt_name)
        #print(self.alt_name)

    def check(self, word):
        if re.search(self.regex, word):
            out = [self.alt_name]
            for mnode in self.sub_class:
                ch = mnode.check(word)
                if ch:
                    out.append(ch)
            return out
        else:
            return False
    def count(self):
        return 1 + sum([mnode.count() for mnode in self.sub_class])

    def __str__(self):
        return self.alt_name

class MorphClassifier:
    def __init__(self, nodes):
        self.nodes = nodes
    
    def check(self, word):
        out = []
        for mnode in self.nodes:
            ch = mnode.check(word)
            if ch:
                out.append(ch)
        return out

    def num_classes(self):
        return sum([mnode.count() for mnode in self.nodes])
def create_morph_classes(lemmas):
    er = MorphNode('er$', '-er', [
        MorphNode('ger$', '-ger'), 
        MorphNode('^aller$', 'aller'), 
        MorphNode('yer$', '-yer', [
            MorphNode('^envoyer$|^renvoyer$', 'envoyer/renvoyer')]), 
        MorphNode("[ée].er$", '-eXer/-éXer', [
            MorphNode("e[lt]er$", '-eler/-eter')
            ])
        ])

    ir = MorphNode('ir$', '-ir', [
        MorphNode('oir$', '-oir', [
            MorphNode('voir$', '-voir', [
                MorphNode('^pouvoir$', 'pouvoir'),
                MorphNode('^mouvoir$|^pleuvoir$', 'mouvoir/pleuvoir'),
                MorphNode('evoir$', '-evoir'),
                MorphNode('^savoir$', 'savoir'),
                MorphNode('^avoir$', 'avoir'),
                MorphNode('pleuvoir$', 'pleuvoir'),
                MorphNode('^ravoir$', "ravoir, inf only, never conj")
            ]),
            MorphNode('^vouloir$', 'vouloir'),
            MorphNode('^falloir$', 'falloir'),
            MorphNode('valoir$', 'valoir'),
            MorphNode('asseoir$|surseoir$', 'asseoir type (maybe include -seoir'),
            MorphNode('^déchoir$', 'dechoir'), #should be included
            ]), 
        MorphNode('cueillir$', '-cuiller'), 
        MorphNode('aillir$', '-aiilir'), 
        MorphNode('^offrir$|^souffrir$|ouvrir$', 'offrir/souffrir/-ouvrir'),
        MorphNode('mentir$|dormir$|servir$|partir$|sortir$|sentir$', 'sortir type'),
        MorphNode('^chauvrir$', 'chauvrir'),
        MorphNode('^vêtir$', 'vêtir'),
        MorphNode('^courir$', 'courir'),
        MorphNode('venir$|tenir$', 'venir type'),
        MorphNode('^mourir$', 'mourir'),
        ])

    irr = MorphNode('re$', '-re', [
        MorphNode('^être$', 'être'),
        MorphNode('[eao]ndre$|rdre$|battre&|^foutre$|^rompre$|vaincre$', 'general -re'), #slight difference
        MorphNode('[aeo]indre$', '-indre w/ root change'),
        MorphNode('soudre$', '-soudre'),
        MorphNode('prendre&', 'prendre'),
        MorphNode('^mettre&', 'mettre'), #could be in with rendre
        MorphNode('coudre&', '-coudre'),
        MorphNode('moudre$', '-moudre'),
        MorphNode('vre$', '-vre', [
            MorphNode('^suivre$', 'suivre'),
            MorphNode('^vivre$', 'vivre'),
            ]),
        MorphNode('[ao]ître$', 'a/oître',[
            MorphNode('naître$', '-naître', [
                MorphNode('connaître$', 'connaître')])
            ]),
        MorphNode('uire$', '-uire',[
            MorphNode('^bruire$', 'bruire')
             ]),
        MorphNode('ure$', '-ure'),
        MorphNode('^boire$', 'boire'),
        MorphNode('^croire$', 'croire'),
        MorphNode('aire&', '-aire', [
            MorphNode('faire$', 'faire'),
            MorphNode('^plaire$|^taire$', 'plaire/taire'),
            MorphNode('traire$', '-traire')
            ]),
        MorphNode('ore$', '-ore'),
        MorphNode('ire&', '-ire (not -uire)', [
            MorphNode('dire$', '-dire'),
            MorphNode('^maudire$', 'maudire'),
            MorphNode('lire$', '-lire'),
            MorphNode('^rire&|^sourire&', 'rire/sourire')
            ])
            
        ])

    morph_classifier = MorphClassifier(nodes=[er, ir, irr])
    lemma_to_class = dict()
    class_lemma_list = dict()
    for lem in lemmas:
        mclass = morph_classifier.check(lem)
        if str(mclass) not in class_lemma_list:
            class_lemma_list[str(mclass)] = [lem]
        else:
            class_lemma_list[str(mclass)].append(lem)
        class_lemma_list[str(mclass)] 
        lemma_to_class[lem] = morph_classifier.check(lem)
    return lemma_to_class, class_lemma_list

def get_lemmas(file_path, pos='VERB'):
    with open(file_path, 'r') as f:
        tokens = parse(f.read())
    return [token['lemma'] for sent in tokens for token in sent if token['upos'] == pos]

def count_classes(lem2class, class_lems, lemmas):
    counts = dict()
    for lem in class_lems:
        counts[lem] = 0
    for lem in lemmas:
        counts[str(lem2class[lem])]+=1
    c_list = [(counts[x], x) for x in counts]
    c_list.sort(reverse=True)
    return c_list

def main():
    replacement_pairs={
    }

    disallowed_tags = [
        "table-tags",
        "inflection-template",
        "multiword-construction",
        "alternative"
    ]

    irrelevant_tags = [
        
    ]

    extract_tags = {
        "tag-marked": ("field to extract", "new_name")
    }


    corpus = "data/antille/train.conllu"
    json_path = "data/fr_verbs.jsonl"
    word_type = "verbs"
    #features_csv = "data/paralex_files/hindi_nouns_features.csv"
    #cells_csv = "data/paralex_files/hindi_nouns_cells.csv"
    f = open(json_path)
    verb_list = json.loads(f.read())[word_type]
    lemmas = get_lemmas(corpus)

    example_tags = set()
    #necessary in final product, should add somewhere else in the pipeline, or go over every option
    for form in verb_list[0]["forms"]:
        example_tags = example_tags.union(set(form["tags"]))

    #long signature, I think necessary
    #cell_transform = CellTransformer("vlexique/vlexique_features.csv", example_tags, feature_order)

    #remove multiword
    verb_list = [lex for lex in verb_list if ' ' not in lex['word']]

    lexemes = [verb['word'] for verb in verb_list]
    #verb_list = clean_data(verb_list, replacement_pairs, disallowed_tags, irrelevant_tags)

    #form_to_lemma = dict([(form['form'], lem['word']) for lem in verb_list for form in lem['forms']] + [(lem['word'], lem['word']) for lem in verb_list])

    lem2class, class_lems = create_morph_classes(lemmas)

    counts = count_classes(lem2class, class_lems, lemmas)
    for x in counts:
        print(x)
#print(lem2class)
    """for x in [(mclass, class_lems[mclass]) for mclass in class_lems]:
        if len(x[1]) < 100:
            print(x)
        else:
            print(x[0])"""
main()
