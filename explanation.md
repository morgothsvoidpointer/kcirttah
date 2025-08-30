This document will explain the main thinking behind the code. 

* Import
  * Scaling for TS/TC
  * Output array
* Analysis of historical results
  * New tactics classification
  * Statistics as a representation of performance
  * The 'how far to go back' problem
  * Historical results output files
* Game theoretic analysis
* Group prediction
* New formations import - via clipboard
* Prediction of proposed lineups
* Future - minute by minute predictor

# Import

The data is imported through my CHPP credentials via the API. (Incidentally, my product on the CHPP is marked as 'declined' but I still have access). The package used is TODO by user TODO

## Match IDs

First of all, match IDs are imported for all seasons go back to February 2023. (It is possible, but not convenient, to change this start date). For each match, the match type is imported:

* Friendly
* CC group stage game X
* CC playoffs (QF,SF,F)
* WC qualifiers
* Nations Cup
* WC R1 game 1-10
* WC R2 game 1-6
* WC R3/R4/R5 game 1-3
* WC SF and F

For each match ID, we import match data:

* The two participants and their respective home/away/neutral/derby status
* Ratings (minute 0) incl IDFK
* Tactic played and rating
* Lineups with individual orders and player IDs
  * The player IDs are needed to find out speciality. Unfortunately, it is not possible to find the spex of players who are retired. They are just set as 'No Spec'.
  * Specs are encoded in a 16-character string corresponding to the 16 possible player positions. 'Z' stands for 'No Spec'. 'E' stands for the empty slot. Rest of specs are what you'd expect (first capital letter of spec name) except for the PDIM/PNF who are encoded with the lower case 'p' and the TDF who is encoded with the lower case 't'. 
  * Position is encoded: N-Normal, O-Offensitve, D-Defensive, M-Towards Middle, W-Towards Wing. Empty slots are encoded either with an 'E' or with a dash '-'.
* Formation is evaluated from the above data and is recorded as a separate string in form 'X-X-X'.
* The number of goals scored by the teams

## Importing TS and TC

Importing historic TS and TC was always a very painful point. As far as I know, Hattrick does not offer this functionality. There are three sites that aggregate those values:

* Duke's hattrick Portal
* ehffutbol
* Pernaug's prediction pages

My rather inelegant way is to scrape those webpages. Unfortunately, the format of the the first two pages makes it very difficult, with values accessible via what looks like plugins that run on the page. Ehffutbol worked until it didn't - my code hits a captcha and refuses to download anything. 

Pernaug's pages are the only ones that work at the moment, but if he stops, I am left high and dry.

Sometimes, the values are inaccurate. Duke's values were particularly bad for this - probably because he would run the import before or after midnight, meaning values were not always dated correctly. Pernaug's values are great and work 99.5% of the time.

If something goes wrong, the values will have to be imported manually. This involves cutting and pasting data manually from ehffutbol for each month over 3 years into a text file, which my code then parses in. Not too onerous, but very annoying.

# TS/TC evolution from the values

The main problem with those imported values is that they are not fractional. (Actually, Pernaug does calculate fractional values, but the others do not, and if we want to keep the code useable with integer values of TS we cannot rely on this). 

So, we have to mimic evolution of TS ourselves. Fortunately, the parameters are (almost) all known:

* The formula for daily updates (at 3AM HT time)
* The gains/losses of TS related to PIC/MOTS
* The resets
* The gains/losses of TC dependent on results

The code:

* Imports the TS/TC values
* Uses them to estimate the match attitude (PIC/PIN/MOTS)
* Uses that to reconstruct the evolution of team spirit
* The TC values can be evaluated exactly, as all parameters are known.

There are two issues with TS:

* We do not know the TS hits from dropping players. Usually, those are input manually by me in the code.
* Sometimes, we estimate match attitude wrong. This is alos hand-corrected.

A plot is generated showing how closely evaluated and actual TS figures match on days of competitive matches. This allows for hand correction.


