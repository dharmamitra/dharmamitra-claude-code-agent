# frag.txt in the Jaina Dialectical Corpus: Extended Parallel Search and the Fragment's Situation

**Report date:** 2026-06-13
**Corpus searched:** `/Users/kengo_1/Documents/E-texts` (local Sanskrit library,
~all of `1_sanskr/` + `4_rellit/` + inbox/review folders), with Unicode-NFC
matching and `rg -uu` (a `.gitignore` at the repo root had silently excluded
the library from earlier sweeps — earlier "zero local hits" results were an
artefact).
**Outcome:** the fragment's argument chain has been found, expanded and partly
flagged as quotation, in **Abhayadevasūri's *Tattvabodhavidhāyinī*** (TBV, the
great 11th-c. Jaina commentary on Siddhasena Divākara's *Sammatitarka*; local
file `1_sanskr/4_rellit/jaina/siddhasena_sammatitarka.xml`). This is the
closest known witness to the fragment in any language and has direct
consequences for the reconstruction (Lacunae 5–8; see the revised
`output/reconstructions/frag.txt.md`).

---

## 1. Method

Two passes over the local corpus:

1. **Rare-lexeme sweep** for the fragment's most distinctive vocabulary
   (bhasmīkārya, punastambha, darśanayogyatā, kapālakāla, atipāpīya, atijaḍa,
   pūrvakālādi, anudbhāsamāna, svaparasambhavin, bhedoparati, punarupalambha,
   sadvyavahāra, paścāddarśana, ādhyāna, tatkarmatā, pūrvadṛś/pūrvadṛg,
   punardṛṣṭi, sphuṭarūpa, parasantāna, grāhyākāra).
2. **Term-matrix scoring** of the candidate witnesses thus surfaced
   (Jñānaśrīmitra's Nibandhāvalī, Prajñākaragupta's PVA, Ratnakīrti's
   Nibandhāvalī and Kṣaṇabhaṅgasiddhis, Jayanta's Nyāyamañjarī, Mallavādin/
   Siṃhasūri's Dvādaśāranayacakra, Prabhācandra's Nyāyakumudacandra, TBV).

### Result matrix (counts per witness)

| term | TBV | Jñānaśrī | PVA | Ratnakīrti | NMañj |
|---|---|---|---|---|---|
| pūrvadṛg- | **14** | 0 | 1 | 0 | 0 |
| pūrvadṛś- | **8** | 0 | 0 | 0 | 0 |
| pūrvakālādi | **5** | 0 | 3 | 0 | 0 |
| sphuṭarūpa | **5** | 0 | 1 | 0 | 0 |
| paścāddarśana | **3** | 0 | 1 | 0 | 1 |
| tatkarmatā | **2** | 0 | 0 | 0 | 4 |
| bhedoparati | **2** | 0 | 0 | 0 | 0 |
| kapālakāla | **2** | 0 | 0 | 0 | 2 |
| punardṛṣṭi- | **1** | 0 | 0 | 0 | 1 |
| parasantāna | 7 | 0 | 4 | 24 | 2 |

The fragment's hapax-like coinages (bhasmīkārya, punastambha, ādhyāna,
atipāpīya, atijaḍa, svaparasambhavin, anudbhāsamāna, *adyāpy āsta*) occur
**nowhere** in the corpus — consistent with the source being a lost work whose
exact wording survives only in the fragment itself.

---

## 2. The TBV parallels

All references are line numbers of the local XML (apparatus stripped); the
debate sits inside the TBV's *nayamīmāṃsā* section on pratyabhijñā and
kṣaṇabhaṅga. The printed edition's marginalia explicitly mark the voice:
"**kṣaṇakṣayavādī sthiratāvedaka-pratyabhijñāvādinaṃ pratyāha**."

### (a) TBV ~16350–16400 ↔ frag L7–L8 — the core match

TBV, in sequence:
1. dilemma: …tadā **varttamānataiva**, na pūrvāparadṛg-avagataikatvam;
2. "pūrvadarśanam **apetatvād asat** kathaṃ varttamānadarśane pratibhāti?
   tadapratibhāse ca **tadgrāhyatāpi pracyutatvād** na pratibhāti";
3. "yadi tu pūrvadṛg-anavagame 'pi tadgrāhyatā pratīyate, tathā sati
   **sakalātīta-dṛg-grāhyatāpi pratīyatām**" (the atiprasaṅga);
4. "**na hi nīlatā'pratipattau nīlo 'rtho 'dhigato bhavati**";
5. "svavedyatayā ca pratibhāsamānaḥ svavedya eva **nānyavedyaḥ**";
6. "na ca **pūrvadṛśo 'pāye tatkarmatā** arthasya **pracyutā** iti na bhāti
   tadgocaraḥ … apratibhāsanād anyathātiprasaṅga **ity ukteḥ**";
7. "**na ca bhinnaṃ pūrvadṛg-avagataṃ nāvabhāti, abhinnaṃ tu**
   tatpratibhāsaviṣayo 'vabhāsata eva … pūrvadṛṣṭatvād eva tasya na tatra
   pratibhāsaḥ — **tac cābhinne 'pi samānam**";
8. "na cābhinnasya pūrvadṛg-gocarasya **sannihitatvāt** pratibhāsaḥ …
   **tatsannidher evāsiddheḥ** | na ca samprati darśanāt tatsannidhisiddhiḥ —
   **itaretarāśrayadoṣāt**."

frag.txt L7–L8, in sequence: pūrvadṛśaś **cyutāyā** jñānāntar**āvedya**tvenā-
pratibhāsane **tatkarmmatā** ⟨lacuna 7⟩ … yadi ca pūrvadarśanabhānuṃ nīlaṃ
pratyakṣeneti tathā sati **bhinnam api pūrvadṛṣṭaṃ tatra bhāsatām** | atha
**bhedād eva na bhāsataḥ, abhinnaṃ** tat pūrvaṃ dṛṣṭaṃ bhāti | **nanu kiṃ
bhinnatvāt** | pūrvadṛṣṭe ghaṭādau na pratyakṣa⟨lacuna 8⟩.

Steps 2/6 = frag's pūrvadṛś-cyuti + tatkarmatā; step 5 = frag's
jñānāntarāvedyatva; step 7 = frag's bhinna/abhinna dilemma **including the
answer** to the fragment's elliptical "nanu kiṃ bhinnatvāt" ("that applies
equally to the non-different"); step 8 = the continuation beyond the
fragment's last preserved words. Step 3 supplies the atiprasaṅga that must
have stood in Lacuna 7; the "**ity ukteḥ**" in step 6 marks the chain as a
*statement of the (Buddhist) source* Abhayadeva is reporting.

### (b) TBV ~14108–14140 ↔ frag L4–L7

"darśanaṃ **sphuṭapratibhāsaṃ** vartamānārthaviṣayatayāvabhāti, smaraṇam apy
**aspaṣṭapratibhāsaṃ** bibhrāṇaṃ **parokṣollekhavad** ābhāti — tat katham ekaḥ
pratibhāsaḥ? pratibhāsanabhede ca rūpa-sparśa-saṃvidor iva **viṣayabhedaḥ**…";
"anyathā sarvatra **bhedoparatiprasaktiḥ**"; "tatrāpi **pūrvadṛg adhunā
nāstīti katham asati sā grāhikā**?"; "atha **tadevedam** iti
darśana-samānādhikaraṇatayā smṛtyutpatteḥ…".

↔ frag: "sa tarhi **pratibhāsabhedaḥ** … **bhedako 'stu**" (L4); "sarvatra
**bhedoparatiprasaṃgāt**" (L7); "**tad evedam** adyāpy āsta iti vyavasāyāt"
(L5); and the Lacuna 6 reconstruction (vivid nīla vs non-vivid pūrvatā = two
appearances) is attested here almost clause for clause.

### (c) TBV ~16638–16640 ↔ frag L6 and L3

"yogino 'pi tadā pratibhāsane tadaiva prakāśarūpasadbhāva iti **vartamānaiva
pūrvakālādiyogatā** bhavet **nātītā** | prakāśamānarūpavirahe ca na tadā
**pūrvakālādiyogitāyāḥ** pratibhāsanam ity **ekatvasyānupalabdher na
pratyabhijñā** kathañcid api sambhavinī … **tajjātīye tu punardarśanaṃ**
pravartate."

↔ frag L6: "yadi tv **apūrvakālādiyogi** tādṛśi pratibhāti, tathā sati …
**varttamānatvam eva | na pūrvatā**"; frag L3: "kintu **tajjātīya**s |
tathātrāpi tulya[jātīya]…". The compound *pūrvakālādi-yogin/-yogitā* is, to my
knowledge, attested only here and in the fragment.

### (d) TBV ~19176–19185 ↔ frag L1–L2

"na cānupalambhe sati **nañ-prayogābhyupagama** iti vaktavyam … atha svarūpāt
pracyutiḥ kathaṃ na **kapālakāle mudgarādihetukaṃ** bhāvāntaraṃ pracyutir
bhavet? atha **kapālakāle ghaṭavināśānabhyupagame** svabhāvata eva ghaṭasya …
kiyatkālāvasthānottarakāla-vināśa-lakṣaṇas tasya **mudgarādisannidhānakāle**
'pi bhāvāt…"

↔ frag L1–L2: vināśa at **kapālakāla** from **anupalambha**; anupalabdhi
**before the mudgara**; abhāva-usage (nañ/asad-vyavahāra). The TBV also runs
the "stays-a-while" trilemma familiar from Dharmottara's Kṣaṇabhaṅgasiddhi
(D4253 253b–254a).

### (e) The Jaina rejoinder, TBV ~19300–19345

Abhayadeva's own reply defends exactly what the fragment attacks: perception
*can* determine **pūrvakālāditva** of its present object without losing
pramāṇya ("yadi hy avidyamānaṃ pūrvakālāditvam … **vartamānāropeṇa** adhyakṣam
adhyavasyet tadā bhaved asya … aprāmāṇyam, etac ca nāsti"), supported by the
counting example (the cognition "one hundred" at the grasp of the last
countable). This confirms that the fragment's position was a live target for
the Jainas and that Abhayadeva had its argumentation — very possibly its text
— in front of him.

---

## 3. Where the fragment is situated — the consolidated picture

Triangulating all witnesses now known:

1. **Genre and lineage.** A Sanskrit kṣaṇabhaṅga polemic of the
   Dharmottara lineage: its L1–L2 (causeless vināśa, kapālakāla, anupalabdhi,
   Sāṃkhya) runs the argument of Dharmottara's *Kṣaṇabhaṅgasiddhi* (Tib.
   D4253) and *PVinṬ* (D4228 220a); its L3→L4 regress is shared nearly
   verbatim with Prajñākaragupta (SA_T11_prpva:7954); its L4–L8
   pratyabhijñā-refutation is the chain the TBV reports with "ity ukteḥ."

2. **Terminus post quem:** Prajñākaragupta (c. 800) — the kāryabheda-regress
   and the *sukhādi* framing presuppose the PVA milieu; the whole
   pūrvadṛś/tatkarmatā problematic presupposes Dharmottara (c. 740–800).

3. **Terminus ante quem:** Abhayadevasūri's TBV (late 10th – early 11th c.),
   which engages and partly reproduces the argumentation. The fragment's text
   (or its immediate source) circulated in the North-Indian debate pool that
   the Jaina dialecticians excerpted.

4. **Authorship hypothesis (unverifiable at present):** the compressed,
   sneering register (*atipāpīyaḥ*, *atijaḍaiḥ*, *tīrthyā yuktiḥ*), the
   Dharmottaran doctrine, and transmission via Jaina quotation all fit the
   profile of **Śaṅkaranandana** (c. 9th–10th c., most works lost/unedited) or
   another post-Dharmottara kṣaṇabhaṅga monograph of that circle. This cannot
   be checked against Śaṅkaranandana's unpublished manuscripts from here; it
   is recorded as a hypothesis, not a finding. What can be excluded:
   Vinītadeva's NBṬ (checked, retracted), Dharmottara's KBhS itself (extant in
   Tibetan, different text), Ratnakīrti and Jñānaśrīmitra (extant Sanskrit,
   different wording), TS/TSP, PVA, Arcaṭa (extant Sanskrit, no verbatim
   match).

5. **Relationship to the TBV.** Two scenarios remain open:
   (a) Abhayadeva worked directly from the fragment's text, paraphrasing with
   his usual expansion and citing turns of it ("ity ukteḥ");
   (b) both depend on a common source. Either way the TBV is the best
   independent control on the fragment's wording now available, and the only
   Sanskrit one.

## 4. Consequences for the reconstruction (applied 2026-06-13)

| Lacuna | Change | Basis |
|---|---|---|
| 5 | ○→◇, text unchanged | TBV: "na hi nīlatā'pratipattau nīlo 'rtho 'dhigato bhavati" — same axiom, same example |
| 6 | ○→◇, text unchanged | TBV: sphuṭa darśana vs aspaṣṭa smaraṇa = two pratibhāsas → viṣayabheda |
| 7 | **rewritten** (47/51 akṣ): ⟨kutaḥ? evaṃ hi sakalātītadṛśām api karmatā pratibhāyād ity atiprasaṅgaḥ \| tasmāt pūrvadṛṣṭatā smṛtisahakāriṇā manasā samāro⟩ ◇ | TBV preserves the atiprasaṅga step and flags the passage "ity ukteḥ" |
| 8 | **rewritten** (44/51 akṣ): ⟨ṃ pūrvadṛṣṭatayā pravartate, kiṃ tarhi sannidhānāt \| sannidhiś ca darśanād eva sidhyati, darśanaṃ ca sannidher itītaretarāśrayaḥ⟩ ◇ | TBV continues the same dilemma with the sannidhāna move and itaretarāśraya — the old two-pramāṇa closure was premature |

New confidence profile: **◆ 1 / ◇ 7 / ○ 0** (was ◆ 1 / ◇ 4 / ○ 3).

## 5. Loose ends worth pursuing

- **Vādidevasūri's *Syādvādaratnākara*** and **Prabhācandra's
  *Prameyakamalamārtaṇḍa*** (not in the local corpus in full) recycle the same
  Buddhist materials as the TBV and may preserve further wording.
- The TBV's *pratīka*-like turns ("ity ukteḥ", "iti vacanāt") could be
  collated systematically against the fragment to test scenario (a) above.
- Śaṅkaranandana's unpublished kṣaṇabhaṅga-related works (Vienna/Beijing
  projects) are the obvious external check on the authorship hypothesis.
- The local corpus `.gitignore` issue: any earlier "no local parallel" claims
  for *other* fragments (e.g. frag_ab) made via plain `rg` should be re-run
  with `-uu`.
