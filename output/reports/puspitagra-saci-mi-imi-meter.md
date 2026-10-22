# Metre of "saci mi imi viśiṣṭa naivarūpā …": Puṣpitāgrā

*Date: 2026-10-21. Tool: `chanda` 1.1.0 (Hrishikesh Terdalkar), editable install from `~/Documents/GitHub/chanda`, called through its Python API with fuzzy matching on. The verse's source was not identified in this session.*

## Verse

```
saci mi imi viśiṣṭa naivarūpā
varapraṇidhāna siyā khu bodhiprāpte /
māhu siya narendra sattvasāro
daśabaladhāri atulyadakṣiṇīyaḥ //
```

## Result

The verse is in **Puṣpitāgrā**, the half-equal (ardhasama) metre of the Aupacchandasika family:

| Pādas | Gaṇas | Pattern (L light, G heavy) | Syllables | Mātrās |
|---|---|---|---|---|
| odd (a, c) | na na ra ya | LLL LLL GLG LGG | 12 | 16 |
| even (b, d) | na ja ja ra + G | LLL LGL LGL GLG G | 13 | 18 |

In verse mode chanda gives Puṣpitāgrā as the only meter that explains all four pādas (match extent 1.0). The runners-up are far behind: Mṛgendramukha at 0.46 and Udgatā at 0.40. Chanda lists the meter as "Aupacchandasika = Puṣpitāgrā", treating Puṣpitāgrā as the syllabically fixed form of the Aupacchandasika type.

## Pāda by pāda

| Pāda | Text | Chanda's scansion | Syl. | Mātrās | Fit |
|---|---|---|---|---|---|
| a | saci mi imi viśiṣṭa naivarūpā | LLL LLL GLG LGG | 12 | 16 | exact |
| b | varapraṇidhāna siyā khu bodhiprāpte | LGL LGL LGL GGG G | 13 | 20 | 2 syllables heavy by position |
| c | māhu siya narendra sattvasāro | GLL LLG LGL GG | 11 | 16 | 1 syllable short, morae correct |
| d | daśabaladhāri atulyadakṣiṇīyaḥ | LLL LGL LGL GLG G | 13 | 18 | exact |

### Pāda b

Expected LLLLGLLGLGLGG. Chanda's scansion differs at two positions:

- **Syllable 2, *ra*,** is heavy only by position before *pr* (va-**ra**-pra-ṇi-dhā-na).
- **Syllable 11, *dhi*,** is heavy only by position before *pr* (bo-**dhi**-prā-pte).

Buddhist Hybrid Sanskrit verse often does not lengthen a short vowel before a stop + r cluster. Reading both syllables light gives the regular even-pāda pattern and the expected 18 mātrās instead of 20.

### Pāda c

As written, the pāda has 11 syllables against the expected 12, but its 16 mātrās are already correct. The heavy *mā* of *māhu* takes the place of two lights. Reading it uncontracted as **ma ahu** restores the syllabic pattern exactly:

```
ma  a   hu  si  ya  na  re  ndra sa  ttva sā  ro
L   L   L   L   L   L   G   L    G   L    G   G     = na na ra ya
```

So the metre favours scanning *mā(h)u* as two light syllables, the sandhi of *mā* + *ahu*, whatever the spelling in the witness. If the edition reads *māhu*, this may be worth an apparatus note.

### Pādas a and d

Both scan exactly with no adjustment. Chanda also flags pāda d as matching Mṛgendramukha, which shares the 13-syllable njjrg shape. The verse-level result settles it as the even pāda of Puṣpitāgrā.

## Raw chanda output

Ganas are given in chanda's Devanagari labels; ल = laghu, ग = guru.

```
saci mi imi viśiṣṭa naivarūpā

  LG: ल ल ल ल ल ल ग ल ग ल ग ग | syl 12 | matra 16 | gana ननरय
  exact: ['औपच्छन्दसिक = पुष्पिताग्रा']
varapraṇidhāna siyā khu bodhiprāpte /

  LG: ल ग ल ल ग ल ल ग ल ग ग ग ग | syl 13 | matra 20 | gana जजजमग
  exact: None
  fuzzy: [('मृगेन्द्रमुख', ('',)), ('औपच्छन्दसिक = पुष्पिताग्रा', ('2',))] 0.846
  fuzzy: [('तामरस', ('',))] 0.75
  fuzzy: [('द्रुतविलम्बित = हरिणप्लुत', ('',)), ('हरिणप्लुता', ('2',))] 0.75
māhu siya narendra sattvasāro

  LG: ग ल ल ल ल ग ल ग ल ग ग | syl 11 | matra 16 | gana भसजगग
  exact: None
  fuzzy: [('प्रहर्षिणी', ('',))] 0.846
  fuzzy: [('औपच्छन्दसिक = पुष्पिताग्रा', ('1',))] 0.833
  fuzzy: [('दोधक', ('',)), ('उपचित्र', ('2',)), ('वेगवती', ('2',))] 0.818
daśabaladhāri atulyadakṣiṇīyaḥ //

  LG: ल ल ल ल ग ल ल ग ल ग ल ग ग | syl 13 | matra 18 | gana नजजरग
  exact: ['मृगेन्द्रमुख', 'औपच्छन्दसिक = पुष्पिताग्रा']
VERSE: (['औपच्छन्दसिक = पुष्पिताग्रा'], 4.42948717948718)
   औपच्छन्दसिक = पुष्पिताग्रा 1.0
   मृगेन्द्रमुख 0.46153846153846156
   उद्गता 0.40454545454545454
```

## Reproduction

Script used (`run_chanda.py`). The main guard is needed because chanda's verse analysis starts worker processes, which crash on macOS without it. Run as `python3 run_chanda.py verse.txt` with the four lines above in `verse.txt`.

```python
import sys
from chanda import analyze_line, analyze_text
def main():
    lines=[l.strip(' /') for l in open(sys.argv[1]) if l.strip()]
    for l in lines:
        r=analyze_line(l, fuzzy=True)
        print(l); print('  LG:', ' '.join(r.lg), '| syl', r.length, '| matra', r.matra, '| gana', r.gana)
        print('  exact:', [n for n,_ in r.chanda] if r.found else None)
        for f in (r.fuzzy or [])[:3]:
            print('  fuzzy:', f.get('chanda'), round(f.get('similarity',0),3))
    res=analyze_text('\n'.join(lines), verse_mode=True, fuzzy=True)
    for v in res.result.verse:
        print('VERSE:', v.chanda)
        for s in v.scores[:3]:
            print('  ', s.name if hasattr(s,'name') else s, getattr(s,'match_extent',None))
if __name__=='__main__':
    main()
```
