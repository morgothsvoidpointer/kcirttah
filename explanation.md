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

The import is handled by the file ht_ratings_export.py. Running the function ht_ratings_export in this file creates ratings array outputs for the opposition (nt_id) and our team (nt_id_mine). They are saved as files:

<nt_id>_ratings.csv and <nt_id_mine>_ratings.csv

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

## Scaling

Now that we have estimated fractional figures for TS and TC for every match day, we can scale the midfield and attack ratings accordingly:

* Extract current TS for today
* Use our value of TS on matchday we've constructed
* Scale the match ratings to be as if the match were played with the current TS
* Repeat the same for TC

## The output array

The output array - saved in file (nt id)_ratings.csv - has a large number of columns. It is uploaded to the repository. It can be examined visually or it can be kept to be used by other routines. 

The columns fall into 3 groups:

* Match-related columns - generally can be ignored, except for:
   * The match date (Match Date)
   * The Competition type (Competition)
   * The campaign id (campaign). Given as the first season of the campaign - e.g. the 92-93 campaign comes up as 92 
* Opposition-related columns. These are the statistics of the teams played by the team we are trying to examine. They are not used in any way and are of general interest with a sole exception of their number of goals (Actual goals_) used for updating confidence.
* Columns related to the team in question, whose ID is part of the file name.
   * Scaled midfield - midfield scaled by TS - at minute 0 (scaled_midfield)
   * Scaled attack - attack scaled by TC - at minute 0 (sc_ra/sc_ca/sc_la)
   * Defence ratings at minute 0 (Right defence/Central defence/Left defence)
   * IDFK (SP) ratings at minute 0 (ISP attack/ISP defence)
   * Formation at minute 0 (Formation)
   * Total Experience (Total exp)
   * Home/Away/Neutral/Derby (HomeOrAway)
   * Attitude - PIC/PIN/MOTS - not included at the moment but should be
   * Slider setting (style of play)
   * Indiv orders at minute 0 (Indiv Order)
   * Specs of starting lineup (spex)
   * Tactic played and rating (Tactic, Tactic skill)
   * Goals scored by team (Actual goals)
   * Our own special tactical classification. More on this later. (T_C)

# Analysis of historical results

Now that we have the past N performnances of two teams, nothing stops us from going ahead and putting them all pairwise into the prediction to calculate the W/L/D probabilities. We ignore friendlies and only consider competition games.

We use the nickarana predictor to do this in 4 cases:

* PIC vs PIN
* PIN vs PIC
* PIC vs PIC
* PIN vs PIN

We obviously do not need to do the last one, as the probabilities will be the same! This is something to address - and also need to include MOTS into the picture.

This creates an enormous amount of data. In several campaings a team will typically play over a 100 competitive games, creating 10000+ pairs of matches. Then, we need to worry about changes in attitude.

More precisely, our output is, given N competition matches for team A and M for team B:

* For each attitude combination (PIC, PIC), (PIC, PIN), (PIN, PIC), a MxN matrix W indicating the win percentage of team B (rows) vs team A (columns), and a corresponding matrix L for the win percentage of team A (rows) vs team B (columns). Each row and column corresponds to the match whose ratings were taken, scaled and put in the predictor.

## The old approach

The old approach was to group the matches - i.e. split the matrices W and L into blocks - by tactic - Normal, CA, Pressing, PC, LS. AIM and AOW were seen as part of tactic 'Normal'. Then, over each group

* (Tactic team A, attitude team A, Tactic team B, attitude team B)

we would take predictions satisfying those criteria and average the win chances. However, this gave overly optimistic predictions. This is because teams play suboptimally surprisingly often. Also, because our analysis does not take into account the quality of opposition those teams faced. What's good against a team you have a 4 level TS advantage over would be mediocre over a team you do not. 

As a result we still ended up considering recent matches individually and optimising strategy for a small number of recent matches. 

## The new approach

The new approach is to not use tactic as the only way of grouping matches togethe. This is the new grouping, which I will refer to as tactic-type:

### Balanced

A balanced approach (label 'bal') is the most standard approach to a match, it satisfies the following criteria:

* Normal, AOW or AIM tactic
* Slider between -0.51 and 0.76, 
* Not 343

### Attacking (att)

An approach that aims to attack without sacrificing midfield or totally abandoning defence. Typically, this would be a tactic someone would use against a CA if too chicken to play 343.

* Normal, AOW, AIM or PC tactic
* Slider above 0.75
* Not 343
* Two defence sectors 13+

### AoA

This is exactly what it says on the tin.

* Normal, AOW, AIM or PC tactic
* Slider above 0.75
* Not 343
* Two defence sectors 13-

### AoD

This is a defensive, cautious version of 'Balanced', where you've clearly come for a point.

* Any Pressing tactic
* Normal, AOW, AIM with slider below -0.5
* Not 343

This combines two different approaches - 541 press and 352 defensive. It may need further subdivision.

### 343

* Any 343, with any tactic

### PC

* Any PC that is not 343, att or AoA.
* This is to cover the 'Spanish-style' PC which is basically balanced+PC, but also the 'defensive 451 PC'

### LS

* Any LS tactic

### 442CA

This also needs splitting to differentiate between 442 with everyone Normal and 442 with weird variations such as sacrificing mf for wing attacks. This is still TODO

* CA
* 442 formation

### Hard CA (hardca)

* CA
* 541, 532, 523 or 443

## Notation

Let us consider just the PIC vs PIC case for simplicity. Others work in the same way.

To establish notation, for team A playing tactic-type A' and team B playing tactic-type B', we have a matrix W(A',B') indicating the win chances of team B and a matrix L(A',B') indicating the win chances of team A. 

 ## Statistics

For each W(A',B') we can look at various statistics:

* The mean of W(A',B').
* The standard deviation of W(A',B')
* Max and min, giving the range of W(A'B')
* Number of standard deviations of max away from mean

There are other things we could do, e.g. excluding obviously 'outlier' rows and columns. The basic principle however is to answer the following questions:

* How reliable is whatever statistic we pick at representing the matrix W(A',B')?
* How reliable is it at representing the probability of the outcome were one team to play A' and the other B', based on the data?
* Can we use this statistic to find the optimal choice of tactic A' for them and of tactic B' for us?

(A statistic here can be defined as any function f(W) mapping W(A',B') to a real value).

Any statistic involving the mean will dependend on standard deviation being 'tight', i.e. small. As we have seen in previous attempts to group past games, if you are expecting a CA and your win probability varies from 70% vs 532 to 40% vs 442 (this is a totally hypothetical example), that's not really useful to anyone at picking a tactic. 

We can first look at tightness of the range, max-min. If the range is 0.05, we are laughing - a 5% error in our mean is nothing to be upset about. If your opponent picks up 3 good IMs in form, he could very easily make that 5%, and that's just life. Typically, the range will be in the 10-12% bracket. This is because even if the starting lineups may be similar, the ratings are affected by the entire game - including inconvenient things such as subs, formation changes and red cards. (Note: check if my ratings are 0' or average!). They are of course also affected by form. A match in which your opponent played 352, had 2 players sent off and had poor form is not representative of the true strength of their 352 tomorrow. 

If we want to exclude outliers, the standard deviation is a better measure of tightness. The trouble with it is that it is usually very small across the board - 3-4%. But we can also see it as a positive and congratulate ourselves on finding consistent categories of match tactics! It really depends on whether you are a half full or half empty sort of person.

Tightness indicates how much we trust any statistic including the mean at being representative. So, if our mean win chance is based on W(bal,bal) for balanced vs balanced (essentially, 352 vs 352) is 40%, will that be representative of what the win chance will actually be in the game? 

I see 3 possible statistics to use, considering the standard deviation is 'tight' and especially if the range is 'tight':

* The mean. This is the standard choice.
* The mean plus the standard deviation. The choice if you are expecting opponents to raise their game for some reason - e.g. pick more players.
* The max provided it is not too many standard deviaitons away from the mean - if you want to be extra pessimistic about your chances.

## Recency

Another constant problem is - how recent a result needs to be to be relevant. This is an issue because on one hand we don't want to consider games from 2 years ago, but on the other some tactic-types will be so rarely played that you won't have enough data to construct a statistic. I settled on the following criteria, which are subject to revision:

* Last 50 competitive matches to be considered
* For each tactic-type, last 10 competitive matches considered

As a sanity check, we can track the mean and standard deviation as we increase the number of matches we consider and plot those quantities against time. If there is a big 'jerk' in the plots, it could mean something happened to the team that would make their results before a certain point in time irrelevant.

Both 'rolling' - i.e. over a sliding window - mean and 'mean from a point till now' can be tracked.

## Implementation

There is code implementing all of the above in the file ht_compare_history.py. The routine:

* Evaluates pairwise predictions. That usually takes a while.
* For each pair of attitudes (PIC-PIC, PIC-PIN, PIN-PIC), evaluates the matrices W and L for each pair of tactics and save them to Markdown with format win_<nt_id_mine>_vs_<nt_id>.csv and loss_<nt_id_mine>_vs_<nt_id>.csv
* Evaluate the matrices of means, sds, maxes and mins and save them to the file stats_<nt_id_mine>_vs_<nt_id>.csv
* Produce plots of time dependence of mean and sd

# Game theory
  


